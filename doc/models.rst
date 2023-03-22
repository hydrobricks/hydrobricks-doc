.. _models:

Models
======

The only model structure implemented so far is :ref:`GSM-SOCONT`

GSM-SOCONT
----------

GSM-SOCONT is a conceptual glacio-hydrological model described in Schaefli2005_.

Some basic properties are given in the following table.

.. list-table:: Properties of the GSM-SOCONT model
   :widths: 50 50
   :header-rows: 0

   * - Spatial structure
     - semi-lumped (elevation bands)
   * - Time step
     - daily

It has the following parameters.

.. list-table:: Parameters of the GSM-SOCONT model
   :widths: 15 15 10 5 5 10 40
   :header-rows: 1

   * - Component
     - Full name
     - Aliases
     - Def. value
     - Range
     - Unit
     - Comments
   * - Precipitation (snow/rain transition)
     - snow_rain_transition: transition_start
     - --
     - 0
     - [-2, 2]
     - °C
     - Temperature below which precipitation is 100% snow.
       The snow/rain transition is linear between transition_start and transition_end
   * - ...
     - snow_rain_transition: transition_end
     - --
     - 2
     - [0, 4]
     - °C
     - Temperature above which precipitation is 100% liquid.
   * - Snow
     - snowpack: degree_day_factor
     - a_snow
     - --
     - [1, 12]
     - mm/d/°C
     - Degree day snow melting factor. a\ :sub:`snow` in Schaefli2005_
   * - ...
     - snowpack: melting_temperature
     - --
     - 0
     - [0, 5]
     - °C
     - Temperature above which the snow starts to melt.
   * - Glacier
     - <name>: degree_day_factor
     - a_ice (single type), a_ice_<name>, a_ice_<i>
     - --
     - [5, 20]
     - mm/d/°C
     - Degree day ice melting factor. a\ :sub:`ice` in Schaefli2005_
   * - ...
     - <name>: melting_temperature
     - --
     - 0
     - [0, 5]
     - °C
     - Temperature above which the ice starts to melt.
   * - Glacier area lumped reservoir
     - glacier-area-rain-snowmelt-storage: response_factor
     - k_snow
     - --
     - [0.05, 0.25]
     - 1/d
     - Response factor for the glacier area lumped reservoir receiving rain and
       snowmelt water. Similar to k\ :sub:`snow` in Schaefli2005_, but different units.
   * - ...
     - glacier-area-icemelt-storage: response_factor
     - k_ice
     - --
     - [0.05, 1]
     - 1/d
     - Response factor for the glacier area lumped reservoir receiving ice melt water.
       Similar to k\ :sub:`ice` in Schaefli2005_, but different units.
   * - Quick runoff (non-linear version)
     - surface-runoff: runoff_coefficient
     - beta
     - --
     - [100, 30000]
     - m^(4/3)/s
     - Parameter to calibrate.
   * - ...
     - surface-runoff: slope
     - J
     - --
     - [0, 90]
     - °
     - Mean slope of the catchment. Should be based on data.
   * - Quick runoff (linear version)
     - surface-runoff: response_factor
     - k_quick
     - --
     - [0.05, 1]
     - 1/d
     - Response factor for the quick reservoir.
   * - Slow reservoir
     - slow-reservoir: capacity
     - A
     - --
     - [10, 3000]
     - mm
     - Maximum storage capacity of the reservoir.
   * - ...
     - slow-reservoir: response_factor
     - k_slow, k_slow_1
     - --
     - [0.001, 1]
     - 1/d
     - Response factor for the slow reservoir. Same as k in Schaefli2005_, but different units.
   * - Baseflow (optional)
     - slow-reservoir: percolation_rate
     - percol
     - --
     - [0, 10]
     - mm/d
     - Percolation rate from the first slow reservoir to the baseflow reservoir
   * - ...
     - slow-reservoir-2: response_factor
     - k_slow_2
     - --
     - [0.001, 1]
     - 1/d
     - Response factor for the baseflow reservoir.



.. list-table:: Pre-defined parameter constraints for the GSM-SOCONT model
   :widths: 20 20 60
   :header-rows: 1

   * - Component
     - Parameters
     - Constraints
   * -
     -
     -


.. [Schaefli2005] Schaefli, B., Hingray, B., Niggli, M., & Musy, A. (2005). A conceptual glacio-hydrological model for high mountainous catchments. Hydrology and Earth System Sciences Discussions, 9(1), 95–109. https://doi.org/10.5194/hessd-2-73-2005