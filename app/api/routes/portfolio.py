"""Portfolio endpoints (auth-protected). Real positions, marked to live market."""
from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUserDep, SessionDep
from app.db.models import Portfolio, Position, User
from app.domain.risk import PortfolioRiskMetrics
from app.services.market.manager import MarketDataManager
from app.services.risk import metrics as M

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

market = MarketDataManager()


class PositionCreate(BaseModel):
    asset: str = Field(min_length=1, max_length=16)
    quantity: float = Field(gt=0)
    entry_price: float | None = None
    side: str = "long"


async def _get_or_create_portfolio(session, user: User) -> Portfolio:
    result = await session.execute(
        select(Portfolio).where(Portfolio.user_id == user.id).limit(1)
    )
    portfolio = result.scalar_one_or_none()
    if portfolio is None:
        portfolio = Portfolio(user_id=user.id, name="Main Portfolio", cash_balance=10_000.0)
        session.add(portfolio)
        await session.commit()
        await session.refresh(portfolio)
    return portfolio


@router.get("")
async def get_portfolio(user: CurrentUserDep, session: SessionDep):
    portfolio = await _get_or_create_portfolio(session, user)
    positions = await _marked_positions(session, portfolio)
    return await _portfolio_summary(portfolio, positions)


@router.get("/positions")
async def get_positions(user: CurrentUserDep, session: SessionDep):
    portfolio = await _get_or_create_portfolio(session, user)
    return await _marked_positions(session, portfolio)


@router.post("/positions", status_code=201)
async def add_position(
    payload: PositionCreate, user: CurrentUserDep, session: SessionDep
):
    portfolio = await _get_or_create_portfolio(session, user)
    asset = payload.asset.upper()
    try:
        ticker = await market.get_ticker(asset)
        current_price = ticker.price
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Could not fetch price for {asset}: {exc}") from exc

    entry = payload.entry_price or current_price
    position = Position(
        portfolio_id=portfolio.id,
        asset=asset,
        symbol=f"{asset}USDT",
        side=payload.side,
        quantity=payload.quantity,
        entry_price=entry,
        current_price=current_price,
    )
    session.add(position)
    await session.commit()
    await session.refresh(position)
    return {
        "id": str(position.id),
        "asset": position.asset,
        "quantity": position.quantity,
        "entry_price": position.entry_price,
        "current_price": current_price,
    }


@router.get("/risk", response_model=PortfolioRiskMetrics)
async def portfolio_risk(user: CurrentUserDep, session: SessionDep):
    portfolio = await _get_or_create_portfolio(session, user)
    positions = await _marked_positions(session, portfolio)
    return await _risk_metrics(positions)


async def _marked_positions(session, portfolio) -> list[dict]:
    result = await session.execute(
        select(Position).where(Position.portfolio_id == portfolio.id)
    )
    positions = list(result.scalars())
    out = []
    for p in positions:
        try:
            ticker = await market.get_ticker(p.asset)
            price = ticker.price
        except Exception:
            price = p.current_price or p.entry_price
        if p.side == "long":
            pnl = (price - p.entry_price) * p.quantity
        else:
            pnl = (p.entry_price - price) * p.quantity
        pnl_pct = (pnl / (p.entry_price * p.quantity)) * 100 if p.entry_price else 0.0
        out.append(
            {
                "id": str(p.id),
                "asset": p.asset,
                "side": p.side,
                "quantity": p.quantity,
                "entry_price": p.entry_price,
                "current_price": price,
                "value": price * p.quantity,
                "unrealized_pnl": round(pnl, 2),
                "unrealized_pnl_pct": round(pnl_pct, 2),
            }
        )
    return out


async def _portfolio_summary(portfolio: Portfolio, positions: list[dict]) -> dict:
    total_value = portfolio.cash_balance + sum(p["value"] for p in positions)
    unrealized = sum(p["unrealized_pnl"] for p in positions)
    invested = sum(p["entry_price"] * p["quantity"] for p in positions)
    pnl_pct = (unrealized / invested * 100) if invested else 0.0
    allocation = {p["asset"]: p["value"] for p in positions}

    risk_metrics = await _risk_metrics(positions)
    return {
        "total_value": round(total_value, 2),
        "cash_balance": round(portfolio.cash_balance, 2),
        "total_pnl": round(unrealized, 2),
        "total_pnl_pct": round(pnl_pct, 2),
        "unrealized_pnl": round(unrealized, 2),
        "realized_pnl": round(portfolio.cash_balance - 10_000.0, 2),
        "positions": positions,
        "allocation": allocation,
        "diversification_score": risk_metrics["diversification_score"],
        "risk_score": risk_metrics["risk_score"],
    }


async def _risk_metrics(positions: list[dict]) -> dict:
    assets = sorted({p["asset"] for p in positions})
    returns_by_asset: dict[str, np.ndarray] = {}
    for asset in assets:
        try:
            candles = await market.get_klines(asset, "15m", 300)
            prices = np.array([c.close for c in candles])
            ret = M.log_returns(prices)
            returns_by_asset[asset] = ret
        except Exception:
            returns_by_asset[asset] = np.array([])

    allocation = {p["asset"]: p["value"] for p in positions}
    correlation = M.correlation_matrix(returns_by_asset)
    div_score = M.diversification_score(allocation, correlation)

    # Portfolio-level returns (equal-weight blend for estimation)
    aligned: list[np.ndarray] = [r for r in returns_by_asset.values() if len(r) > 2]
    portfolio_returns = np.mean(np.vstack([r[-min(len(r) for r in aligned):] for r in aligned]), axis=0) if aligned else np.array([])
    var95 = M.value_at_risk(portfolio_returns, 0.95) if len(portfolio_returns) else 0.0
    sharpe = M.sharpe_ratio(portfolio_returns) if len(portfolio_returns) else 0.0

    total_value = sum(p["value"] for p in positions)
    vol_component = min(1.0, abs(var95) * 10.0)
    conc_component = 1.0 - div_score
    risk_score = round(0.5 * vol_component + 0.5 * conc_component, 4)

    return {
        "total_value": round(total_value, 2),
        "total_pnl": round(sum(p["unrealized_pnl"] for p in positions), 2),
        "total_pnl_pct": round(sum(p["unrealized_pnl_pct"] for p in positions), 2),
        "realized_pnl": 0.0,
        "unrealized_pnl": round(sum(p["unrealized_pnl"] for p in positions), 2),
        "risk_score": risk_score,
        "diversification_score": div_score,
        "correlation_matrix": correlation,
        "allocation": allocation,
        "var_95": round(var95, 6),
        "sharpe_ratio": round(sharpe, 4),
    }
