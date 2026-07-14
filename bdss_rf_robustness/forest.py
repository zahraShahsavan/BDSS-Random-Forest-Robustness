from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd


@dataclass
class TreeNode:
    feature: int
    threshold: float
    left: int
    right: int
    label: object | None = None


@dataclass
class TreeModel:
    nodes: Dict[int, TreeNode]


@dataclass
class ForestModel:
    trees: List[TreeModel]
    labels: List[object]
    feature_names: List[str]
    target_name: str


def load_pickle(path: Path):
    try:
        import joblib

        return joblib.load(path)
    except Exception:
        import pickle

        with open(path, "rb") as fh:
            return pickle.load(fh)


def unwrap_random_forest(obj):
    """Return the RandomForestClassifier object from common saved formats.

    The assignment says files are named ``*_rf.pkl``, but some packages save a
    dictionary with metadata around the estimator instead of the estimator
    directly. This helper accepts both forms.
    """
    if hasattr(obj, "estimators_"):
        return obj
    if isinstance(obj, dict):
        preferred_keys = [
            "model",
            "rf",
            "random_forest",
            "classifier",
            "clf",
            "estimator",
            "best_estimator",
            "best_estimator_",
        ]
        for key in preferred_keys:
            value = obj.get(key)
            if hasattr(value, "estimators_"):
                return value
        for value in obj.values():
            if hasattr(value, "estimators_"):
                return value
    raise TypeError(
        "Could not find a scikit-learn RandomForest object in the pickle. "
        f"Loaded object type: {type(obj).__name__}. "
        "If it is a dict, expected one value to have an 'estimators_' attribute."
    )


def load_dataset_frame(dataset_dir: Path, name: str, split: str) -> pd.DataFrame:
    return pd.read_csv(dataset_dir / name / f"{name}_{split}.csv")


def load_sklearn_forest(datasets_dir: Path, name: str) -> ForestModel:
    dataset_dir = datasets_dir / name
    train = pd.read_csv(dataset_dir / f"{name}_train.csv")
    target_name = train.columns[-1]
    feature_names = list(train.columns[:-1])
    rf = unwrap_random_forest(load_pickle(dataset_dir / f"{name}_rf.pkl"))
    labels = list(getattr(rf, "classes_", sorted(train[target_name].unique())))
    trees: List[TreeModel] = []

    for estimator in rf.estimators_:
        sk_tree = estimator.tree_
        nodes: Dict[int, TreeNode] = {}
        for idx in range(sk_tree.node_count):
            left = int(sk_tree.children_left[idx])
            right = int(sk_tree.children_right[idx])
            if left == right or left < 0:
                counts = sk_tree.value[idx][0]
                label = labels[int(np.argmax(counts))]
                nodes[idx] = TreeNode(feature=-1, threshold=0.0, left=-1, right=-1, label=label)
            else:
                nodes[idx] = TreeNode(
                    feature=int(sk_tree.feature[idx]),
                    threshold=float(sk_tree.threshold[idx]),
                    left=left,
                    right=right,
                    label=None,
                )
        trees.append(TreeModel(nodes))
    return ForestModel(trees=trees, labels=labels, feature_names=feature_names, target_name=target_name)


def iter_leaf_paths(tree: TreeModel):
    """Yield (label, path), where path is [(feature, threshold, take_left), ...]."""

    def rec(node_id: int, path):
        node = tree.nodes[node_id]
        if node.label is not None:
            yield node.label, path
            return
        yield from rec(node.left, path + [(node.feature, node.threshold, True)])
        yield from rec(node.right, path + [(node.feature, node.threshold, False)])

    yield from rec(0, [])
