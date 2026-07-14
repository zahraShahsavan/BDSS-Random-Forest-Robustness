from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from .bdd import BDDManager
from .encoding import tree_leaf_bdds
from .forest import ForestModel
from .discretization import FeatureEncoding
from .selectors import select_variable


@dataclass
class FrontierLeaf:
    assignment: Dict[str, int]
    state_bdds: Dict[Tuple[int, ...], int]
    next_tree: int


@dataclass
class ComposeStats:
    peak_nodes: int = 0
    splits: int = 0
    trees_composed: int = 0


def state_size(manager: BDDManager, state_bdds: Dict[tuple, int]) -> int:
    return sum(manager.node_count(bdd) for bdd in state_bdds.values())


def compose_one_tree(manager: BDDManager, state_bdds, leaf_bdds, label_to_idx):
    new: Dict[Tuple[int, ...], int] = {}
    for state, state_root in state_bdds.items():
        for label, leaf_root in leaf_bdds:
            idx = label_to_idx[label]
            next_state = list(state)
            next_state[idx] += 1
            next_state = tuple(next_state)
            term = manager.land(state_root, leaf_root)
            if term == 0:
                continue
            new[next_state] = manager.lor(new.get(next_state, 0), term)
    return new


def restrict_state_bdds(manager: BDDManager, state_bdds, var: str, value: int):
    return {state: manager.restrict(root, var, value) for state, root in state_bdds.items() if manager.restrict(root, var, value) != 0}


def budgeted_compose(
    manager: BDDManager,
    forest: ForestModel,
    encodings: Sequence[FeatureEncoding],
    tree_count: int,
    budget: int,
    selector: str,
    input_bits: Sequence[str],
    seed: int = 0,
) -> Tuple[List[FrontierLeaf], ComposeStats]:
    label_to_idx = {label: i for i, label in enumerate(forest.labels)}
    leaf_cache = [tree_leaf_bdds(manager, encodings, tree) for tree in forest.trees[:tree_count]]
    initial = {tuple(0 for _ in forest.labels): manager.const(True)}
    frontier = [FrontierLeaf({}, initial, 0)]
    final: List[FrontierLeaf] = []
    stats = ComposeStats()

    while frontier:
        item = frontier.pop()
        state_bdds = item.state_bdds
        t = item.next_tree
        while t < tree_count:
            branch_leaf_bdds = [
                (label, manager.restrict_many(root, item.assignment))
                for label, root in leaf_cache[t]
            ]
            candidate = compose_one_tree(manager, state_bdds, branch_leaf_bdds, label_to_idx)
            size = state_size(manager, candidate)
            stats.peak_nodes = max(stats.peak_nodes, size)
            if size > budget and len(item.assignment) < len(input_bits):
                free = [v for v in input_bits if v not in item.assignment]
                split_var = select_variable(manager, state_bdds, free, selector, seed + stats.splits)
                for value in (1, 0):
                    child_assignment = dict(item.assignment)
                    child_assignment[split_var] = value
                    child_states = restrict_state_bdds(manager, state_bdds, split_var, value)
                    if child_states:
                        frontier.append(FrontierLeaf(child_assignment, child_states, t))
                stats.splits += 1
                break
            state_bdds = candidate
            t += 1
            stats.trees_composed = max(stats.trees_composed, t)
        else:
            final.append(FrontierLeaf(item.assignment, state_bdds, t))

    return final, stats


def winning_label_for_state(state: Tuple[int, ...], labels: Sequence[object]):
    max_votes = max(state)
    return labels[state.index(max_votes)]


def win_bdd_for_label(manager: BDDManager, leaf: FrontierLeaf, labels: Sequence[object], label) -> int:
    out = manager.const(False)
    for state, root in leaf.state_bdds.items():
        if winning_label_for_state(state, labels) == label:
            out = manager.lor(out, root)
    return out
