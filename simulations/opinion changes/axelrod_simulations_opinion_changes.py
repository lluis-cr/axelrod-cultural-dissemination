# Axelrod Model Simulations
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import copy
from collections import Counter
import csv
import pandas as pd
from pathlib import Path

from survey_preprocessing import (
    ATTITUDE_COLS,
    CHANGED_COLS,
    load_clean_t1_t4_endpoint_changes,
    print_resolved_paths,
)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]



def run_simulation(
        topology, n_traits, n_features, grid_x, grid_y, N, avg_k_target, t_max, seed, experiment, initial_data = None, target_changes=None):
    
    # Seed RNG
    rd.seed(seed)
    # Graph creation
    G, pos, is_lattice = create_graph(topology=topology,
        N=N,
        avg_k=avg_k_target,
        grid_x=grid_x,
        grid_y=grid_y,
        seed=seed
        )
    
    N_actual = G.number_of_nodes()

    if initial_data is None:
        # Random Axelrod initialisation
        trait_min = 0
        trait_max = n_traits - 1

        features = {
            u: [rd.randint(trait_min, trait_max) for _ in range(n_features)]
            for u in G.nodes
        }

    else:
        # Empirical survey initialisation from T1 data
        features = initialise_features(G, initial_data)

    # Keep the initial T1 state fixed for endpoint comparisons.
    initial_features = copy.deepcopy(features)
    # Specify non-isolated nodes
    non_isolated_nodes = [node for node in G.nodes() if G.degree(node) > 0]

    # Count successful copying events separately from endpoint changes.
    successful_changes = 0

    # Current differences from the initial T1 state.
    feature_endpoint_changes = [0] * n_features
    current_endpoint_changes = 0

    # Stopping status.
    target_reached = False
    stop_reason = "t_max_reached"

    # Run model loop
    for interaction in range(1,t_max + 1):
        # Pick a node and one neighbour at random.
        u = rd.choice(non_isolated_nodes)
        v = rd.choice(list(nx.neighbors(G,u)))
        # Compute common and differing features.
        f_u,f_v = features[u],features[v]
        if f_u != f_v:
            # Indices of differing features.
            non_common_index = [i for i,j in enumerate(zip(f_u,f_v)) if j[0] != j[1]]
            common = (n_features - len(non_common_index))/n_features

            # Copy one differing feature with probability equal to overlap.
            prob = rd.random()
            if prob <= common:
                # Choose a differing feature.
                feature_to_change = rd.choice(non_common_index)

                # Compare against the initial T1 value.
                initial_value = initial_features[u][feature_to_change]

                was_different = (
                    features[u][feature_to_change] != initial_value
                )

                # Perform the copying event.
                features[u][feature_to_change] = f_v[feature_to_change]

                successful_changes += 1

                is_different = (
                    features[u][feature_to_change] != initial_value
                )

                # Update the current T1-to-present difference.
                endpoint_delta = int(is_different) - int(was_different)
                feature_endpoint_changes[feature_to_change] += endpoint_delta
                current_endpoint_changes += endpoint_delta

                # Stop at the observed endpoint-change total.
                if (
                    target_changes is not None
                    and current_endpoint_changes == target_changes
                ):
                    target_reached = True
                    stop_reason = "target_reached"
                    break

        # Check for absorption every N attempted updates.
        if interaction % N_actual == 0 and is_frozen(
            G, features, n_features
        ):
            stop_reason = (
                "frozen_before_target"
                if target_changes is not None and not target_reached
                else "frozen"
            )
            break
    stopping_step = interaction

    # Run-level outputs.
    final_unique_cultures = count_unique_cultures(features)
    initial_unique_cultures = count_unique_cultures(initial_features)
    avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
    isolates = list(nx.isolates(G))

    # Store results.
    results = {
        "experiment": experiment,
        "script": "axelrod_simulations",
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
        "isolated_nodes": len(isolates),
        "initial_unique_cultures": initial_unique_cultures,
        "final_unique_cultures": final_unique_cultures,
        "stopping_step": stopping_step,

        # Kept for compatibility with older analysis code.
        "frozen_step": stopping_step,

        "frozen": is_frozen(G, features, n_features),
        "stop_reason": stop_reason,

        # Cumulative copying events.
        "successful_changes": successful_changes,

        # Current number of entries different from T1.
        "endpoint_changes": current_endpoint_changes,

        "target_changes": target_changes,
        "target_reached": target_reached
    }


    for idx, count in enumerate(feature_endpoint_changes):
        results[f"feature_{idx}_changes"] = count
        results[f"feature_{idx}_relative_changes"] = (
            count / current_endpoint_changes
            if current_endpoint_changes > 0
            else 0
        )
    
    return results


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

def initialise_features(G, data):
    # Assign one survey response vector to each graph node.
    if len(data) != G.number_of_nodes():
        raise ValueError(
            f"Initial data has {len(data)} rows, "
            f"but graph has {G.number_of_nodes()} nodes."
        )

    features = {}

    for node, (_, row) in zip(G.nodes(), data.iterrows()):
        features[node] = row.tolist()

    return features


# Experiment block.
cleaned_survey = load_clean_t1_t4_endpoint_changes(PROJECT_ROOT)
print_resolved_paths(
    "axelrod_simulations.py",
    project_root=PROJECT_ROOT,
    script_dir=SCRIPT_DIR,
    sim_results=SCRIPT_DIR / "survey_model_T1_T4_feature_changes.csv",
)

attitude_cols = ATTITUDE_COLS
changed_cols = CHANGED_COLS
t1_data_with_id = cleaned_survey["t1_data_with_id"]
t1_data = cleaned_survey["t1_data"]
observed_changes = cleaned_survey["observed_changes"]

# Basic checks.
print("T1 data shape:", t1_data.shape)
print("Observed changes shape:", observed_changes[changed_cols].shape)
print("T1 columns used:", list(t1_data.columns))
print("Observed change columns used:", list(observed_changes[changed_cols].columns))

# Parameters.
grid_x = 10
grid_y = 10
N = len(t1_data)
n_features = t1_data.shape[1]
n_traits = 5
t_max = 200000

# Observed feature changes between T1 and T4.
target_changes = int(observed_changes[changed_cols].sum().sum())

# Check that model settings match the survey data.
print("N:", N)
print("n_features:", n_features)
print("target_changes:", target_changes)

avg_k_target = 4
experiment = "survey_T1_to_T4_target_changes"
topologies = ["complete"]
seeds = range(50)

# CSV log file.
filename = SCRIPT_DIR / "survey_model_T1_T4_feature_changes.csv"

# Run counter.
total_runs = len(topologies) * len(seeds)
run_number = 0

# Run all seeds and write the log.
with open(filename, "w", newline="") as f:
    writer = None

    for topology in topologies:
        for seed in seeds:

            run_number += 1

            results = run_simulation(
                topology=topology,
                n_traits=n_traits,
                n_features=n_features,
                grid_x=grid_x,
                grid_y=grid_y,
                N=N,
                avg_k_target=avg_k_target,
                t_max=t_max,
                seed=seed,
                experiment=experiment,
                initial_data =t1_data,
                target_changes=target_changes
            )

            if writer is None:
                writer = csv.DictWriter(f, fieldnames=results.keys())
                writer.writeheader()
            
            writer.writerow(results)

            print(
                f"Run {run_number}/{total_runs} complete | "
                f"seed={seed}, copying events={results['successful_changes']}, "
                f"endpoint changes={results['endpoint_changes']}, "
                f"target={target_changes}, "
                f"stop={results['stop_reason']}"
            )
