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
Everything beyond that — glacier evolution, custom calibration logic — is
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
       latitude: 47.3

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

``file`` and ``discretization`` are mutually exclusive (``columns``,
``land_cover_areas`` and ``unit_ids_raster`` only apply to the CSV case). The
delineation computes each band's area, mean elevation, slope and aspect from
the DEM — so, for instance, SOCONT's default kinematic-wave surface runoff
(which needs the slope) works out of the box. With gridded forcing, the hydro
unit ids raster is generated automatically in the output directory. The
delineation requires the optional packages ``geopandas``, ``shapely``,
``rasterio`` and ``pyproj``. For other discretizations (aspect, radiation,
combined criteria) use the :ref:`preprocessing API <preprocessing>`.


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
     # derived from the gridded data itself (elevation_gradient below).
     # outline: outline.shp
     # dem: dem.tif

   forcing:
     gridded:
       precipitation:
         path: RhiresD_v2.0_swiss.lv95     # a netCDF file or a folder
         file_pattern: "RhiresD_*.nc"      # when path is a folder
         var_name: RhiresD                 # variable name in the file
         crs: 2056                         # EPSG id (omit to read from file)
         dim_x: E                          # dimension names (defaults:
         dim_y: N                          # time, x, y)
       temperature:
         path: TabsD_v2.0_swiss.lv95
         file_pattern: "TabsD_*.nc"
         var_name: TabsD
         crs: 2056
         dim_x: E
         dim_y: N
         elevation_gradient: true          # needs hydro_units.outline + dem
     pet:
       method: Oudin
       latitude: 47.3

Station and gridded sources can be **mixed** — for example gridded
precipitation with a station temperature — with one source per variable
(declaring a variable both in ``columns`` and in ``gridded`` is an error).
With ``elevation_gradient: true``, elevation gradients are derived from the
gridded data and applied to the hydro units; this needs the catchment
``outline`` and ``dem`` in the ``hydro_units`` section. The PET is taken from
a ``pet`` source when given, and computed from the temperature otherwise
(``latitude`` can be omitted when an outline/DEM is provided, as it is then
derived from the catchment).

The gridded files are read lazily at run time, so ``validate`` checks the
paths, patterns and options, while the data itself (variable names, grid,
time coverage) is checked when the model runs. Reading gridded data requires
the optional packages ``xarray``, ``rioxarray``, ``rasterio`` and ``netCDF4``.

The ``hydrobricks init`` wizard also handles these cases: answer ``dem`` to
the *hydro units source* question to delineate elevation bands, and
``gridded`` to the *forcing source* question — the wizard then reads your
netCDF files to propose the variable names, the dimension names and the data
period.


Section reference
-----------------

``model``
   Either ``name`` — a pre-built model class (``socont``, ``gr4j``,
   ``gr6j``, ``hbv96``) — or ``structure`` — a
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
   (e.g. ``slope``); ``land_cover_areas`` can replace the single ``area``
   column with a mapping of land cover name to area column; and
   ``unit_ids_raster`` (required with gridded forcing) is the raster of
   hydro unit ids. ``outline`` and ``dem`` (together) define a catchment —
   required for the delineation, and enabling elevation gradients derived
   from gridded data.

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
   PET is taken from a ``pet`` source when given, and computed from the
   temperature otherwise (``pet.method``, default ``Oudin``, with
   ``pet.latitude`` unless an outline/DEM is given).

``observations``
   Optional observed discharge (``file``, ``time``, ``column``), loaded
   over the full simulation span and returned as a
   ``DischargeObservations``.

``periods``
   Declares the :ref:`modelling periods <api_periods>`: any of
   ``calibration``, ``validation`` and ``simulation`` as
   ``[start, end]`` pairs (the simulation span defaults to their union),
   plus the ``spinup`` policy (days or e.g. ``'2y'``, default 0). A bare
   pair (``periods: [1981-01-01, 2020-12-31]``) declares the simulation
   span only. The model is set up over the full span, ready for
   ``evaluate_periods``.

``output``
   Output directory (default: ``output`` next to the project file).

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

Calibration follows the same pattern: load a project file without parameter
values (with ``param:`` forcing references where the corrections should be
calibrated), select ``project.parameters.allow_changing`` and hand the objects
to the :ref:`trainer <calibration>` — this is how the calibration examples of
the repository are written. Two variations are available on top:

* ``hb.load_project(..., setup=False)`` builds everything but does **not**
  set the model up — for the cases where something must happen in between,
  such as configuring recordings for auxiliary observations. Call
  ``project.setup()`` afterwards.
* ``project.setup(period='calibration')`` sets the model up over one declared
  period instead of the full span (the spin-up policy is clamped to that
  period) — the split-sample workflow: calibrate on the calibration period,
  then reload the project (full span) and score every period with
  ``evaluate_periods``.
