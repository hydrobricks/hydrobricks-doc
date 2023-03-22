.. _main-components:

Main components
===============

Model structure
---------------


Spatial structure
-----------------


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
* **prior**: prior distribution to use for the calibration. See :ref:`_calibration`

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


Forcing data
------------
