.. _preprocessing:

Preprocessing
=============

This page covers the preprocessing steps required before running simulations that
use the :ref:`snow redistribution <snow-redistribution>` or the
:ref:`melt-driven glacier evolution <internal_glacier_evolution>` features.
All preprocessing classes live in the ``hydrobricks.preprocessing`` module.

* :ref:`Catchment connectivity <catchment-connectivity>` — derives the fraction of
  flow that leaves each hydro unit toward each downslope neighbor; required for snow
  redistribution.
* :ref:`Glacier evolution lookup tables <glacier-lookup-tables>` — precomputes the
  relationship between cumulative ice loss and glacier area per hydro unit; required
  for the delta-h and area-scaling glacier evolution methods.


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

If an ice thickness GeoTIFF is available (e.g. from :cite:t:`Farinotti2019`),
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
Ice thickness is then estimated per elevation band using the Bahr et al. (1997)
volume–area formula.

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
  the topography; otherwise uses the Bahr et al. formula at each step.

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
