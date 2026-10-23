"""Generate the solver benchmark tables used in doc/solvers.rst.

Run from this directory with a Python that has hydrobricks installed, giving
the path of the hydrobricks repository (for the Sitter example project):
    python benchmark_solvers.py C:/path/to/hydrobricks

The setup is the Socont model of examples/basics/sitter_project.yaml, with its
parameters as they are. The model needs not be good: every solver is compared
against a reference run of the same model, so the scores measure the
discretization error only. The reference is the Runge-Kutta scheme at a
15-minute step, with the daily forcing spread evenly over the day
(precipitation and PET shared between the steps, temperature held), so that
the steps of the compared runs differ only by the integration.

The run time is that of the integration alone (the core run, with the
parameters and the forcing already in place), the best of several repetitions.
"""

import copy
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

import hydrobricks as hb
from hydrobricks.forcing import Forcing

SOLVERS = [
    "euler_explicit",
    "heun_explicit",
    "runge_kutta",
    "implicit_euler",
    "crank_nicolson",
    "exponential_euler",
    "analytic_linear",
]
STEPS_H = [24, 12, 6, 3, 1]  # compared time steps [h]
REF_SOLVER = "runge_kutta"
REF_STEP_MIN = 15
TIMING_REPEATS = 7


def load_config(example_dir):
    with open(example_dir / "sitter_project.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def daily_forcing(config, example_dir):
    """Spatialized daily forcing, built once by a first run."""
    project = hb.load_project(config, base_dir=example_dir)
    project.run()
    return project.forcing


def refine_forcing(forcing, n_sub):
    """Spread a daily forcing over n_sub steps per day."""
    if n_sub == 1:
        return forcing
    refined = copy.deepcopy(forcing)
    ts = refined.data2D
    start = pd.Timestamp(ts.time.iloc[0])
    n_steps = len(ts.time) * n_sub
    ts.time = pd.Series(pd.date_range(start, periods=n_steps, freq=f"{1440 // n_sub}min"))
    for i, name in enumerate(ts.data_name):
        values = np.repeat(ts.data[i], n_sub, axis=0)
        if name in (Forcing.Variable.P, Forcing.Variable.PET):
            values = values / n_sub
        ts.data[i] = values
    return refined


def build_model(config, example_dir, solver, step_min):
    cfg = copy.deepcopy(config)
    cfg["model"]["options"]["solver"] = solver
    project = hb.load_project(cfg, base_dir=example_dir, setup=False)
    start, end = project.periods.full_span.bounds
    if step_min % 1440 == 0:
        step, unit = step_min // 1440, "day"
    else:
        step, unit = step_min, "minute"
    project.model.setup(
        spatial_structure=project.hydro_units,
        output_path=str(project.output_dir),
        start_date=start,
        end_date=end,
        spinup=project.periods.spinup,
        time_step=step,
        time_step_unit=unit,
    )
    return project


def run_daily(project, forcing, n_sub, timed=False):
    """Run and return the outlet discharge summed per day [mm/d]."""
    model = project.model
    model.run(parameters=project.parameters, forcing=forcing)
    run_time = None
    if timed:
        times = []
        for _ in range(TIMING_REPEATS):
            model.model.reset()
            model._set_parameter_values(project.parameters)
            model._set_forcing(forcing)
            t0 = time.perf_counter()
            model.model.run()
            times.append(time.perf_counter() - t0)
        run_time = min(times)
    # A sub-daily run ends at the first step of the end date: keep full days
    q = np.asarray(model.get_outlet_discharge())
    n_days = len(q) // n_sub
    q = q[: n_days * n_sub].reshape(n_days, n_sub).sum(axis=1)
    return q, run_time


def nse(sim, ref):
    n = min(len(sim), len(ref))
    sim, ref = sim[:n], ref[:n]
    return 1 - np.sum((sim - ref) ** 2) / np.sum((ref - ref.mean()) ** 2)


def kge(sim, ref):
    """Kling-Gupta efficiency, 2012 version (variability as a ratio of the CVs)."""
    n = min(len(sim), len(ref))
    sim, ref = sim[:n], ref[:n]
    r = np.corrcoef(sim, ref)[0, 1]
    beta = sim.mean() / ref.mean()
    gamma = (sim.std() / sim.mean()) / (ref.std() / ref.mean())
    return 1 - np.sqrt((r - 1) ** 2 + (beta - 1) ** 2 + (gamma - 1) ** 2)


def main(repo_dir):
    example_dir = Path(repo_dir) / "examples" / "basics"
    config = load_config(example_dir)
    forcing = daily_forcing(config, example_dir)
    obs = None

    # Reference run
    n_ref = 1440 // REF_STEP_MIN
    ref_project = build_model(config, example_dir, REF_SOLVER, REF_STEP_MIN)
    q_ref, _ = run_daily(ref_project, refine_forcing(forcing, n_ref), n_ref)
    obs = np.asarray(ref_project.observations.data[0])[: len(q_ref)]
    print(f"Reference ({REF_SOLVER}, {REF_STEP_MIN} min): NSE vs obs = "
          f"{nse(q_ref, obs):.3f}, KGE vs obs = {kge(q_ref, obs):.3f}")

    # Check of the reference against the Crank-Nicolson scheme at the same step
    cn_project = build_model(config, example_dir, "crank_nicolson", REF_STEP_MIN)
    q_cn, _ = run_daily(cn_project, refine_forcing(forcing, n_ref), n_ref)
    print(f"Reference check (crank_nicolson, {REF_STEP_MIN} min): "
          f"1 - NSE = {1 - nse(q_cn, q_ref):.1e}")

    peak = np.argmax(q_ref)
    rows = []
    for solver in SOLVERS:
        for step_h in STEPS_H:
            n_sub = 24 // step_h
            project = build_model(config, example_dir, solver, step_h * 60)
            q, run_time = run_daily(
                project, refine_forcing(forcing, n_sub), n_sub, timed=step_h == 24
            )
            rows.append({
                "solver": solver,
                "step_h": step_h,
                "nse_ref": nse(q, q_ref),
                "kge_ref": kge(q, q_ref),
                "nse_obs": nse(q, obs),
                "kge_obs": kge(q, obs),
                "peak_err_pct": 100 * (q[peak] - q_ref[peak]) / q_ref[peak],
                "max_err_pct": 100 * np.max(np.abs(q[: len(q_ref)] - q_ref[: len(q)]))
                / q_ref[peak],
                "run_time_s": run_time,
            })
            print(rows[-1], flush=True)

    df = pd.DataFrame(rows)
    daily = df[df.step_h == 24].set_index("solver")
    daily["rel_time"] = daily.run_time_s / daily.run_time_s.min()
    pd.set_option("display.width", 200)
    print()
    print(daily[["rel_time", "nse_ref", "kge_ref", "peak_err_pct", "max_err_pct",
                 "nse_obs", "kge_obs"]].round(4))
    for score in ("nse_ref", "kge_ref"):
        print()
        print(df.pivot(index="solver", columns="step_h", values=score)
              .loc[SOLVERS, STEPS_H].round(4))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../../../hydrobricks")
