.. _advanced:

Advanced features
=================

This page covers different features for more advanced simulations:

* :ref:`Land cover evolution <land-cover-evolution>` — supply time-varying land cover
  (e.g., glacier) evolution from external data (CSV or shapefiles).
* :ref:`Internal glacier evolution <internal_glacier_evolution>` — derive changing glacier area
  internally from modelled ice loss (delta-h or area scaling methods).
* :ref:`Snow to ice transformation <snow-to-ice-transformation>` — convert accumulated
  snow on glaciers to ice at the end of each accumulation season.
* :ref:`Snow redistribution <snow-redistribution>` — prevent unrealistic snow
  accumulation at high elevations using gravitational transport.


.. _land-cover-evolution:

Land cover evolution
--------------------

Land cover fractions can evolve over time within each hydro unit. 
This allows you to simulate processes like glacier retreat, afforestation, or urbanization.
This section covers externally driven evolution, where the area time series is
supplied directly from remote sensing or an external model. Two input formats are
supported: CSV files and shapefiles.

The initial hydro unit areas serve as the starting point; evolution data takes effect
at the dates provided. Changes dated before the simulation start are applied immediately.


.. _land_cover_evolution_csv:

Using CSV files
^^^^^^^^^^^^^^^

The most direct approach: supply a CSV file recording land cover areas at a series of
dates. Call ``load_from_csv()`` once per land cover type; multiple calls accumulate
changes for different land covers into the same action object.

.. code-block:: python

   changes = actions.ActionLandCoverChange()
   changes.load_from_csv(
      '/path/to/surface_changes_glacier_debris.csv',
      hydro_units,
      land_cover='glacier_debris',
      area_unit='km2',
      match_with='elevation'
   )
   model.add_action(changes)

**Parameters** (see also :ref:`API <api_action_land_cover_change>`):

* ``path`` — path to the CSV file.
* ``hydro_units`` — the ``HydroUnits`` instance used for matching.
* ``land_cover`` — name of the land cover to update (e.g., ``'glacier'``,
  ``'glacier_debris'``).
* ``area_unit`` — unit of the area values: ``'m2'`` or ``'km2'``.
* ``match_with`` — how to identify hydro units in the first column:
  ``'elevation'`` *(default)* or ``'id'``.

The CSV format:

* **Header row**: from the second column onward, the dates of the snapshots 
  when land cover changes occur; format ``YYYY-MM-DD``.
* **Remaining rows**: one row per hydro unit that changes, with the identifier value
  followed by the area at each snapshot date.

Hydro units not listed in the file are assumed unchanged. The generic soil cover
fraction (``open``, or its ``ground`` alias) is adjusted automatically to preserve the
total unit area.

.. note::

   The water balance is conserved across land cover changes. When a cover's area
   changes, the water and snow stored on the land that changes hands is transferred
   between the changed cover and the generic soil cover that absorbs the difference, so
   no water is created or destroyed. Glacier ice volume is conserved by the
   :ref:`glacier evolution <internal_glacier_evolution>` methods; an externally driven
   reduction of a glacier's area (CSV or shapefile) removes the ice on the lost area,
   as that ice is assumed to have melted.

.. code-block:: text
   :caption: Example CSV file for land cover evolution (areas in km²).

   elevation,2020-08-01,2025-08-01,2030-08-01,...
   4274,0.013,0.003,0,...
   4310,0.019,0.009,0,...
   4346,0.052,0.042,0.032,...
   4382,0.072,0.062,0.052,...
   4418,0.129,0.119,0.109,...


.. _land_cover_evolution_shapefiles:

Using shapefiles
^^^^^^^^^^^^^^^^^

Hydrobricks can derive the land cover time series automatically from a sequence of
extents provided as shapefiles, specifically for glaciers 
(see also :ref:`API <api_action_land_cover_change>`):

.. code-block:: python

   times = ['2008-01-01', '2010-01-01', '2016-01-01']
   full_glaciers = [
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
      catchment,
      times,
      full_glaciers,
      debris_glaciers,
      with_debris=True,
      method='raster',
      interpolate_yearly=True)
   model.add_action(changes)

**Parameters**:

* ``catchment`` — the ``Catchment`` object (must be discretized into hydro units).
* ``times`` — list of dates (``'YYYY-MM-DD'``) corresponding to each shapefile.
* ``full_glaciers`` — list of paths to shapefiles covering all glacier ice (clean ice
  and debris together), one per date.
* ``debris_glaciers`` — list of paths to debris-only shapefiles, one per date;
  required when ``with_debris=True``.
* ``with_debris`` — if ``True``, splits glacier area into bare-ice and debris-covered
  components; default ``False``.
* ``method`` — area extraction method: ``'vector'`` *(default, more precise)* or
  ``'raster'`` *(faster)*.
* ``interpolate_yearly`` — if ``True`` *(default)*, linearly interpolates areas to
  yearly time steps between the provided dates.

The function also returns a dataframe that can be exported as CSV and reloaded later
using the :ref:`CSV option <land_cover_evolution_csv>`, avoiding repeated raster
processing on subsequent runs:

.. code-block:: python

   changes_df[0].to_csv('/path/to/surface_changes_glacier_ice.csv', index=False)
   changes_df[1].to_csv('/path/to/surface_changes_glacier_debris.csv', index=False)
   changes_df[2].to_csv('/path/to/surface_changes_open.csv', index=False)

The hydro units can also be initialized directly from the derived time series:

.. code-block:: python

   hyd_units.initialize_from_land_cover_change('glacier_ice', changes_df[0])
   hyd_units.initialize_from_land_cover_change('glacier_debris', changes_df[1])


.. _internal_glacier_evolution:

Internal glacier evolution
--------------------------

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
and large glaciers.

The lookup table must be precomputed before running the simulation — see
:ref:`Delta-h lookup table <glacier_lookup_delta_h>` on the preprocessing page.
Once computed (and optionally saved to CSV), link it to the model. The glacier area
is updated at the beginning of the provided month, for example each October 1st
(the start of the hydrological year in Switzerland):

.. code-block:: python

   changes = actions.ActionGlacierEvolutionDeltaH()
   changes.load_from(
      glacier_evolution,
      land_cover='glacier',
      update_month='October'
   )
   model.add_action(changes)

**Parameters for** ``load_from()``
(see also :ref:`API <api_action_glacier_delta_h>`):

* ``obj`` — a ``GlacierEvolutionDeltaH`` preprocessing instance carrying the lookup
  tables.
* ``land_cover`` — land cover name to update; default ``'glacier'``.
* ``update_month`` — month when glacier areas are updated; full English name or integer
  1–12; default ``'October'``.

If the lookup table was saved by the preprocessing step, it can also be loaded
directly from CSV, bypassing the ``GlacierEvolutionDeltaH`` object:

.. code-block:: python

   changes = actions.ActionGlacierEvolutionDeltaH()
   changes.load_from_csv('/path/to/results/folder/')
   model.add_action(changes)

**Parameters for** ``load_from_csv()``:

* ``dir_path`` — path to the directory containing the lookup table files.
* ``land_cover`` — land cover name to update; default ``'glacier'``.
* ``filename_area`` — name of the area lookup table file; default
  ``'glacier_evolution_lookup_table_area.csv'``.
* ``filename_volume`` — name of the volume lookup table file; default
  ``'glacier_evolution_lookup_table_volume.csv'``.
* ``update_month`` — month when glacier areas are updated; default ``'October'``.


.. _glacier_evolution_area_scaling:

Simple area-scaling method
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The area-scaling method establishes a relationship between cumulative ice loss 
and glacier area per hydro unit. It is computationally simpler than the delta-h 
method but less accurate, as it does not account for the glacier dynamics.
It is suitable for applications where the glacier is small and is not expected
to advance during the simulation period.

The lookup table must be precomputed before running the simulation — see
:ref:`Area-scaling lookup table <glacier_lookup_area_scaling>` on the preprocessing
page. Once computed (and optionally saved to CSV), link it to the model:

.. code-block:: python

   changes = hb.actions.ActionGlacierEvolutionAreaScaling()
   changes.load_from(
      glacier_evolution,
      land_cover='glacier',
      update_month='October'
   )
   model.add_action(changes)

**Parameters for** ``load_from()``
(see also :ref:`API <api_action_glacier_area_scaling>`):

* ``obj`` — a ``GlacierEvolutionAreaScaling`` preprocessing instance carrying the
  lookup tables.
* ``land_cover`` — land cover name to update; default ``'glacier'``.
* ``update_month`` — month when glacier areas are updated; full English name or integer
  1–12; default ``'October'``.

If the lookup table has been saved previously, skip recomputation and load it directly:

.. code-block:: python

   changes = hb.actions.ActionGlacierEvolutionAreaScaling()
   changes.load_from_csv('/path/to/results/')
   model.add_action(changes)

**Parameters for** ``load_from_csv()``:

* ``dir_path`` — path to the directory containing the lookup table files.
* ``land_cover`` — land cover name to update; default ``'glacier'``.
* ``filename_area`` — name of the area lookup table file; default
  ``'glacier_evolution_lookup_table_area.csv'``.
* ``filename_volume`` — name of the volume lookup table file; default
  ``'glacier_evolution_lookup_table_volume.csv'``.
* ``update_month`` — month when glacier areas are updated; default ``'October'``.


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


.. _snow-to-ice-transformation:

Snow to ice transformation
--------------------------

At the end of each accumulation season, snow that has accumulated on glacier land
covers is converted to glacier ice. This process is important when using melt-driven
glacier evolution methods (delta-h or area scaling) because these track ice volume to
derive glacier area — snow that remains at season end should be reclassified as ice
to avoid underestimating ice thickness.

.. note::

   This action is used together with the
   :ref:`delta-h <glacier_evolution_delta_h>` or
   :ref:`area-scaling <glacier_evolution_area_scaling>` evolution methods,
   which track ice volume and thickness.
   It is not needed for externally driven land cover changes via CSV or shapefile.

.. code-block:: python

   snow_to_ice = actions.ActionGlacierSnowToIceTransformation(
      update_month='September',
      update_day=30,
      land_cover='glacier'
   )
   model.add_action(snow_to_ice)

**Parameters** (see also :ref:`API <api_action_snow_to_ice>`):

* ``update_month`` — month when the conversion is applied, at the end of the
  accumulation season; full English name or integer 1–12; default ``'September'``.
* ``update_day`` — day of the month when the conversion is applied; default ``30``.
* ``land_cover`` — name of the glacier land cover to update; default ``'glacier'``.


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
at high elevations — so-called "snow towers". Hydrobricks addresses this by moving snow
downslope across hydro units. Two redistribution methods are available, selected through
the ``snow_redistribution`` option:

* ``'transport:snow_slide'`` — the SnowSlide algorithm (:cite:t:`Bernhardt2010`). Snow
  exceeding a slope-dependent holding capacity (decreasing with slope) is transported
  downslope.
* ``'transport:snow_redistribution_frey'`` — the conceptual model of
  :cite:t:`Frey2015`. The snow above a land-cover-specific holding capacity ``H_v`` (the
  ``snow_holding_capacity`` parameter, registered per land cover) is redistributed,
  scaled by a distribution coefficient that increases with slope and decreases with snow
  density, and by a calibratable correction coefficient ``correction`` (``C``). The snow
  density is a constant parameter (``snow_density``).
* ``'transport:snow_redistribution_frey_dynamic'`` — the same Frey & Holzmann method, but
  with the snow density evolving over time: fresh snow density is derived from air
  temperature and the snowpack settles toward a maximum density. Drier (fresher) snow is
  then more mobile.

Enable snow redistribution at model creation:

.. code-block:: python

   socont = models.Socont(
      soil_storage_nb=2,
      snow_redistribution='transport:snow_slide'
   )

Both methods require a slope property on the hydro units and a connectivity CSV file
describing the downslope pathways between hydro units (see
:ref:`Catchment connectivity <catchment-connectivity>` for how to compute it):

.. code-block:: python

   hydro_units.set_connectivity('/path/to/connectivity.csv')

Resources:

* `Working example implementation <https://github.com/hydrobricks/hydrobricks/blob/main/python/examples/basics/snow_redistribution.py>`_
