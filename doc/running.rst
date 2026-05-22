.. _running:

Running the model and outputs
==============================

.. _model-instance:

Running the model
-----------------

Once you have defined the :ref:`hydro units <spatial-structure>`,
:ref:`parameters <parameters>`, and :ref:`forcing <forcing-data>`, set up and
run the model:

.. code-block:: python

   socont.setup(spatial_structure=hydro_units, output_path='/path/to/dir',
                start_date='1981-01-01', end_date='2020-12-31')

   socont.run(parameters=parameters, forcing=forcing)

The outlet discharge (in mm/d) can then be retrieved:

.. code-block:: python

   sim_ts = socont.get_outlet_discharge()

To export all internal fluxes and states to a NetCDF file for further analysis:

.. code-block:: python

   socont.dump_outputs('/output/dir/')


Initializing state variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, all water storages (snowpack, soil reservoirs, etc.) start empty at
the beginning of the simulation. To initialize them to more realistic values,
call ``initialize_state_variables()`` between ``setup()`` and ``run()``:

.. code-block:: python

   socont.initialize_state_variables(parameters=parameters, forcing=forcing)
   socont.run(parameters=parameters, forcing=forcing)

This runs the model once over the full simulation period, captures the final
storage values, and uses them as the starting point for subsequent runs. When
the model is run multiple times — as during calibration — it resets to these
saved values at the start of each run rather than to empty reservoirs.


Warmup period
^^^^^^^^^^^^^^

Even with ``initialize_state_variables()``, the very first years of a
simulation are typically unreliable because the storages have not yet settled
into a realistic seasonal cycle. This initial period is called the **warmup**
or **spin-up** period, and it is conventionally set to one or two years.

During the warmup, snow accumulation and discharge are usually underestimated
because the snowpack starts from the previous season's final state, which may
not match the actual initial conditions. For this reason, the warmup years
should be excluded from evaluation, calibration, and analysis. The calibration
setup accepts a ``warmup`` argument for this purpose — see the
:ref:`calibration page <calibration>`.


Evaluation
^^^^^^^^^^^

After a run, performance metrics can be computed by comparing the simulated
discharge to observations. Load observations from a CSV file (discharge in
mm/d):

.. code-block:: python

   obs = hb.Observations()
   obs.load_from_csv('/path/to/obs.csv', column_time='Date', time_format='%d/%m/%Y',
                     content={'discharge': 'Discharge (mm/d)'})
   obs_ts = obs.data[0]

   nse = socont.eval('nse', obs_ts)
   kge_2012 = socont.eval('kge_2012', obs_ts)

Metrics are provided by the `HydroErr package <https://hydroerr.readthedocs.io>`_.
Any metric from their
`full list <https://hydroerr.readthedocs.io/en/stable/list_of_metrics.html>`_
can be used by passing its function name as a string.


Outputs
-------

Results are available at three levels of detail:

1. `Direct outputs`_ — scalar or time-series summaries available immediately
   after a run.
2. A `NetCDF output file`_ — per-hydro-unit fluxes and states, exported on
   demand.
3. :ref:`Auxiliary files <others>` — spatialized forcing, log files, and
   calibration records.


Direct outputs
^^^^^^^^^^^^^^^

The following outputs are accessible on the model object after a run:

**Time series:**

* ``get_outlet_discharge()``: daily discharge at the basin outlet (mm/d)

**Integrated totals over the simulation period:**

* ``get_total_outlet_discharge()``: total discharge at the outlet
* ``get_total_et()``: total evapotranspiration
* ``get_total_water_storage_changes()``: net change in total water storage
  from the start to the end of the simulation
* ``get_total_snow_storage_changes()``: net change in snow storage


.. _netcdf-output-file:

NetCDF output file
^^^^^^^^^^^^^^^^^^^

A detailed NetCDF file is exported with ``model.dump_outputs('some/path')``.
How much data it contains depends on the ``record_all`` option set at model
creation:

* ``record_all=False`` (default): only outlet discharge and a few selected
  time series are stored. Use this during calibration.
* ``record_all=True``: every flux and state variable is recorded at every
  time step. This is useful for diagnosing model behaviour but slows execution
  and produces large files.

**File structure**

Dimensions:

* ``time``: the temporal axis
* ``hydro_units``: one entry per hydro unit (e.g., per elevation band)
* ``aggregated_values``: catchment-scale (lumped) quantities
* ``distributed_values``: per-hydro-unit quantities
* ``land_covers``: one entry per land cover type

Global attributes that map variable indices to names:

* ``labels_aggregated``: names of lumped elements (fluxes and states)
* ``labels_distributed``: names of distributed elements
* ``labels_land_covers``: names of land covers

To inspect the available labels:

.. code-block:: python

   results = hb.Results('path/to/netcdf_results_file')
   print(results.results.attrs)

Example output for GSM-Socont with two glacier types:

.. code-block:: text

   labels_aggregated =
      "glacier_area_rain_snowmelt_storage:content",
      "glacier_area_rain_snowmelt_storage:outflow:output",
      "glacier_area_icemelt_storage:content",
      "glacier_area_icemelt_storage:outflow:output",
      "outlet";

   labels_distributed =
      "ground:content",
      "ground:infiltration:output",
      "ground:runoff:output",
      "glacier_ice:content",
      "glacier_ice:outflow_rain_snowmelt:output",
      "glacier_ice:melt:output",
      "glacier_debris:content",
      "glacier_debris:outflow_rain_snowmelt:output",
      "glacier_debris:melt:output",
      "ground_snowpack:content",
      "ground_snowpack:snow",
      "ground_snowpack:melt:output",
      "glacier_ice_snowpack:content",
      "glacier_ice_snowpack:snow",
      "glacier_ice_snowpack:melt:output",
      "glacier_debris_snowpack:content",
      "glacier_debris_snowpack:snow",
      "glacier_debris_snowpack:melt:output",
      "slow_reservoir:content",
      "slow_reservoir:et:output",
      "slow_reservoir:outflow:output",
      "slow_reservoir:percolation:output",
      "slow_reservoir:overflow:output",
      "slow_reservoir_2:content",
      "slow_reservoir_2:outflow:output",
      "surface_runoff:content",
      "surface_runoff:outflow:output";

   labels_land_covers =
      "ground",
      "glacier_ice",
      "glacier_debris";

**Variables in the file:**

* ``time`` (1D): dates as Modified Julian Dates (days since 1858-11-17 00:00)
* ``hydro_units_ids`` (1D): IDs of the hydro units
* ``hydro_units_areas`` (1D): area of each hydro unit [m²]
* ``sub_basin_values`` (2D): lumped time series, indexed by ``labels_aggregated``
* ``hydro_units_values`` (2D): distributed time series, indexed by
  ``labels_distributed``. Two important subtypes:

  * **Flux variables** (names ending in ``:output``, unit: mm): already weighted
    by land cover fraction and relative hydro unit area. You can sum them
    directly over all hydro units to get the catchment-total contribution of a
    component (e.g., total glacier melt).
  * **State variables** (names ending in ``:content`` or ``:snow``, unit: mm):
    the water depth stored in a reservoir. These are *not* area-weighted — to
    aggregate over the catchment, multiply each value by its land cover fraction
    and relative hydro unit area.

* ``land_cover_fractions`` (2D, optional): time series of land cover fractions,
  present when glacier or other land cover evolution is active.


.. _others:

Auxiliary outputs
^^^^^^^^^^^^^^^^^^

* **Spatialized forcing** (``forcing.nc``): the per-unit forcing time series,
  saved with ``forcing.create_file()``. Useful for inspecting what the model
  actually received as input.
* **Log files** (``hydrobricks_...log``): execution logs that record warnings
  and errors, useful for debugging.
* **Hydro units raster** (``hydro_units.tif``): a GeoTIFF with unit IDs as
  pixel values, useful for spatial visualization.
* **Hydro units table** (``hydro_units.csv``): unit properties (elevation,
  area, land cover fractions) in tabular form.
* **Annual radiation raster** (``annual_potential_radiation.tif``): potential
  clear-sky solar radiation, saved during preprocessing.
* **Calibration records**: SPOTPY saves every model evaluation to CSV or SQL
  during calibration.
