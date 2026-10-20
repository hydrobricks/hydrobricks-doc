.. _forcing-data:

Forcing data
============

The ``Forcing`` class manages all meteorological input data. It reads station
or gridded observations and spatializes them to produce per-unit time series
for every hydro unit. Provide the hydro units when creating the instance:

.. code-block:: python

   forcing = hb.Forcing(hydro_units)

Three input types are supported:

1. **Meteorological station data** spatially interpolated using elevation gradients
2. **Gridded NetCDF data** aggregated to the hydro units
3. **Already spatialized series**, one column per hydro unit or per group of units

All forcing operations — corrections, spatialization, and PET computation —
are queued when defined and executed together, in a fixed order, just before
the model run. This means you can define operations in any order in your script
without worrying about execution sequence.


Loading meteorological station data
-------------------------------------

Station time series are loaded from one or more CSV files. A single file can
contain several variables as separate columns. You specify which column holds
the dates, the date format, and how column names map to hydrobricks variable
names (more information in :ref:`the Python API <api_forcing>`):

.. code-block:: python

   forcing.load_station_data_from_csv(
      'path/to/forcing.csv', 
      column_time='Date', 
      time_format='%d/%m/%Y',
      content={
         'precipitation': 'precip(mm/day)', 
         'temperature': 'temp(C)',
         'pet': 'pet_sim(mm/day)'
      }
   )

A typical forcing CSV:

.. code-block:: text
   :caption: Example of a CSV file containing forcing data.

   Date,precip(mm/day),temp(C),sunshine_dur(h),pet_sim(mm/day)
   01/01/1981,8.24,-0.98,0.42,0.58
   02/01/1981,4.02,-3.35,0.08,0
   03/01/1981,22.27,0.96,0.44,0.95
   04/01/1981,28.85,-2.11,0.08,0
   05/01/1981,8.89,-5.62,0.07,0.06
   ...


Correcting station data
""""""""""""""""""""""""

Raw station data can be corrected before spatialization. A common use case is
compensating for precipitation undercatch, where gauges systematically
under-record precipitation during snowfall:

.. code-block:: python

   forcing.correct_station_data(
      variable='precipitation', 
      correction_factor=1.1
   )

The default method is multiplicative (multiply the data by the factor). An
additive correction is also available, for example to apply a temperature bias
correction:

.. code-block:: python

   forcing.correct_station_data(
      variable='temperature', 
      method='additive', 
      correction_factor=0.5
   )


.. _spatialization:

Spatialization
"""""""""""""""

A single meteorological station records conditions at one point. Spatialization
distributes those measurements across all hydro units using an elevation-based
method. Specify the variable, the method, and the method's parameters:

.. code-block:: python

   forcing.spatialize_from_station_data(
      variable='temperature', 
      method='additive_elevation_gradient',
      ref_elevation=1250,
      gradient=-0.6
   )

This example applies a −0.6 °C/100 m lapse rate relative to a reference
elevation of 1250 m. To make the gradient a calibrated parameter rather than
a fixed value, reference a ``ParameterSet`` entry by name:

.. code-block:: python

   forcing.spatialize_from_station_data(
      variable='temperature',
      method='additive_elevation_gradient',
      ref_elevation=1250,
      gradient='param:temp_gradients'
   )

   parameters.add_data_parameter('temp_gradients', -0.6, min_value=-1, max_value=0)

Supported variables: ``temperature``, ``precipitation``, ``pet``.
Available methods and their parameters are described in
:ref:`the Python API <api_forcing>`.


Loading gridded NetCDF data
-----------------------------

Gridded meteorological products (e.g., reanalyses, radar precipitation) are
often distributed as NetCDF files. Hydrobricks reads all files matching a
wildcard pattern in a given folder and aggregates them to the hydro units:

.. code-block:: python

   forcing.spatialize_from_gridded_data(
      variable='precipitation',
      path='path/to/netcdf/folder',
      file_pattern="RhiresD_ch01r.swisscors_*.nc",
      data_crs=21781,
      var_name='RhiresD',
      dim_x='chx',
      dim_y='chy',
      dim_time='time',
      raster_hydro_units='unit_ids.tif'
   )

Arguments:

* ``variable``: name of the hydrobricks variable to spatialize
  (e.g., ``'precipitation'``, ``'temperature'``).
* ``path``: path to a single NetCDF file or to a folder containing multiple files.
* ``var_name``: name of the variable inside the NetCDF file (e.g., ``'RhiresD'``).
* ``dim_x``, ``dim_y``, ``dim_time``: names of the x, y, and time dimensions.
* ``raster_hydro_units``: path to a GeoTIFF raster of hydro unit IDs, used to assign
  grid cells to units.
* ``file_pattern`` *(optional)*: filename glob pattern when ``path`` is a folder;
  ``*`` matches any sequence of characters (e.g., year numbers). If omitted,
  ``path`` is treated as a single file. Remove files outside the simulation period
  to speed up loading.
* ``data_crs`` *(optional)*: EPSG code of the NetCDF coordinate reference system
  (look up codes at https://epsg.io/). If omitted, the CRS is read from the file.
* ``method`` *(optional)*: spatialization method; currently only
  ``'regrid_from_netcdf'`` is supported (default).
* ``apply_data_gradient`` *(optional)*: if ``True``, elevation-based gradients are
  retrieved from the data and applied to each hydro unit (useful for temperature and
  precipitation). Defaults to ``True`` for temperature and precipitation variables,
  ``False`` for all others.


.. _spatialized-forcing:

Loading already spatialized data
---------------------------------

Some datasets are not a station to interpolate but series that are already resolved
in space: a distributed product, or a series computed once per elevation band. They
are read with ``load_spatialized_data_from_csv()``, one call per variable, and are
taken as they are — no gradient, no correction, no spatialization step afterwards.

The file holds one time column and one data column per hydro unit:

.. code-block:: python

   forcing.load_spatialized_data_from_csv(
      'precipitation.csv',
      variable='precipitation',
      column_time='date',
      time_format='%Y-%m-%d',
   )

The columns can also be shared by groups of units. ``columns_are`` then names a
hydro-unit property whose value picks the column, so a series computed per elevation
band is read by every unit of that band:

.. code-block:: python

   hydro_units.load_from_csv(
      'hydro_units.csv',
      column_elevation='elevation',
      column_area='area',
      other_columns={'band': 'band'},   # the band number of each unit
   )

   forcing.load_spatialized_data_from_csv(
      'temperature.csv',
      variable='temperature',
      column_time='date',
      columns_are='band',               # column headers are band numbers
   )

A unit with no matching column is an error rather than a silently missing series.

A variable that repeats every year — a climatology such as the potential clear-sky
radiation of each unit — is given by day of the year instead of by date, and is
expanded onto the dates of the other variables:

.. code-block:: python

   forcing.load_spatialized_data_from_csv(
      'potential_radiation.csv',
      variable='solar_radiation',
      column_day_of_year='day_of_year',   # 366 rows, one per day of the year
   )

Load a dated variable first, since the climatology has no dates of its own.
``examples/advanced/prevah_ticino.py`` uses all three forms together.


.. _pet:

Computing PET
-------------

When PET observations are not available, hydrobricks can compute them
internally from other meteorological variables using the
`pyet <https://pypi.org/project/pyet/>`_ package:

.. code-block:: python

   forcing.compute_pet(method='Hamon', use=['t', 'lat'], lat=47.3)

The ``method`` argument accepts any method listed in the
`pyet documentation <https://pypi.org/project/pyet/>`_. The ``use`` list names
the input variables in pyet's notation. The time series for these variables
are retrieved from the forcing data after spatialization, so PET is computed
per hydro unit, using the unit's temperature, for example. 
A catchment latitude (``lat``) can be given as a fixed value; 
if omitted, the latitude of each hydro unit is used.

Beyond pyet's own methods, ``'Hamon_vapor_density'`` selects the vapour-density
form of the Hamon equation (:cite:t:`Schulla2000`), the one used by
:ref:`PREVAH-UniBE <prevah-unibe>`:

.. math::

   E_P = 0.1651 \cdot \frac{h_d}{12} \cdot \frac{216.7 \, e_s}{T + 273.3}

where :math:`h_d` is the day length [h], :math:`e_s` the saturation vapour
pressure at the air temperature :math:`T` [hPa] and :math:`T` the daily mean air
temperature [°C]. It needs temperature and latitude only:

.. code-block:: python

   forcing.compute_pet(method='Hamon_vapor_density', use=['t', 'lat'], lat=47.3)

Note that the default ``'Hamon'`` is pyet's exponential variant of the same
equation, which gives markedly higher values (about 1.5 times as much on an
Alpine test catchment). The two are not interchangeable.