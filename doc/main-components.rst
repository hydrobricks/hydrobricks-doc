.. _main-components:

Main components
===============

Model structure
---------------

.. code-block:: python

   socont = models.Socont(soil_storage_nb=2)


.. _spatial-structure:

Spatial structure
-----------------

The catchment is discretized into sub units named hydro units.
These hydro units can represent HRUs, pixels, elevation bands, etc.
Their properties are loaded from csv files containing at minimum data on each unit area
and elevation. Loading such a file can be done as follows:

.. code-block:: python
   :caption: Example of the creation of hydro units with a signe land cover.

   hydro_units = hb.HydroUnits()
   hydro_units.load_from_csv(
      'path/to/file.csv', area_unit='m2', column_elevation='elevation',
      column_area='area')

The default land cover is named ``ground`` and it has no specific behaviour.
When there is more than one land cover, these can be specified.
Each hydro unit is then assigned a fraction of the provided land covers
For example, for a catchment with a pure ice glacier and a debris-covered glacier, one
then needs to provide the area for each land cover type and for each hydro unit:

.. code-block:: python
   :caption: Example of the creation of hydro units with multiple land covers.

   land_cover_names = ['ground', 'glacier_ice', 'glacier_debris']
   land_cover_types = ['ground', 'glacier', 'glacier']

   hydro_units = hb.HydroUnits(land_cover_types, land_cover_names)
   hydro_units.load_from_csv(
      'path/to/file.csv', area_unit='km', column_elevation='Elevation',
      columns_areas={'ground': 'Area Non Glacier',
                     'glacier_ice': 'Area Ice',
                     'glacier_debris': 'Area Debris'})

For a description of the options, refer to :ref:`the Python API <api_hydrounits>`.

.. code-block:: text
   :caption: Example of a csv file containing elevation bands data.

   Elevation, Area Non Glacier, Area Ice, Area Debris
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


Parameters
----------

The parameters are managed as parameter sets in an object that is an instance of the
ParameterSet class.
It means that there is a single variable containing all the parameters for a model.
Within it, different properties are defined for each parameter:

* **component**: the component to which it refers to (e.g., glacier, slow_reservoir)
* **name**: the detailed name of the parameter (e.g., degree_day_factor)
* **unit**: the parameter unit (e.g., mm/d/°C)
* **aliases**: aliases for the parameter name; this is the short version of the
  parameter name (e.g., a_snow)
* **value**: the value assigned to the parameter
* **min**: the minimum value the parameter can accept
* **max**: the maximum value the parameter can accept
* **default_value**: the parameter default value; only few parameters have default
  values, such as the melting temperature, and these are usually not necessary to
  calibrate
* **mandatory**: defines if the parameter value need to be provided by the user or if
  it can use a default value
* **prior**: prior distribution to use for the calibration. See :ref:`the calibration page <calibration>`

For a description of the options, refer to :ref:`the Python API <api_parameterset>`.

Creating a parameter set
^^^^^^^^^^^^^^^^^^^^^^^^

When using a pre-build model structure, the parameters for this structure can be
generated using the ``model.generate_parameters()`` function.
For example, the following code creates a definition of the Socont model structure and
generates the parameter set for the given structure, accounting for the options, such
as the number of soil storages. Within this parameter set, the basic attributes are
defined, such as the name, aliases, units, min/max values, etc.

.. code-block:: python

   socont = models.Socont(soil_storage_nb=2)
   parameters = socont.generate_parameters()


Assigning the parameter values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To set parameter values, the ``set_values()`` function of the parameter set can be used
with a dictionary as argument. The dictionary can use the full parameter names
(e.g. ``snowpack:degree_day_factor`` with no space), or one of the aliases
(e.g., ``a_snow``):

.. code-block:: python

   parameters.set_values({'A': 100, 'k_slow': 0.01, 'a_snow': 5})

For a description of the options, refer to `the Python API </en/latest/api/hydrobricks.html#hydrobricks.ParameterSet.set_values>`_.

Parameter constraints
^^^^^^^^^^^^^^^^^^^^^

Some constraints can be added between parameters. Some of these are built-in when the
parameter set is generated and are described in the respective model description.
For example, in GSM-Socont, the degree day for the snow must be inferior to the one for
the ice (``a_snow < a_ice``).

Constraints between parameters can be added by the user as follows:

.. code-block:: python

   parameters.define_constraint('k_slow_2', '<', 'k_slow_1')

The supported operators are: ``>`` (or ``gt``), ``>=`` (or ``ge``), ``<`` (or ``lt``),
``<=`` (or ``le``).

On the contrary, pre-definied constraints can be removed:

.. code-block:: python

   parameters.remove_constraint('a_snow', '<', 'a_ice')


Parameter ranges
^^^^^^^^^^^^^^^^

The parameters are usually generated with a pre-defined range.
This range is used to ensure that a provided value falls within the authorized range
and to define the boundaries for the calibration algorithm.
The pre-defined ranges can be changed as follows:

.. code-block:: python

   parameters.change_range('a_snow', 2, 5)


Adding data-related parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Data-related parameters target for example the spatialisation of the forcing data.
As these are not model-dependent, but data-dependent, they are not pre-defined by
the model and need to be added ba the user:

.. code-block:: python

   parameters.add_data_parameter('precip_corr_factor', 1, min_value=0.7, max_value=1.3)
   parameters.add_data_parameter('precip_gradient', 0.05, min_value=0, max_value=0.2)
   parameters.add_data_parameter('temp_gradients', -0.6, min_value=-1, max_value=0)

For the meaning of these parameters and the spatialisation procedures implemented in
hydrobricks, refer to the section on :ref:`forcing data<Forcing data>`.

It is also possible, for certain parameters, to define monthly values and ranges:

.. code-block:: python

   parameters.add_data_parameter(
       'temp_gradients',
       [-0.6, -0.6, -0.6, -0.6, -0.7, -0.7, -0.8, -0.8, -0.8, -0.7, -0.7, -0.6],
       min_value=[-0.8, -0.8, -0.8, -0.8, -0.8, -0.8, -0.8, -0.8, -0.8, -0.8, -0.8, -0.8],
       max_value=[-0.3, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3, -0.3])

Forcing data
------------

