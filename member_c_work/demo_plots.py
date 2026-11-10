"""Generate clearly labelled demonstration figures (not research results)."""
import numpy as np
from .data_generation import generate_train_test
from .visualization import plot_geometric_outputs, plot_ellipse_outputs


def main():
    rng = np.random.default_rng(5201)
    circle = generate_train_test(rng, n=100, m=120, b=1, sigma=.15)
    plot_geometric_outputs({"SMOKE_TEST_ONLY clean points": circle["test_clean"],
                            "SMOKE_TEST_ONLY raw": circle["test_noisy"]},
                           output="member_c_work/artifacts/demo/SMOKE_TEST_ONLY_circle_plots.png")
    ellipse = generate_train_test(rng, n=100, m=120, b=.75, sigma=.15)
    plot_ellipse_outputs({"SMOKE_TEST_ONLY raw": ellipse["test_noisy"]}, b=.75,
                         output="member_c_work/artifacts/demo/SMOKE_TEST_ONLY_ellipse_plot.pdf")
    print("Generated TEST/DEMO figures; do not report them as experimental evidence.")


if __name__ == "__main__":
    main()

