import ast
import networkx as nx
import itertools
from matplotlib import pyplot as plt

with open("main/auth.py", "r") as f:
    code = f.read()

tree = ast.parse(code)
func = tree.body[0]

G = nx.DiGraph()
counter = 0
stack = []
entry_node = f"n{counter}"
G.add_node(entry_node, label="start")
prev = [entry_node]
counter += 1

def add_node(label):
    global counter
    node = f"n{counter}"
    G.add_node(node, label=f'"{label}"')
    counter += 1
    return node

def visit(statements, prev_nodes):
    current_nodes = []
    for stmt in statements:
        if isinstance(stmt, ast.If):
            test_label = ast.unparse(stmt.test)
            test_node = add_node(f"if {test_label}")
            for p in prev_nodes:
                G.add_edge(p, test_node)
            # then-branch
            then_nodes = visit(stmt.body, [test_node])
            # else-branch
            else_nodes = visit(stmt.orelse, [test_node]) if stmt.orelse else [test_node]
            prev_nodes = then_nodes + else_nodes
        elif isinstance(stmt, ast.Return):
            return_node = add_node(f"return {ast.unparse(stmt.value)}")
            for p in prev_nodes:
                G.add_edge(p, return_node)
            return []
        else:
            label = ast.unparse(stmt)
            node = add_node(label)
            for p in prev_nodes:
                G.add_edge(p, node)
            prev_nodes = [node]
    return prev_nodes

final_nodes = visit(func.body, prev)

print("Комбінації для умови \"if not username or not password\":")
print(" not username | not password | A or B ")
for A, B in itertools.product([True, False], repeat=2):
    result = A or B
    print(f" {A!s:12} | {B!s:12} | {result!s:12}")

print("Шляхи виконання (all_simple_paths):")
for node in G.nodes:
    if G.out_degree(node) == 0:
        for path in nx.all_simple_paths(G, source="n0", target=node):
            print(path)

nx.nx_pydot.write_dot(G, "cfg.dot")

M = G.number_of_edges() - G.number_of_nodes() + 2
print("Циклoматична складність:", M)
