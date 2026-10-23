.. _project-files:

Project files
=============

The quickest way to set up a simulation is a **project file**: a single YAML
file that declares the whole canonical workflow — which model to build, where
the input files are, how to spatialize the station forcing over the elevation
bands, the modelling periods and the parameter values. Hydrobricks validates
the file as a whole (reporting every problem at once, with hints) and wires up
the model, either from the command line or from Python.

A project file covers the common cases: a catchment discretized into
elevation bands (loaded from a CSV, or :ref:`delineated from a DEM
<project-files-discretization>`), forced either by one meteorological station
(CSV, spatialized with elevation gradients) or by :ref:`gridded netCDF data
<project-files-gridded>` (aggregated per hydro unit) — the two can be mixed,
one source per variable — plus an optional observed discharge series.
A :ref:`calibration section <project-files-calibration>` can declare how the
parameters are optimized, an :ref:`actions section <project-files-actions>`
replays a glacier evolution during the run, and :ref:`study files
<study-files>` cross several project settings into a comparison matrix.
Everything beyond that — custom calibration logic, land cover changes — is
done in Python, starting from the objects the loader returns (see
:ref:`below <project-files-python>`).


Creating a project file
-----------------------

The ``hydrobricks`` command (installed with the package) includes an
interactive wizard that writes the file for you. It reads your CSV files and
proposes the column names, the date format and the data period, so most
questions are answered by pressing Enter:

.. code-block:: console

   $ hydrobricks init
   $ hydrobricks validate project.yaml
   $ hydrobricks run project.yaml

``init`` generates *configuration, not code*: the file can be edited by hand
or regenerated at any time. The generated file ends with the model's full
parameter list (with valid ranges and units) as commented placeholders — fill
them in, then check the file with ``validate``.

``validate`` builds the whole setup and reports every problem in one pass:
unknown keys and typos, missing files, column names not found in the CSV 
headers (listing the available columns), unknown model or parameter names, 
and periods not covered by the forcing data.

``run`` runs the model over the full simulation span, writes the simulated
discharge and the results NetCDF file to the output directory, and — when
observations are declared — prints the scores for each declared period
(calibration / validation / simulation).


An annotated example
--------------------

.. code-block:: yaml

   model:
     name: socont              # socont, gr4j, gr6j, hbv or hbv96
     options:                  # forwarded to the model class (see the models page)
       soil_storage_nb: 2
       surface_runoff: linear_storage

   hydro_units:
     # CSV of elevation bands, with two header rows (names, then units).
     file: hydro_units.csv
     columns:
       elevation: elevation    # column names in the CSV
       area: area
       # Any other entry is loaded as a hydro unit property, e.g.
       # slope: slope          # needed by Socont's kinematic-wave runoff

   forcing:
     file: meteo.csv
     time: {column: date, format: "%d/%m/%Y"}
     columns:
       precipitation: precip(mm/day)
       temperature: temp(C)
       # pet: pet(mm/day)      # provide a PET column, or set forcing.pet below
     ref_elevation: 1253       # station elevation, for the gradients [m]
     temperature:
       gradient: -0.6          # additive lapse rate per 100 m [°C]
     precipitation:
       correction_factor: 0.75 # optional undercatch correction
       gradient: 0.05          # optional multiplicative gradient per 100 m
     pet:
       method: Oudin           # computed with pyet when no 'pet' column is given
       lat: 47.3

   observations:               # optional
     file: discharge.csv
     time: {column: Date, format: "%d/%m/%Y"}
     column: Discharge (mm/d)

   periods:
     calibration: [1981-01-01, 2000-12-31]
     validation: [2001-01-01, 2020-12-31]
     spinup: 2y                # replayed to initialize the states (see Periods)

   output: output              # directory for the results (default: 'output')

   parameters:
     A: 458
     a_snow: 2
     k_slow_1: 0.9
     k_slow_2: 0.8
     k_quick: 1
     percol: 9.8

   calibration:                # optional: how to optimize the parameters
     algorithm: sceua
     repetitions: 10000
     objective: kge_2012
     transform: power(0.2)
     parameters: [a_snow, A, k_slow_1, k_slow_2, k_quick, percol]
     options: {ngs: 8}         # optional: the algorithm's own settings

Relative paths are resolved from the directory containing the project file.
Two example project files are available in the
`examples directory <https://github.com/hydrobricks/hydrobricks/tree/main/examples/basics>`_:
``sitter_project.yaml`` (station forcing, complete and runnable with the
repository's Sitter at Appenzell test data, together with
``run_from_project_file.py``) and ``gridded_dem_project.yaml`` (DEM-delineated
hydro units with gridded MeteoSwiss forcing — point its two grid paths to your
local copies of the products).

.. _project-files-discretization:

Hydro units delineated from a DEM
---------------------------------

Instead of loading a prepared CSV, the hydro units can be delineated directly
from the catchment outline and DEM — the project then needs no preprocessing
at all:

.. code-block:: yaml

   hydro_units:
     outline: outline.shp
     dem: dem.tif
     discretization:
       method: equal_intervals   # or 'quantiles'
       distance: 100             # band height [m] (equal_intervals)
       # number: 25              # number of bands (quantiles)
       # min_elevation: 400      # optional fixed bounds, to homogenize runs
       # split_discontinuous: true  # one hydro unit per connected patch
       # min_patch_area: 10000      # smallest patch to promote [m2]
       # connectivity: 8            # 8 (default) or 4

``file`` and ``discretization`` are mutually exclusive (``columns``,
``columns_areas`` and ``unit_ids_raster`` only apply to the CSV case). The
delineation computes each band's area, mean elevation, slope and aspect from
the DEM — so, for instance, SOCONT's default kinematic-wave surface runoff
(which needs the slope) works out of the box. With gridded forcing, the hydro
unit ids raster is generated automatically in the output directory. The
delineation requires the optional packages ``geopandas``, ``shapely``,
``rasterio`` and ``pyproj``. For other discretizations (aspect, radiation,
combined criteria) use the :ref:`preprocessing API <preprocessing>`.

Only the part of the DEM covering the catchment is read (the outline plus a
1 km margin, rounded outwards to a 1 km grid), so a large regional or national
DEM can be given as is — see
:meth:`Catchment.extract_dem <hydrobricks.Catchment.extract_dem>` to change or
disable the cropping.

An elevation band usually covers several spatially disconnected patches;
``split_discontinuous`` turns each patch into its own hydro unit, with
``min_patch_area`` and ``connectivity`` as described in
:ref:`Spatially discontinuous units <discontinuous-hydro-units>`.


.. _project-files-lateral:

Lateral processes between hydro units
-------------------------------------

The lateral processes — the snow redistribution
(``transport:snow_slide``) — move water between hydro units, so they need to
know the slope of each unit and how the units are connected. The slope is
always part of the hydro units (computed by the delineation, and read from a
hydro units CSV when it has a ``slope`` column), while the connectivity table
is produced by the preprocessing
(:meth:`Catchment.calculate_connectivity
<hydrobricks.Catchment.calculate_connectivity>`) and declared with
``hydro_units.connectivity``:

.. code-block:: yaml

   hydro_units:
     file: hydro_units.csv
     unit_ids_raster: unit_ids.tif
     connectivity: connectivity.csv

The connectivity is only meaningful when the units are spatially connected
patches, i.e. with ``split_discontinuous`` (see
:ref:`Spatially discontinuous units <discontinuous-hydro-units>`). A model
declaring a lateral process without it is rejected: the process would have no
target unit and would silently redistribute nothing.


.. _project-files-subbasins:

Subbasins and gauges
--------------------

A catchment can be run as a :ref:`river network of subbasins <subbasins>`: the
``subbasins`` section names the table of subbasins (``id``, ``downstream``,
optional ``name`` and reach properties such as ``length``), and the hydro units
CSV carries the subbasin of each unit in the column ``hydro_units_column``
(default ``subbasin``). The channel routing along the reaches is a model
option (see :ref:`channel routing <channel-routing>`). The ``observations``
section then accepts a list of gauges: the first entry is the primary signal
(the catchment outlet, or any gauge), the others are additional signals of the
calibration (each scored at its subbasin outlet, with its own ``metric`` and
``weight``). A gauge in m³/s (``units: m3/s``) is converted with the area
drained at its subbasin.

.. code-block:: yaml

   model:
     name: socont
     options:
       channel_routing: muskingum

   hydro_units:
     file: hydro_units.csv          # with a 'subbasin' column

   subbasins:
     file: subbasins.csv            # id, downstream, name, length [m]
     hydro_units_column: subbasin

   observations:
     - file: q_stgallen.csv         # the primary gauge
       time: {column: Date, format: "%d/%m/%Y"}
       column: Q
       units: m3/s
     - file: q_appenzell.csv        # an additional gauge, by subbasin id or name
       time: {column: Date, format: "%d/%m/%Y"}
       column: Q
       subbasin: Appenzell
       metric: nse
       weight: 0.5

   parameters:
     channel_celerity: 1.2
     muskingum_x: 0.2

From Python, ``project.observations`` is the primary gauge and
``project.gauges`` the additional ones; ``project.calibrate()`` passes them as
extra signals, and ``evaluate_periods(project.model, gauge, project.periods)``
scores any gauge at its own outlet.


.. _project-files-gridded:

Gridded forcing
---------------

The forcing can also come from gridded netCDF products (e.g. the MeteoSwiss
``RhiresD``/``TabsD`` grids), declared per variable in a ``gridded`` section.
The grid cells are aggregated over each hydro unit, which requires a raster
of the hydro unit ids (``hydro_units.unit_ids_raster``, as produced by the
preprocessing, e.g. ``catchment.save_unit_ids_raster()``):

.. code-block:: yaml

   hydro_units:
     file: hydro_units.csv
     unit_ids_raster: unit_ids.tif
     # Optional: with an outline and a DEM, elevation gradients can be
     # derived from the gridded data itself (apply_data_gradient below).
     # outline: outline.shp
     # dem: dem.tif

   forcing:
     gridded:
       precipitation:
         path: RhiresD_v2.0_swiss.lv95     # a netCDF file or a folder
         file_pattern: "RhiresD_*.nc"      # when path is a folder
         var_name: RhiresD                 # variable name in the file
         data_crs: 2056                    # EPSG id (omit to read from file)
         dim_x: E                          # dimension names (defaults:
         dim_y: N                          # time, x, y)
       temperature:
         path: TabsD_v2.0_swiss.lv95
         file_pattern: "TabsD_*.nc"
         var_name: TabsD
         data_crs: 2056
         dim_x: E
         dim_y: N
         apply_data_gradient: true         # needs hydro_units.outline + dem
     pet:
       method: Oudin
       lat: 47.3

Station, gridded and :ref:`spatialized <project-files-spatialized>` sources can
be **mixed** — for example gridded precipitation with a station temperature — with
one source per variable (declaring a variable in two of them is an error).
With ``apply_data_gradient: true``, elevation gradients are derived from the
gridded data and applied to the hydro units; this needs the catchment
``outline`` and ``dem`` in the ``hydro_units`` section. The PET is taken from
a ``pet`` source when given, and computed from the temperature otherwise
(``lat`` can be omitted when an outline/DEM is provided, as it is then
derived from the catchment).

The gridded files are read lazily at run time, so ``validate`` checks the
paths, patterns and options, while the data itself (variable names, grid,
time coverage) is checked when the model runs. Reading gridded data requires
the optional packages ``xarray``, ``rioxarray``, ``rasterio`` and ``netCDF4``.

All forcing sources are restricted to the modelling period (the span of the
declared periods) before being spatialized: the station CSV is read over that
period only, and the gridded sources are cut before the regridding, so a long
record does not have to be loaded, regridded and carried to the model in full.
Each source must cover the period; one that does not fails with an explicit
message. A gridded source extending past the other variables (gridded products
are updated at their own cadence, e.g. a PET stack holding the current year
while the meteorological one stops at the end of the previous one) is trimmed
to the common period, whereas a shorter or shifted one is an error. A
``day_of_year`` climatology is not trimmed, being indexed by the day of the
year rather than by dates.

The ``hydrobricks init`` wizard also handles these cases: answer ``dem`` to
the *hydro units source* question to delineate elevation bands, and
``gridded`` to the *forcing source* question — the wizard then reads your
netCDF files to propose the variable names, the dimension names and the data
period.


Parameters outside the default range
------------------------------------

A parameter is normally given as a plain value. Reproducing a published parameter
set sometimes needs a value outside the range hydrobricks allows for it by default,
and the parameter can then carry its own range:

.. code-block:: yaml

   parameters:
     k_quick: 1.2                                 # a plain value
     melt_t_snow: {value: -1.0, min: -3.0, max: 5.0}

The range is widened before the value is set. The value must lie inside the range
given for it, and ``min`` and ``max`` go together: either both or neither.


.. _project-files-spatialized:

Already spatialized forcing
---------------------------

A third source covers series that are not a station to interpolate but are already
resolved in space: a distributed product, or a series computed once per elevation
band. They are declared per variable in a ``spatialized`` section, and are taken as
they are, with no gradient and no correction:

.. code-block:: yaml

   hydro_units:
     file: hydro_units.csv
     columns:
       elevation: elevation
       band: band                       # the band number of each unit

   forcing:
     spatialized:
       precipitation:
         file: precipitation.csv
         time: {column: date, format: "%Y-%m-%d"}
         columns_are: band              # column headers are band numbers
       temperature:
         file: temperature.csv
         time: {column: date, format: "%Y-%m-%d"}
         columns_are: band
       solar_radiation:
         file: potential_radiation.csv
         day_of_year: day_of_year       # a climatology, 366 rows
     pet:
       method: Hamon
       lat: 46.4

Each file holds one time column and one data column per hydro unit. ``columns_are``
says what the headers mean: ``id`` (the default) for hydro unit ids, or the name of a
property declared in ``hydro_units.columns``, whose value picks the column. Grouped
columns are shared, so one series per elevation band is read by every unit of that
band. A unit with no matching column is an error rather than a silently missing
series.

A variable that repeats every year is given by ``day_of_year`` instead of ``time``,
and is expanded onto the dates of the dated variables. Those are loaded first
whatever the order in the file, so a climatology can be declared anywhere in the
section.


.. _project-files-radiation:

Potential radiation
-------------------

A radiation-driven snow melt — ``melt:temperature_index``, the default of
:ref:`PREVAH-UniBE <prevah-unibe>` and an option of the other models — needs the
potential clear-sky radiation of each hydro unit. A ``radiation`` section computes it
from the catchment DEM with the
:ref:`potential radiation <potential-solar-radiation>` of the preprocessing module,
once for every day of the year, and aggregates it on the hydro units:

.. code-block:: yaml

   hydro_units:
     outline: catchment.shp
     dem: dem.tif
     discretization: {method: equal_intervals, distance: 100}   # or unit_ids_raster

   forcing:
     file: meteo.csv
     # ...
     radiation:
       resolution: 100            # optional: grid [m], default: the DEM resolution
       with_cast_shadows: true    # optional (default: true)

The section needs the catchment ``outline`` and ``dem``, and a raster of the hydro unit
ids: the ``unit_ids_raster``, or the one the ``discretization`` writes. All its options
are optional: ``resolution`` (the grid of the computation, coarser being faster),
``atmos_transmissivity`` (default 0.75), ``steps_per_hour`` (default 4) and
``with_cast_shadows`` (default ``true``); ``radiation: potential`` takes them all by
default. The computation is the slowest part of a load, so its result is kept in the
``cache`` and reused by every project on the same DEM and options. The files are
written to ``<output>/radiation``.

A radiation of your own is declared like any other variable instead —
``solar_radiation`` in ``columns``, ``gridded`` or ``spatialized`` (e.g. a
``daily_potential_radiation.nc`` computed once for several studies, as a gridded
source) — but not in both places. A model that reads a radiation no source provides
is reported when the project is loaded.

The radiation melt factor is calibrated against the radiation it multiplies: the
coefficients of a model calibrated with another radiation (e.g. the per-hydrotope one
of the original PREVAH) do not carry over.


Section reference
-----------------

``model``
   Either ``name`` — a pre-built model class (``socont``, ``gr4j``,
   ``gr6j``, ``hbv``, ``hbv96``, ``prevah_unibe``) — or ``structure`` — a
   :ref:`custom model structure <custom-structures>` declared as data (a
   YAML file path or an inline mapping). ``options`` is passed to the model
   constructor (see the :ref:`models page <models>` for each model's
   options).

``hydro_units``
   Either ``file`` — the elevation-band CSV consumed by
   ``HydroUnits.load_from_csv`` (two header rows: names, then units) — or
   ``discretization`` to delineate the bands from the DEM (see
   :ref:`above <project-files-discretization>`). With a CSV, ``columns``
   maps the ``elevation`` and ``area`` columns (defaults: ``elevation``
   and ``area``); any additional entry is loaded as a hydro unit property
   (e.g. ``slope``); ``columns_areas`` can replace the single ``area``
   column with a mapping of land cover name to area column; and
   ``unit_ids_raster`` (required with gridded forcing) is the raster of
   hydro unit ids. ``connectivity`` is the lateral connectivity table
   (see :ref:`above <project-files-lateral>`). ``outline`` and ``dem``
   (together) define a catchment — required for the delineation, and
   enabling elevation gradients derived from gridded data.

``forcing``
   A station CSV, gridded netCDF sources, or both (one source per
   variable); a ``precipitation`` source is required. For the **station**
   part, ``file``, ``time`` (``column``, ``format``) and ``columns`` map
   the forcing variables to the CSV columns. The temperature is
   spatialized with an additive elevation gradient
   (``temperature.gradient``, default −0.6 °C/100 m), the precipitation
   with an optional multiplicative ``correction_factor`` and ``gradient``
   (constant otherwise). ``ref_elevation`` (the station elevation) is
   required whenever a gradient is used. The **gridded** part maps each
   variable to a netCDF source (see :ref:`above <project-files-gridded>`).
   ``radiation`` computes the potential radiation from the DEM (see
   :ref:`above <project-files-radiation>`).
   PET is taken from a ``pet`` source when given, and computed from the
   temperature otherwise (``pet.method``, default ``Oudin``, with
   ``pet.lat`` unless an outline/DEM is given).

``subbasins``
   Optional river network (see :ref:`above <project-files-subbasins>`):
   ``file`` is the subbasin table and ``hydro_units_column`` the column of
   the hydro units CSV naming each unit's subbasin (default ``subbasin``).

``observations``
   Optional observed discharge (``file``, ``time``, ``column``), loaded
   over the full simulation span and returned as a
   ``DischargeObservations``. A list declares several gauges: the first is
   the primary signal, the others additional signals; each may carry
   ``subbasin`` (an id or a name of the network), ``units`` (``mm``,
   default, or ``m3/s``), and for additional gauges ``metric`` and
   ``weight``.

``periods``
   Declares the :ref:`modelling periods <api_periods>`: any of
   ``calibration``, ``validation`` and ``simulation`` as
   ``[start, end]`` pairs (the simulation span defaults to their union),
   plus the ``spinup`` policy (days or e.g. ``'2y'``, default 0). A bare
   pair (``periods: [1981-01-01, 2020-12-31]``) declares the simulation
   span only. The model is set up over the full span, ready for
   ``evaluate_periods``.

``actions``
   Optional: changes applied to the model during the simulation (see
   :ref:`below <project-files-actions>`). ``glacier_evolution`` replays a
   precomputed glacier evolution lookup table.

``calibration``
   Optional: how to optimize the parameters (see
   :ref:`below <project-files-calibration>`). ``algorithm`` (a SPOTPY
   algorithm name, default ``sceua``), ``repetitions``, ``objective`` (a
   metric name, default: the non-parametric KGE), ``transform`` (an optional
   :ref:`discharge transformation <discharge-transformations>` applied in the
   objective, e.g. ``power(0.2)``) and ``parameters`` — the names of the
   parameters to calibrate (model parameters or ``data_parameters``).
   Declaring it requires ``observations`` and a calibration period.
   ``options`` is a mapping of the algorithm's own settings, forwarded to its
   SPOTPY ``sample()`` (e.g. ``{ngs: 8, kstop: 20}`` for ``sceua``, ``trials``
   for ``dds``); their names belong to SPOTPY, so an unknown one fails when the
   calibration starts. ``database`` optionally keeps every sampled set (see
   :ref:`below <project-files-calibration>`).

``output``
   Output directory (default: ``output`` next to the project file).

``cache``
   Directory for the cache of expensive forcing spatializations (e.g.
   regridding gridded data per hydro unit, or the potential radiation),
   automatically reloaded when the
   same setup is reused. Default: ``<output>/cache``; set it explicitly to
   share one cache between several projects on the same data.

``parameters``
   Parameter values by name or alias, passed to
   ``ParameterSet.set_values``. Values can also be set later in Python on
   the returned parameter set (e.g. by a calibration).

``data_parameters``
   Calibratable forcing corrections. Any station gradient or correction
   factor can be a ``param:<name>`` reference instead of a number (e.g.
   ``correction_factor: param:precip_corr_factor``); each referenced name
   is declared here with its ``value`` and optional ``min``/``max`` bounds,
   and becomes a data parameter of the returned parameter set — selectable
   for calibration like any model parameter:

   .. code-block:: yaml

      forcing:
        temperature:
          gradient: param:temp_gradients
        precipitation:
          correction_factor: param:precip_corr_factor

      data_parameters:
        temp_gradients: {value: -0.6, min: -1, max: 0}
        precip_corr_factor: {value: 0.85, min: 0.7, max: 1.3}


.. _project-files-python:

Using project files from Python
-------------------------------

:func:`hydrobricks.load_project` accepts a path to a YAML file (or an
equivalent ``dict``) and returns a :class:`~hydrobricks.Project` — the same
wired-up objects the step-by-step API produces:

.. code-block:: python

   import hydrobricks as hb

   project = hb.load_project('project.yaml')

   simulated = project.run()   # date-indexed pandas Series

   scores = hb.evaluate_periods(
       project.model, project.observations, project.periods,
       metrics=('nse', 'kge_2012'),
   )

The ``Project`` fields are the live objects (``model``, ``forcing``,
``parameters``, ``observations``, ``periods``), so the project file never
limits you: load it, then keep customizing in Python — set or calibrate
parameters on ``project.parameters``, add actions to ``project.model``, or
use ``project.forcing`` in a calibration setup.

.. code-block:: python

   project = hb.load_project('project.yaml')      # the common part
   project.parameters.set_values({'a_snow': 3})   # anything beyond it: Python
   project.model.run(parameters=project.parameters, forcing=project.forcing)

Two variations are available on top:

* ``hb.load_project(..., setup=False)`` builds everything but does **not**
  set the model up — for the cases where something must happen in between,
  such as configuring recordings for auxiliary observations. Call
  ``project.setup()`` afterwards.
* ``project.setup(period='calibration')`` sets the model up over one declared
  period instead of the full span (the spin-up policy is clamped to that
  period) — the split-sample workflow: calibrate on the calibration period,
  then reload the project (full span) and score every period with
  ``evaluate_periods``.


.. _project-files-actions:

Glacier evolution
-----------------

The glacier extent can evolve during the simulation, following a lookup table
precomputed once from the ice thickness — the delta-h parameterization (Huss
et al., 2010; Seibert et al., 2018) or the simpler area scaling. The table is
built with the :ref:`preprocessing API <preprocessing>`
(:class:`~hydrobricks.preprocessing.GlacierEvolutionDeltaH` or
:class:`~hydrobricks.preprocessing.GlacierEvolutionAreaScaling`, which write
the two lookup CSV files), and replayed by the project file:

.. code-block:: yaml

   model:
     name: socont
     options:
       land_cover_types: [ground, glacier]
       land_cover_names: [ground, glacier]
       glacier_infinite_storage: false   # the ice volume is tracked

   hydro_units:
     outline: outline.shp
     dem: dem.tif
     discretization: {method: equal_intervals, distance: 100}
     land_covers:
       glacier: {ice_thickness: ice_thickness.tif}

   actions:
     glacier_evolution:
       method: delta_h              # or 'area_scaling'
       lookup_tables: glacier/      # directory holding the two lookup CSVs
       land_cover: glacier          # the cover to update (default: 'glacier')
       update_month: October        # applied every year (default: 'October')

The lookup tables are read from ``lookup_tables`` under their default names
(``glacier_evolution_lookup_table_area.csv`` and
``..._volume.csv``; override them with ``filename_area`` / ``filename_volume``).
Their first row is the initial state, which must match the glacier area the
hydro units start from — so the same glacier extent has to initialize both the
lookup table and the ``hydro_units.land_covers``. The ice volume is tracked, so
the glacier cannot be an infinite storage.

Other actions (land cover changes, snow-to-ice transformation) are added in
Python on ``project.model`` (see :ref:`below <project-files-python>`).


.. _project-files-calibration:

Calibrating a project
---------------------

With a ``calibration`` section (and ``observations`` plus a calibration
period), the whole split-sample workflow is one call —
:meth:`Project.calibrate <hydrobricks.Project.calibrate>`:

.. code-block:: python

   project = hb.load_project('project.yaml')

   best = project.calibrate()          # optimizes on the calibration period
   print(best['score'], best['parameters'])

   simulated = project.run()           # best values applied, full span
   scores = hb.evaluate_periods(
       project.model, project.observations, project.periods,
       metrics=('kge_2012', 'nse'),
   )

``calibrate()`` optimizes the declared ``parameters`` with the declared
``algorithm``/``objective``/``transform`` on the calibration period (with the
project's spin-up), applies the best values to ``project.parameters`` and
returns the :func:`trainer.get_best <hydrobricks.trainer.get_best>` record
(plus the SPOTPY ``sampler`` for further analysis). Every setting can be
overridden per call — ``project.calibrate(algorithm='mc', repetitions=500)``
— so the file holds the defaults, not a straitjacket. Since a model instance
is single-use, the calibration runs on a fresh internal build of the project
over the calibration period; the loaded project stays set up over the full
span, ready for the validation ``run()``.

Only the best set survives the call. To keep the whole sample — every
parameter set with its objective value, i.e. what a convergence analysis of
the optimization needs — declare a ``database``:

.. code-block:: yaml

   calibration:
     algorithm: sceua
     repetitions: 10000
     parameters: [a_snow, A]
     database:
       format: csv              # or 'sql', 'hdf5'
       path: sampled/runs       # default: <output>/calibration
       save_simulations: false  # default

.. warning::

   ``save_simulations`` stores the **simulated series of every iteration**,
   one column per time step and per repetition: some 1 GB for 10 000
   repetitions over 40 years, held for the whole calibration. It is off by
   default, and the parameters and objective values alone are enough for a
   convergence analysis.

The same is available without any Python through :ref:`study files
<study-files>`, which also cross several settings (catchments, models,
objectives, transformations, ...) into a comparison matrix. For anything
beyond a single objective — auxiliary observations such as snow cover,
weighted multi-signal objectives, Pareto calibration — hand the project's
objects to the :ref:`trainer <calibration>` directly (load with ``param:``
forcing references where the corrections should be calibrated, and select
``project.parameters.allow_changing``).
