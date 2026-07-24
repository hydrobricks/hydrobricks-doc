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


# --------------------------------------------------------------------------- #
# Per-solver panels: how each scheme constructs its end-of-step value.
#
# All panels use the same single step of the linear reservoir, taken large
# enough (h = 1.5 d, so k*h = 0.75) that the schemes are visually distinct.
# The exact curve is the continuous solution S(t) = (I/k)(1 - e^{-k t}); each
# scheme is shown building the estimate it places at the end of the step.
# --------------------------------------------------------------------------- #

H = 1.5  # illustrative step length [days]


def exact_curve(t_end=None):
    t_end = H if t_end is None else t_end
    ts = [i * t_end / 200 for i in range(201)]
    return ts, [(I / K) * (1 - math.exp(-K * t)) for t in ts]


def solver_panel(title, subtitle):
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    tc, vc = exact_curve()
    ax.plot(tc, vc, color=BLUE, linewidth=2.4, zorder=2, label="Exact solution")
    exact_end = vc[-1]
    ax.plot([0], [0], marker="o", color=BLUE, markersize=6, zorder=5)
    ax.plot([H], [exact_end], marker="o", markerfacecolor="white",
            markeredgecolor=BLUE, markeredgewidth=1.6, markersize=6, zorder=5)
    ax.set_xlim(-0.12, H + 0.35)
    ax.set_xlabel("time [days]")
    ax.set_ylabel("storage [mm]")
    ax.set_title(title, fontsize=11, loc="left", pad=16)
    ax.text(0.0, 1.02, subtitle, transform=ax.transAxes, fontsize=8.5,
            color="#52514e", va="bottom")
    style(ax)
    return fig, ax, exact_end


def tangent(ax, x0, y0, slope, x1, **kw):
    ax.plot([x0, x1], [y0, y0 + slope * (x1 - x0)], **kw)


def mark_end(ax, y, color, label):
    ax.plot([H], [y], marker="o", color=color, markersize=7, zorder=6)
    ax.annotate(label, (H, y), textcoords="offset points", xytext=(8, 0),
                va="center", fontsize=8.5, color=color)


def fig_euler_explicit():
    fig, ax, _ = solver_panel(
        "euler_explicit",
        "one slope, evaluated at the start, extrapolated over the whole step")
    k1 = I - K * 0.0
    y_end = 0.0 + H * k1
    tangent(ax, 0, 0, k1, H, color=ORANGE, linewidth=1.8, linestyle="--",
            zorder=3)
    ax.annotate("slope k$_1$ = I - k S$_0$", (0.5, 2.5),
                textcoords="offset points", xytext=(6, -2), fontsize=8.5,
                color=ORANGE)
    mark_end(ax, y_end, ORANGE, f"Euler = {y_end:.2f}")
    ax.set_ylim(-0.4, y_end + 1.2)
    fig.tight_layout()
    fig.savefig("solver_euler_explicit.png", dpi=150)


def fig_heun_explicit():
    fig, ax, _ = solver_panel(
        "heun_explicit",
        "average of the start slope and the slope predicted at the step end")
    k1 = I - K * 0.0
    pred = 0.0 + H * k1  # Euler predictor
    k2 = I - K * pred
    y_end = 0.0 + H * (k1 + k2) / 2
    # Predictor tangent (start slope) and corrector slope at the predicted end.
    tangent(ax, 0, 0, k1, H, color=GRAY, linewidth=1.4, linestyle=":", zorder=3)
    ax.plot([H], [pred], marker="s", color=GRAY, markersize=5, zorder=5)
    ax.annotate("predictor (Euler)", (H, pred), textcoords="offset points",
                xytext=(-4, 8), ha="right", fontsize=8, color=GRAY)
    tangent(ax, H, pred, k2, H - 0.6, color=YELLOW, linewidth=1.6, zorder=3)
    ax.annotate("corrector slope k$_2$", (H - 0.55, pred - K * 0.55 * 0),
                textcoords="offset points", xytext=(-2, 6), ha="right",
                fontsize=8, color="#b57a00")
    # Averaged-slope step from the start.
    tangent(ax, 0, 0, (k1 + k2) / 2, H, color=ORANGE, linewidth=1.8, zorder=4)
    mark_end(ax, y_end, ORANGE, f"Heun = {y_end:.2f}")
    ax.set_ylim(-0.4, pred + 1.0)
    fig.tight_layout()
    fig.savefig("solver_heun_explicit.png", dpi=150)


def fig_rk4():
    fig, ax, _ = solver_panel(
        "runge_kutta (rk4)",
        "four slopes (start, twice mid-step, end) combined in a 1:2:2:1 average")
    s0 = 0.0
    k1 = I - K * s0
    k2 = I - K * (s0 + H / 2 * k1)
    k3 = I - K * (s0 + H / 2 * k2)
    k4 = I - K * (s0 + H * k3)
    y_end = s0 + H * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    stages = [(0.0, s0, k1, "k$_1$"),
              (H / 2, s0 + H / 2 * k1, k2, "k$_2$"),
              (H / 2, s0 + H / 2 * k2, k3, "k$_3$"),
              (H, s0 + H * k3, k4, "k$_4$")]
    for x, y, sl, name in stages:
        half = 0.28
        tangent(ax, x - half, y - sl * half, sl, x + half, color=YELLOW,
                linewidth=1.4, zorder=3)
        ax.plot([x], [y], marker="s", color=GRAY, markersize=4.5, zorder=5)
        ax.annotate(name, (x, y), textcoords="offset points", xytext=(2, 7),
                    fontsize=8, color="#b57a00")
    tangent(ax, 0, 0, (k1 + 2 * k2 + 2 * k3 + k4) / 6, H, color=ORANGE,
            linewidth=1.8, zorder=4)
    mark_end(ax, y_end, ORANGE, f"RK4 = {y_end:.2f}")
    ax.set_ylim(-0.4, s0 + H * k1 + 0.6)
    fig.tight_layout()
    fig.savefig("solver_rk4.png", dpi=150)


def fig_analytic():
    fig, ax, exact_end = solver_panel(
        "analytic_linear",
        "the linear ODE is integrated in closed form: the step is the exact curve")
    tc, vc = exact_curve()
    ax.fill_between(tc, 0, vc, color=BLUE, alpha=0.10, linewidth=0, zorder=1)
    mark_end(ax, exact_end, AQUA, f"analytic = {exact_end:.2f}")
    ax.annotate("S(t+h) = S e$^{-kh}$ + (I/k)(1 - e$^{-kh}$)", (0.08, exact_end),
                textcoords="offset points", xytext=(4, -18), fontsize=8.5,
                color="#52514e")
    ax.set_ylim(-0.4, exact_end + 1.2)
    fig.tight_layout()
    fig.savefig("solver_analytic.png", dpi=150)


def fig_implicit_euler():
    fig, ax, exact_end = solver_panel(
        "implicit_euler",
        "slope taken at the (unknown) end state; solved so the step matches it")
    # S_end = S0 + h (I - k S_end)
    y_end = (0.0 + H * I) / (1 + K * H)
    k_end = I - K * y_end
    # The chord from the start has exactly the end-of-step slope.
    tangent(ax, 0, 0, k_end, H + 0.25, color=ORANGE, linewidth=1.8, zorder=4)
    tangent(ax, H - 0.5, y_end - k_end * 0.5, k_end, H + 0.2, color=GRAY,
            linewidth=1.3, linestyle=":", zorder=3)
    ax.annotate("slope k(S$_{end}$)", (H, y_end), textcoords="offset points",
                xytext=(-6, -14), ha="right", fontsize=8, color="#52514e")
    mark_end(ax, y_end, ORANGE, f"implicit = {y_end:.2f}")
    ax.annotate("undershoots, never oscillates", (0.1, 0.05),
                xycoords="axes fraction", fontsize=8, color=GRAY)
    ax.set_ylim(-0.4, exact_end + 1.2)
    fig.tight_layout()
    fig.savefig("solver_implicit_euler.png", dpi=150)


def fig_crank_nicolson():
    fig, ax, exact_end = solver_panel(
        "crank_nicolson (default)",
        "average of the start and end slopes (trapezoidal rule)")
    # S_end (1 + k h / 2) = S0 (1 - k h / 2) + I h
    y_end = (0.0 * (1 - K * H / 2) + I * H) / (1 + K * H / 2)
    k_start = I - K * 0.0
    k_end = I - K * y_end
    k_avg = (k_start + k_end) / 2
    # Short start- and end-slope segments at their evaluation points, kept away
    # from the crowded top-right where the exact and CN endpoints nearly meet.
    tangent(ax, 0, 0, k_start, 0.55, color=GRAY, linewidth=1.3, linestyle=":",
            zorder=3)
    ax.annotate("start slope", (0.5, k_start * 0.5), textcoords="offset points",
                xytext=(5, -1), fontsize=8, color=GRAY)
    tangent(ax, H - 0.45, y_end - k_end * 0.45, k_end, H + 0.05, color=GRAY,
            linewidth=1.3, linestyle=":", zorder=3)
    ax.annotate("end slope", (H - 0.45, y_end - k_end * 0.45),
                textcoords="offset points", xytext=(2, -12), fontsize=8,
                color=GRAY)
    tangent(ax, 0, 0, k_avg, H, color=ORANGE, linewidth=1.8, zorder=4)
    ax.annotate("averaged slope", (1.0, k_avg), textcoords="offset points",
                xytext=(6, -13), fontsize=8, color=ORANGE)
    mark_end(ax, y_end, ORANGE, f"CN = {y_end:.2f}")
    ax.set_ylim(-0.4, exact_end + 1.2)
    fig.tight_layout()
    fig.savefig("solver_crank_nicolson.png", dpi=150)


def fig_exponential_euler():
    fig, ax, exact_end = solver_panel(
        "exponential_euler",
        "outflow linearized around the start, then integrated exactly")
    # Linear tangent of Q(S) = k S around S0, plus the exact integral (which,
    # for a linear store, is the exact curve itself).
    tc, vc = exact_curve()
    ax.fill_between(tc, 0, vc, color=BLUE, alpha=0.10, linewidth=0, zorder=1)
    mark_end(ax, exact_end, AQUA, f"exp. Euler = {exact_end:.2f}")
    ax.annotate("Q(S) $\\approx$ Q(S$_0$) + k (S - S$_0$)", (0.08, exact_end),
                textcoords="offset points", xytext=(4, -18), fontsize=8.5,
                color="#52514e")
    ax.annotate("exact for linear stores; ~2nd order for smooth non-linear ones",
                (0.09, 0.07), xycoords="axes fraction", fontsize=7.5, color=GRAY)
    ax.set_ylim(-0.4, exact_end + 1.2)
    fig.tight_layout()
    fig.savefig("solver_exponential_euler.png", dpi=150)


PER_SOLVER_FIGURES = [
    fig_euler_explicit,
    fig_heun_explicit,
    fig_rk4,
    fig_analytic,
    fig_implicit_euler,
    fig_crank_nicolson,
    fig_exponential_euler,
]


if __name__ == "__main__":
    fig_trajectories()
    fig_orders()
    fig_equilibrium()
    for make in PER_SOLVER_FIGURES:
        make()
    print("Figures written.")
