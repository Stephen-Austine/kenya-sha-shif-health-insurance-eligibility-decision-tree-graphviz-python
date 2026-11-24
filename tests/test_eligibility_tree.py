"""Run from the repository root:  python -m unittest discover -s tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import health_insurance_eligibility_tree as t  # noqa: E402


class StructureTests(unittest.TestCase):
    def test_original_node_labels_preserved(self):
        self.assertEqual(t.NODES["A"][0], "Kenyan Citizen?")
        self.assertEqual(t.NODES["H"][0], "Income Level Above Threshold (Eligible)")
        self.assertEqual(t.NODES["L"][0], "Age > 65 (Senior Citizen Eligible)")

    def test_it_is_a_tree(self):
        self.assertEqual(len(t.NODES), 12)
        self.assertEqual(len(t.EDGES), 11)           # a tree has n - 1 edges
        reachable = {t.ROOT} | {dst for _, dst, _ in t.EDGES}
        self.assertEqual(reachable, set(t.NODES))     # everything hangs off the root
        incoming = [dst for _, dst, _ in t.EDGES]
        self.assertEqual(len(incoming), len(set(incoming)))  # one parent each

    def test_leaves_and_outcomes(self):
        self.assertEqual(sorted(t.leaves()), ["C", "E", "H", "I", "J", "K", "L"])
        self.assertEqual(sorted(l for l in t.leaves() if t.is_eligible(l)), ["E", "H", "J", "L"])

    def test_every_leaf_has_exactly_one_path(self):
        paths = t.root_to_leaf_paths()
        self.assertEqual(len(paths), 7)
        self.assertEqual(sorted(p[-1][0] for p in paths), sorted(t.leaves()))

    def test_unemployed_age_branches_are_exhaustive(self):
        labels = sorted(lbl for src, _, lbl in t.EDGES if src == "G")
        self.assertEqual(labels, ["Age 18-65", "Age < 18", "Age > 65"])


class GraphvizSourceTests(unittest.TestCase):
    def test_dot_source_contains_all_nodes_and_edges(self):
        try:
            tree = t.create_insurance_tree()
        except ImportError:
            self.skipTest("graphviz python package not installed")
        src = tree.source
        for node_id, (label, _) in t.NODES.items():
            self.assertIn(label, src)
        self.assertEqual(src.count("->"), 11)

    def test_highlight_marks_only_one_path(self):
        try:
            tree = t.create_insurance_tree(highlight_leaf="I")
        except ImportError:
            self.skipTest("graphviz python package not installed")
        self.assertEqual(tree.source.count('penwidth=3.2'), 4)  # A-B, B-D, D-F, F-I


if __name__ == "__main__":
    unittest.main()
