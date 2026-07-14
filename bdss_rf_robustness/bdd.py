from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class BDDNode:
    var: Optional[str]
    low: int
    high: int


class BDDManager:
    """Small reduced ordered BDD manager.

    Node 0 is false, node 1 is true. All other nodes are canonical for the
    configured variable order.
    """

    def __init__(self, variable_order: Sequence[str]):
        self.variable_order = list(variable_order)
        self.level = {v: i for i, v in enumerate(self.variable_order)}
        self.nodes: List[BDDNode] = [
            BDDNode(None, 0, 0),
            BDDNode(None, 1, 1),
        ]
        self.unique: Dict[Tuple[str, int, int], int] = {}
        self._apply_cache: Dict[Tuple[str, int, int], int] = {}
        self._not_cache: Dict[int, int] = {}
        self._restrict_cache: Dict[Tuple[int, str, int], int] = {}

    def const(self, value: bool) -> int:
        return 1 if value else 0

    def var(self, name: str) -> int:
        if name not in self.level:
            raise KeyError(f"Unknown BDD variable {name!r}")
        return self.mk(name, 0, 1)

    def mk(self, var: str, low: int, high: int) -> int:
        if low == high:
            return low
        key = (var, low, high)
        found = self.unique.get(key)
        if found is not None:
            return found
        idx = len(self.nodes)
        self.nodes.append(BDDNode(var, low, high))
        self.unique[key] = idx
        return idx

    def node_count(self, root: int) -> int:
        seen: Set[int] = set()

        def visit(u: int) -> None:
            if u in seen or u < 2:
                return
            seen.add(u)
            n = self.nodes[u]
            visit(n.low)
            visit(n.high)

        visit(root)
        return len(seen)

    def support(self, root: int) -> Set[str]:
        out: Set[str] = set()
        seen: Set[int] = set()

        def visit(u: int) -> None:
            if u in seen or u < 2:
                return
            seen.add(u)
            n = self.nodes[u]
            out.add(n.var)
            visit(n.low)
            visit(n.high)

        visit(root)
        return out

    def node_variables(self, root: int) -> List[str]:
        out: List[str] = []
        seen: Set[int] = set()

        def visit(u: int) -> None:
            if u in seen or u < 2:
                return
            seen.add(u)
            n = self.nodes[u]
            out.append(n.var)
            visit(n.low)
            visit(n.high)

        visit(root)
        return out

    def negate(self, u: int) -> int:
        if u == 0:
            return 1
        if u == 1:
            return 0
        cached = self._not_cache.get(u)
        if cached is not None:
            return cached
        n = self.nodes[u]
        out = self.mk(n.var, self.negate(n.low), self.negate(n.high))
        self._not_cache[u] = out
        return out

    def apply(self, op_name: str, op: Callable[[bool, bool], bool], a: int, b: int) -> int:
        key = (op_name, a, b)
        cached = self._apply_cache.get(key)
        if cached is not None:
            return cached
        if a < 2 and b < 2:
            out = self.const(op(bool(a), bool(b)))
            self._apply_cache[key] = out
            return out

        va = self.nodes[a].var if a >= 2 else None
        vb = self.nodes[b].var if b >= 2 else None
        if va is None:
            top = vb
        elif vb is None:
            top = va
        else:
            top = va if self.level[va] <= self.level[vb] else vb

        al, ah = self._cofactor_top(a, top)
        bl, bh = self._cofactor_top(b, top)
        out = self.mk(top, self.apply(op_name, op, al, bl), self.apply(op_name, op, ah, bh))
        self._apply_cache[key] = out
        return out

    def _cofactor_top(self, u: int, top: str) -> Tuple[int, int]:
        if u < 2:
            return u, u
        n = self.nodes[u]
        if n.var == top:
            return n.low, n.high
        return u, u

    def land(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        if a == 1:
            return b
        if b == 1:
            return a
        return self.apply("and", lambda x, y: x and y, a, b)

    def lor(self, a: int, b: int) -> int:
        if a == 1 or b == 1:
            return 1
        if a == 0:
            return b
        if b == 0:
            return a
        return self.apply("or", lambda x, y: x or y, a, b)

    def xor(self, a: int, b: int) -> int:
        return self.apply("xor", lambda x, y: x ^ y, a, b)

    def restrict(self, root: int, var: str, value: int) -> int:
        key = (root, var, value)
        cached = self._restrict_cache.get(key)
        if cached is not None:
            return cached
        if root < 2:
            return root
        n = self.nodes[root]
        if n.var == var:
            out = n.high if value else n.low
        else:
            out = self.mk(n.var, self.restrict(n.low, var, value), self.restrict(n.high, var, value))
        self._restrict_cache[key] = out
        return out

    def restrict_many(self, root: int, assignment: Dict[str, int]) -> int:
        out = root
        for var, value in assignment.items():
            out = self.restrict(out, var, int(value))
        return out

    def exists(self, root: int, variables: Iterable[str]) -> int:
        out = root
        for var in variables:
            low = self.restrict(out, var, 0)
            high = self.restrict(out, var, 1)
            out = self.lor(low, high)
        return out

    def count_models(self, root: int, variables: Optional[Sequence[str]] = None) -> int:
        order = self.variable_order if variables is None else list(variables)
        order_set = set(order)

        @lru_cache(None)
        def rec(u: int, next_level: int) -> int:
            if u == 0:
                return 0
            if u == 1:
                return 2 ** (len(order) - next_level)
            n = self.nodes[u]
            if n.var not in order_set:
                return rec(n.low, next_level) + rec(n.high, next_level)
            lvl = order.index(n.var)
            skipped = max(0, lvl - next_level)
            return (2 ** skipped) * (rec(n.low, lvl + 1) + rec(n.high, lvl + 1))

        return rec(root, 0)

    def shortest_distance(self, root: int, reference: Dict[str, int], charged_vars: Set[str]) -> Tuple[float, Dict[str, int]]:
        memo: Dict[int, Tuple[float, Dict[str, int]]] = {}

        def rec(u: int) -> Tuple[float, Dict[str, int]]:
            if u == 0:
                return float("inf"), {}
            if u == 1:
                return 0.0, {}
            if u in memo:
                return memo[u]
            n = self.nodes[u]
            ref = int(reference.get(n.var, 0))
            cost0 = (1 if n.var in charged_vars and ref != 0 else 0)
            cost1 = (1 if n.var in charged_vars and ref != 1 else 0)
            d0, a0 = rec(n.low)
            d1, a1 = rec(n.high)
            if cost0 + d0 <= cost1 + d1:
                out = (cost0 + d0, {**a0, n.var: 0})
            else:
                out = (cost1 + d1, {**a1, n.var: 1})
            memo[u] = out
            return out

        return rec(root)

