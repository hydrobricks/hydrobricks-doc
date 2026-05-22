.. _basics:

The basics
==========

Model structure
---------------

Hydrobricks models are built from three kinds of objects: **bricks**,
**processes**, and **fluxes**.

A **brick** is any storage that holds water — a snowpack, a glacier, a soil
reservoir, and so on. Each brick can contain multiple water containers: the
snowpack, for instance, tracks snow and liquid water separately.

A **process** extracts water from a brick. Snowmelt, evapotranspiration (ET),
and reservoir outflow are all processes. Each brick can have one or more
processes assigned to it.

A **flux** carries extracted water somewhere: to another brick, to the
atmosphere, or to the basin outlet. Together, bricks, processes, and fluxes
form a directed water-transport graph that is solved at each time step.

Currently, only pre-built model structures are available. An instance is
created by calling the model class with the desired options:

.. code-block:: python

   socont = models.Socont(soil_storage_nb=2)

The available models and their options are described on the
:ref:`models page <models>`.


.. _spatial-structure:

Spatial structure
-----------------

The catchment is discretized into sub-units called **hydro units**, which can
represent elevation bands, hydrological response units (HRUs), raster pixels,
or any other spatial partition. Hydro units can be defined in two ways: loaded
from a CSV file, or generated automatically from a DEM.

.. image:: images/hydro_units.png
   :alt: Example of discretization of a catchment into (a) elevation bands,
         (b) aspect, and (c) radiation. Aspect and radiation discretizations are
         then combined with elevation bands to form HRUs. Source: :cite:t:`Argentin2025`
   :width: 600px
   :align: center


Loading hydro units from a CSV file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The simplest way to define hydro units is to load them from a CSV file. At
minimum, the file must contain the area and mean elevation of each unit:

.. code-block:: python

   hydro_units = hb.HydroUnits()
   hydro_units.load_from_csv(
      'path/to/file.csv', column_elevation='elevation', column_area='area')

The CSV must have two header rows: the first with column names, the second
with units. A minimal example:

.. code-block:: text
   :caption: Example of a CSV file with hydro unit areas.

   num, elevation, area
   -,m,m^2
   0, 790, 2457500
   1, 840, 4481250
   2, 890, 5630625
   3, 940, 5598125
   4, 990, 4551250
   5, 1040, 4579375
   6, 1090, 4128125
   7, 1140, 4807500
   8, 1190, 4643750
   9, 1240, 4662500
   10, 1290, 4158750
   11, 1340, 3496875
   12, 1390, 2361250

By default, each hydro unit has a single ``ground`` land cover. Catchments
with glaciers or other distinct surface types require multiple land covers.
Each land cover has a type (which determines its physical behaviour) and a
name (which distinguishes it from other covers of the same type). For example,
a catchment with bare-ice and debris-covered glacier areas uses three covers:

.. code-block:: python

   land_cover_names = ['ground', 'glacier_ice', 'glacier_debris']
   land_cover_types = ['ground', 'glacier', 'glacier']

   hydro_units = hb.HydroUnits(land_cover_types, land_cover_names)
   hydro_units.load_from_csv(
      'path/to/file.csv', column_elevation='Elevation',
      columns_areas={'ground': 'Area Non Glacier',
                     'glacier_ice': 'Area Ice',
                     'glacier_debris': 'Area Debris'})

The CSV must list the area of each land cover per hydro unit
(more information in :ref:`the Python API <api_hydrounits>`):

.. code-block:: text
   :caption: Example of a CSV file with areas for multiple land cover types.

   Elevation, Area Non Glacier, Area Ice, Area Debris
   m, km2, km2, km2
   3986, 2.408, 0, 0
   4022, 2.516, 0, 0
   4058, 2.341, 0, 0.003
   4094, 2.351, 0, 0.006
   4130, 2.597, 0, 0.01
   4166, 2.726, 0, 0.006
   4202, 2.687, 0, 0.061
   4238, 2.947, 0, 0.065
   4274, 2.924, 0.013, 0.06
   4310, 2.785, 0.019, 0.058
   4346, 2.578, 0.052, 0.176
   4382, 2.598, 0.072, 0.369
   4418, 2.427, 0.129, 0.384
   4454, 2.433, 0.252, 0.333
   4490, 2.210, 0.288, 0.266
   4526, 2.136, 0.341, 0.363
   4562, 1.654, 0.613, 0.275


Generating hydro units from a DEM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When spatial data are available, hydro units can be generated automatically
from a DEM, with discretization criteria chosen to match the melt model in use:

* **Elevation only** — sufficient for ``'degree_day'``
* **Elevation + aspect** — required for ``'degree_day_aspect'``
* **Elevation + radiation** — recommended for ``'temperature_index'``

See :ref:`melt models<melt-models>` for a description of each.

The following example discretizes a study area into 50 m elevation bands
combined with aspect classes. The elevation range covers the entire catchment
(1912–2893 m), with some margin added for the bands:

.. code-block:: python

   study_area = catchment.Catchment(outline='path/to/watershed/shapefile.shp')
   success = study_area.extract_dem('path/to/dem.tif')
   study_area.discretize_by(
      ['elevation', 'aspect'],
      elevation_method='equal_intervals',
      elevation_distance=50,
      min_elevation=1900,
      max_elevation=2900,
   )


Discretizing by potential solar radiation
""""""""""""""""""""""""""""""""""""""""""

The ``'temperature_index'`` melt model requires per-unit radiation values.
Hydrobricks computes the daily mean potential clear-sky direct solar radiation
at the DEM surface [W/m²] using the equation of :cite:t:`Hock1999`. The radiation
resolution defaults to the DEM resolution; for high-resolution DEMs, specify
a coarser resolution to keep computation times reasonable.

.. code-block:: python

   study_area = catchment.Catchment(outline='path/to/watershed/shapefile.shp')
   success = study_area.extract_dem('path/to/dem.tif')
   study_area.calculate_daily_potential_radiation('path/to/file', resolution)

Because radiation depends only on topography, not on the simulation year, the
result can be saved to a GeoTIFF and reloaded in future runs. The default
filename is ``'annual_potential_radiation.tif'``:

.. code-block:: python

   study_area = catchment.Catchment(outline='path/to/watershed/shapefile.shp')
   success = study_area.extract_dem('path/to/dem.tif')
   study_area.load_mean_annual_radiation_raster(
       'path/to/file', filename='annual_potential_radiation.tif')

With the radiation loaded, pass it as a discretization criterion:

.. code-block:: python

   study_area.discretize_by(
      ['elevation', 'radiation'],
      elevation_method='equal_intervals',
      elevation_distance=50,
      min_elevation=1900,
      max_elevation=2900,
      radiation_method='equal_intervals',
      radiation_distance=65,
      min_radiation=0,
      max_radiation=260
   )

