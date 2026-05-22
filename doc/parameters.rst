.. _parameters:

Parameters
==========

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
-------------------------

For pre-built models, call ``generate_parameters()`` on the model instance.
This produces a ``ParameterSet`` populated with all parameters appropriate for
the chosen model configuration, including their names, aliases, units, and
default ranges:

.. code-block:: python

   socont = models.Socont(soil_storage_nb=2)
   parameters = socont.generate_parameters()


Assigning parameter values
---------------------------

Use ``set_values()`` with a dictionary. Keys can be either the full parameter
name (e.g., ``snowpack:degree_day_factor``) or any alias (e.g., ``a_snow``):

.. code-block:: python

   parameters.set_values({'A': 100, 'k_slow': 0.01, 'a_snow': 5})


Parameter constraints
----------------------

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
-----------------

Each parameter is generated with a default range. The calibration algorithm
samples within this range, and values outside it are rejected. To adjust the
range for a parameter:

.. code-block:: python

   parameters.change_range('a_snow', 2, 5)


Calibratable forcing parameters
---------------------------------

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
:ref:`Spatialization <spatialization>` section on the :ref:`forcing page <forcing-data>`.

For seasonally varying quantities such as temperature lapse rates, monthly
values and ranges can be specified:

.. code-block:: python

   parameters.add_data_parameter(
       'temp_gradients',
       [-0.6, -0.6, -0.6, -0.6, -0.7, -0.7, -0.8, -0.8, -0.8, -0.7, -0.7, -0.6],
       min_value=[-0.8]*12,
       max_value=[-0.3]*12)
