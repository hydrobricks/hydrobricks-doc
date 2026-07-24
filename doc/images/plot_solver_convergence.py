"""Generate the solver convergence figures used in doc/solvers.rst.

Run from this directory with any Python that has matplotlib:
    python plot_solver_convergence.py

The test problem is a linear storage (k = 0.5/d, initially empty) filling
under a constant 5 mm/d precipitation — the same setup as the convergence
tests of the C++ test suite (SolverTest.cpp, SolverConvergence).
"""

import math

import matplotlib.pyplot as plt

K = 0.5  # response factor [1/d]
I = 5.0  # constant inflow [mm/d]

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
GRAY = "#898781"


def exact_step(s, h):
    a = math.exp(-K * h)
    return s * a + (I / K) * (1 - a)


def euler_step(s, h):
    return s + h * (I - K * s)


def heun_step(s, h):
    k1 = I - K * s
    k2 = I - K * (s + h * k1)
    return s + h * (k1 + k2) / 2


def rk4_step(s, h):
    k1 = I - K * s
    k2 = I - K * (s + h / 2 * k1)
    k3 = I - K * (s + h / 2 * k2)
    k4 = I - K * (s + h * k3)
    return s + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6


def run(step, h, t_end):
    times, values = [0.0], [0.0]
    s = 0.0
    for i in range(round(t_end / h)):
        s = step(s, h)
        times.append((i + 1) * h)
        values.append(s)
    return times, values


def final_error(step, h, t_end):
    return abs(run(step, h, t_end)[1][-1] - run(exact_step, h, t_end)[1][-1])


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)


def fig_trajectories():
    fig, ax = plt.subplots(figsize=(7, 3.6))
    t, v = run(exact_step, 0.02, 2)
    ax.plot(t, v, color=BLUE, linewidth=2.4, label="Exact solution")
    for h, color, label in [(1, ORANGE, "Euler, 24 h step"),
                            (0.5, AQUA, "Euler, 12 h step"),
                            (0.25, YELLOW, "Euler, 6 h step")]:
        t, v = run(euler_step, h, 2)
        ax.plot(t, v, color=color, linewidth=1.7, marker="o", markersize=3.5,
                label=label)
    ax.set_xlabel("time [days]")
    ax.set_ylabel("storage [mm]")
    ax.legend(frameon=False, fontsize=9)
    style(ax)
    fig.tight_layout()
    fig.savefig("solver_convergence_trajectories.png", dpi=150)


def fig_orders():
    steps = [1, 0.5, 0.25]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for step_fn, color, name, order in [(euler_step, BLUE, "Euler", 1),
                                        (heun_step, ORANGE, "Heun", 2),
                                        (rk4_step, AQUA, "RK4", 4)]:
        errors = [final_error(step_fn, h, 2) for h in steps]
        ax.loglog(steps, errors, color=color, linewidth=1.8, marker="o",
                  markersize=5, label=f"{name} (order {order})")
        for i in range(2):
            ratio = errors[i] / errors[i + 1]
            x = math.sqrt(steps[i] * steps[i + 1])
            y = math.sqrt(errors[i] * errors[i + 1])
            ax.annotate(f"÷{ratio:.1f}", (x, y), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=9, color="#52514e")
    ax.set_xlabel("time step [days] (log scale)")
    ax.set_ylabel("error at day 2 [mm] (log scale)")
    ax.set_xticks(steps, ["24 h", "12 h", "6 h"])
    ax.set_xticks([], minor=True)
    ax.invert_xaxis()
    ax.legend(frameon=False, fontsize=9)
    style(ax)
    fig.tight_layout()
    fig.savefig("solver_convergence_orders.png", dpi=150)


def fig_equilibrium():
    fig, ax = plt.subplots(figsize=(7, 3.6))
    t_e, v_e = run(exact_step, 0.05, 10)
    t_u, v_u = run(euler_step, 1, 10)
    ax.axhline(I / K, color=GRAY, linewidth=1, linestyle="--")
    ax.text(0.15, I / K + 0.25, "equilibrium I/k = 10 mm", color=GRAY, fontsize=9)
    ax.plot(t_e, v_e, color=BLUE, linewidth=2.4, label="Exact solution")
    ax.plot(t_u, v_u, color=ORANGE, linewidth=1.7, marker="o", markersize=3.5,
            label="Euler, 24 h step")
    ax.fill_between(t_u, [v for _, v in zip(t_u, v_u)],
                    [exact_step_interp(t_e, v_e, t) for t in t_u],
                    color=ORANGE, alpha=0.15, linewidth=0)
    ax.annotate("gap 1.18 mm", (2, 6.9), textcoords="offset points",
                xytext=(10, 10), fontsize=9, color="#52514e",
                arrowprops=dict(arrowstyle="-", color="#52514e", linewidth=0.8))
    ax.annotate("gap 0.06 mm", (9, 9.95), textcoords="offset points",
                xytext=(0, -25), ha="center", fontsize=9, color="#52514e",
                arrowprops=dict(arrowstyle="-", color="#52514e", linewidth=0.8))
    ax.set_xlabel("time [days]")
    ax.set_ylabel("storage [mm]")
    ax.set_ylim(0, 11.5)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    style(ax)
    fig.tight_layout()
    fig.savefig("solver_equilibrium.png", dpi=150)


def exact_step_interp(times, values, t):
    for i in range(1, len(times)):
        if t <= times[i]:
            a, b = times[i - 1], times[i]
            va, vb = values[i - 1], values[i]
            return va + (vb - va) * (t - a) / (b - a)
    return values[-1]


if __name__ == "__main__":
    fig_trajectories()
    fig_orders()
    fig_equilibrium()
    print("Figures written.")
