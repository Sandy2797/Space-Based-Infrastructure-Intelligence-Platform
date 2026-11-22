"""Reusable evaluation metrics (Month 1 design version).

Undefined results (zero denominator) are returned as None, never as 0 or 1.
"""
from __future__ import annotations
from collections import Counter
from typing import Sequence, Hashable


def _div(n: float, d: float):
    return None if d == 0 else n / d


def confusion_matrix(y_true: Sequence[Hashable], y_pred: Sequence[Hashable], labels=None):
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    labels = list(labels) if labels is not None else sorted(set(y_true) | set(y_pred), key=str)
    counts = Counter(zip(y_true, y_pred))
    return labels, [[counts[(t, p)] for p in labels] for t in labels]


def precision_recall_f1(tp: int, fp: int, fn: int):
    p = _div(tp, tp + fp)
    r = _div(tp, tp + fn)
    f1 = None if p is None or r is None or (p + r) == 0 else 2 * p * r / (p + r)
    return p, r, f1


def per_class_metrics(y_true, y_pred, labels=None):
    labels, m = confusion_matrix(y_true, y_pred, labels)
    out = {}
    for i, lab in enumerate(labels):
        tp = m[i][i]
        fp = sum(m[r][i] for r in range(len(labels))) - tp
        fn = sum(m[i]) - tp
        p, r, f1 = precision_recall_f1(tp, fp, fn)
        out[lab] = {"precision": p, "recall": r, "f1": f1, "support": sum(m[i])}
    return out


def macro_f1(y_true, y_pred, labels=None):
    f1s = [v["f1"] for v in per_class_metrics(y_true, y_pred, labels).values()]
    if any(f is None for f in f1s):
        return None  # at least one class undefined: report it, do not hide it
    return sum(f1s) / len(f1s)


def iou(box_a, box_b):
    """Boxes as (xmin, ymin, xmax, ymax)."""
    ix = max(0.0, min(box_a[2], box_b[2]) - max(box_a[0], box_b[0]))
    iy = max(0.0, min(box_a[3], box_b[3]) - max(box_a[1], box_b[1]))
    inter = ix * iy
    area = lambda b: max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    return _div(inter, area(box_a) + area(box_b) - inter)


def mae(y_true, y_pred):
    return _div(sum(abs(a - b) for a, b in zip(y_true, y_pred)), len(y_true))


def rmse(y_true, y_pred):
    v = _div(sum((a - b) ** 2 for a, b in zip(y_true, y_pred)), len(y_true))
    return None if v is None else v ** 0.5


def chronological_split(dates, values, cutoff):
    """Train on dates < cutoff, test on dates >= cutoff. No shuffling."""
    pairs = sorted(zip(dates, values))
    train = [p for p in pairs if p[0] < cutoff]
    test = [p for p in pairs if p[0] >= cutoff]
    return train, test


def persistence_forecast(train_values, horizon):
    return [train_values[-1]] * horizon
