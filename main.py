"""Hermes entrypoint: `python main.py api` starts the server;
`python main.py` runs the agent swarm from the CLI."""
import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn

logging.basicConfig(level=logging.INFO)


async def run_cli():
    from app.db.session import init_db
    from app.agents.supervisor import SupervisorAgent

    await init_db()
    supervisor = SupervisorAgent()
    assets = ["BTC", "ETH"]
    for asset in assets:
        print(f"\n=== Running Hermes workflow for {asset} ===")
        try:
            result = await supervisor.run_workflow(asset, interval="15m")
            rec = result.get("recommendation", {})
            print(
                f"  Direction: {rec.get('direction')}  "
                f"Position: ${rec.get('suggested_position'):,.2f}  "
                f"Risk: {rec.get('risk_level')}"
            )
            print(f"  Rationale: {rec.get('rationale')}")
        except Exception as exc:  # noqa: BLE001
            print(f"  Workflow failed: {exc}")
        print("-" * 60)


def run_api():
    from app.core.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "app.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        run_api()
    else:
        asyncio.run(run_cli())
