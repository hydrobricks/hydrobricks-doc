.. _preprocessing:

Preprocessing
=============

This page covers preprocessing steps that prepare spatial inputs for the model.
All preprocessing classes live in the ``hydrobricks.preprocessing`` module and are
accessible through the ``Catchment`` object.

* :ref:`Catchment topography <catchment-topography>` — compute slope and aspect from
  the DEM; required when discretizing by slope or aspect.
* :ref:`Catchment discretization <catchment-discretization>` — divide the catchment
  into hydro units based on elevation, aspect, slope, or radiation.
* :ref:`Catchment connectivity <catchment-connectivity>` — derive the fraction of
  flow leaving each hydro unit toward each downslope neighbor; required for snow
  redistribution.
* :ref:`Potential solar radiation <potential-solar-radiation>` — compute daily mean
  clear-sky direct radiation per DEM cell; required when discretizing by radiation.
* :ref:`Glacier evolution lookup tables <glacier-lookup-tables>` — precompute the
  relationship between cumulative ice loss and glacier area per hydro unit; required
  for the delta-h and area-scaling glacier evolution methods.


.. _catchment-topography:

Catchment topography
--------------------

``CatchmentTopography`` computes slope and aspect from the DEM. It is accessible via
``catchment.topography`` and is called automatically by discretization when needed,
so explicit use is only required in special cases (e.g. generating a hillshade for
visualization).

Slope and aspect are computed on demand from the loaded DEM:

.. code-block:: python

   catchment = hb.Catchment(outline='path/to/watershed.shp')
   catchment.extract_dem('path/to/dem.tif')
   catchment.topography.calculate_slope_aspect()

After this call, ``catchment.topography.slope`` and ``catchment.topography.aspect``
hold 2D arrays (in degrees) at the DEM resolution.

.. note::

   ``discretize_by()`` calls ``calculate_slope_aspect()`` automatically if it has not
   been called yet, so an explicit call is usually unnecessary.

When computing potential solar radiation at a coarser resolution, the DEM is first
resampled and slope/aspect are recalculated at the target resolution:

.. code-block:: python

   catchment.topography.resample_dem_and_calculate_slope_aspect(
      resolution=100,
      output_path='path/to/output/dir/'
   )

**Parameters** (see also :ref:`API <api_catchment_topography>`):

* ``resolution`` — target pixel size in meters; if ``None`` or equal to the DEM
  resolution, the original DEM is used without resampling.
* ``output_path`` — directory where the resampled DEM GeoTIFF is written; required
  when resampling.


.. _catchment-discretization:

Catchment discretization
-------------------------

``CatchmentDiscretization`` divides the catchment into hydro units. It is accessible
via ``catchment.discretization``, but most workflows call it through the ``Catchment``
convenience methods ``catchment.discretize_by()`` and
``catchment.create_elevation_bands()``.

**Elevation bands only**

For models that need elevation-based units only, use the ``create_elevation_bands()``
shortcut:

.. code-block:: python

   catchment = hb.Catchment(outline='path/to/watershed.shp')
   catchment.extract_dem('path/to/dem.tif')
   catchment.create_elevation_bands(
      method='equal_intervals',
      distance=100,
      min_elevation=1800,
      max_elevation=3200
   )

**Parameters** (see also :ref:`API <api_catchment_discretization>`):

* ``method`` — ``'equal_intervals'`` *(default)*: fixed contour spacing set by
  ``distance``; ``'quantiles'``: equal-area bands set by ``number``.
* ``number`` — number of bands for the ``'quantiles'`` method.
* ``distance`` — band spacing in meters for the ``'equal_intervals'`` method;
  default ``50``.
* ``min_elevation`` / ``max_elevation`` — force the elevation range, useful to keep
  band boundaries consistent across runs.

**Multiple criteria**

To combine elevation with aspect, slope, or radiation, use ``discretize_by()``. The
``criteria`` argument is a list of any combination of ``'elevation'``, ``'aspect'``,
``'slope'``, and ``'radiation'``.

.. code-block:: python

   catchment.discretize_by(
      ['elevation', 'aspect'],
      elevation_method='equal_intervals',
      elevation_distance=50,
      min_elevation=1900,
      max_elevation=2900
   )

Additional keyword arguments control each criterion independently:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Parameter
     - Description
   * - ``elevation_method``
     - ``'equal_intervals'`` (use ``elevation_distance``) or ``'quantiles'``
       (use ``elevation_number``); default ``'equal_intervals'``.
   * - ``elevation_distance``
     - Band spacing in meters; default ``100``.
   * - ``elevation_number``
     - Number of bands for the quantiles method; default ``100``.
   * - ``min_elevation`` / ``max_elevation``
     - Force the elevation range.
   * - ``slope_method``
     - ``'equal_intervals'`` or ``'quantiles'``; default ``'equal_intervals'``.
   * - ``slope_distance``
     - Band spacing in degrees; default ``15``.
   * - ``slope_number``
     - Number of slope bands for quantiles; default ``6``.
   * - ``min_slope`` / ``max_slope``
     - Force the slope range (degrees); defaults ``0`` / ``90``.
   * - ``radiation_method``
     - ``'equal_intervals'`` or ``'quantiles'``; default ``'equal_intervals'``.
   * - ``radiation_distance``
     - Band spacing in W/m²; default ``50``.
   * - ``radiation_number``
     - Number of radiation bands for quantiles; default ``5``.
   * - ``min_radiation`` / ``max_radiation``
     - Force the radiation range.

.. note::

   Aspect is always split into four cardinal-direction classes (N, E, S, W) and
   has no configurable parameters.

After discretization, save the hydro unit table and the unit-ID raster for
reuse in subsequent runs:

.. code-block:: python

   catchment.save_hydro_units_to_csv('path/to/hydro_units.csv')
   catchment.save_unit_ids_raster('path/to/output/dir/')

To reload an existing unit-ID raster instead of rerunning discretization:

.. code-block:: python

   catchment.load_unit_ids_from_raster('path/to/output/dir/', 'unit_ids.tif')


.. _potential-solar-radiation:

Potential solar radiation
--------------------------

The ``'temperature_index'`` melt model and radiation-based discretization both
require per-cell daily mean potential clear-sky direct solar radiation [W/m²].
Hydrobricks computes it using the equation of :cite:t:`Hock1999`, accounting for
terrain slope, aspect, latitude, and optionally cast shadows.

Because radiation depends only on topography, not the simulation period, it is
computed once and saved for reuse.

.. code-block:: python

   catchment = hb.Catchment(outline='path/to/watershed.shp')
   catchment.extract_dem('path/to/dem.tif')
   catchment.calculate_daily_potential_radiation(
      output_path='path/to/output/dir/',
      resolution=100
   )

``calculate_daily_potential_radiation()`` writes two files to ``output_path``:

* ``daily_potential_radiation.nc`` — daily mean radiation for each day of the year.
* ``annual_potential_radiation.tif`` — mean annual radiation, used as the
  discretization input.

**Parameters** (see also :ref:`API <api_potential_solar_radiation>`):

* ``output_path`` — directory where the output files are written.
* ``resolution`` — computation resolution in meters; defaults to the DEM resolution.
  For high-resolution DEMs, specify a coarser value to keep run times manageable.
* ``atmos_transmissivity`` — mean clear-sky atmospheric transmissivity; default
  ``0.75`` (value from :cite:t:`Hock1999`).
* ``steps_per_hour`` — number of solar-angle integration steps per hour; default
  ``4``. Higher values improve accuracy at the cost of computation time.
* ``with_cast_shadows`` — if ``True`` *(default)*, terrain cast shadows are included.

On subsequent runs, reload the saved annual mean raster instead of recomputing:

.. code-block:: python

   catchment.load_mean_annual_radiation_raster(
      'path/to/output/dir/',
      filename='annual_potential_radiation.tif'
   )

With the radiation loaded, include ``'radiation'`` in the discretization criteria:

.. code-block:: python

   catchment.discretize_by(
      ['elevation', 'radiation'],
      elevation_method='equal_intervals',
      elevation_distance=50,
      radiation_method='equal_intervals',
      radiation_distance=65,
      min_radiation=0,
      max_radiation=260
   )


.. _catchment-connectivity:

Catchment connectivity
----------------------

Snow redistribution requires a connectivity table describing how water (or snow)
flows between hydro units. Hydrobricks derives this from the DEM flow direction using
the D8 algorithm (via the ``pysheds`` library).

The catchment must already have a DEM and hydro units defined before this step
(see :ref:`Generating hydro units from a DEM <spatial-structure>`).

.. code-block:: python

   catchment = hb.Catchment(outline='path/to/watershed.shp')
   catchment.extract_dem('path/to/dem.tif')
   catchment.discretize_by(['elevation', 'aspect'], ...)

   connectivity = catchment.calculate_connectivity(mode='multiple')

**Parameters** (see also :ref:`API <api_catchment_connectivity>`):

* ``mode`` — ``'multiple'`` *(default)*: keeps all downslope connections weighted
  by contributing flow; ``'single'``: keeps only the dominant connection.
* ``force_connectivity`` — if ``True``, units with no downslope neighbor within the
  catchment are connected to their neighbors proportionally to the shared border
  length; default ``False``.
* ``precision`` — number of decimal places for connectivity fractions; default ``3``.

The result is a ``DataFrame``; save it to CSV for later use:

.. code-block:: python

   connectivity.to_csv('path/to/connectivity.csv', index=False)

When setting up the model, load it into the ``HydroUnits`` object:

.. code-block:: python

   hydro_units.set_connectivity('path/to/connectivity.csv')

Or pass the ``DataFrame`` directly if it is already in memory:

.. code-block:: python

   hydro_units.set_connectivity(connectivity)


.. _glacier-lookup-tables:

Glacier evolution lookup tables
--------------------------------

Both melt-driven glacier evolution methods require a lookup table that maps
cumulative ice loss to glacier area and volume for each hydro unit. This table is
computed once from static glacier data and reused across model runs.

.. note::

   Both methods use elevation bands for the glacier itself, which are typically
   finer (e.g. 10 m) than the hydro units used for the rest of the catchment.
   The delta-h method in particular is designed for 10 m bands
   (:cite:t:`Seibert2018`).


.. _glacier_lookup_delta_h:

Delta-h lookup table
^^^^^^^^^^^^^^^^^^^^^

Two initialization paths are available depending on the available input data.

**From an ice thickness raster**

If an ice thickness GeoTIFF is available (e.g. from :cite:t:`Grab2021` or :cite:t:`Farinotti2019`),
pass it to ``compute_initial_ice_thickness()``. The glacier extent is derived
automatically from the non-zero thickness pixels.

.. code-block:: python

   import hydrobricks.preprocessing as preprocessing

   catchment = hb.Catchment(outline='path/to/watershed.shp')
   catchment.extract_dem('path/to/dem.tif')

   glacier_evolution = preprocessing.GlacierEvolutionDeltaH()
   glacier_df = glacier_evolution.compute_initial_ice_thickness(
      catchment,
      ice_thickness='path/to/ice_thickness.tif',
      elevation_bands_distance=10
   )
   glacier_evolution.compute_lookup_table(catchment=catchment)

**From a glacier outline only**

When no thickness data is available, supply a glacier outline shapefile instead.
Ice thickness is then estimated per elevation band using the
:cite:t:`Bahr1997` volume–area formula.

.. code-block:: python

   glacier_evolution = preprocessing.GlacierEvolutionDeltaH()
   glacier_df = glacier_evolution.compute_initial_ice_thickness(
      catchment,
      glacier_outline='path/to/glacier_outline.shp',
      elevation_bands_distance=10
   )
   glacier_evolution.compute_lookup_table(catchment=catchment)

**Parameters for** ``compute_initial_ice_thickness()``
(see also :ref:`API <api_preproc_glacier_delta_h>`):

* ``catchment`` — the ``Catchment`` object with DEM loaded.
* ``ice_thickness`` — path to a GeoTIFF of glacier thickness in meters; provide
  either this or ``glacier_outline``, not both.
* ``glacier_outline`` — path to a shapefile of glacier extent; used when no
  thickness raster is available.
* ``elevation_bands_distance`` — spacing between elevation bands in meters;
  default ``10``.
* ``pixel_based_approach`` — if ``True`` *(default)*, glacier area evolution uses
  the topography; otherwise uses the :cite:t:`Bahr1997` formula at each step.

**Parameters for** ``compute_lookup_table()``:

* ``catchment`` — required when ``pixel_based_approach=True``.
* ``nb_increments`` — number of melt increments in the table; default ``200``.
* ``update_width`` — whether to update glacier width at each increment per
  Eq. 7 of :cite:t:`Seibert2018`; default ``True``.
  Ignored when ``pixel_based_approach=True``.

The lookup table can be inspected via ``glacier_df`` and saved for reuse:

.. code-block:: python

   glacier_df.to_csv('path/to/glacier_profile.csv', index=False)
   glacier_evolution.save_as_csv('path/to/output/dir/')

``save_as_csv()`` writes two files to the specified directory:

* ``glacier_evolution_lookup_table_area.csv`` — glacier area (m²) per hydro unit
  and melt increment.
* ``glacier_evolution_lookup_table_volume.csv`` — glacier volume (m³) per hydro
  unit and melt increment.

On subsequent runs, skip recomputation and load the saved files:

.. code-block:: python

   changes = actions.ActionGlacierEvolutionDeltaH()
   changes.load_from_csv('path/to/output/dir/')
   model.add_action(changes)


.. _glacier_lookup_area_scaling:

Area-scaling lookup table
^^^^^^^^^^^^^^^^^^^^^^^^^^

The area-scaling method derives glacier area from ice volume using a power-law
relationship. It requires an ice thickness GeoTIFF.

.. code-block:: python

   import hydrobricks.preprocessing as preprocessing

   catchment = hb.Catchment(outline='path/to/watershed.shp')
   catchment.extract_dem('path/to/dem.tif')

   glacier_evolution = preprocessing.GlacierEvolutionAreaScaling()
   glacier_evolution.compute_lookup_table(
      catchment,
      ice_thickness='path/to/ice_thickness.tif'
   )

**Parameters for** ``compute_lookup_table()``
(see also :ref:`API <api_preproc_glacier_area_scaling>`):

* ``catchment`` — the ``Catchment`` object with DEM loaded and hydro units defined.
* ``ice_thickness`` — path to a GeoTIFF of glacier thickness in meters.
* ``nb_increments`` — number of melt increments in the table; default ``200``.

Save the result for reuse:

.. code-block:: python

   glacier_evolution.save_as_csv('path/to/output/dir/')

On subsequent runs:

.. code-block:: python

   changes = hb.actions.ActionGlacierEvolutionAreaScaling()
   changes.load_from_csv('path/to/output/dir/')
   model.add_action(changes)
