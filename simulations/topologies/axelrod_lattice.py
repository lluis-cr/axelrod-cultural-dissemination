# Axelrod Model
import networkx as nx
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random as rd
import copy
from collections import Counter
import csv
import os
import sys

# Parameters.
grid_x = 10
grid_y = 10
n_features = 5
n_traits = 3
t_max = 200000

# Seed.
seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
rd.seed(seed)

# Lattice graph.
G = nx.grid_2d_graph(grid_x, grid_y)
N = G.number_of_nodes()
pos = {i:i for i in G.nodes()}

traits = range(n_traits)
trait_min, trait_max = min(traits), max(traits)

# Random initial culture vectors.
features = {u:[rd.randint(trait_min, trait_max) for _ in range(n_features)] for u in G.nodes}

initial_features = copy.deepcopy(features)

# Absorbing state check.
def is_frozen(G, features, n_features):
    for u, v in G.edges():
        overlap = sum(1 for i in range(n_features) if features[u][i] == features[v][i])
        if 0 < overlap < n_features:
            return False
    return True


# Count unique cultural vectors.
def count_unique_cultures(features):
    culture_counts = Counter(tuple(v) for v in features.values())
    return len(culture_counts)

print("Initial unique cultures: " + str(count_unique_cultures(features)))

initial_unique_cultures = list(set(tuple(f) for f in initial_features.values()))
initial_culture_index = {
    c: i for i, c in enumerate(initial_unique_cultures)
}

initial_grid = np.zeros((grid_x, grid_y))

for node in G.nodes():
    x, y = node
    initial_grid[x, y] = initial_culture_index[
        tuple(initial_features[node])
    ]

# Run model.
for interaction in range(1,t_max + 1):
    # Pick a node and one neighbour at random.
    u = rd.choice(list(G.nodes()))
    v = rd.choice(list(nx.neighbors(G,u)))

    f_u,f_v = features[u],features[v]
    if f_u != f_v:
        # Indices of differing features.
        non_common_index = [i for i,j in enumerate(zip(f_u,f_v)) if j[0] != j[1]]
        common = (n_features - len(non_common_index))/n_features

        # Copy one differing feature with probability equal to overlap.
        prob = rd.random()
        if prob <= common:
            feature_to_change = rd.choice(non_common_index)
            features[u][feature_to_change]=f_v[feature_to_change]

    # Check for absorption every N attempted updates.
    if interaction % N == 0 and is_frozen(G, features, n_features):
        print("Frozen at step " + str(interaction))
        break

print("Final unique cultures: " + str(count_unique_cultures(features)))

# Run-level outputs.
final_unique_cultures = count_unique_cultures(features)
initial_unique_cultures = count_unique_cultures(initial_features)

avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()

# Store results.
results = {
    "experiment": "validation_lattice",
    "script": "old_lattice_script",
    "seed": seed,
    "topology": "lattice",
    "grid_x": grid_x,
    "grid_y": grid_y,
    "N": G.number_of_nodes(),
    "edges": G.number_of_edges(),
    "avg_degree": avg_degree,
    "n_features": n_features,
    "n_traits": n_traits,
    "t_max": t_max,
    "initial_unique_cultures": initial_unique_cultures,
    "final_unique_cultures": final_unique_cultures,
    "frozen_step": interaction,
    "frozen": is_frozen(G, features, n_features)
}

# Write log row.
filename = "axelrod_validation_log.csv"
file_exists = os.path.isfile(filename)

with open(filename, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results.keys())

    if not file_exists:
        writer.writeheader()

    writer.writerow(results)
