.. _models:

Models
======

The following model structures are currently implemented:

* :ref:`GSM-Socont <gsm-socont>`
* :ref:`GR4J <gr4j>`


Common options
--------------

All models accept the following options at instantiation:

* ``solver``: numerical solver to use; choices are ``heun_explicit`` (default),
  ``runge_kutta``, and ``euler_explicit``.
* ``record_all`` (default ``False``): when ``True``, all fluxes and state
  variables are recorded at every time step. This slows computation and
  produces large output files. Enable only for diagnostic analysis, not
  during calibration.
* ``land_cover_types``: list of land cover types (e.g., ``['ground', 'glacier']``).
  See :ref:`the section on the spatial structure <spatial-structure>`.
* ``land_cover_names``: list of land cover names. Each entry must correspond
  to a type in ``land_cover_types``. Names distinguish similar types, for
  example bare-ice and debris-covered glaciers.
  See :ref:`the section on the spatial structure <spatial-structure>`.

Example:

.. code-block:: python

    socont = models.Socont(solver="heun_explicit", record_all=False)


.. _gsm-socont:

GSM-Socont
----------

GSM-Socont is a conceptual glacio-hydrological model described in :cite:t:`Schaefli2005`.

* **Spatial structure**: semi-lumped (elevation bands)
* **Time step**: daily


Specific options
^^^^^^^^^^^^^^^^^

* ``soil_storage_nb``: ``1`` or ``2``. Number of soil reservoirs; the second
  represents the baseflow component.
* ``surface_runoff``: ``socont_runoff`` (the original non-linear quick reservoir)
  or ``linear_storage`` (a classic linear storage).
* ``snow_melt_process``: melt model to use; see :ref:`melt models <melt-models>`.
  Default: ``"melt:degree_day"``.


Parameters
^^^^^^^^^^^


**Precipitation (snow/rain transition)**

* ``prec_t_start`` (optional)

  - Unit: °C
  - Default: 0 °C
  - Range: [-2, 2] °C
  - Description: Temperature below which precipitation is 100% snow. The rain/snow transition is linear between ``prec_t_start`` and ``prec_t_end``.
  - Full name: ``snow_rain_transition:transition_start``

* ``prec_t_end`` (optional)

  - Unit: °C
  - Default: 2 °C
  - Range: [0, 4] °C
  - Description: Temperature above which precipitation is 100% liquid.
  - Full name: ``snow_rain_transition:transition_end``


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
         The rain/snow transition is linear between ``prec_t_start`` and ``prec_t_end``.
       | Optional parameter.
       | Full name: ``snow_rain_transition:transition_start``
   * - ...
     - ``prec_t_end``
     - | 2
       | [0, 4]
     - °C
     - | Temperature above which precipitation is 100% liquid.
       | Optional parameter.
       | Full name: ``snow_rain_transition:transition_end``
   * - Snow (``melt:degree_day``)
     - ``a_snow``
     - | --
       | [1, 12]
     - mm/d/°C
     - | Degree-day snow melt factor. :math:`a_\mathrm{snow}` in :cite:t:`Schaefli2005`.
       | Full name: ``snowpack:degree_day_factor``
   * - ...
     - ``melt_t_snow``
     - | 0
       | [0, 5]
     - °C
     - | Temperature above which snow starts to melt.
       | Optional parameter.
       | Full name: ``snowpack:melting_temperature``
   * - Glacier (``melt:degree_day``)
     - ``a_ice`` (single type), ``a_ice_<name>``, ``a_ice_<i>``
     - | --
       | [5, 20]
     - mm/d/°C
     - | ``<name>`` is the land cover name (e.g., ``glacier_debris``);
         ``<i>`` is the index of similar land covers.
       | Examples: ``a_ice_glacier_debris``, ``a_ice_1``.
       | Degree-day ice melt factor. :math:`a_\mathrm{ice}` in :cite:t:`Schaefli2005`.
       | Full name: ``<name>:degree_day_factor``
   * - ...
     - ``melt_t_ice``
     - | 0
       | [0, 5]
     - °C
     - | Temperature above which ice starts to melt.
       | Optional parameter.
       | Full name: ``<name>:melting_temperature``
   * - Glacier area lumped reservoir
     - ``k_snow``
     - | --
       | [0.05, 0.25]
     - 1/d
     - | Response factor for the lumped reservoir receiving rain and snowmelt
         water from the glacier area. Similar to :math:`k_\mathrm{snow}` in
         :cite:t:`Schaefli2005`, but in different units.
       | Full name: ``glacier_area_rain_snowmelt_storage:response_factor``
   * - ...
     - ``k_ice``
     - | --
       | [0.05, 1]
     - 1/d
     - | Response factor for the lumped reservoir receiving ice melt water.
         Similar to :math:`k_\mathrm{ice}` in :cite:t:`Schaefli2005`, but in different units.
       | Full name: ``glacier_area_icemelt_storage:response_factor``
   * - Quick runoff (non-linear version)
     - ``beta``
     - | --
       | [100, 30000]
     - m^(4/3)/s
     - | Runoff coefficient (to calibrate).
       | Full name: ``surface_runoff:runoff_coefficient``
   * - ...
     - ``J``
     - | --
       | [0, 90]
     - °
     - | Mean slope of the catchment. Should be based on terrain data.
       | Full name: ``surface_runoff:slope``
   * - Quick runoff (linear version)
     - ``k_quick``
     - | --
       | [0.05, 1]
     - 1/d
     - | Response factor for the quick reservoir.
       | Full name: ``surface_runoff:response_factor``
   * - Slow reservoir
     - ``A``
     - | --
       | [10, 3000]
     - mm
     - | Maximum storage capacity of the slow reservoir.
       | Full name: ``slow_reservoir:capacity``
   * - ...
     - ``k_slow``, ``k_slow_1``
     - | --
       | [0.001, 1]
     - 1/d
     - | Response factor for the slow reservoir. Same as :math:`k` in :cite:t:`Schaefli2005`,
         but in different units.
       | Full name: ``slow_reservoir:response_factor``
   * - Baseflow (optional)
     - ``percol``
     - | --
       | [0, 10]
     - mm/d
     - | Percolation rate from the first slow reservoir to the baseflow reservoir.
       | Full name: ``slow_reservoir:percolation_rate``
   * - ...
     - ``k_slow_2``
     - | --
       | [0.001, 1]
     - 1/d
     - | Response factor for the baseflow reservoir.
       | Full name: ``slow_reservoir_2:response_factor``


When ``snow_melt_process="melt:degree_day_aspect"``, replace ``a_snow`` and
``a_ice`` with aspect-specific factors:

.. list-table:: Additional parameters for ``melt:degree_day_aspect``
   :widths: 10 10 5 5 70
   :header-rows: 1

   * - Component
     - Name
     - Def. value, range
     - Unit
     - Comments
   * - Snow / Glacier
     - ``<component>:degree_day_factor_n``
     - | --
       | [0, 20]
     - mm/d/°C
     - | Degree-day factor for north-facing slopes.
       | Full name: ``snowpack:degree_day_factor_n`` / ``<name>:degree_day_factor_n``
   * - ...
     - ``<component>:degree_day_factor_s``
     - | --
       | [2, 20]
     - mm/d/°C
     - | Degree-day factor for south-facing slopes.
   * - ...
     - ``<component>:degree_day_factor_ew``
     - | --
       | [2, 20]
     - mm/d/°C
     - | Degree-day factor for east/west-facing slopes.
   * - ...
     - ``<component>:melting_temperature``
     - | 0
       | [0, 5]
     - °C
     - | Optional. Same meaning as ``melt_t_snow`` / ``melt_t_ice``.

When ``snow_melt_process="melt:temperature_index"``, replace ``a_snow`` and
``a_ice`` with:

.. list-table:: Additional parameters for ``melt:temperature_index``
   :widths: 10 10 5 5 70
   :header-rows: 1

   * - Component
     - Name
     - Def. value, range
     - Unit
     - Comments
   * - Snow / Glacier
     - ``<component>:melt_factor``
     - | --
       | [0, 12]
     - mm/d/°C
     - | Base melt factor :math:`m` (independent of radiation).
       | Full name: ``snowpack:melt_factor`` / ``<name>:melt_factor``
   * - ...
     - ``<component>:radiation_coefficient``
     - | --
       | [0, 1]
     - m² W⁻¹ mm d⁻¹ °C⁻¹
     - | Radiation scaling coefficient :math:`r_j` for snow or ice.
       | Full name: ``snowpack:radiation_coefficient`` / ``<name>:radiation_coefficient``
   * - ...
     - ``<component>:melting_temperature``
     - | 0
       | [0, 5]
     - °C
     - | Optional. Melt temperature threshold.

See :ref:`melt models <melt-models>` for the governing equations of each option.


Pre-defined parameter constraints:

.. list-table:: Pre-defined parameter constraints for GSM-Socont
   :widths: 30 70
   :header-rows: 1

   * - Component
     - Constraints
   * - Glacier
     - ``a_snow < a_ice``
   * - Slow reservoir
     - | ``k_slow_1 < k_quick``
       | ``k_slow_2 < k_quick``
       | ``k_slow_2 < k_slow_1``


.. _gr4j:

GR4J
----

GR4J (Génie Rural à 4 paramètres Journalier) is a parsimonious daily
rainfall-runoff model described in :cite:t:`Perrin2003`. It is well suited for
non-glacierized or weakly glacierized catchments. Snow can optionally be
accounted for using either the CemaNeige model or a simple degree-day
approach.

* **Spatial structure**: lumped
* **Time step**: daily


Specific options
^^^^^^^^^^^^^^^^^

* ``snow_melt_process``: snow model to use. Options:

  * ``None`` (default): no snow accounting.
  * ``"melt:cemaneige"``: CemaNeige thermal-state model (recommended for
    catchments with significant seasonal snow). See :ref:`processes page <processes>`.
  * ``"melt:degree_day"``: simple degree-day model.

* ``snow_redistribution``: optional snow redistribution process
  (e.g., ``'transport:snow_slide'``).
  See the :ref:`snow redistribution section <snow-redistribution>`.


Parameters
^^^^^^^^^^^

.. list-table:: Core parameters of the GR4J model
   :widths: 10 10 5 5 70
   :header-rows: 1

   * - Component
     - Name
     - Def. value, range
     - Unit
     - Comments
   * - Production store
     - ``X1``
     - | 350
       | [100, 1200]
     - mm
     - | Maximum capacity of the production store.
       | Full name: ``production_store:capacity``
   * - Groundwater exchange
     - ``X2``
     - | 0
       | [-10, 5]
     - mm/d
     - | Groundwater exchange coefficient. Negative values indicate a net loss
         (deep percolation); positive values indicate recharge from outside the
         catchment.
       | Full name: ``uh_input:exchange_factor``
   * - Routing store
     - ``X3``
     - | 90
       | [1, 500]
     - mm
     - | Maximum capacity of the routing store.
       | Full name: ``uh_input:routing_capacity``
   * - Unit hydrograph
     - ``X4``
     - | 1.7
       | [0.5, 4]
     - d
     - | Time base of the unit hydrograph. Must be > 0.5 d.
       | Full name: ``uh_input:uh_base_time``

When ``snow_melt_process='melt:cemaneige'``, the following snow parameters are
added:

.. list-table:: Additional CemaNeige snow parameters
   :widths: 10 10 5 5 70
   :header-rows: 1

   * - Component
     - Name
     - Def. value, range
     - Unit
     - Comments
   * - Snowpack
     - ``Kf``
     - | --
       | [1, 10]
     - mm/d/°C
     - | Degree-day melt factor.
       | Full name: ``ground_snowpack:degree_day_factor``
   * - ...
     - ``CTG``
     - | --
       | [0, 1]
     - --
     - | Cold content weighting factor. Controls how quickly the thermal state
         of the snowpack tracks air temperature. Values close to 1 give longer
         memory.
       | Full name: ``ground_snowpack:cold_content_factor``
   * - ...
     - ``Tmelt``
     - | 0
       | [0, 2]
     - °C
     - | Melt temperature threshold.
       | Optional parameter.
       | Full name: ``ground_snowpack:melting_temperature``
   * - ...
     - ``Cn``
     - | --
       | [50, 1000]
     - mm
     - | Mean annual solid precipitation. Used to scale the melt factor at low
         snow accumulation.
       | Full name: ``ground_snowpack:mean_annual_snow``

When ``snow_melt_process='melt:degree_day'``, only ``a_snow`` (alias ``Kf``)
and ``Tmelt`` are added.


Usage examples
^^^^^^^^^^^^^^^

Minimal run without snow:

.. code-block:: python

   import hydrobricks as hb
   import hydrobricks.models as models

   gr4j = models.GR4J()

   parameters = gr4j.generate_parameters()
   parameters.set_values({'X1': 350, 'X2': 0, 'X3': 90, 'X4': 1.7})

   hydro_units = hb.HydroUnits()
   hydro_units.load_from_csv('path/to/hydro_units.csv',
                              column_elevation='elevation', column_area='area')

   forcing = hb.Forcing(hydro_units)
   forcing.load_station_data_from_csv(
       'path/to/meteo.csv', column_time='Date', time_format='%d/%m/%Y',
       content={'precipitation': 'precip(mm/day)', 'pet': 'pet(mm/day)'})
   forcing.spatialize_from_station_data(variable='precipitation',
                                        ref_elevation=1250, gradient=0.05)
   forcing.spatialize_from_station_data(variable='pet')

   gr4j.setup(spatial_structure=hydro_units, output_path='path/to/outputs',
              start_date='1981-01-01', end_date='2020-12-31')
   gr4j.run(parameters=parameters, forcing=forcing)

With CemaNeige snow:

.. code-block:: python

   gr4j = models.GR4J(snow_melt_process='melt:cemaneige')

   parameters = gr4j.generate_parameters()
   parameters.set_values({
       'X1': 350, 'X2': 0, 'X3': 90, 'X4': 1.7,
       'Kf': 4, 'CTG': 0.5, 'Cn': 300,
   })

   forcing = hb.Forcing(hydro_units)
   forcing.load_station_data_from_csv(
       'path/to/meteo.csv', column_time='Date', time_format='%d/%m/%Y',
       content={'precipitation': 'precip(mm/day)', 'temperature': 'temp(C)'})
   # temperature_min and temperature_max are only required for hydro units < 1500 m
   forcing.spatialize_from_station_data(variable='temperature',
                                        method='additive_elevation_gradient',
                                        ref_elevation=1250, gradient=-0.6)
   forcing.spatialize_from_station_data(variable='precipitation',
                                        method='multiplicative_elevation_gradient',
                                        ref_elevation=1250, gradient=0.05)
   forcing.compute_pet(method='Hamon', use=['t', 'lat'], lat=47.3)

