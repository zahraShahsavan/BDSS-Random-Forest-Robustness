from bdss_rf_robustness.bdd import BDDManager
from bdss_rf_robustness.composition import budgeted_compose, win_bdd_for_label
from bdss_rf_robustness.discretization import all_input_bits, build_feature_encodings
from bdss_rf_robustness.forest import ForestModel, TreeModel, TreeNode


def main():
    tree = TreeModel(
        {
            0: TreeNode(feature=0, threshold=0.5, left=1, right=2),
            1: TreeNode(feature=-1, threshold=0.0, left=-1, right=-1, label="A"),
            2: TreeNode(feature=-1, threshold=0.0, left=-1, right=-1, label="B"),
        }
    )
    forest = ForestModel(trees=[tree, tree, tree], labels=["A", "B"], feature_names=["x"], target_name="y")
    encodings = build_feature_encodings(forest)
    bits = all_input_bits(encodings)
    manager = BDDManager(bits)
    leaves, stats = budgeted_compose(manager, forest, encodings, tree_count=3, budget=1000, selector="modal", input_bits=bits)
    assert len(leaves) == 1
    a = win_bdd_for_label(manager, leaves[0], forest.labels, "A")
    b = win_bdd_for_label(manager, leaves[0], forest.labels, "B")
    assert manager.count_models(a, bits) == 1
    assert manager.count_models(b, bits) == 1
    print("Synthetic smoke test passed.")


if __name__ == "__main__":
    main()

