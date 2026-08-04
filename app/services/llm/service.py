"""LLM reasoning service.

Uses OpenRouter (OpenAI-compatible) when an API key is configured; otherwise
falls back to a deterministic, transparent summary built from the real
signal values — never hallucinated.
"""
from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def available(self) -> bool:
        return bool(self.settings.OPENROUTER_API_KEY)

    async def summarize(self, system_prompt: str, user_prompt: str, max_tokens: int = 700) -> str:
        if not self.available:
            return self._deterministic_fallback(user_prompt)
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self.settings.OPENROUTER_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/hermes-crypto-pilot",
                    },
                    json={
                        "model": self.settings.LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "max_tokens": max_tokens,
                        "temperature": 0.3,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM call failed, using fallback: %s", exc)
            return self._deterministic_fallback(user_prompt)

    async def explain_signal(self, signal_summary: str) -> str:
        return await self.summarize(
            system_prompt=(
                "You are the head research analyst for a crypto intelligence platform. "
                "Explain trade signals clearly, honestly, and concisely in under 150 words. "
                "Never fabricate data; only reason from the numbers provided. Note uncertainties."
            ),
            user_prompt=signal_summary,
        )

    async def daily_market_report(self, digest: str) -> str:
        return await self.summarize(
            system_prompt=(
                "You are a professional market analyst writing a daily crypto intelligence "
                "report for investors. Be precise, balanced, and structured. Under 300 words."
            ),
            user_prompt=digest,
            max_tokens=1200,
        )

    @staticmethod
    def _deterministic_fallback(user_prompt: str) -> str:
        return (
            "Summary generated deterministically (no LLM key configured). Based on the "
            f"provided signal values:\n\n{user_prompt}\n\n"
            "Recommendation: weight position sizes to risk metrics; the highest-confidence "
            "signals are those where technical, consensus, and sentiment probabilities align."
        )
