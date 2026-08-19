# Axelrod Alternative Topologies
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import copy
from collections import Counter
import csv
import os
import sys

# Build one of the four graph topologies.
def create_graph(topology, N=100, avg_k=4, grid_x=10, grid_y=10, seed=None):
    match topology:
        case "lattice":
            G = nx.grid_2d_graph(grid_x, grid_y)
            pos = {node: node for node in G.nodes()}
            is_lattice = True

        case "er":
            p = avg_k / (N - 1)
            G = nx.erdos_renyi_graph(N, p, seed=seed)
            pos = nx.spring_layout(G, seed=seed)
            is_lattice = False

        case "complete":
            G = nx.complete_graph(N)
            pos = nx.spring_layout(G, seed=seed)
            is_lattice = False

        case "scale_free":
            m = avg_k // 2
            G = nx.barabasi_albert_graph(N, m, seed=seed)
            pos = nx.spring_layout(G, seed=seed)
            is_lattice = False

        case _:
            raise ValueError(f"Unknown topology: {topology}")

    return G, pos, is_lattice

# Parameters.
grid_x = 10
grid_y = 10
n_features = 5
n_traits = 3
t_max = 200000

# Seed.
seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
rd.seed(seed)

topology = "lattice"
avg_k_target = 4

G, pos, is_lattice = create_graph(
    topology=topology,
    N=100,
    avg_k=avg_k_target,
    grid_x=grid_x,
    grid_y=grid_y,
    seed=seed
)

N = G.number_of_nodes()

traits = range(n_traits)
trait_min, trait_max = min(traits), max(traits)

# Random initial culture vectors.
features = {u:[rd.randint(trait_min, trait_max) for _ in range(n_features)] for u in G.nodes}

initial_features = copy.deepcopy(features)
non_isolated_nodes = [node for node in G.nodes() if G.degree(node) > 0]

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


# Plot the current state.
def plot_state(G, features, pos, is_lattice, title, grid_x=10, grid_y=10):
    unique_cultures = list(set(tuple(f) for f in features.values()))
    culture_index = {c: i for i, c in enumerate(unique_cultures)}

    if is_lattice:
        grid_labels = np.zeros((grid_x, grid_y))

        for node in G.nodes():
            x, y = node
            grid_labels[x, y] = culture_index[tuple(features[node])]

        plt.figure(figsize=(8, 8))
        plt.imshow(
            grid_labels.T,
            cmap=plt.cm.tab20,
            interpolation="nearest"
        )
        plt.title(title)
        plt.axis("off")
        plt.show()

    else:
        node_colours = [
            culture_index[tuple(features[node])]
            for node in G.nodes()
        ]

        plt.figure(figsize=(8, 8))
        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=node_colours,
            cmap=plt.cm.tab20,
            node_size=80
        )
        nx.draw_networkx_edges(
            G,
            pos,
            edge_color="lightgray",
            width=0.5
        )
        plt.title(title)
        plt.axis("off")
        plt.show()


# Initial state.
plot_state(
    G,
    initial_features,
    pos,
    is_lattice,
    title=f"Initial state — {count_unique_cultures(initial_features)} unique cultures",
    grid_x=grid_x,
    grid_y=grid_y
)

# Run model.
for interaction in range(1,t_max + 1):
    # Pick a node and one neighbour at random.
    u = rd.choice(non_isolated_nodes)
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
        break

# Run-level outputs.
final_unique_cultures = count_unique_cultures(features)
initial_unique_cultures = count_unique_cultures(initial_features)
avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
isolates = list(nx.isolates(G))

# Store results.
results = {
    "experiment": "topology_comparison",
    "script": "new_topology_script",
    "seed": seed,
    "topology": topology,
    "grid_x": grid_x,
    "grid_y": grid_y,
    "N": G.number_of_nodes(),
    "edges": G.number_of_edges(),
    "avg_degree": avg_degree,
    "avg_k_target":avg_k_target,
    "n_features": n_features,
    "n_traits": n_traits,
    "t_max": t_max,
    "isolated_nodes": len(list(nx.isolates(G))),
    "initial_unique_cultures": initial_unique_cultures,
    "final_unique_cultures": final_unique_cultures,
    "frozen_step": interaction,
    "frozen": is_frozen(G, features, n_features)
}

print("Initial unique cultures:", initial_unique_cultures)
print("Final unique cultures:", final_unique_cultures)
print("Frozen step:", interaction)
print("Average degree:", avg_degree)
print("Number of isolated nodes:", len(isolates))

# Final state.
plot_state(
    G,
    features,
    pos,
    is_lattice,
    title=f"Final state — {count_unique_cultures(features)} unique cultures",
    grid_x=grid_x,
    grid_y=grid_y
)
