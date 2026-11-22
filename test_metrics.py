import pytest
from metrics import *


def test_confusion_and_per_class():
    y_true = ["human", "human", "natural", "natural", "natural"]
    y_pred = ["human", "natural", "natural", "natural", "human"]
    labels, m = confusion_matrix(y_true, y_pred, ["human", "natural"])
    assert m == [[1, 1], [1, 2]]
    pc = per_class_metrics(y_true, y_pred, ["human", "natural"])
    assert pc["human"]["precision"] == pytest.approx(0.5)
    assert pc["natural"]["recall"] == pytest.approx(2 / 3)
    assert macro_f1(y_true, y_pred, ["human", "natural"]) == pytest.approx((0.5 + 2 / 3) / 2)


def test_undefined_is_none():
    assert precision_recall_f1(0, 0, 0) == (None, None, None)
    assert precision_recall_f1(0, 0, 3)[0] is None


def test_macro_f1_undefined_class():
    assert macro_f1(["a", "a"], ["a", "a"], ["a", "b"]) is None


def test_iou():
    assert iou((0, 0, 2, 2), (1, 1, 3, 3)) == pytest.approx(1 / 7)
    assert iou((0, 0, 1, 1), (2, 2, 3, 3)) == 0.0


def test_mae_rmse():
    assert mae([1, 2, 3], [1, 2, 5]) == pytest.approx(2 / 3)
    assert rmse([0, 0], [3, 4]) == pytest.approx((12.5) ** 0.5)


def test_chronological_split_no_leak():
    train, test = chronological_split([3, 1, 2, 4], [30, 10, 20, 40], 3)
    assert max(d for d, _ in train) < min(d for d, _ in test)


def test_persistence():
    assert persistence_forecast([1, 2, 7], 3) == [7, 7, 7]


def test_length_mismatch():
    with pytest.raises(ValueError):
        confusion_matrix([1], [1, 2])
