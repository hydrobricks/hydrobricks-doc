.. _advanced:

Advanced features
=================

This page covers three features for multi-decade or physically complex simulations:

* :ref:`Land cover evolution <land-cover-evolution>` — supply time-varying glacier
  extents from observations (CSV or shapefiles). Best for historical simulations with
  a known extent time series.
* :ref:`Glacier evolution <glacier-evolution>` — derive changing glacier area
  internally from modelled ice loss (delta-h or area scaling). Required when no
  observed extent series exists, e.g. for future projections.
* :ref:`Snow redistribution <snow-redistribution>` — prevent unrealistic snow
  accumulation at high elevations using the SnowSlide gravitational transport
  algorithm.


.. _land-cover-evolution:

Land cover evolution
--------------------

Land cover fractions can evolve over time within each hydro unit. For multi-decade
simulations, glacier retreat can substantially alter the catchment response, and
ignoring it produces unrealistic results.

This section covers externally driven evolution, where the area time series is
supplied directly from remote sensing or an external model. Two input formats are
supported: CSV files and shapefiles.

The initial hydro unit areas serve as the starting point; evolution data takes effect
at the dates provided. Changes dated before the simulation start are applied immediately.


.. _land_cover_evolution_csv:

Using CSV files
^^^^^^^^^^^^^^^

The most direct approach: supply a CSV file recording land cover areas at a series of
dates. Hydrobricks interpolates between snapshots during the simulation.

.. code-block:: python

   changes = actions.ActionLandCoverChange()
   changes.load_from_csv(
      '/path/to/surface_changes_glacier_debris.csv',
      hydro_units,
      area_unit='km2',
      match_with='elevation'
   )
   model.add_action(changes)

``load_from_csv()`` can be called multiple times for different files — for instance,
one per land cover type.

The CSV format:

* **First row**: land cover name (e.g., ``glacier_debris``), repeated for each date column.
* **Second row**: the date of each snapshot.
* **Remaining rows**: one row per hydro unit that changes, starting with the unit
  identifier (elevation or ID), then the area at each snapshot date.

Hydro units not listed in the file are assumed unchanged. The ``ground`` fraction is
adjusted automatically to preserve the total unit area.

Hydro units can be identified either by elevation (``match_with='elevation'``) or by
ID (``match_with='id'``).

.. code-block:: text
   :caption: Example CSV file for land cover evolution (areas in km²).

   bands,glacier_debris,glacier_debris,glacier_debris,...
   ,01/08/2020,01/08/2025,01/08/2030,...
   4274,0.013,0.003,0,...
   4310,0.019,0.009,0,...
   4346,0.052,0.042,0.032,...
   4382,0.072,0.062,0.052,...
   4418,0.129,0.119,0.109,...


.. _land_cover_evolution_shapefiles:

Using shapefiles
^^^^^^^^^^^^^^^^^

Glacier extents from field surveys or remote sensing are often available as shapefiles.
Hydrobricks can derive the land cover time series automatically from a sequence of such
extents:

.. code-block:: python

   times = ['2008-01-01', '2010-01-01', '2016-01-01']
   ice_glaciers = [
      '/path/to/glacier_ice_2008.shp',
      '/path/to/glacier_ice_2010.shp',
      '/path/to/glacier_ice_2016.shp'
   ]
   debris_glaciers = [
      '/path/to/glacier_debris_2008.shp',
      '/path/to/glacier_debris_2010.shp',
      '/path/to/glacier_debris_2016.shp'
   ]
   changes, changes_df = actions.ActionLandCoverChange.create_action_for_glaciers(
      study_area,
      times,
      ice_glaciers,
      debris_glaciers,
      with_debris=True,
      method='raster',
      interpolate_yearly=True)
   model.add_action(changes)

The function also returns a dataframe that can be exported as CSV and reloaded later
using the :ref:`CSV option <land_cover_evolution_csv>`, avoiding repeated raster
processing on subsequent runs:

.. code-block:: python

   changes_df[0].to_csv('/path/to/surface_changes_glacier_ice.csv', index=False)
   changes_df[1].to_csv('/path/to/surface_changes_glacier_debris.csv', index=False)
   changes_df[2].to_csv('/path/to/surface_changes_ground.csv', index=False)

The hydro units can also be initialized directly from the derived time series:

.. code-block:: python

   hyd_units.initialize_from_land_cover_change('glacier_ice', changes_df[0])
   hyd_units.initialize_from_land_cover_change('glacier_debris', changes_df[1])


Handling missing early data
""""""""""""""""""""""""""""

If the earliest available glacier extent is dated after the simulation start, assume a
constant initial state by duplicating the earliest entry and assigning it the simulation
start date:

.. code-block:: python

   times = ['2005-01-01', '2008-01-01', '2010-01-01', '2016-01-01']
   ice_glaciers = [
      '/path/to/Glacier_ice_2008.shp',  # used as the 2005 initial state
      '/path/to/Glacier_ice_2008.shp',
      '/path/to/Glacier_ice_2010.shp',
      '/path/to/Glacier_ice_2016.shp'
   ]


.. _glacier-evolution:

Glacier evolution
-----------------

The two methods below drive glacier area changes from modelled ice loss rather than
external observations. Both require an initial ice thickness raster and produce a
lookup table that maps cumulative mass loss to glacier area. This makes them suitable
for future projections where no observed extent time series exist.

.. note::

   Both methods apply only to bare-ice glacier land covers and do not handle
   debris-covered glacier areas.


.. _glacier_evolution_delta_h:

Delta-h method
^^^^^^^^^^^^^^^

The delta-h method (:cite:t:`Huss2010`, as implemented by :cite:t:`Seibert2018`) redistributes ice loss
according to a characteristic elevation-dependent melt profile, capturing the tendency
of glaciers to thin faster at lower elevations. It is the preferred approach for medium
and large glaciers. We recommend using 10 m elevation bands for the glacier, consistent
with :cite:t:`Seibert2018`.

First, compute the initial ice thickness and build the lookup table from an ice
thickness raster:

.. code-block:: python

   study_area = catchment.Catchment(outline='path/to/watershed/shapefile.shp')
   glacier_evolution = preprocessing.GlacierEvolutionDeltaH()
   glacier_df = glacier_evolution.compute_initial_ice_thickness(
      study_area,
      ice_thickness=glacier_thickness,
      elevation_bands_distance=10
   )
   glacier_evolution.compute_lookup_table(update_width=False)

Then link the lookup table to the model. The glacier area is updated each October (the
end of the hydrological year):

.. code-block:: python

   changes = actions.ActionGlacierEvolutionDeltaH()
   changes.load_from(
      glacier_evolution, 
      land_cover='glacier',
      update_month='October'
   )
   model.add_action(changes)

The lookup table and initial glacier dataframe can be saved for later reuse:

.. code-block:: python

   glacier_df.to_csv('/path/to/surface_changes_glacier.csv', index=False)
   glacier_evolution.save_as_csv('/path/to/results/folder/')


.. _glacier_evolution_area_scaling:

Simple area-scaling method
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The area-scaling method derives glacier area from ice volume using a volume–area
power-law relationship. It is simpler than delta-h and best suited for small glaciers
where a detailed elevation-dependent melt profile is not warranted.

First, compute the lookup table from an ice thickness raster:

.. code-block:: python

   study_area = catchment.Catchment(outline='path/to/watershed/shapefile.shp')

   glacier_evolution = hb.preprocessing.GlacierEvolutionAreaScaling()
   glacier_evolution.compute_lookup_table(
      study_area, 
      ice_thickness='path/to/ice_thickness.tif'
   )

   # Save for later reuse
   glacier_evolution.save_as_csv('/path/to/results/')

Then link the lookup table to the model:

.. code-block:: python

   changes = hb.actions.ActionGlacierEvolutionAreaScaling()
   changes.load_from(
      glacier_evolution, 
      land_cover='glacier',
      update_month='October'
   )
   model.add_action(changes)

If the lookup table has been saved previously, skip recomputation and load it directly:

.. code-block:: python

   changes = hb.actions.ActionGlacierEvolutionAreaScaling()
   changes.load_from_csv('/path/to/results/')
   model.add_action(changes)


.. _glacier_options:

Glacier-related options
^^^^^^^^^^^^^^^^^^^^^^^

Two options control the internal glacier representation and must match the evolution
method in use:

``glacier_infinite_storage``
   When ``True``, the glacier is treated as having unlimited thickness: the area can
   change but ice does not thin. Use with the externally driven methods (CSV or
   shapefiles), which supply area directly without tracking ice volume.

``snow_ice_transformation``
   Rate at which accumulated snow converts to glacier ice [mm/day]; default
   ``0.002`` mm/day. Set to ``False`` to disable. Enable with the melt-driven methods,
   which track ice thickness to derive area.

Recommended settings:

* For **externally driven** area changes (CSV or shapefile):

  .. code-block:: python

     glacier_infinite_storage = True
     snow_ice_transformation = False

* For **melt-driven** glacier evolution (delta-h or area scaling):

  .. code-block:: python

     glacier_infinite_storage = False
     snow_ice_transformation = True

Pass these options at model initialization:

.. code-block:: python

   socont = models.Socont(
      ...,
      glacier_infinite_storage=glacier_infinite_storage,
      snow_ice_transformation=snow_ice_transformation
   )


.. _snow-redistribution:

Snow redistribution
-------------------

.. list-table::
   :widths: 50 50

   * - .. figure:: images/snow_redistribution_before.png
          :alt: Snow height without snow redistribution
          :align: center

     - .. figure:: images/snow_redistribution_after.png
          :alt: Snow height with snow redistribution
          :align: center

Without redistribution, elevation-band models can accumulate unrealistic amounts of snow
at high elevations — so-called "snow towers". Hydrobricks addresses this with the
SnowSlide algorithm (:cite:t:`Bernhardt2010`), which simulates gravitational transport of snow
downslope across elevation bands.

Enable snow redistribution at model creation:

.. code-block:: python

   socont = models.Socont(
      soil_storage_nb=2,
      snow_redistribution='transport:snow_slide'
   )

A connectivity CSV file describing the downslope pathways between hydro units is also
required:

.. code-block:: python

   hydro_units.set_connectivity('/path/to/connectivity.csv')

Resources:

* `Working example implementation <https://github.com/hydrobricks/hydrobricks/blob/main/python/examples/basics/snow_redistribution.py>`_
* `Script to compute the connectivity CSV <https://github.com/hydrobricks/hydrobricks/blob/main/python/examples/preprocessing/compute_lateral_connectivity.py>`_
