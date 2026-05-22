.. _parameters:

Parameters and forcing data
============================

.. _parameters-section:

Parameters
----------

All parameters for a model run are held in a single ``ParameterSet`` object.
Each parameter has the following attributes
(more information in :ref:`the Python API <api_parameterset>`):

* **component**: the model component it belongs to (e.g., ``glacier``, ``slow_reservoir``)
* **name**: the full parameter name (e.g., ``degree_day_factor``)
* **unit**: the physical unit (e.g., ``mm/d/°C``)
* **aliases**: short names accepted by ``set_values()`` (e.g., ``a_snow``)
* **value**: the currently assigned value
* **min** / **max**: the valid range, used during calibration and for validation
* **default_value**: a pre-set value, if any. Parameters with defaults (such as melt
  temperatures) are optional — you only need to set them if you want to deviate from
  the default.
* **mandatory**: whether the user must supply a value (i.e., the parameter has no default)
* **prior**: prior distribution for Bayesian or Monte Carlo calibration —
  see :ref:`the calibration page <calibration>`


Creating a parameter set
^^^^^^^^^^^^^^^^^^^^^^^^^

For pre-built models, call ``generate_parameters()`` on the model instance.
This produces a ``ParameterSet`` populated with all parameters appropriate for
the chosen model configuration, including their names, aliases, units, and
default ranges:

.. code-block:: python

   socont = models.Socont(soil_storage_nb=2)
   parameters = socont.generate_parameters()


Assigning parameter values
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``set_values()`` with a dictionary. Keys can be either the full parameter
name (e.g., ``snowpack:degree_day_factor``) or any alias (e.g., ``a_snow``):

.. code-block:: python

   parameters.set_values({'A': 100, 'k_slow': 0.01, 'a_snow': 5})


Parameter constraints
^^^^^^^^^^^^^^^^^^^^^^

Constraints enforce ordering relationships between parameters. They are checked
during calibration — any parameter set that violates a constraint is rejected.
To add a custom constraint:

.. code-block:: python

   parameters.define_constraint('k_slow_2', '<', 'k_slow_1')

Supported operators: ``>`` (or ``gt``), ``>=`` (or ``ge``), ``<`` (or ``lt``),
``<=`` (or ``le``).

Models define some constraints automatically — for example, GSM-Socont requires
``a_snow < a_ice`` because the ice melt factor must exceed the snow melt factor.
These built-in constraints can be removed when needed:

.. code-block:: python

   parameters.remove_constraint('a_snow', '<', 'a_ice')


Parameter ranges
^^^^^^^^^^^^^^^^^

Each parameter is generated with a default range. The calibration algorithm
samples within this range, and values outside it are rejected. To adjust the
range for a parameter:

.. code-block:: python

   parameters.change_range('a_snow', 2, 5)


Calibratable forcing parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some aspects of forcing data preparation — elevation gradients, correction
factors — can themselves be calibrated. Because these depend on the input data
rather than the model structure, they are not generated automatically and must
be added explicitly:

.. code-block:: python

   parameters.add_data_parameter('precip_corr_factor', 1, min_value=0.7, max_value=1.3)
   parameters.add_data_parameter('precip_gradient', 0.05, min_value=0, max_value=0.2)
   parameters.add_data_parameter('temp_gradients', -0.6, min_value=-1, max_value=0)

The first argument is the parameter name, the second is the initial value.
For details on how these parameters link to spatialization operations, see the
:ref:`Spatialization <spatialization>` section below.

For seasonally varying quantities such as temperature lapse rates, monthly
values and ranges can be specified:

.. code-block:: python

   parameters.add_data_parameter(
       'temp_gradients',
       [-0.6, -0.6, -0.6, -0.6, -0.7, -0.7, -0.8, -0.8, -0.8, -0.7, -0.7, -0.6],
       min_value=[-0.8]*12,
       max_value=[-0.3]*12)


.. _forcing-data:

Forcing data
------------

The ``Forcing`` class manages all meteorological input data. It reads station
or gridded observations and spatializes them to produce per-unit time series
for every hydro unit. Provide the hydro units when creating the instance:

.. code-block:: python

   forcing = hb.Forcing(hydro_units)

Two input types are supported:

1. **Meteorological station data** spatially interpolated using elevation gradients
2. **Gridded NetCDF data** aggregated to the hydro units


Loading meteorological station data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Station time series are loaded from one or more CSV files. A single file can
contain several variables as separate columns. You specify which column holds
the dates, the date format, and how column names map to hydrobricks variable
names (more information in :ref:`the Python API <api_forcing>`):

.. code-block:: python

   forcing.load_station_data_from_csv(
       'path/to/forcing.csv', column_time='Date', time_format='%d/%m/%Y',
       content={'precipitation': 'precip(mm/day)', 'temperature': 'temp(C)',
                'pet': 'pet_sim(mm/day)'})

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
       variable='precipitation', correction_factor=0.75)

The default method is multiplicative (multiply the data by the factor). An
additive correction is also available, for example to apply a temperature bias
correction:

.. code-block:: python

   forcing.correct_station_data(
       variable='temperature', method='additive', correction_factor=0.5)


.. _spatialization:

Spatialization
"""""""""""""""

A single meteorological station records conditions at one point. Spatialization
distributes those measurements across all hydro units using an elevation-based
method. Specify the variable, the method, and the method's parameters:

.. code-block:: python

   forcing.spatialize_from_station_data(
       variable='temperature', method='additive_elevation_gradient',
       ref_elevation=1250, gradient=-0.6)

This example applies a −0.6 °C/100 m lapse rate relative to a reference
elevation of 1250 m. To make the gradient a calibrated parameter rather than
a fixed value, reference a ``ParameterSet`` entry by name:

.. code-block:: python

   forcing.spatialize_from_station_data(
       variable='temperature', method='additive_elevation_gradient',
       ref_elevation=1250, gradient='param:temp_gradients')

   parameters.add_data_parameter('temp_gradients', -0.6, min_value=-1, max_value=0)

Supported variables: ``temperature``, ``precipitation``, ``pet``.
Available methods and their parameters are described in
:ref:`the Python API <api_forcing>`.


Computing PET
""""""""""""""

When PET observations are not available, hydrobricks can compute them
internally from other meteorological variables using the
`pyet <https://pypi.org/project/pyet/>`_ package:

.. code-block:: python

   forcing.compute_pet(method='Hamon', use=['t', 'lat'], lat=47.3)

The ``method`` argument accepts any method listed in the
`pyet documentation <https://pypi.org/project/pyet/>`_. The ``use`` list names
the input variables in pyet's notation. A catchment latitude (``lat``) can be
given as a fixed value; if omitted, the latitude of each hydro unit is used.

All forcing operations — corrections, spatialization, and PET computation —
are queued when defined and executed together, in a fixed order, just before
the model run. This means you can define operations in any order in your script
without worrying about execution sequence.


Loading gridded NetCDF data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Key arguments:

* ``file_pattern``: filename glob pattern; ``*`` matches any sequence of characters
  (e.g., year numbers). Remove files outside the simulation period to speed up loading.
* ``data_crs``: EPSG code of the NetCDF coordinate reference system
  (look up codes at https://epsg.io/).
* ``var_name``: name of the variable inside the NetCDF file (e.g., ``'RhiresD'``).
* ``dim_x``, ``dim_y``, ``dim_time``: names of the x, y, and time dimensions.
* ``raster_hydro_units``: GeoTIFF raster of hydro unit IDs, used to assign
  grid cells to units.
