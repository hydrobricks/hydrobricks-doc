.. _models:

Models
======

The only model structure implemented so far is :ref:`GSM-Socont`.


Common options
--------------

All models have the following options that can be provided at model creation:

* ``solver``: choice of the solver to use; the options are: ``heun_explicit`` (default),
  ``runge_kutta``, and ``euler_explicit``.
* ``record_all`` (default False): when True, the model will record all fluxes and state
  values for each time step. This slows down the computations and create large output
  files. Therefore, it should not be enabled during the calibration phase, but only when
  one needs to analyse the behaviour of the model in details. When False, the model
  will output the catchment discharge and some selected timeseries.
* ``land_cover_types``: a list of the land cover types to use (e.g., ``glacier``).
  See :ref:`the section on the spatial structure <spatial-structure>`.
* ``land_cover_names``: a list of the land cover names to use.
  Each element must match the land cover types explained above.
  The names are used in the model to distinguish similar land cover types, for example
  when using a bare-ice glacier and a debris-covered glacier.
  See :ref:`the section on the spatial structure <spatial-structure>`.

For example:

.. code-block:: python

    socont = models.Socont(solver="heun_explicit", record_all=False)


GSM-Socont
----------

GSM-Socont is a conceptual glacio-hydrological model described in Schaefli2005_.

Some basic properties are given in the following table.

.. list-table:: Properties of the GSM-Socont model
   :widths: 50 50
   :header-rows: 0
   :stub-columns: 1

   * - Spatial structure
     - semi-lumped (elevation bands)
   * - Time step
     - daily


Specific options
^^^^^^^^^^^^^^^^

The implemented GSM-Socont version comes with some options:

* ``soil_storage_nb``: 1 or 2. This is the number of soil reservoirs to consider
  (the second one represents the baseflow).
* ``surface_runoff``: ``socont_runoff`` (the original non-linear quick reservoir) or
  ``linear_storage`` (a classic linear storage).

Parameters
^^^^^^^^^^

It has the parameters listed below.

.. list-table:: Parameters of the GSM-Socont model
   :widths: 10 10 5 5 70
   :header-rows: 1

   * - Component
     - Name
     - Def. value, range
     - Unit
     - Comments
   * - Precipitation (snow/rain transition)
     - ``prec_t_start``
     - | 0
       | [-2, 2]
     - °C
     - | Temperature below which precipitation is 100% snow.
         The snow/rain transition is linear between transition_start and transition_end
       | Optional parameter.
       | Full name: snow_rain_transition: transition_start
   * - ...
     - ``prec_t_end``
     - | 2
       | [0, 4]
     - °C
     - | Temperature above which precipitation is 100% liquid.
       | Optional parameter.
       | Full name: snow_rain_transition: transition_end
   * - Snow
     - ``a_snow``
     - | --
       | [1, 12]
     - mm/d/°C
     - | Degree day snow melting factor. a\ :sub:`snow` in Schaefli2005_
       | Full name: snowpack: degree_day_factor
   * - ...
     - ``melt_t_snow``
     - | 0
       | [0, 5]
     - °C
     - | Temperature above which the snow starts to melt.
       | Optional parameter.
       | Full name: snowpack: melting_temperature
   * - Glacier
     - ``a_ice`` (single type), ``a_ice_<name>``, ``a_ice_<i>``
     - | --
       | [5, 20]
     - mm/d/°C
     - | With <name> being the provided name of the land cover (e.g. glacier_debris)
       | Degree day ice melting factor. a\ :sub:`ice` in Schaefli2005_
       | Full name: <name>: degree_day_factor
   * - ...
     - ``melt_t_ice``
     - | 0
       | [0, 5]
     - °C
     - | With <name> being the provided name of the land cover (e.g. glacier_debris)
       | Temperature above which the ice starts to melt.
       | Optional parameter.
       | Full name: <name>: melting_temperature
   * - Glacier area lumped reservoir
     - ``k_snow``
     - | --
       | [0.05, 0.25]
     - 1/d
     - | Response factor for the glacier area lumped reservoir receiving rain and
         snowmelt water. Similar to k\ :sub:`snow` in Schaefli2005_, but different units.
       | Full name: glacier_area_rain_snowmelt_storage: response_factor
   * - ...
     - ``k_ice``
     - | --
       | [0.05, 1]
     - 1/d
     - | Response factor for the glacier area lumped reservoir receiving ice melt water.
         Similar to k\ :sub:`ice` in Schaefli2005_, but different units.
       | Full name: glacier_area_icemelt_storage: response_factor
   * - Quick runoff (non-linear version)
     - ``beta``
     - | --
       | [100, 30000]
     - m^(4/3)/s
     - | Parameter to calibrate.
       | Full name: surface_runoff: runoff_coefficient
   * - ...
     - ``J``
     - | --
       | [0, 90]
     - °
     - | Mean slope of the catchment. Should be based on data.
       | Full name: surface_runoff: slope
   * - Quick runoff (linear version)
     - ``k_quick``
     - | --
       | [0.05, 1]
     - 1/d
     - | Response factor for the quick reservoir.
       | Full name: surface_runoff: response_factor
   * - Slow reservoir
     - ``A``
     - | --
       | [10, 3000]
     - mm
     - | Maximum storage capacity of the reservoir.
       | Full name: slow_reservoir: capacity
   * - ...
     - ``k_slow``, ``k_slow_1``
     - | --
       | [0.001, 1]
     - 1/d
     - | Response factor for the slow reservoir. Same as k in Schaefli2005_,
         but different units.
       | Full name: slow_reservoir: response_factor
   * - Baseflow (optional)
     - ``percol``
     - | --
       | [0, 10]
     - mm/d
     - | Percolation rate from the first slow reservoir to the baseflow reservoir
       | Full name: slow_reservoir: percolation_rate
   * - ...
     - ``k_slow_2``
     - | --
       | [0.001, 1]
     - 1/d
     - | Response factor for the baseflow reservoir.
       | Full name: slow_reservoir_2: response_factor


The pre-defined constraints on the parameters are defined below.

.. list-table:: Pre-defined parameter constraints for the GSM-Socont model
   :widths: 30 70
   :header-rows: 1

   * - Component
     - Constraints
   * - Glacier
     - a_snow < a_ice
   * - Slow reservoir
     - | k_slow_1 < k_quick
       | k_slow_2 < k_quick
       | k_slow_2 < k_slow_1


References
----------

.. [Schaefli2005] Schaefli, B., Hingray, B., Niggli, M., & Musy, A. (2005). A conceptual glacio-hydrological model for high mountainous catchments. Hydrology and Earth System Sciences Discussions, 9(1), 95–109. https://doi.org/10.5194/hessd-2-73-2005