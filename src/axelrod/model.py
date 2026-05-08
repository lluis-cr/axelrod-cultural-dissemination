from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

class AxelrodModel:
    def __init__(self, N=30, F=5, q=10, seed=None):
        self.N = N
        self.F = F
        self.q = q
        self.rng = np.random.default_rng(seed)

        # culture[i, j, :] is the feature vector of agent (i, j)
        self.culture = self.rng.integers(0, q, size=(N, N, F))

    def neighbors(self, i, j):
        """Von Neumann neighborhood with open boundaries."""
        nbrs = []
        if i > 0:
            nbrs.append((i - 1, j))
        if i < self.N - 1:
            nbrs.append((i + 1, j))
        if j > 0:
            nbrs.append((i, j - 1))
        if j < self.N - 1:
            nbrs.append((i, j + 1))
        return nbrs

    def similarity(self, a, b):
        """Fraction of matching features between two vectors."""
        return np.mean(a == b)

    def step(self):
        """Perform one asynchronous update. Return True if a change occurred."""
        i = self.rng.integers(0, self.N)
        j = self.rng.integers(0, self.N)

        nbrs = self.neighbors(i, j)
        ni, nj = nbrs[self.rng.integers(0, len(nbrs))]

        a = self.culture[i, j]
        b = self.culture[ni, nj]

        sim = self.similarity(a, b)

        # no interaction if totally different or identical
        if sim == 0.0 or sim == 1.0:
            return False

        # interact with probability = similarity
        if self.rng.random() < sim:
            diff_idx = np.where(a != b)[0]
            k = diff_idx[self.rng.integers(0, len(diff_idx))]

            # copy neighbor's trait into agent a
            self.culture[i, j, k] = self.culture[ni, nj, k]
            return True

        return False

    def active_edges_count(self):
        """Count neighbor pairs that can still interact."""
        active = 0
        for i in range(self.N):
            for j in range(self.N):
                for ni, nj in self.neighbors(i, j):
                    # avoid double counting
                    if (ni, nj) < (i, j):
                        continue
                    a = self.culture[i, j]
                    b = self.culture[ni, nj]
                    matches = np.sum(a == b)
                    if 0 < matches < self.F:
                        active += 1
        return active

    def run(self, max_steps=200000, check_every=1000):
        """Run until frozen or max_steps reached."""
        history_active = []

        for t in range(max_steps):
            self.step()

            if t % check_every == 0:
                active = self.active_edges_count()
                history_active.append((t, active))
                if active == 0:
                    break

        return history_active

    def culture_labels(self):
        """
        Map each full feature vector to a unique integer label,
        so we can color cultural domains.
        """
        flat = self.culture.reshape(-1, self.F)
        unique_rows, labels = np.unique(flat, axis=0, return_inverse=True)
        return labels.reshape(self.N, self.N)

    def feature_grid(self, feature_idx=0):
        """Return one feature slice for visualization."""
        return self.culture[:, :, feature_idx]


def save_demo_outputs(output_dir="results/figures"):
    """Run the baseline demo and save visualisations to disk."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    model = AxelrodModel(N=40, F=5, q=12, seed=42)

    initial_feature_path = output_path / "initial_feature_0.png"
    plt.figure(figsize=(6, 6))
    plt.imshow(model.feature_grid(0), interpolation="nearest")
    plt.title("Initial state: feature 0")
    plt.colorbar(label="Trait value")
    plt.tight_layout()
    plt.savefig(initial_feature_path, dpi=150)
    plt.close()

    history = model.run(max_steps=300000, check_every=2000)

    final_domains_path = output_path / "final_cultural_domains.png"
    labels = model.culture_labels()
    plt.figure(figsize=(6, 6))
    plt.imshow(labels, interpolation="nearest")
    plt.title("Final cultural domains")
    plt.colorbar(label="Culture label")
    plt.tight_layout()
    plt.savefig(final_domains_path, dpi=150)
    plt.close()

    activity_decay_path = output_path / "activity_decay.png"
    times = [t for t, a in history]
    active = [a for t, a in history]
    plt.figure(figsize=(7, 4))
    plt.plot(times, active)
    plt.xlabel("Steps")
    plt.ylabel("Number of active edges")
    plt.title("Activity decay over time")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(activity_decay_path, dpi=150)
    plt.close()

    return {
        "initial_feature": initial_feature_path,
        "final_domains": final_domains_path,
        "activity_decay": activity_decay_path,
        "history": history,
    }


if __name__ == "__main__":
    outputs = save_demo_outputs()
    print("Saved Axelrod model outputs:")
    for name, path in outputs.items():
        if name != "history":
            print(f"- {name}: {path}")
