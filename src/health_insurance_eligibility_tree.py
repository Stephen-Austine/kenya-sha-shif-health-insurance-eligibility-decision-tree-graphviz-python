#!/usr/bin/env python3
"""
SHA / SHIF health-insurance eligibility decision tree, drawn with Graphviz.

A small teaching model of "who is eligible?" for Kenya's Social Health
Authority (SHA) / Social Health Insurance Fund (SHIF).  It is a SIMPLIFIED
classroom decision tree, not the official eligibility or contribution rules -
check https://sha.go.ke for those.

    python src/health_insurance_eligibility_tree.py                  # writes output/insurance_tree.png
    python src/health_insurance_eligibility_tree.py --format svg
    python src/health_insurance_eligibility_tree.py --list-paths     # print every decision path
    python src/health_insurance_eligibility_tree.py --view           # also open the image

Needs the Graphviz *system* package (the ``dot`` command) and ``pip install graphviz``.

The node ids (A-L), labels and edges are exactly those of the original script;
they are stored in two tables (NODES, EDGES) so the diagram, the tests and the
README all come from a single source of truth.
"""
import argparse

# node id -> (label, kind)    kind: question | answer | eligible | not_eligible
NODES = {
    "A": ("Kenyan Citizen?", "question"),
    "B": ("Yes", "answer"),
    "C": ("No (Not Eligible)", "not_eligible"),
    "D": ("Employment Status", "question"),
    "E": ("Formal Employment (Eligible)", "eligible"),
    "F": ("Informal Employment", "question"),
    "G": ("Unemployed", "question"),
    "H": ("Income Level Above Threshold (Eligible)", "eligible"),
    "I": ("Income Below Threshold (Not Eligible)", "not_eligible"),
    "J": ("Age < 18 (Dependent Eligible)", "eligible"),
    "K": ("Age 18-65 (Not Eligible)", "not_eligible"),
    "L": ("Age > 65 (Senior Citizen Eligible)", "eligible"),
}

# (from, to, edge label) - an empty label means an unlabeled edge
EDGES = [
    # root: citizenship
    ("A", "B", "Yes"),
    ("A", "C", "No"),
    # employment status
    ("B", "D", ""),
    ("D", "E", "Formal Employment"),
    ("D", "F", "Informal Employment"),
    ("D", "G", "Unemployed"),
    # informal employment: income level
    ("F", "H", "Above Threshold"),
    ("F", "I", "Below Threshold"),
    # unemployed: age check
    ("G", "J", "Age < 18"),
    ("G", "K", "Age 18-65"),
    ("G", "L", "Age > 65"),
]

ROOT = "A"

STYLES = {  # kind -> Graphviz node attributes
    "question": dict(shape="box", style="rounded,filled", fillcolor="#e9f1fb", color="#2a78d6"),
    "answer": dict(shape="ellipse", style="filled", fillcolor="#efeeea", color="#8a8985"),
    "eligible": dict(shape="box", style="rounded,filled", fillcolor="#e3f5ed", color="#1baf7a"),
    "not_eligible": dict(shape="box", style="rounded,filled", fillcolor="#fdecea", color="#e34948"),
}


def leaves():
    """Ids of nodes with no outgoing edge."""
    sources = {src for src, _, _ in EDGES}
    return [n for n in NODES if n not in sources]


def root_to_leaf_paths():
    """Every decision path as a list of (node_id, edge_label_taken_to_get_here)."""
    children = {}
    for src, dst, label in EDGES:
        children.setdefault(src, []).append((dst, label))

    paths = []

    def walk(node, trail):
        if node not in children:
            paths.append(trail)
            return
        for child, label in children[node]:
            walk(child, trail + [(child, label)])

    walk(ROOT, [(ROOT, "")])
    return paths


def is_eligible(leaf_id):
    return NODES[leaf_id][1] == "eligible"


def create_insurance_tree(highlight_leaf=None, fontname="Helvetica"):
    """Build and return the graphviz.Digraph (nothing is written to disk yet)."""
    from graphviz import Digraph

    tree = Digraph(format="png", comment="SHA/SHIF Eligibility Tree")
    tree.attr(bgcolor="#fcfcfb", nodesep="0.35", ranksep="0.55", pad="0.3")
    tree.attr("node", fontname=fontname, fontsize="12", fontcolor="#0b0b0b", penwidth="1.8", margin="0.18,0.1")
    tree.attr("edge", fontname=fontname, fontsize="11", fontcolor="#52514e", color="#8a8985", penwidth="1.3")

    on_path_nodes, on_path_edges = set(), set()
    if highlight_leaf:
        for trail in root_to_leaf_paths():
            if trail[-1][0] == highlight_leaf:
                ids = [n for n, _ in trail]
                on_path_nodes = set(ids)
                on_path_edges = set(zip(ids, ids[1:]))

    for node_id, (label, kind) in NODES.items():
        attrs = dict(STYLES[kind])
        if highlight_leaf and node_id not in on_path_nodes:
            attrs.update(fillcolor="#f7f7f5", color="#c9c8c3", fontcolor="#8a8985")
        tree.node(node_id, label, **attrs)

    for src, dst, label in EDGES:
        attrs = {}
        if highlight_leaf:
            if (src, dst) in on_path_edges:
                attrs.update(color="#eb6834", penwidth="3.2", fontcolor="#0b0b0b")
            else:
                attrs.update(color="#d9d8d3", fontcolor="#b0afa9")
        tree.edge(src, dst, label, **attrs)
    return tree


def render_tree(output_dir="output", fmt="png", view=False, **kwargs):
    """Render to ``<output_dir>/insurance_tree.<fmt>`` (the .gv source is kept next to it)."""
    tree = create_insurance_tree(**kwargs)
    tree.format = fmt
    return tree.render("insurance_tree", directory=output_dir, view=view, cleanup=False)


def format_paths():
    """One line per decision path:  answers given along the way  =>  outcome."""
    lines = []
    for trail in root_to_leaf_paths():
        answers = [label for _, label in trail if label]
        leaf_label = NODES[trail[-1][0]][0]
        lines.append("%s  =>  %s" % (" > ".join(answers), leaf_label))
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render the SHA/SHIF eligibility decision tree with Graphviz.")
    parser.add_argument("--output-dir", default="output", help="where to write the image (default: output/)")
    parser.add_argument("--format", default="png", choices=["png", "svg", "pdf"], help="image format (default: png)")
    parser.add_argument("--view", action="store_true", help="open the rendered image in the default viewer")
    parser.add_argument("--list-paths", action="store_true", help="print every root-to-leaf decision path and exit")
    args = parser.parse_args(argv)

    if args.list_paths:
        for line in format_paths():
            print(line)
        return
    try:
        from graphviz import ExecutableNotFound
    except ImportError:
        parser.exit(1, "The 'graphviz' Python package is missing - run: pip install graphviz\n")
    try:
        print("wrote", render_tree(args.output_dir, args.format, args.view))
    except ExecutableNotFound:
        parser.exit(1, "The Graphviz program 'dot' was not found. Install the Graphviz system package "
                       "(macOS: brew install graphviz | Ubuntu: sudo apt install graphviz | "
                       "Windows: winget install Graphviz.Graphviz) and make sure it is on your PATH.\n")


if __name__ == "__main__":
    main()
