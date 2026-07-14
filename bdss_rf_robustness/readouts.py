from __future__ import annotations

from typing import Dict, List, Sequence

import pandas as pd

from .bdd import BDDManager
from .composition import FrontierLeaf, win_bdd_for_label
from .discretization import FeatureEncoding, sample_to_bits
from .forest import ForestModel
from .selectors import information_gain_scores, p_value_scores, shapley_scores, solution_bdd


def aggregate_solution_bdd(manager: BDDManager, leaves: Sequence[FrontierLeaf]) -> int:
    out = manager.const(False)
    for leaf in leaves:
        out = manager.lor(out, solution_bdd(manager, leaf.state_bdds))
    return out


def variable_rankings(manager: BDDManager, leaves: Sequence[FrontierLeaf], input_bits: Sequence[str]) -> pd.DataFrame:
    root = aggregate_solution_bdd(manager, leaves)
    ig = information_gain_scores(manager, root, input_bits)
    pv = p_value_scores(manager, root, input_bits)
    sh = shapley_scores(manager, root, input_bits)
    rows = []
    for bit in input_bits:
        rows.append({"bit": bit, "information_gain": ig.get(bit, 0.0), "shapley": sh.get(bit, 0.0), "p_value_strength": pv.get(bit, 0.0)})
    return pd.DataFrame(rows).sort_values(["information_gain", "p_value_strength"], ascending=False)


def robustness_for_sample(
    manager: BDDManager,
    forest: ForestModel,
    leaves: Sequence[FrontierLeaf],
    encodings: Sequence[FeatureEncoding],
    row,
    input_bits: Sequence[str],
) -> List[dict]:
    reference = sample_to_bits(row, encodings)
    charged = set(input_bits)
    rows = []
    for label in forest.labels:
        best_distance = float("inf")
        best_changes = {}
        for leaf in leaves:
            entry_cost = sum(1 for bit, value in leaf.assignment.items() if reference.get(bit, 0) != value)
            win_root = win_bdd_for_label(manager, leaf, forest.labels, label)
            dist, assignment = manager.shortest_distance(win_root, reference, charged)
            total = entry_cost + dist
            if total < best_distance:
                best_distance = total
                best_changes = {bit: val for bit, val in assignment.items() if bit in charged and reference.get(bit, 0) != val}
        rows.append({"target_label": label, "robustness": best_distance, "changed_bits": ",".join(sorted(best_changes))})
    finite = [r["robustness"] for r in rows if r["robustness"] != float("inf")]
    untargeted = min((r["robustness"] for r in rows if r["robustness"] > 0), default=float("inf"))
    for r in rows:
        r["untargeted_radius"] = untargeted
    return rows

