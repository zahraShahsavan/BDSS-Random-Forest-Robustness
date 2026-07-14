from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log2
from typing import Dict, List, Sequence

import pandas as pd

from .forest import ForestModel


@dataclass
class FeatureEncoding:
    feature_index: int
    feature_name: str
    thresholds: List[float]
    bit_names: List[str]

    @property
    def cells(self) -> int:
        return len(self.thresholds) + 1

    def threshold_cell(self, threshold: float) -> int:
        return self.thresholds.index(threshold)

    def value_to_cell(self, value: float) -> int:
        for idx, threshold in enumerate(self.thresholds):
            if value <= threshold:
                return idx
        return len(self.thresholds)

    def cell_to_bits(self, cell: int) -> Dict[str, int]:
        if not self.bit_names:
            return {}
        cell = min(cell, self.cells - 1)
        return {bit: (cell >> j) & 1 for j, bit in enumerate(self.bit_names)}


def build_feature_encodings(forest: ForestModel) -> List[FeatureEncoding]:
    thresholds: Dict[int, set] = {i: set() for i in range(len(forest.feature_names))}
    for tree in forest.trees:
        for node in tree.nodes.values():
            if node.label is None and node.feature >= 0:
                thresholds[node.feature].add(node.threshold)

    encodings: List[FeatureEncoding] = []
    for feature_index, feature_name in enumerate(forest.feature_names):
        values = sorted(thresholds[feature_index])
        cells = len(values) + 1
        bit_count = 0 if cells <= 1 else ceil(log2(cells))
        bit_names = [f"x{feature_index}_b{j}" for j in range(bit_count)]
        encodings.append(FeatureEncoding(feature_index, feature_name, values, bit_names))
    return encodings


def all_input_bits(encodings: Sequence[FeatureEncoding]) -> List[str]:
    return [bit for enc in encodings for bit in enc.bit_names]


def sample_to_bits(row: pd.Series, encodings: Sequence[FeatureEncoding]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for enc in encodings:
        cell = enc.value_to_cell(float(row[enc.feature_name]))
        out.update(enc.cell_to_bits(cell))
    return out

