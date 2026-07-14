from __future__ import annotations

import math
import random
from collections import Counter
from typing import Dict, Iterable, List, Sequence

from .bdd import BDDManager


def entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


def solution_bdd(manager: BDDManager, state_bdds: Dict[tuple, int]) -> int:
    out = manager.const(False)
    for bdd in state_bdds.values():
        out = manager.lor(out, bdd)
    return out


def information_gain_scores(manager: BDDManager, root: int, variables: Sequence[str]) -> Dict[str, float]:
    total = manager.count_models(root, variables)
    if total == 0:
        return {v: 0.0 for v in variables}
    scores = {}
    for var in variables:
        high = manager.count_models(manager.restrict(root, var, 1), variables)
        scores[var] = entropy(high / total)
    return scores


def p_value_scores(manager: BDDManager, root: int, variables: Sequence[str]) -> Dict[str, float]:
    """Return a simple chi-square strength score; larger means stronger association.

    The assignment asks to minimize p-value. To avoid SciPy as a dependency,
    this function returns the chi-square statistic, which has the same ordering
    for this 2x2 test.
    """
    total_models = 2 ** len(variables)
    sat = manager.count_models(root, variables)
    unsat = total_models - sat
    scores = {}
    for var in variables:
        sat1 = manager.count_models(manager.restrict(root, var, 1), variables)
        sat0 = sat - sat1
        all1 = total_models // 2
        all0 = total_models // 2
        unsat1 = all1 - sat1
        unsat0 = all0 - sat0
        rows = [sat, unsat]
        cols = [all1, all0]
        obs = [[sat1, sat0], [unsat1, unsat0]]
        stat = 0.0
        for i in range(2):
            for j in range(2):
                exp = rows[i] * cols[j] / total_models if total_models else 0
                if exp > 0:
                    stat += (obs[i][j] - exp) ** 2 / exp
        scores[var] = stat
    return scores


def shapley_scores(manager: BDDManager, root: int, variables: Sequence[str], samples: int = 64, seed: int = 0) -> Dict[str, float]:
    """Monte-Carlo Shapley approximation for the coalition count game.

    A coalition fixes its variables to 1 and leaves the others free. The value is
    the number of satisfying extensions.
    """
    rng = random.Random(seed)
    scores = {v: 0.0 for v in variables}

    def value(coalition):
        bdd = root
        for var in coalition:
            bdd = manager.restrict(bdd, var, 1)
        free = [v for v in variables if v not in coalition]
        return manager.count_models(bdd, free)

    for _ in range(max(1, samples)):
        order = list(variables)
        rng.shuffle(order)
        coalition = set()
        prev = value(coalition)
        for var in order:
            coalition.add(var)
            cur = value(coalition)
            scores[var] += cur - prev
            prev = cur
    return {v: s / max(1, samples) for v, s in scores.items()}


def select_variable(
    manager: BDDManager,
    state_bdds: Dict[tuple, int],
    free_variables: Sequence[str],
    strategy: str,
    seed: int = 0,
) -> str:
    root = solution_bdd(manager, state_bdds)
    support = [v for v in free_variables if v in manager.support(root)]
    candidates = support or list(free_variables)
    if not candidates:
        raise ValueError("No free variable is available for splitting")

    if strategy == "info_gain":
        scores = information_gain_scores(manager, root, candidates)
        return max(candidates, key=lambda v: (scores[v], -manager.level[v]))
    if strategy == "p_value":
        scores = p_value_scores(manager, root, candidates)
        return max(candidates, key=lambda v: (scores[v], -manager.level[v]))
    if strategy == "shapley":
        scores = shapley_scores(manager, root, candidates, seed=seed)
        return max(candidates, key=lambda v: (abs(scores[v]), -manager.level[v]))
    if strategy == "random_node":
        vars_by_node = [v for v in manager.node_variables(root) if v in candidates]
        return random.Random(seed).choice(vars_by_node or candidates)
    if strategy == "modal":
        counts = Counter(v for v in manager.node_variables(root) if v in candidates)
        if not counts:
            return candidates[0]
        return max(candidates, key=lambda v: (counts[v], -manager.level[v]))
    raise ValueError(f"Unknown selector strategy {strategy!r}")

