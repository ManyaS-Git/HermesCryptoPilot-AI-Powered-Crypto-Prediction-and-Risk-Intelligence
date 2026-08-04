"""Probability calibration.

- ``platt_scaling``: fits a logistic regression on the logit of raw model
  probabilities against realised outcomes (classic Platt scaling).
- ``shrinkage``: when there is too little outcome history, probabilities are
  shrunk toward 0.5 proportionally to available evidence to prevent
  overconfidence — never random.
"""
from __future__ import annotations

import numpy as np


def platt_scaling(
    probabilities: np.ndarray, outcomes: np.ndarray
) -> "Callable[[np.ndarray], np.ndarray]":
    """Fit Platt scaling and return a calibrator callable.

    ``probabilities``: raw model probabilities (0..1).
    ``outcomes``: realised binary outcomes (0/1) aligned with probabilities.
    Requires >= 20 samples and both classes present.
    """
    from sklearn.linear_model import LogisticRegression

    probs = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    y = np.asarray(outcomes, dtype=int)

    if len(probs) < 20 or len(np.unique(y)) < 2:
        return None

    logit = np.log(probs / (1.0 - probs)).reshape(-1, 1)
    model = LogisticRegression(C=1.0)
    model.fit(logit, y)

    def calibrator(raw: np.ndarray) -> np.ndarray:
        raw = np.clip(np.asarray(raw, dtype=float), 1e-6, 1 - 1e-6)
        logits = np.log(raw / (1.0 - raw)).reshape(-1, 1)
        return model.predict_proba(logits)[:, 1]

    return calibrator


def shrink_probability(probability: float, sample_count: int, strength: float = 0.15) -> float:
    """Shrink a probability toward 0.5 when evidence is scarce."""
    if sample_count <= 0:
        return 0.5
    alpha = min(1.0, sample_count * strength)
    return float(0.5 * (1.0 - alpha) + probability * alpha)


def expected_calibrated_probability(
    raw_probability: float, history_probs: np.ndarray, history_outcomes: np.ndarray
) -> tuple[float, str, int]:
    """Calibrate a raw probability using available outcome history.

    Returns ``(calibrated_probability, method, samples_used)``.
    """
    samples = int(len(history_probs))
    if samples >= 20 and len(np.unique(history_outcomes)) >= 2:
        calibrator = platt_scaling(history_probs, history_outcomes)
        if calibrator is not None:
            return float(np.clip(calibrator(np.array([raw_probability]))[0], 0.01, 0.99)), "platt_scaling", samples
    return shrink_probability(raw_probability, samples), "shrinkage", samples
