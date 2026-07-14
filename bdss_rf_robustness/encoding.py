from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

from .bdd import BDDManager
from .discretization import FeatureEncoding
from .forest import TreeModel, iter_leaf_paths


def leq_constant(manager: BDDManager, bit_names: Sequence[str], tau: int) -> int:
    """Encode binary value represented by bit_names as <= tau.

    bit_names are little-endian: bit_names[0] is the least significant bit.
    """
    if not bit_names:
        return manager.const(True)
    psi = manager.const(True)
    for j in range(len(bit_names)):
        bit = manager.var(bit_names[j])
        if ((tau >> j) & 1) == 0:
            psi = manager.land(manager.negate(bit), psi)
        else:
            psi = manager.lor(manager.negate(bit), psi)
    return psi


def node_test_bdd(manager: BDDManager, encodings: Sequence[FeatureEncoding], feature: int, threshold: float) -> int:
    enc = encodings[feature]
    tau = enc.threshold_cell(threshold)
    return leq_constant(manager, enc.bit_names, tau)


def path_bdd(manager: BDDManager, encodings: Sequence[FeatureEncoding], path) -> int:
    out = manager.const(True)
    for feature, threshold, take_left in path:
        test = node_test_bdd(manager, encodings, feature, threshold)
        out = manager.land(out, test if take_left else manager.negate(test))
    return out


def tree_leaf_bdds(manager: BDDManager, encodings: Sequence[FeatureEncoding], tree: TreeModel):
    leaves = []
    for label, path in iter_leaf_paths(tree):
        leaves.append((label, path_bdd(manager, encodings, path)))
    return leaves

