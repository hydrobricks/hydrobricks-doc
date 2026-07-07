.. _parameters:

Parameters and calibration
==========================

All parameters for a model run are held in a single ``ParameterSet`` object.
Each parameter has the following attributes
(more information in :ref:`the Python API <api_parameterset>`):

* **component**: the model component it belongs to (e.g., ``glacier``, ``slow_reservoir``)
* **name**: the full parameter name (e.g., ``degree_day_factor``)
* **unit**: the physical unit (e.g., ``mm/d/°C``)
* **aliases**: short names accepted by ``set_values()`` (e.g., ``a_snow``)
* **value**: the currently assigned value
* **min** / **max**: the valid range, used during calibration and for validation
* **default_value**: a pre-set value, if any. Parameters with defaults (such as melt
  temperatures) are optional — you only need to set them if you want to deviate from
  the default.
* **mandatory**: whether the user must supply a value (i.e., the parameter has no default)
* **prior**: prior distribution for Bayesian or Monte Carlo calibration —
  see :ref:`the calibration page <calibration>`
* **transform**: an optional monotonic mapping between the parameter's real value
  and a transformed value used during calibration —
  see :ref:`Parameter transforms <parameter-transforms>`


Creating a parameter set
-------------------------

For pre-built models, call ``generate_parameters()`` on the model instance.
This produces a ``ParameterSet`` populated with all parameters appropriate for
the chosen model configuration, including their names, aliases, units, and
default ranges:

.. code-block:: python

   socont = models.Socont(soil_storage_nb=2)
   parameters = socont.generate_parameters()


Assigning parameter values
---------------------------

Use ``set_values()`` with a dictionary. Keys can be either the full parameter
name (e.g., ``snowpack:degree_day_factor``) or any alias (e.g., ``a_snow``).
The matching is case-insensitive, so the literature capitalisation can be used
as is (e.g., ``PERC`` and ``perc`` are equivalent):

.. code-block:: python

   parameters.set_values({'A': 100, 'k_slow': 0.01, 'a_snow': 5})


Parameter constraints
----------------------

Constraints enforce ordering relationships between parameters. They are checked
during calibration — any parameter set that violates a constraint is rejected.
To add a custom constraint:

.. code-block:: python

   parameters.define_constraint('k_slow_2', '<', 'k_slow_1')

Supported operators: ``>`` (or ``gt``), ``>=`` (or ``ge``), ``<`` (or ``lt``),
``<=`` (or ``le``).

Models define some constraints automatically — for example, GSM-Socont requires
``a_snow < a_ice`` because the ice melt factor must exceed the snow melt factor.
These built-in constraints can be removed when needed:

.. code-block:: python

   parameters.remove_constraint('a_snow', '<', 'a_ice')


Parameter ranges
-----------------

Each parameter is generated with a default range. The calibration algorithm
samples within this range, and values outside it are rejected. To adjust the
range for a parameter:

.. code-block:: python

   parameters.change_range('a_snow', 2, 5)


.. _parameter-transforms:

Parameter transforms
---------------------

A parameter can carry a **transform**: a monotonic mapping between its *real*
value (the one passed to the C++ engine and stored in the parameter set) and a
*transformed* value used during calibration. Searching in transformed space makes
the optimisation better behaved — a storage capacity that spans orders of
magnitude is calibrated in log space, while an exchange coefficient that may be
negative or positive is calibrated through an inverse hyperbolic sine.

Pre-built models attach the appropriate transforms automatically. GR4J and GR6J
follow the airGR ``TransfoParam`` conventions:

.. list-table::
   :header-rows: 1
   :widths: 22 26 52

   * - Parameter
     - Transform (real → transformed)
     - Rationale
   * - X1 (production store capacity)
     - ``log``
     - spans orders of magnitude, > 0
   * - X2 (groundwater exchange)
     - ``asinh``
     - signed (import or export)
   * - X3 (routing store capacity)
     - ``log``
     - spans orders of magnitude, > 0
   * - X4 (unit-hydrograph base time)
     - ``log(X4 - 0.5)``
     - log-like, enforces X4 > 0.5
   * - X5 (exchange threshold, GR6J)
     - ``asinh``
     - signed
   * - X6 (exponential store, GR6J)
     - ``log``
     - > 0

How it works:

* The model always keeps and runs the **real** value; the transform is used only
  to map to and from the optimiser's search space.
* ``get_for_spotpy()`` maps each parameter's real ``min``/``max`` through its
  transform, so the optimiser searches the transformed bounds.
* During calibration, the sampled (transformed) values are mapped back to real
  values automatically before each model run.
* A ``log`` transform is undefined at zero, so where the default lower bound would
  fall there it is raised slightly for calibration (e.g. GR4J/GR6J X1 to 1 mm and
  X4 to 0.51 d).

Inspect or set transformed values directly:

.. code-block:: python

   import math

   parameters.set_values({'X1': 350})                 # real value
   parameters.get_transformed('X1')                   # -> log(350)

   # Set a value given in transformed space (mapped back to the real value):
   parameters.set_values({'X1': math.log(500)}, transformed=True)
   parameters.get('X1')                               # -> 500.0

Attach a custom transform to any parameter with a ``(real → transformed,
transformed → real)`` pair of monotonic functions:

.. code-block:: python

   parameters.set_transform('k_slow', math.log, math.exp)

Transforms are not supported on list-valued parameters.


Calibratable forcing parameters
---------------------------------

Some aspects of forcing data preparation — elevation gradients, correction
factors — can themselves be calibrated. Because these depend on the input data
rather than the model structure, they are not generated automatically and must
be added explicitly:

.. code-block:: python

   parameters.add_data_parameter('precip_corr_factor', 1, min_value=0.7, max_value=1.3)
   parameters.add_data_parameter('precip_gradient', 0.05, min_value=0, max_value=0.2)
   parameters.add_data_parameter('temp_gradients', -0.6, min_value=-1, max_value=0)

The first argument is the parameter name, the second is the initial value.
For details on how these parameters link to spatialization operations, see the
:ref:`Spatialization <spatialization>` section on the :ref:`forcing page <forcing-data>`.

For seasonally varying quantities such as temperature lapse rates, monthly
values and ranges can be specified:

.. code-block:: python

   parameters.add_data_parameter(
      'temp_gradients',
      [-0.6, -0.6, -0.6, -0.6, -0.7, -0.7, -0.8, -0.8, -0.8, -0.7, -0.7, -0.6],
      min_value=[-0.8]*12,
      max_value=[-0.3]*12
   )


.. _calibration:

Calibration using SPOTPY
--------------------------

Hydrobricks uses the `SPOTPY package <https://spotpy.readthedocs.io/en/latest/>`_ for
parameter calibration and sensitivity analysis. SPOTPY provides a unified interface to
many optimization and sampling algorithms and records every model evaluation so results
can be analysed after sampling.

By default, all parameters generated by ``generate_parameters()`` are eligible for
calibration. To restrict calibration to a specific subset, list the aliases or full
names of the parameters that should vary:

.. code-block:: python

   parameters.allow_changing = ['a_snow', 'k_quick', 'A', 'k_slow_1', 'percol',
                                'k_slow_2', 'precip_corr_factor']

Create a SPOTPY setup object that bundles the model, parameters, forcing, observations,
and objective function. The calibration helpers live in the ``hydrobricks.trainer``
module. The ``warmup`` argument (in days) excludes the opening period of each run from
the objective function to avoid spin-up artefacts — see the
:ref:`spin-up section <spinup>` for background. Alternatively, declare explicit
:ref:`calibration/validation periods <periods>` with a built-in spin-up, which scores
the whole calibration period instead of trimming its start:

.. code-block:: python

   import hydrobricks.trainer as trainer

   spot_setup = trainer.SpotpySetup(
      socont,
      parameters,
      forcing,
      obs,
      warmup=365,
      obj_func='nse'
   )

.. note::

   You do not need to worry about the sign of the objective function. Hydrobricks
   always computes it as a **skill** (higher is better): metrics that are naturally
   maximized (NSE, KGE, ...) are used as-is, while error metrics (MSE, RMSE, ...) are
   negated internally so that higher is still better. The sign each SPOTPY algorithm
   expects is then applied automatically from the algorithm's optimization direction
   (some minimize, e.g. SCE-UA and NSGA-II; most maximize). There is therefore no
   ``invert_obj_func`` flag: just pass a metric name (or a "higher is better" callable)
   as ``obj_func`` and run the calibration through
   :func:`trainer.calibrate <hydrobricks.trainer.calibrate>` (below), which applies the
   correct sign for the chosen algorithm.

With the setup object ready, run the calibration with
:func:`trainer.calibrate <hydrobricks.trainer.calibrate>`, choosing an algorithm based
on the goal:

**Optimization** (finding the best parameter set): SCE-UA is well suited to
multi-parameter hydrological calibration problems:

.. code-block:: python

   sampler = trainer.calibrate(
      spot_setup,
      'sceua',
      10000,
      dbname='socont_SCEUA',
      dbformat='csv',
   )

**Sensitivity analysis** (understanding which parameters matter): Monte Carlo sampling
covers the full parameter space without steering towards any optimum:

.. code-block:: python

   sampler = trainer.calibrate(
      spot_setup,
      'mc',
      10000,
      dbname='socont_MC',
      dbformat='csv',
      save_sim=False,
   )

After sampling, retrieve the best parameter set and its score with
:func:`trainer.get_best <hydrobricks.trainer.get_best>`, and the full table of evaluated
sets with :func:`trainer.get_results <hydrobricks.trainer.get_results>`. Both report the
score in **metric space** (higher is better, with the optimizer sign undone), so a KGE of
0.7 reads as ``0.7``, never ``-0.7``:

.. code-block:: python

   best = trainer.get_best(sampler)
   print(best['score'], best['parameters'])   # e.g. 0.83 {'a_snow': 4.2, ...}

   results = trainer.get_results(sampler)      # pandas DataFrame: a 'score' column + params

SPOTPY's own analysis tools also work on the raw records from ``sampler.getdata()``,
e.g. to visualize parameter interactions and isolate high-performing samples (note that
``getdata()`` stores the raw, possibly sign-flipped objective):

.. code-block:: python

   records = sampler.getdata()

   # Plot parameter interactions across all samples
   spotpy.analyser.plot_parameterInteraction(records)
   plt.tight_layout()
   plt.show()

   # Restrict to the top-performing 10 % (posterior distribution)
   posterior = spotpy.analyser.get_posterior(records, percentage=10)
   spotpy.analyser.plot_parameterInteraction(posterior)
   plt.tight_layout()
   plt.show()


.. _periods:

Calibration, validation and simulation periods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For split-sample testing, the periods can be declared once and drive the whole
workflow — the model setup, the calibration and the per-period evaluation:

.. code-block:: python

   periods = hb.Periods(
      calibration=('1981-01-01', '2000-12-31'),
      validation=('2001-01-01', '2020-12-31'),
      spinup='4y',
   )

The ``simulation`` span defaults to the union of the declared periods (earliest
start to latest end). The ``spinup`` (see the :ref:`spin-up section <spinup>`)
replaces the ``warmup``: each model replays the first years of its own period to
warm the storages, so the **whole** declared period is evaluated and the
calibration and validation periods can be contiguous without losing a year of
observations.

Set the calibration model up over the calibration period and pass ``periods``
to the setup (``warmup`` must then be left unset):

.. code-block:: python

   socont.setup(
      spatial_structure=hydro_units,
      output_path='/path/to/dir',
      period=periods.calibration,
      spinup=periods.spinup,
   )

   obs = hb.DischargeObservations(periods)   # loaded over the full span
   obs.load_from_csv(...)

   spot_setup = trainer.SpotpySetup(
      socont, parameters, forcing, obs,
      obj_func='kge_2012',
      periods=periods,
   )
   sampler = trainer.calibrate(spot_setup, 'sceua', 10000)

For the validation, do **not** restart cold on the validation period: re-run the
best parameters once over the full span (continuous, warm states) and read the
score of every period from its date slice:

.. code-block:: python

   best = trainer.get_best(sampler)

   # A fresh model over the full span (a model instance is single-use).
   socont_full.setup(
      spatial_structure=hydro_units,
      output_path='/path/to/dir',
      period=periods.simulation,
      spinup=periods.spinup,
   )
   parameters.set_values(best['parameters'])
   socont_full.run(parameters, forcing)

   scores = hb.evaluate_periods(socont_full, obs, periods,
                                metrics=('kge_2012', 'nse'))
   print(scores)   # one row per period, one column per metric

The same forcing object serves every period (the forcing may be longer than the
modelling period; only coverage is required). A single date slice can also be
scored directly with ``model.eval(metric, obs, period=periods.validation)``.
See the complete example in ``examples/basics/calibrate_validate_periods.py``.


.. _parallel_calibration:

Parallel calibration
^^^^^^^^^^^^^^^^^^^^^

Depending on the calibration approach, the model can be run many times with independent 
parameter sets, so it can be spread across CPU cores. SPOTPY ships parallel backends 
(``parallel='mpc'`` for multiprocessing), but to use them the setup has to be sent to
worker processes. The model, forcing, and observations are backed by the C++ core and
cannot be pickled, so they must be **rebuilt inside each worker** rather than shipped.

The simplest way to do this is
:func:`calibrate_from_factory <hydrobricks.trainer.calibrate_from_factory>`. You write a
single *factory* — a module-level function that builds everything and returns a
``(model, parameters, forcing, obs)`` tuple — and one call does the rest. The same code
runs sequentially or in parallel; only ``parallel`` changes.

.. code-block:: python

   import hydrobricks.trainer as trainer

   def build():
       # Build the model, parameters, forcing and observations here, then:
       return socont, parameters, forcing, obs

   if __name__ == '__main__':
       sampler = trainer.calibrate_from_factory(
           build,
           'mc',
           10000,
           warmup=365,
           obj_func='nse',
           dbname='socont_MC',
           dbformat='csv',
           parallel='mpc',     # 'seq' for a single process
           n_workers=4,        # optional; default is all logical CPUs
       )
       results = sampler.getdata()

.. note::

   - The ``'mpc'`` backend requires the optional `pathos <https://pypi.org/project/pathos/>`_
     package (``pip install pathos``).
   - The factory must be a top-level (module-level) function so it can be pickled; lambdas
     and closures will not work.
   - On Windows (and any platform that spawns workers) the call must run under an
     ``if __name__ == '__main__':`` guard.
   - Not every algorithm benefits equally: independent samplers such as ``mc``, ``lhs``,
     ``rope`` and the ``dream`` chains scale close to linearly with the number of cores,
     whereas SCE-UA is largely sequential and sees only a modest speedup.

For finer control you can assemble the pieces yourself:
:meth:`SpotpySetup.from_factory <hydrobricks.trainer.SpotpySetup.from_factory>` (whose
factory returns just ``(model, forcing, obs)``, with ``parameters`` passed separately)
builds the picklable setup, and
:func:`calibrate <hydrobricks.trainer.calibrate>` runs a given setup with the chosen
backend and ``n_workers``. The single-process path is unchanged: a ``SpotpySetup`` built
directly from objects (no factory) still works with ``parallel='seq'`` (the default).

.. _glacier_mass_balance_calibration:

Calibrating on glacier mass balance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On glacierized catchments, the observed glacier **mass balance** (e.g. from
`GLAMOS <https://www.glamos.ch>`_) is a strong, independent constraint on the snow and
ice melt parameters.
Hydrobricks can use it alongside discharge during calibration. Everything happens on the
Python side; the simulation itself is unchanged (there is no data assimilation).

Observed mass balance is loaded from a CSV file with
:class:`GlacierMassBalanceObservations
<hydrobricks.evaluation.glacier_mass_balance.GlacierMassBalanceObservations>`, one of the
auxiliary observation classes in the :mod:`hydrobricks.evaluation` subpackage. The GLAMOS
"fixdate" products have a dedicated preset (whole-glacier or per elevation band; annual,
winter and summer balances), with the observation periods taken from the per-row dates in
the file, so calendar and hydrological years are both handled:

.. code-block:: python

   glacier_mb = hb.GlacierMassBalanceObservations.from_glamos(
       '/path/to/massbalance_fixdate.csv',
       kind='whole',                 # or 'elevationbins'
       glacier_id='B43-03',
       balance_types=('annual', 'winter', 'summer'),
   )

For non-GLAMOS data, ``from_csv`` reads any tabular CSV: map the value and period
columns (explicit ``date_start_col`` / ``date_end_col``, or a ``year_col`` with a
``hydro_year_start`` month), optionally add elevation-band columns, and set the units:

.. code-block:: python

   glacier_mb = hb.GlacierMassBalanceObservations.from_csv(
       '/path/to/mass_balance.csv',
       value_col='Ba', balance_type='annual',
       year_col='year', hydro_year_start='October',   # or date_start_col/date_end_col
       value_unit='mm_we',
   )

What is compared (glaciological vs. geodetic)
"""""""""""""""""""""""""""""""""""""""""""""

Hydrobricks computes the **glaciological (surface) mass balance** — accumulation minus
ablation at the glacier surface, which is exactly what the glaciological method (stakes,
as used by GLAMOS) measures. Per glacier hydro unit and observation period:

.. math::

   B = \Delta S - \sum_t M_\text{ice}

where :math:`S` is the glacier snowpack water equivalent (a stock) and
:math:`M_\text{ice}` the glacier ice-melt flux. This follows from
:math:`B = (P_\text{snow} + \text{refreeze}) - (M_\text{snow} + M_\text{ice})` together
with :math:`\mathrm{d}S/\mathrm{d}t = P_\text{snow} + \text{refreeze} - M_\text{snow}`, so
the snowfall, snowmelt and refreezing terms collapse into :math:`\Delta S` and only the
snowpack stock and the ice melt are needed.

This **flux-based surface** balance is preferred over a state difference
:math:`\Delta(\text{snow} + \text{ice})`. With a delta-h evolution, the state difference
per elevation band is contaminated by the dynamic ice redistribution and becomes a
*geodetic* per-band balance, whereas GLAMOS reports the *glaciological* (surface) balance
per band. The flux formula excludes dynamics and stays a clean surface balance whether or
not the geometry evolves, and works with both the default infinite ice storage and a
finite ice storage. Per-band values are normalized by the model's own (time-varying)
glacier area, for self-consistency with the simulated geometry.

.. note::

   The glacier snowpack and ice-melt series must be recorded so they can be read from
   memory each iteration (no file dump). Two options:

   * create the model with ``record_all=True`` (records everything), or
   * record only what the signal needs by calling ``glacier_mb.configure_recording(model)``
     **before** ``model.setup()`` — a lightweight, targeted alternative that logs just the
     required stores and fluxes (see :ref:`selective_recording`).

   Both a **static glacier** (the default ``glacier_infinite_storage=True``) and an
   evolving glacier (delta-h or area-scaling action) work in a calibration loop: the
   glacier extent and ice volume are automatically reset to their initial state at the
   start of every run, so the model re-runs cleanly across the many iterations.

Three ways to use the mass balance
""""""""""""""""""""""""""""""""""

Discharge stays the **primary** signal (the ``discharge`` argument of
:class:`SpotpySetup <hydrobricks.trainer.SpotpySetup>`); auxiliary signals such as
glacier mass balance are passed as a list to ``extra_observations``. Each auxiliary
signal carries its own ``metric``, ``weight``, ``mode`` and ``tolerance`` (set on the
object), and the setup-level ``combine`` argument selects how the objective terms are
aggregated:

* ``mode='objective'`` with ``combine='weighted'`` — a single score combining the
  discharge and mass-balance goodness of fit, ``discharge_weight * f(Q) + weight *
  f(MB)``. Works with every SPOTPY algorithm (including SCE-UA).
* ``mode='objective'`` with ``combine='pareto'`` — returns a ``[discharge, mass
  balance]`` objective vector for a multi-objective sampler (SPOTPY's ``NSGAII``),
  yielding a Pareto front rather than a single best run.

.. note::

   **Comparable ranges.** Mixing a discharge KGE/NSE (≤ 1, where 1 is perfect) with an
   auxiliary RMSE (in the signal's units, where 0 is perfect) in a weighted sum would let
   the largest-magnitude term dominate and make the weights meaningless. By default
   (``normalize=True``, for ``combine='weighted'``) each term is therefore combined as a
   **benchmark skill score**: an error metric ``E`` becomes ``1 - E / E_ref`` where
   ``E_ref`` is the error of predicting the mean/climatology of that signal's
   observations (for RMSE, an NSE-like score), while skill metrics (NSE, KGE, ...) are
   used as they are. Every term then shares the same scale — **1 = perfect, 0 = no better
   than the benchmark** — so ``discharge_weight`` and each signal's ``weight`` are
   directly comparable. Pass ``normalize=False`` to combine the raw oriented metrics
   instead. ``combine='pareto'`` is unaffected (each objective is optimized on its own).

* ``mode='constraint'`` — a behavioural pass/fail filter: runs whose mean absolute
  mass-balance error exceeds a tolerance are rejected, while the discharge metric remains
  the objective. The tolerance is either absolute, in the signal's units, via
  ``tolerance`` (mm w.e.), or relative via ``relative_tolerance`` (a fraction of the mean
  absolute observed value, e.g. ``0.1`` for 10 %). Set exactly one of the two.

.. code-block:: python

   # Weighted multi-objective (discharge KGE + mass-balance NSE)
   glacier_mb.metric, glacier_mb.weight, glacier_mb.mode = 'nse', 1.0, 'objective'
   spot_setup = trainer.SpotpySetup(
       socont, parameters, forcing, discharge,
       warmup=365,
       obj_func='kge_2012',
       extra_observations=[glacier_mb],
       combine='weighted',
       discharge_weight=1.0,
   )
   sampler = trainer.calibrate(spot_setup, 'sceua', 5000, dbformat='ram')

   # Pareto front (NSGAII needs n_obj via sample_kwargs)
   spot_setup = trainer.SpotpySetup(
       socont, parameters, forcing, discharge, warmup=365,
       obj_func='kge_2012',
       extra_observations=[glacier_mb], combine='pareto',
   )
   sampler = trainer.calibrate(
       spot_setup, 'NSGAII', 5000, dbformat='ram',
       sample_kwargs={'n_obj': 2, 'n_pop': 50},
   )

   # Behavioural filter (reject runs whose mass balance is off by > 500 mm w.e.)
   glacier_mb_constraint = hb.GlacierMassBalanceObservations.from_glamos(
       '/path/to/massbalance_fixdate.csv', kind='whole', glacier_id='B43-03',
       mode='constraint', tolerance=500.0,   # or relative_tolerance=0.1
   )
   spot_setup = trainer.SpotpySetup(
       socont, parameters, forcing, discharge, warmup=365,
       obj_func='kge_2012',
       extra_observations=[glacier_mb_constraint],
   )

The simulated mass balance can also be computed on its own (for plotting or evaluation)
with the observation's ``simulated`` method after a run:

.. code-block:: python

   socont.run(parameters=parameters, forcing=forcing)
   sim_mb = glacier_mb.simulated(socont)

A complete example is available in
`calibrate_with_glacier_mass_balance.py
<https://github.com/hydrobricks/hydrobricks/blob/main/examples/advanced/calibrate_with_glacier_mass_balance.py>`_.

.. _snow_cover_calibration:

Calibrating on snow cover
^^^^^^^^^^^^^^^^^^^^^^^^^^

Observed **snow cover fraction** from remote sensing (e.g. `MODIS
<https://nsidc.org/data/modis>`_) is another independent constraint, particularly on the
snow accumulation and melt parameters. It is used alongside discharge with
:class:`SnowCoverObservations <hydrobricks.evaluation.snow_cover.SnowCoverObservations>`,
another auxiliary observation class in the :mod:`hydrobricks.evaluation` subpackage,
scored by RMSE by default. As with glacier mass balance, everything happens on the Python
side; the simulation itself is unchanged (there is no data assimilation).

From SWE to a snow-cover fraction
"""""""""""""""""""""""""""""""""

The model stores only the snow water equivalent (SWE) per hydro unit, with no explicit
snow-cover-fraction state. The fraction of a hydro unit that is snow-covered is therefore
derived from the recorded SWE at evaluation time, through a simple linear depletion curve:

.. math::

   f = \min\!\left(1, \frac{\text{SWE}}{\text{SWE}_\text{full}}\right)

i.e. the covered fraction grows linearly with SWE until it reaches a full-cover threshold
``swe_full`` [mm w.e.] (a fixed, configurable argument of the observation; default
``100``). When a hydro unit carries several land covers (open ground, glacier, ...), each
with its own snowpack, the unit-level fraction is the land-cover-fraction-weighted mean of
the per-cover fractions. Pass ``land_covers=['open']`` to restrict the signal to specific
land covers (e.g. to ignore snow on glaciers).

Loading the observations
""""""""""""""""""""""""

The observations are per ``(hydro unit, date)`` fractions in ``[0, 1]``. A remote-sensing
raster stack is aggregated per hydro unit (reusing the raster of hydro-unit ids, as for the
gridded forcing); cloud/nodata pixels are ignored, ``value_scale`` rescales e.g. a 0–100 %
product to a fraction, and ``valid_min`` / ``valid_max`` drop out-of-range **quality/error
codes** (many snow products encode clouds, water or no-decision as values above 100). Four
loaders are available, all sharing the aggregation and filtering options:

``from_modis`` reads the MODIS daily snow products (MOD10A1 / MYD10A1), distributed as
HDF-EOS tiles in the sinusoidal projection, one date per file. It parses the date from the
file name, mosaics the tiles of a date, reprojects to the hydro-unit raster's CRS, and
aggregates. The HDF-EOS georeferencing is read from the file's ``StructMetadata`` and the
files are read with xarray's ``netcdf4`` engine, so **no special HDF4/GDAL build is
needed**:

.. code-block:: python

   snow_cover = hb.SnowCoverObservations.from_modis(
       '/path/to/MOD10A1_tiles/',        # a folder of tiles (or a single file)
       raster_hydro_units='/path/to/unit_ids.tif',
       hydro_units=catchment.hydro_units,
       file_pattern='MOD10A1*.hdf',
       variable='NDSI_Snow_Cover',
       value_scale=0.01,                 # 0-100 % -> 0-1
       valid_min=0, valid_max=100,       # drop quality/error codes (> 100)
       min_valid_ratio=0.5,              # drop a unit/date with too many cloudy pixels
       swe_full=100.0,
       cache_dir='/path/to/cache',       # optional: cache the aggregated result
   )

Aggregating a multi-year archive of daily tiles is slow (it reprojects and reduces one
tile per date), so pass ``cache_dir`` to store the per-``(unit, date)`` result as a CSV
named ``snow_cover_<hash>.csv``. The hash is built from the hydro-unit id raster (the
discretization), the aggregation options and a signature of the input tiles, so a later
run with the same inputs loads the CSV directly — while different discretizations or
options never collide. The cache uses the same long format as ``from_csv``. The same
``cache_dir`` option is available on ``from_netcdf`` and ``from_hdf5`` (whose spatial
reprojection and per-unit extraction are likewise worth caching).

For data already stacked into a NetCDF (or HDF5) file with a time dimension, use
``from_netcdf`` (or ``from_hdf5``, which needs the ``h5netcdf`` package):

.. code-block:: python

   snow_cover = hb.SnowCoverObservations.from_netcdf(
       '/path/to/snow_cover.nc',
       raster_hydro_units='/path/to/unit_ids.tif',
       hydro_units=catchment.hydro_units,
       var_name='NDSI_Snow_Cover',
       value_scale=0.01, nodata=255, valid_max=100, swe_full=100.0,
   )

Pre-aggregated per-unit fractions (prepared externally) load from a long-format CSV with
``from_csv`` by mapping the date, unit-id and value columns:

.. code-block:: python

   snow_cover = hb.SnowCoverObservations.from_csv(
       '/path/to/snow_cover.csv',
       date_col='date', unit_col='unit_id', value_col='scf',
       value_scale=1.0, swe_full=100.0,
   )

.. note::

   The snowpack snow-content series (and the land-cover fractions) must be recorded so they
   can be read from memory each iteration. As for glacier mass balance, either create the
   model with ``record_all=True``, or record only what the signal needs by calling
   ``snow_cover.configure_recording(model)`` **before** ``model.setup()`` (see
   :ref:`selective_recording`).

Using the snow cover
""""""""""""""""""""

Snow cover is combined with discharge exactly like glacier mass balance — the same
``mode`` (``'objective'`` / ``'constraint'``), ``weight``, ``tolerance`` /
``relative_tolerance`` and setup-level ``combine`` apply (see
:ref:`glacier_mass_balance_calibration`). The observation's units here are a fraction in
``[0, 1]``, so a constraint ``tolerance`` is also a fraction:

.. code-block:: python

   spot_setup = trainer.SpotpySetup(
       socont, parameters, forcing, discharge,
       warmup=365,
       obj_func='kge_2012',
       extra_observations=[snow_cover],   # metric defaults to 'rmse'
       combine='weighted',
   )
   sampler = trainer.calibrate(spot_setup, 'sceua', 5000, dbformat='ram')

The simulated snow cover can also be computed on its own (for plotting or evaluation) with
the observation's ``simulated`` method after a run:

.. code-block:: python

   socont.run(parameters=parameters, forcing=forcing)
   sim_scf = snow_cover.simulated(socont)

A complete example is available in
`calibrate_with_snow_cover.py
<https://github.com/hydrobricks/hydrobricks/blob/main/examples/advanced/calibrate_with_snow_cover.py>`_.

Prior distributions
^^^^^^^^^^^^^^^^^^^

The default prior distribution is uniform over the parameter range defined by ``min``
and ``max``. A non-uniform prior can be assigned when prior knowledge — from the
literature or previous calibrations — justifies concentrating the search:

.. code-block:: python

   parameters.set_prior('a_snow', spotpy.parameter.Normal(mean=4, stddev=2))

Prior distributions provided by SPOTPY: ``Uniform``, ``Normal``, ``logNormal``,
``Chisquare``, ``Exponential``, ``Gamma``, ``Wald``, ``Weibull``.
