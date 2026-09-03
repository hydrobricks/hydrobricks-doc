.. _study-files:

Study files (comparing settings)
================================

A **study file** declares a whole comparison experiment as data: a base
:ref:`project configuration <project-files>` plus a ``matrix`` — in the spirit
of a GitHub Actions matrix — whose dimensions are crossed into independent
**jobs**, one calibration and assessment per combination. This makes
*multi-anything* comparisons (catchments × model structures × objective
functions × discharge transformations × ...) a one-file affair:

.. code-block:: console

   $ hydrobricks study list my_study.yaml          # the jobs and their status
   $ hydrobricks study validate my_study.yaml      # check every job up front
   $ hydrobricks study run my_study.yaml <job_id>  # run ONE job
   $ hydrobricks study run my_study.yaml --all     # or everything pending
   $ hydrobricks study assess my_study.yaml        # aggregate + comparison pivot

Each job is fully independent and **idempotent** (a finished job writes a JSON
record and is skipped on re-run), so a big grid parallelizes by simply
launching one process per job — see :ref:`below <study-files-parallel>`.


An annotated example
--------------------

.. code-block:: yaml

   name: my-study
   output: results            # study directory: jobs/, results/, cache/

   base:                      # a project-config skeleton: everything shared
     periods:
       calibration: [1981-01-01, 2000-12-31]
       validation: [2001-01-01, 2020-12-31]
       spinup: 4y
     forcing:
       time: {column: date, format: "%d/%m/%Y"}
       columns:
         precipitation: precip(mm/day)
         temperature: temp(C)
         pet: pet(mm/day)
     calibration:
       algorithm: sceua
       repetitions: 10000

   variants:                  # named config patches, per dimension
     catchment:
       appenzell:
         hydro_units: {file: appenzell/hydro_units.csv}
         forcing: {file: appenzell/meteo.csv, ref_elevation: 1253}
         observations:
           file: appenzell/discharge.csv
           time: {column: Date, format: "%d/%m/%Y"}
           column: Discharge (mm/d)
       stgallen:
         # ... same structure ...
     model:
       socont2:
         model:
           name: socont
           options: {soil_storage_nb: 2, surface_runoff: linear_storage}
         calibration:
           parameters: [a_snow, A, k_slow_1, k_slow_2, k_quick, percol]
       gr4j:
         model: {name: gr4j}
         calibration:
           parameters: [X1, X2, X3, X4, a_snow]

   matrix:                    # the grid: dimensions are crossed into jobs
     catchment: [appenzell, stgallen]
     model: [socont2, gr4j]
     objective: [kge_2012, kge_np]      # shorthand -> calibration.objective
     transform: [none, "power(0.2)"]    # shorthand -> calibration.transform
     exclude:                           # remove combinations (partial match)
       - {model: gr4j, transform: "power(0.2)"}
     include:                           # append extra combinations
       - {catchment: appenzell, model: socont2,
          objective: nse, transform: none}

   evaluation:                # cross-assessment of every finished job
     metrics: [kge_2012, kge_np, nse]
     transforms: [none, "power(0.2)"]

This study crosses 2 catchments × 2 models × 2 objectives × 2 transforms
(minus the excluded combinations, plus the included one). Every job
calibrates on the calibration period, re-runs the best parameter set over the
full span, and scores every declared period × evaluation transform × metric.


How matrix values are applied
-----------------------------

Any project-configuration key can be a dimension — that is what makes the
formulation generic. For a dimension ``d`` with value ``v``:

1. **Variant patch** — if the dimension appears under ``variants``, ``v``
   names a patch (``variants.d.v``) that is deep-merged onto the base config.
   Use this for anything structural: catchments, models, forcing datasets, ...
2. **Dotted config path** — if ``d`` contains a dot, it is a config path set
   to ``v`` directly, e.g. ``calibration.algorithm: [sceua, mc]`` or
   ``model.options.soil_storage_nb: [1, 2]``.
3. **Shorthand** — ``objective`` maps to ``calibration.objective`` and
   ``transform`` to ``calibration.transform``, so the two most common
   comparison axes stay terse.

``exclude`` entries remove every combination matching *all* their items
(partial match, like GitHub Actions); ``include`` entries — which must give a
value for every dimension — are appended after the exclusions, so they can
re-add or extend the grid.

Each job then gets its own output directory (``<output>/jobs/<job_id>``) and
shares the study cache (``<output>/cache``): identical expensive steps, such
as regridding the same gridded forcing for two model structures, run once.
The job id is the sanitized matrix values joined with ``__`` — e.g.
``appenzell__socont2__kge_2012__power-0.2`` — and doubles as the result file
name.


Results
-------

A finished job writes ``<output>/results/<job_id>.json`` holding the matrix
values, the calibration score, the best parameter values and the long-format
scores (period × transform × metric). ``assess`` aggregates all finished jobs
into a tidy table, ``<output>/results/scores.csv``, with one column per matrix
dimension plus ``period``, ``eval_transform``, ``eval_metric``, ``score`` and
``calibration_score`` — ready to pivot however you like:

.. code-block:: text

   eval_transform                            none              power(0.2)
   eval_metric                           kge_2012 kge_np   nse   kge_2012 kge_np   nse
   catchment model   objective transform
   appenzell socont2 kge_2012  none         0.512  0.535 0.427      0.777  0.774 0.412
   ...

The evaluation metrics/transforms are decoupled from the calibration ones
(the ``evaluation`` section), so you can, for instance, compare how a KGE′
calibration and a non-parametric-KGE calibration each score on a low-flow
(``power(0.2)``) evaluation.


Using studies from Python
-------------------------

:func:`hydrobricks.load_study` returns a :class:`~hydrobricks.Study` with the
resolved jobs:

.. code-block:: python

   import hydrobricks as hb

   study = hb.load_study('my_study.yaml')

   [job.id for job in study.jobs]      # the grid
   study.validate()                    # optional: check every job's files

   study.run('appenzell__socont2__kge_2012__none')   # one job
   study.run_all()                                   # everything pending

   scores = study.assess()             # tidy long-format DataFrame
   print(study.pivot(period='validation'))

``load_study`` validates the study structure (dimensions, variants,
include/exclude, calibration settings) and reports every problem at once,
prefixed with the job id. The per-job project configurations (declared files,
CSV columns, ...) are checked when a job runs — or all at once with
``study.validate()`` / ``hydrobricks study validate``.

Each ``StudyJob`` exposes its resolved project ``config`` (a plain mapping
accepted by :func:`hydrobricks.load_project`), so a single job can also be
inspected or run manually.


.. _study-files-parallel:

Parallelizing the jobs
----------------------

``run_all()`` is a sequential loop; for large grids, launch one **process**
per job instead — the jobs are independent and idempotent, so any process
launcher works.

Bash / GNU parallel:

.. code-block:: bash

   hydrobricks study list my_study.yaml | awk '/pending/{print $2}' \
     | parallel -j 8 hydrobricks study run my_study.yaml {}

SLURM array (one array task per job):

.. code-block:: bash

   mapfile -t JOBS < <(hydrobricks study list my_study.yaml | awk '/pending/{print $2}')
   sbatch --array=0-$(( ${#JOBS[@]} - 1 )) --wrap \
     'hydrobricks study run my_study.yaml ${JOBS[$SLURM_ARRAY_TASK_ID]}'

Windows PowerShell:

.. code-block:: powershell

   hydrobricks study list my_study.yaml |
     Select-String '\[pending\]\s+(\S+)' |
     ForEach-Object { $_.Matches[0].Groups[1].Value } |
     ForEach-Object { Start-Job { hydrobricks study run my_study.yaml $using:_ } }
   Get-Job | Wait-Job

When enough jobs have finished, ``hydrobricks study assess`` (or
``study.assess()``) aggregates whatever is there — it does not require the
whole grid to be done.


Section reference
-----------------

``name``
   Optional study name (shown by ``study list``).

``output``
   The study directory (default: ``study`` next to the study file). Holds
   ``jobs/<job_id>/`` (each job's model outputs), ``results/`` (the JSON
   records and ``scores.csv``) and ``cache/`` (shared across jobs).

``base``
   A project-configuration skeleton (see :ref:`project files
   <project-files>`), holding everything shared across jobs — typically the
   ``periods``, the shared ``forcing`` settings, ``data_parameters`` and the
   ``calibration`` defaults. It does not need to be complete on its own; the
   variant patches complete it.

``variants``
   Named config patches per dimension: ``variants.<dimension>.<name>`` is
   deep-merged onto the base when the matrix selects ``<name>``.

``matrix``
   The dimensions (each a non-empty list of values) plus the optional
   ``exclude`` and ``include`` lists. Every job needs a resolved
   ``calibration`` section with ``repetitions`` and ``parameters``.

``evaluation``
   The cross-assessment applied to every finished job: ``metrics`` (metric
   names) and ``transforms`` (:ref:`discharge transformations
   <discharge-transformations>` specifications). Defaults to the job's own
   calibration objective and transform.
