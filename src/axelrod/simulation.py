"""Lightweight simulation entry points for baseline runs."""

from .model import save_demo_outputs


def run_baseline_demo(output_dir="results/figures"):
    """Run the baseline example and save its figures."""
    return save_demo_outputs(output_dir=output_dir)
