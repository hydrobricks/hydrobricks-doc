.. _preprocessing:

Preprocessing
=============

This page covers preprocessing steps that prepare spatial inputs for the model.
All preprocessing classes live in the ``hydrobricks.preprocessing`` module and are
accessible through the ``Catchment`` object.

* :ref:`Catchment topography <catchment-topography>` — compute slope and aspect from
  the DEM; required when discretizing by slope or aspect.
* :ref:`Catchment discretization <catchment-discretization>` — divide the catchment
  into hydro units based on elevation, aspect, slope, radiation, or sub-catchment
  membership.
* :ref:`Land cover extraction <land-cover-extraction>` — set the land-cover fractions
  of each hydro unit from a raster (e.g. ESA WorldCover, CORINE) or a vector dataset
  (e.g. swissTLMRegio).
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

A hillshade can be generated for visualization purposes:

.. code-block:: python

   hillshade = catchment.topography.get_hillshade(
      azimuth=315,
      altitude=45,
      z_factor=1
   )

``get_hillshade()`` returns a 2D NumPy array of values in the range 0–255. It
requires that the DEM has been loaded (``catchment.extract_dem()``); slope and
aspect do not need to be pre-computed.

**Parameters** (see also :ref:`API <api_catchment_topography>`):

* ``resolution`` — target pixel size in meters; if ``None`` or equal to the DEM
  resolution, the original DEM is used without resampling.
* ``output_path`` — directory where the resampled DEM GeoTIFF is written; required
  when resampling.

For ``get_hillshade()``:

* ``azimuth`` — sun azimuth in degrees (0–360); default ``315`` (north-west).
* ``altitude`` — sun elevation angle in degrees (0–90); default ``45``.
* ``z_factor`` — vertical exaggeration factor to amplify relief; default ``1``.


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
* ``split_discontinuous`` / ``min_patch_area`` / ``connectivity`` — optionally create
  one hydro unit per connected patch, see
  :ref:`Spatially discontinuous units <discontinuous-hydro-units>`.

**Multiple criteria**

To combine elevation with aspect, slope, radiation, or sub-catchment membership, use
``discretize_by()``. The ``criteria`` argument is a list of any combination of
``'elevation'``, ``'aspect'``, ``'slope'``, ``'radiation'``, and ``'sub_catchments'``.

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
   * - ``sub_catchments``
     - Path to a vector file of sub-catchment polygons; required when
       ``'sub_catchments'`` is in ``criteria``.
   * - ``split_discontinuous``
     - Split a hydro unit made of several disconnected patches into one hydro unit
       per patch; default ``False``. Requires scipy.
   * - ``min_patch_area``
     - Minimum area (m²) for a disconnected patch to become its own hydro unit;
       default ``None`` (no minimum).
   * - ``connectivity``
     - Pixel connectivity defining a patch, ``8`` *(default)* or ``4``.

.. note::

   Aspect is always split into four cardinal-direction classes (N, E, S, W) and
   has no configurable parameters.

**Sub-catchments**

Including ``'sub_catchments'`` in the criteria keeps a hydro unit from spanning
spatially-distant areas: each DEM cell is assigned to the sub-catchment polygon
covering it, and units are formed within a single sub-catchment. The polygons must
cover the whole catchment; if any part of the catchment is left uncovered, an error is
raised (the area is not silently dropped).

.. code-block:: python

   catchment.discretize_by(
      ['elevation', 'sub_catchments'],
      elevation_distance=50,
      sub_catchments='path/to/sub_catchments.shp'
   )

The resulting sub-catchment id of each unit is stored as the ``sub_catchment``
hydro-unit property.

.. _discontinuous-hydro-units:

**Spatially discontinuous units**

Hydro units are defined by combinations of criteria, not by geometry: all the cells
matching a combination share the same unit id, wherever they are in the catchment. A
single hydro unit therefore usually covers several spatially disconnected patches —
for instance the 2000–2050 m north-facing band on two opposite valley flanks. This is
the default behaviour and is often what is wanted, as it keeps the number of units
low.

It has a cost, though: the mean slope, aspect, latitude and longitude of such a unit
average over patches that may be kilometers apart, which matters for the processes
using them (e.g. the lateral snow redistribution).

Set ``split_discontinuous=True`` to create one hydro unit per connected patch
instead. Unlike ``'sub_catchments'``, it needs no additional data:

.. code-block:: python

   catchment.discretize_by(
      ['elevation', 'aspect'],
      elevation_distance=100,
      split_discontinuous=True,
      min_patch_area=10000
   )

``min_patch_area`` (m²) guards against a proliferation of tiny units: a patch smaller
than this threshold does not become its own unit but is merged into the largest
retained patch of the same unit, so no area is ever lost. If no patch of a unit
reaches the threshold, the unit is left unsplit. ``connectivity`` selects whether
diagonal neighbours belong to the same patch (``8``, the default) or not (``4``).

.. note::

   Splitting refines the discretization: it increases the number of hydro units and
   renumbers them. The unit-ID raster changes accordingly, so any cached gridded
   forcing, radiation or snow-cover aggregation is recomputed.

After discretization, save the hydro unit table and the unit-ID raster for
reuse in subsequent runs:

.. code-block:: python

   catchment.save_hydro_units_to_csv('path/to/hydro_units.csv')
   catchment.save_unit_ids_raster('path/to/output/dir/')

To reload an existing unit-ID raster instead of rerunning discretization:

.. code-block:: python

   catchment.load_unit_ids_from_raster('path/to/output/dir/', 'unit_ids.tif')


.. _land-cover-extraction:

Land cover extraction
---------------------

Once the catchment has been discretized, the land-cover fractions of each hydro unit
can be set from a categorical raster or a vector dataset. This is handled by the
``CatchmentLandCover`` class, accessible via ``catchment.land_cover``. Each source
class is mapped to a hydrobricks land cover (``open``, ``forest``, ``glacier``,
``lake``, or a user-defined name); classes without a mapping entry fall into the
residual absorbed by the generic (soil) cover. Covers targeted by the mapping that the
catchment does not yet declare are registered automatically.

**From a raster (e.g. ESA WorldCover, CORINE)**

.. code-block:: python

   catchment = hb.Catchment(outline='path/to/watershed.shp')
   catchment.extract_dem('path/to/dem.tif')
   catchment.create_elevation_bands(distance=50)

   catchment.land_cover.extract_from_raster(
      'path/to/worldcover.tif',
      dataset='esa_worldcover'
   )

The raster is warped onto the DEM grid even when its coordinate reference system
differs from the catchment (e.g. ESA WorldCover is provided in EPSG:4326 while the DEM
is projected), so no manual reprojection is required.

.. note::

   ESA WorldCover is distributed as many 3°×3° tiles. Point at the tile covering the
   catchment (or a VRT/mosaic of the relevant tiles), not the containing directory.

**From a vector dataset (e.g. swissTLMRegio)**

.. code-block:: python

   catchment.land_cover.extract_from_shapefile(
      'path/to/land_cover.shp',
      class_field='OBJEKTART',
      mapping={'Wald': 'forest', 'Gletscher': 'glacier'}
   )

The polygons are reprojected to the catchment CRS and rasterized onto the DEM grid;
each cell is assigned to a single class (the first match in the mapping wins).

.. note::

   For convenience, the ``Catchment`` also exposes the equivalent passthroughs
   ``catchment.extract_land_cover_from_raster(...)`` and
   ``catchment.extract_land_cover_from_shapefile(...)``.

**Class mapping**

The class-to-cover mapping can be supplied as a ``mapping`` dict and/or selected from
a built-in ``dataset`` preset. Built-in presets are ``'esa_worldcover'`` and
``'corine'`` (exposed as ``CatchmentLandCover.PRESETS``); a ``mapping`` dict overrides
or extends the chosen preset. At least one of ``mapping`` or ``dataset`` must be
provided.

.. code-block:: python

   # Preset, with a couple of classes overridden
   catchment.land_cover.extract_from_raster(
      'path/to/worldcover.tif',
      dataset='esa_worldcover',
      mapping={50: 'urban'}  # map built-up to a user-defined cover
   )

**Parameters** (see also :ref:`API <api_land_cover_extraction>`):

* ``raster_path`` / ``shapefile_path`` — path to the land-cover dataset.
* ``class_field`` *(shapefile only)* — attribute field holding each feature's class
  code.
* ``mapping`` — dict mapping source class codes to hydrobricks land-cover names.
* ``dataset`` — name of a built-in preset: ``'esa_worldcover'`` or ``'corine'``.
* ``all_touched`` *(shapefile only)* — if ``True`` *(default)*, a cell is assigned to a
  class as soon as a polygon touches it; if ``False``, only cells whose centre falls
  within a polygon are assigned.

.. note::

   These methods set the *initial* land-cover fractions and must be called before
   ``Model.setup()``. The generic soil cover (``open``) absorbs the residual area
   automatically, so it is never passed as a mapping target on its own.


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
* ``land_cover`` — name of the glacier land cover to initialize; if ``None``
  *(default)*, the single land cover of type ``glacier`` is detected automatically.
* ``initialize_cover`` — if ``True`` *(default)*, the glacier land-cover fractions of
  each hydro unit are set from the extracted areas, so the model starts with the actual
  glacier extent. Set to ``False`` only if you initialize the glacier cover separately
  (e.g. from a land-cover-change CSV or shapefiles).

.. note::

   Because ``compute_initial_ice_thickness()`` initializes the glacier cover by default,
   you should **not** also call ``catchment.initialize_area_from_land_cover_change()`` for
   the same glacier — doing so applies the glacier area twice and drives the residual
   (generic ``open``) cover negative. Pass ``initialize_cover=False`` if you need to set
   the cover yourself.

**Parameters for** ``compute_lookup_table()``:

* ``catchment`` — required when ``pixel_based_approach=True``.
* ``nb_increments`` — number of melt increments in the table; default ``200``.
* ``update_width`` — whether to update glacier width at each increment per
  Eq. 7 of :cite:t:`Seibert2018`; default ``True``.
  Ignored when ``pixel_based_approach=True``.

**Calibrating the delta-h profile from two surveys (optional)**

By default ``compute_lookup_table()`` uses the generic polynomial delta-h
parameterization of :cite:t:`Huss2010`. If two ice thickness surveys are available
(e.g. from two different years), the observed elevation-dependent thinning profile
can be derived from the data and used instead:

.. code-block:: python

   # Derive observed delta-h profile from two thickness rasters
   observed_dh = glacier_evolution.compute_ice_thickness_change(
      catchment,
      ice_thickness_old='path/to/thickness_2000.tif',
      ice_thickness_new='path/to/thickness_2020.tif',
      elevation_bands_distance=10
   )

   # Use it when building the lookup table
   glacier_evolution.compute_lookup_table(
      catchment=catchment,
      observed_dh=observed_dh
   )

**Parameters for** ``compute_ice_thickness_change()``:

* ``catchment`` — the ``Catchment`` object with DEM loaded.
* ``ice_thickness_old`` — path to the GeoTIFF of the earlier glacier thickness survey
  (in meters).
* ``ice_thickness_new`` — path to the GeoTIFF of the more recent glacier thickness
  survey (in meters).
* ``elevation_bands_distance`` — spacing between elevation bands in meters;
  default ``10``.
* ``smooth_window`` — window size for 1-D rolling smoothing applied to the
  aggregated thinning curve before normalization; ``None`` disables smoothing;
  default ``5``.
* ``nodata`` — value to treat as no-data in the input rasters (replaced with NaN);
  default ``None``.

The method returns a ``DataFrame`` with the normalized thinning profile (columns
``dh`` and ``normalized_elevation``) that is passed directly to
``compute_lookup_table()`` via the ``observed_dh`` argument.

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

The area-scaling method establishes a relationship between cumulative ice loss 
and glacier area per hydro unit. It is computationally simpler than the delta-h 
method but less accurate, as it does not account for the glacier dynamics.
It is suitable for applications where the glacier is small and is not expected
to advance during the simulation period. It requires an ice thickness GeoTIFF.

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
