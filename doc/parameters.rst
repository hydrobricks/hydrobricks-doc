.. _parameters:

Parameters and calibration
==========================

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
* **transform**: an optional monotonic mapping between the parameter's real value
  and a transformed value used during calibration —
  see :ref:`Parameter transforms <parameter-transforms>`


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


.. _parameter-transforms:

Parameter transforms
---------------------

A parameter can carry a **transform**: a monotonic mapping between its *real*
value (the one passed to the C++ engine and stored in the parameter set) and a
*transformed* value used during calibration. Searching in transformed space makes
the optimisation better behaved — a storage capacity that spans orders of
magnitude is calibrated in log space, while an exchange coefficient that may be
negative or positive is calibrated through an inverse hyperbolic sine.

Pre-built models attach the appropriate transforms automatically. GR4J and GR6J
follow the airGR ``TransfoParam`` conventions:

.. list-table::
   :header-rows: 1
   :widths: 22 26 52

   * - Parameter
     - Transform (real → transformed)
     - Rationale
   * - X1 (production store capacity)
     - ``log``
     - spans orders of magnitude, > 0
   * - X2 (groundwater exchange)
     - ``asinh``
     - signed (import or export)
   * - X3 (routing store capacity)
     - ``log``
     - spans orders of magnitude, > 0
   * - X4 (unit-hydrograph base time)
     - ``log(X4 - 0.5)``
     - log-like, enforces X4 > 0.5
   * - X5 (exchange threshold, GR6J)
     - ``asinh``
     - signed
   * - X6 (exponential store, GR6J)
     - ``log``
     - > 0

How it works:

* The model always keeps and runs the **real** value; the transform is used only
  to map to and from the optimiser's search space.
* ``get_for_spotpy()`` maps each parameter's real ``min``/``max`` through its
  transform, so the optimiser searches the transformed bounds.
* During calibration, the sampled (transformed) values are mapped back to real
  values automatically before each model run.
* A ``log`` transform is undefined at zero, so where the default lower bound would
  fall there it is raised slightly for calibration (e.g. GR4J/GR6J X1 to 1 mm and
  X4 to 0.51 d).

Inspect or set transformed values directly:

.. code-block:: python

   import math

   parameters.set_values({'X1': 350})                 # real value
   parameters.get_transformed('X1')                   # -> log(350)

   # Set a value given in transformed space (mapped back to the real value):
   parameters.set_values({'X1': math.log(500)}, transformed=True)
   parameters.get('X1')                               # -> 500.0

Attach a custom transform to any parameter with a ``(real → transformed,
transformed → real)`` pair of monotonic functions:

.. code-block:: python

   parameters.set_transform('k_slow', math.log, math.exp)

Transforms are not supported on list-valued parameters.


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
      max_value=[-0.3]*12
   )


.. _calibration:

Calibration using SPOTPY
--------------------------

Hydrobricks uses the `SPOTPY package <https://spotpy.readthedocs.io/en/latest/>`_ for
parameter calibration and sensitivity analysis. SPOTPY provides a unified interface to
many optimization and sampling algorithms and records every model evaluation so results
can be analysed after sampling.

By default, all parameters generated by ``generate_parameters()`` are eligible for
calibration. To restrict calibration to a specific subset, list the aliases or full
names of the parameters that should vary:

.. code-block:: python

   parameters.allow_changing = ['a_snow', 'k_quick', 'A', 'k_slow_1', 'percol',
                                'k_slow_2', 'precip_corr_factor']

Create a SPOTPY setup object that bundles the model, parameters, forcing, observations,
and objective function. The ``warmup`` argument (in days) excludes the opening period of
each run from the objective function to avoid spin-up artefacts — see the
:ref:`warmup section <running>` for background:

.. code-block:: python

   spot_setup = hb.SpotpySetup(
      socont, 
      parameters, 
      forcing, 
      obs, 
      warmup=365,
      obj_func='nse'
   )

.. note::

   SPOTPY always **maximizes** the objective function. For metrics that
   should be minimized (e.g., MSE, RMSE), set ``invert_obj_func=True`` to
   negate the value:

   .. code-block:: python

      spot_setup = hb.SpotpySetup(
         socont, 
         parameters, 
         forcing, 
         obs, 
         warmup=365,
         obj_func='mse', 
         invert_obj_func=True
      )

   Metrics such as NSE and KGE are naturally maximized and do not need
   inversion.

With the setup object ready, choose an algorithm based on the goal:

**Optimization** (finding the best parameter set): SCE-UA is well suited to
multi-parameter hydrological calibration problems:

.. code-block:: python

   sampler = spotpy.algorithms.sceua(
      spot_setup, 
      dbname='socont_SCEUA', 
      dbformat='csv'
   )
   sampler.sample(10000)

**Sensitivity analysis** (understanding which parameters matter): Monte Carlo sampling
covers the full parameter space without steering towards any optimum:

.. code-block:: python

   sampler = spotpy.algorithms.mc(
      spot_setup, 
      dbname='socont_MC', 
      dbformat='csv',
      save_sim=False
   )
   sampler.sample(10000)

After sampling, retrieve the results for analysis. SPOTPY provides built-in tools for
visualizing parameter interactions and isolating high-performing samples:

.. code-block:: python

   results = sampler.getdata()

   # Plot parameter interactions across all samples
   spotpy.analyser.plot_parameterInteraction(results)
   plt.tight_layout()
   plt.show()

   # Restrict to the top-performing 10 % (posterior distribution)
   posterior = spotpy.analyser.get_posterior(results, percentage=10)
   spotpy.analyser.plot_parameterInteraction(posterior)
   plt.tight_layout()
   plt.show()


Prior distributions
^^^^^^^^^^^^^^^^^^^

The default prior distribution is uniform over the parameter range defined by ``min``
and ``max``. A non-uniform prior can be assigned when prior knowledge — from the
literature or previous calibrations — justifies concentrating the search:

.. code-block:: python

   parameters.set_prior('a_snow', spotpy.parameter.Normal(mean=4, stddev=2))

Prior distributions provided by SPOTPY: ``Uniform``, ``Normal``, ``logNormal``,
``Chisquare``, ``Exponential``, ``Gamma``, ``Wald``, ``Weibull``.
