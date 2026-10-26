.. _models:

Models
======

The following model structures are currently implemented:

* :ref:`GSM-Socont <gsm-socont>`
* :ref:`GR4J <gr4j>`
* :ref:`GR6J <gr6j>`
* :ref:`HBV-96 <hbv96>`
* :ref:`PREVAH-UniBE <prevah-unibe>`

Beyond the pre-built structures, a model can be defined entirely through a file —
its stores, processes and fluxes declared in a YAML file — with
:ref:`custom structures <custom-structures>`.


Common options
--------------

All models accept the following options at instantiation:

* ``solver``: numerical solver to use; choices are ``exponential_euler``
  (default), ``heun_explicit``, ``runge_kutta``, ``euler_explicit``,
  ``analytic_linear``, ``implicit_euler``, and ``crank_nicolson``. See the
  :ref:`solvers page <solvers>` for their properties and how to choose.
* ``channel_routing`` (default ``"none"``): the channel routing between the subbasins
  of a :ref:`river network <subbasins>`; ``"lag"``, ``"muskingum"`` or
  ``"muskingum_cunge"`` enable the travel time along the reaches (see
  :ref:`channel routing <channel-routing>`). Irrelevant for a catchment without a
  declared network.
* ``route_local_runoff`` (default ``False``): when ``True``, a subbasin's own
  runoff travels through half of its reach instead of joining at its outlet with
  no delay (see :ref:`channel routing <channel-routing>`).
* ``record_all`` (default ``False``): when ``True``, all fluxes and state
  variables are recorded at every time step. This slows computation and
  produces large output files. Enable only for diagnostic analysis, not
  during calibration.
* ``land_cover_types``: list of land cover types (e.g., ``['open', 'glacier']``).
  See :ref:`the section on the spatial structure <spatial-structure>`.
* ``land_cover_names``: list of land cover names. Each entry must correspond
  to a type in ``land_cover_types``. Names distinguish similar types, for
  example bare-ice and debris-covered glaciers.
  See :ref:`the section on the spatial structure <spatial-structure>`.

Example:

.. code-block:: python

    socont = models.Socont(solver="exponential_euler", record_all=False)


Shared processes
----------------

.. _snow-melt-params:

Snow / Glacier melt
^^^^^^^^^^^^^^^^^^^

The melt model is selected via the ``snow_melt_process`` option. See
:ref:`melt models <melt-models>` for the governing equations of each option.

**Simple degree-day method** (``melt:degree_day``)

* ``<component>:degree_day_factor`` *(mm/d/°C, no default, [2, 20])*

  - Degree-day factor.
  - Full name: ``snowpack:degree_day_factor`` / ``<name>:degree_day_factor``.

* ``<component>:melting_temperature`` *(optional, °C, default: 0, [0, 5])*

  - Melt temperature threshold.
  - Full name: ``snowpack:melting_temperature`` / ``<name>:melting_temperature``.


**Aspect-based degree-day method** (``melt:degree_day_aspect``)

The melt model uses aspect-specific factors to account for the influence of slope 
orientation on melt rates. It includes the following parameters:

* ``<component>:degree_day_factor_n`` *(mm/d/°C, no default, [0, 20])*

  - Degree-day factor for north-facing slopes.
  - Full name: ``snowpack:degree_day_factor_n`` / ``<name>:degree_day_factor_n``.

* ``<component>:degree_day_factor_s`` *(mm/d/°C, no default, [2, 20])*

  - Degree-day factor for south-facing slopes.
  - Full name: ``snowpack:degree_day_factor_s`` / ``<name>:degree_day_factor_s``.

* ``<component>:degree_day_factor_ew`` *(mm/d/°C, no default, [2, 20])*

  - Degree-day factor for east/west-facing slopes.
  - Full name: ``snowpack:degree_day_factor_ew`` / ``<name>:degree_day_factor_ew``.

* ``<component>:melting_temperature`` *(optional, °C, default: 0, [0, 5])*

  - Melt temperature threshold.
  - Full name: ``snowpack:melting_temperature`` / ``<name>:melting_temperature``.


**Melt based on potential solar radiation** (``melt:temperature_index``)

This melt model is based on the temperature-index method of :cite:t:`Hock1999`, which 
accounts for the influence of solar radiation on melt rates. It requires potential 
solar radiation as a model input (which can be computed by HydroBricks), 
and includes the following parameters:

* ``<component>:melt_factor`` *(mm/d/°C, no default, [0, 12])*

  - Base melt factor :math:`m` (independent of radiation).
  - Full name: ``snowpack:melt_factor`` / ``<name>:melt_factor``.

* ``<component>:radiation_coefficient`` *(m² W⁻¹ mm d⁻¹ °C⁻¹, no default, [0, 1])*

  - Radiation scaling coefficient :math:`r_j` for snow or ice.
  - Full name: ``snowpack:radiation_coefficient`` / ``<name>:radiation_coefficient``.

* ``<component>:melting_temperature`` *(optional, °C, default: 0, [0, 5])*

  - Melt temperature threshold.
  - Full name: ``snowpack:melting_temperature`` / ``<name>:melting_temperature``.


**CemaNeige model** (``melt:cemaneige``)

The CemaNeige model is a thermal-state snow model described in :cite:t:`Valery2014`. 
It is exclusively for snow and includes the following parameters:

* ``Kf`` *(mm/d/°C, no default, [1, 10])*

  - Degree-day melt factor.
  - Full name: ``open_snowpack:degree_day_factor``.

* ``CTG`` *(dimensionless, no default, [0, 1])*

  - Cold content weighting factor. Controls how quickly the thermal state of the snowpack
    tracks air temperature. Values close to 1 give longer memory.
  - Full name: ``open_snowpack:cold_content_factor``.

* ``Tmelt`` *(optional, °C, default: 0, [0, 2])*

  - Melt temperature threshold.
  - Full name: ``open_snowpack:melting_temperature``.

* ``Cn`` *(mm, no default, [50, 1000])*

  - Mean annual solid precipitation. Used to scale the melt factor at low snow accumulation.
  - Full name: ``open_snowpack:mean_annual_snow``.


.. _snow-redistribution-params:

Snow redistribution
^^^^^^^^^^^^^^^^^^^

Snow redistribution simulates lateral transport of snow between hydro units, driven
by either the SnowSlide method (:cite:t:`Bernhardt2010`) or the conceptual model of
:cite:t:`Frey2015`. It is activated by setting ``snow_redistribution`` to one of
``"transport:snow_slide"``, ``"transport:snow_redistribution_frey"`` or
``"transport:snow_redistribution_frey_dynamic"``. The aliases below (e.g.
``snow_slide_coeff``) are the same for every model — see the
:ref:`process formulas and full parameter list <snow-redistribution-processes>`
on the :ref:`processes page <processes>`.


.. _glacier-modules:

Glacier modules
^^^^^^^^^^^^^^^

Models that support a ``glacier`` land cover handle the glacierized area through a
pluggable **glacier module**, selected with the ``glacier_module`` option. This lets
different glacier formulations be swapped in without changing the model.

* ``glacier_module`` (default ``"gsm"``): the glacier formulation, given either as a
  registry name or as a ``GlacierModule`` instance (for a custom formulation).

Currently available:

* ``"gsm"`` — the Glacier Sub-Model of GSM-Socont (:cite:t:`Schaefli2005`): the
  glacierized area routes its rain + snowmelt and its ice melt into two catchment-level
  linear reservoirs draining to the outlet (parameters :math:`k_\mathrm{snow}`,
  :math:`k_\mathrm{ice}`), bypassing the soil routine. Ice melt is suppressed while snow
  covers the ice, and the ice is treated as an infinite store by default
  (``glacier_infinite_storage``). This is the formulation used by both GSM-Socont and HBV.

* ``"prevah"`` — the glacier module of :ref:`PREVAH-UniBE <prevah-unibe>`
  (:cite:t:`Viviroli2007b`): the glacierized area is split at the equilibrium line into
  an **ice** cover (ablation zone) and a **firn** cover (accumulation zone), each melting
  only when snow-free. Three per-unit linear reservoirs drain the melt with increasing
  storage times: the rain and snowmelt on the glacier (:math:`k_\mathrm{snow}`), the ice
  melt (:math:`k_\mathrm{ice}`) and the firn melt (:math:`k_\mathrm{firn}`). The firn
  reservoir feeds the groundwater store rather than the outlet
  (``firn_to_groundwater=True``), as in PREVAH. Each reservoir drains through a
  translation element that delays its outflow by a fixed time
  (:ref:`routing:delay <routing-processes>`, aliases ``lag_snow``, ``lag_ice`` and
  ``lag_firn`` [d]), starting at PREVAH's translation times of 2 h, 1 h and none. The
  delays keep their meaning in hours at any time step: on an hourly step a whole
  number of hours is an exact shift, and on a daily step a delay of a few hours moves
  the matching share of each day's outflow onto the next day. The covers are prepared with
  :ref:`initialize_glacier_covers_split_by_elevation <glacier-cover-init>`; a cover whose
  name contains ``firn`` is treated as the accumulation zone.

When a glacier cover is present, the model builds a glacier-free **base** structure (used
by ice-free units) and a **with-glacier** variant (used by glacierized units), so ice-free
units carry no glacier bricks.

A custom formulation subclasses ``GlacierModule`` (in ``hydrobricks.modules.glacier``),
implementing ``add_bricks``, ``land_cover_keys`` and ``parameter_aliases``, and is either
registered under a name with the ``@GlacierModule.register("name")`` decorator or passed
directly as an instance:

.. code-block:: python

  import hydrobricks.models as models
  from hydrobricks.modules.glacier import GSM

  socont = models.Socont(
      glacier_module=GSM(),  # or glacier_module="gsm"
      land_cover_names=['open', 'glacier'],
      land_cover_types=['open', 'glacier'],
  )


.. _gsm-socont:

GSM-Socont
----------

GSM-Socont is a conceptual glacio-hydrological model described in :cite:t:`Schaefli2005`.

* **Spatial structure**: semi-lumped (elevation bands)
* **Time step**: daily


Specific options
^^^^^^^^^^^^^^^^^

* ``soil_storage_nb``: ``1`` or ``2``. Number of soil reservoirs; the second
  represents the baseflow component (not in the original model).
* ``surface_runoff``: ``socont_runoff`` (the original non-linear quick reservoir)
  or ``linear_storage`` (a classic linear storage).
* ``snow_melt_process``: melt model to use; see :ref:`melt models <melt-models>`.
  Default: ``"melt:degree_day"``.
* ``glacier_infinite_storage`` (default ``True``): treat the glacier ice as an
  infinite store.
* ``glacier_module`` (default ``"gsm"``): glacier formulation; see
  :ref:`glacier modules <glacier-modules>`.


Parameters
^^^^^^^^^^^


**Precipitation (snow/rain transition)**

* ``prec_t_start`` *(optional, °C, default: 0, [-2, 2])*

  - Temperature below which precipitation is 100% snow. The rain/snow transition is linear
    between ``prec_t_start`` and ``prec_t_end``.
  - Full name: ``snow_rain_transition:transition_start``.

* ``prec_t_end`` *(optional, °C, default: 2, [0, 4])*

  - Temperature above which precipitation is 100% liquid.
  - Full name: ``snow_rain_transition:transition_end``.


**Snow** (``melt:degree_day``)

* ``a_snow`` *(mm/d/°C, no default, [1, 12])*

  - Degree-day snow melt factor. :math:`a_\mathrm{snow}` in :cite:t:`Schaefli2005`.
  - Full name: ``snowpack:degree_day_factor``.

* ``melt_t_snow`` *(optional, °C, default: 0, [0, 5])*

  - Temperature above which snow starts to melt.
  - Full name: ``snowpack:melting_temperature``.


**Glacier** (``melt:degree_day``)

* ``a_ice`` (single type), ``a_ice_<name>``, ``a_ice_<i>`` *(mm/d/°C, no default, [5, 20])*

  - Degree-day ice melt factor. :math:`a_\mathrm{ice}` in :cite:t:`Schaefli2005`.
    ``<name>`` is the land cover name (e.g., ``glacier_debris``); ``<i>`` is the index of
    similar land covers (e.g., ``a_ice_glacier_debris``, ``a_ice_1``).
  - Full name: ``<name>:degree_day_factor``.

* ``melt_t_ice`` *(optional, °C, default: 0, [0, 5])*

  - Temperature above which ice starts to melt.
  - Full name: ``<name>:melting_temperature``.


**Glacier area lumped reservoir**

* ``k_snow`` *(1/d, no default, [0.05, 0.25])*

  - Response factor for the lumped reservoir receiving rain and snowmelt water from the
    glacier area. Similar to :math:`k_\mathrm{snow}` in :cite:t:`Schaefli2005`, but in
    different units.
  - Full name: ``glacier_area_rain_snowmelt_storage:response_factor``.

* ``k_ice`` *(1/d, no default, [0.05, 1])*

  - Response factor for the lumped reservoir receiving ice melt water. Similar to
    :math:`k_\mathrm{ice}` in :cite:t:`Schaefli2005`, but in different units.
  - Full name: ``glacier_area_icemelt_storage:response_factor``.


**Quick runoff (non-linear version)**

* ``beta`` *(m^(4/3)/s, no default, [100, 30000])*

  - Runoff coefficient (to calibrate).
  - Full name: ``surface_runoff:runoff_coefficient``.


**Quick runoff (linear version)**

* ``k_quick`` *(1/d, no default, [0.05, 1])*

  - Response factor for the quick reservoir.
  - Full name: ``surface_runoff:response_factor``.


**Slow reservoir**

* ``A`` *(mm, no default, [10, 3000])*

  - Maximum storage capacity of the slow reservoir.
  - Full name: ``slow_reservoir:capacity``.

* ``k_slow``, ``k_slow_1`` *(1/d, no default, [0.001, 1])*

  - Response factor for the slow reservoir. Same as :math:`k` in :cite:t:`Schaefli2005`,
    but in different units.
  - Full name: ``slow_reservoir:response_factor``.


**Baseflow (optional)**

* ``percol`` *(mm/d, no default, [0, 10])*

  - Percolation rate from the first slow reservoir to the baseflow reservoir.
  - Full name: ``slow_reservoir:percolation_rate``.

* ``k_slow_2`` *(1/d, no default, [0.001, 1])*

  - Response factor for the baseflow reservoir.
  - Full name: ``slow_reservoir_2:response_factor``.


For the ``melt:degree_day_aspect`` and ``melt:temperature_index`` options, see
:ref:`Snow / Glacier melt parameters <snow-melt-params>` under Shared processes.


Pre-defined parameter constraints:

* **Glacier**

  - ``a_snow < a_ice``

* **Slow reservoir**

  - ``k_slow_1 < k_quick``
  - ``k_slow_2 < k_quick``
  - ``k_slow_2 < k_slow_1``


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
  See the :ref:`snow redistribution section <snow-redistribution-params>`.
* ``snow_sublimation_process``: optional snow sublimation process removing snow
  water equivalent directly to the atmosphere (``'sublimation:constant'`` or
  ``'sublimation:pet'``). Default ``None``.
  See the :ref:`snow sublimation section <snow-sublimation>`.


Parameters
^^^^^^^^^^^

**Production store**

* ``X1`` *(mm, default: 350, [100, 1200])*

  - Maximum capacity of the production store.
  - Full name: ``production_store:capacity``.


**Groundwater exchange**

* ``X2`` *(mm/d, default: 0, [-10, 5])*

  - Groundwater exchange coefficient. Negative values indicate a net loss (deep percolation);
    positive values indicate recharge from outside the catchment.
  - Full name: ``uh_input:exchange_factor``.


**Routing store**

* ``X3`` *(mm, default: 90, [1, 500])*

  - Maximum capacity of the routing store.
  - Full name: ``uh_input:routing_capacity``.


**Unit hydrograph**

* ``X4`` *(d, default: 1.7, [0.5, 4])*

  - Time base of the unit hydrograph. Must be > 0.5 d.
  - Full name: ``uh_input:uh_base_time``.

For CemaNeige parameters (``melt:cemaneige``), see
:ref:`Snow / Glacier melt parameters <snow-melt-params>` under Shared processes.
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
  hydro_units.load_from_csv(
    'path/to/hydro_units.csv',
    column_elevation='elevation', 
    column_area='area'
  )

  forcing = hb.Forcing(hydro_units)
  forcing.load_station_data_from_csv(
    'path/to/meteo.csv', 
    column_time='Date', 
    time_format='%d/%m/%Y',
    content={'precipitation': 'precip(mm/day)', 'pet': 'pet(mm/day)'}
  )
  forcing.spatialize_from_station_data(
    variable='precipitation',
    ref_elevation=1250, 
    gradient=0.05
  )
  forcing.spatialize_from_station_data(variable='pet')

  gr4j.setup(
    spatial_structure=hydro_units, 
    output_path='path/to/outputs',
    start_date='1981-01-01', 
    end_date='2020-12-31'
  )
  gr4j.run(parameters=parameters, forcing=forcing)


.. _gr6j:

GR6J
----

GR6J (:cite:t:`Pushpalatha2011`) is a six-parameter daily rainfall-runoff model
that extends :ref:`GR4J <gr4j>` to improve low-flow simulation while preserving
high-flow performance. It keeps the GR4J production store, interception,
throughfall and ET unchanged, and modifies only the routing (see
:ref:`GR6J routing <routing-processes>`):

* the groundwater exchange becomes threshold-based, ``F = X2 (R/X3 - X5)`` (the
  GR5J form), where the dimensionless threshold ``X5`` lets the exchange change
  sign within the year;
* an additional exponential routing store (coefficient ``X6``) is added in
  parallel to the power routing store, which is effective at reproducing long
  recessions.

* **Spatial structure**: lumped
* **Time step**: daily


Specific options
^^^^^^^^^^^^^^^^^

Identical to :ref:`GR4J <gr4j>` (``discrete``, ``snow_melt_process``,
``snow_redistribution``).


Parameters
^^^^^^^^^^^

X1-X4 are identical to :ref:`GR4J <gr4j>`. GR6J adds two parameters:

**Groundwater exchange threshold**

* ``X5`` *(-, default: 0, [-2, 2])*

  - Threshold on the routing-store filling ratio ``R/X3`` at which the
    groundwater exchange changes sign (commonly negative; range follows airGR).
  - Full name: ``uh_input:exchange_threshold``.


**Exponential store**

* ``X6`` *(mm, default: 4, [0.05, 20])*

  - Coefficient of the exponential routing store. Must be > 0.
  - Full name: ``uh_input:exp_store_coeff``.

For CemaNeige parameters (``melt:cemaneige``), see
:ref:`Snow / Glacier melt parameters <snow-melt-params>` under Shared processes.


Usage example
^^^^^^^^^^^^^

GR6J is used exactly like :ref:`GR4J <gr4j>`, with two extra parameters:

.. code-block:: python

  import hydrobricks as hb
  import hydrobricks.models as models

  gr6j = models.GR6J()

  parameters = gr6j.generate_parameters()
  parameters.set_values({'X1': 350, 'X2': 0, 'X3': 90, 'X4': 1.7, 'X5': 0, 'X6': 4})

  # ... load hydro_units and forcing as for GR4J ...

  gr6j.setup(
    spatial_structure=hydro_units,
    output_path='path/to/outputs',
    start_date='1981-01-01',
    end_date='2020-12-31'
  )
  gr6j.run(parameters=parameters, forcing=forcing)


.. _hbv96:

HBV-96
------

HBV-96 (:cite:t:`Lindstrom1997`) is the revised version of the HBV model
(:cite:t:`Bergstrom1976`), a widely used conceptual rainfall-runoff model.
The hydrobricks implementation consists of an abstract ``HBV`` base class,
which holds the routines shared by the HBV versions, and the ``HBV96`` model
class, which adds the HBV-96 response routine. Future HBV variants only need 
to provide their own response routine.

The structure chains four routines:

* **Snow routine**: degree-day melt (CFMAX, TT) with liquid water retention in
  the snowpack (holding capacity CWH) and refreezing of the retained water
  (refreezing coefficient CFR). As in the original model, rain falls onto the
  snowpack: it is added to the liquid water storage, where it can be retained
  and refrozen; without snow it passes through to the ground within the same
  time step. See :ref:`snowpack water retention <snow-water-retention>`.
* **Soil moisture routine**: the incoming water (rain and snowpack outflow) is
  split between the soil moisture storage (capacity FC) and the response
  routine using the beta function; evapotranspiration is limited by the LP
  fraction (see :ref:`infiltration:hbv <infiltration-processes>` and
  :ref:`et:hbv <evapotranspiration>`). With several land covers each has, by
  default, its own soil moisture store (as in the original HBV);
  set ``share_soil=True`` to use a single shared store.
* **Response routine** (HBV-96 specific): a non-linear upper zone
  (:math:`Q_0 = k_{uz} \cdot UZ^{1+\alpha}`), a constant-rate percolation
  (PERC) to a linear lower zone (:math:`Q_1 = k_{lz} \cdot LZ`), and an
  optional capillary transport (CFLUX) returning water from the upper zone to
  the soil moisture storage.
* **Transformation function**: the total runoff is smoothed by the MAXBAS
  triangular unit hydrograph (see :ref:`routing:hbv <routing-processes>`).

The model is integrated by the ODE solver, so the results are
a continuous approximation of the original discrete HBV-96 formulation.

Beyond the default ``open`` cover, HBV supports the land cover types of the original
HBV — ``forest``, ``water`` and ``glacier`` — each with its own
behaviour; see
:ref:`HBV land covers <hbv-land-covers>`.

* **Spatial structure**: lumped or semi-lumped (elevation bands)
* **Time step**: daily, or shorter (see
  :ref:`computation time step <computation-time-step>`); MAXBAS is a duration in days,
  so it routes the same shape at any step


Specific options
^^^^^^^^^^^^^^^^^

* ``snow_melt_process``: melt model to use; see :ref:`melt models <melt-models>`.
  Default: ``"melt:degree_day"``. Must be ``"melt:degree_day"`` when snow
  refreezing is enabled.
* ``share_soil`` (default ``False``): share a single soil moisture store across all
  land covers instead of one store per cover (see
  :ref:`HBV land covers <hbv-land-covers>`).
* ``forest_interception`` (default ``False``): add a canopy interception store on each
  ``forest`` cover (only relevant with a ``forest`` cover; see
  :ref:`HBV land covers <hbv-land-covers>`).
* ``glacier_infinite_storage`` (default ``True``): treat the glacier ice as an
  infinite store (only relevant with a ``glacier`` cover).
* ``glacier_module`` (default ``"gsm"``): glacier formulation; see
  :ref:`glacier modules <glacier-modules>` (only relevant with a ``glacier`` cover).
* ``snow_water_retention_process``: outflow process of the snowpack liquid
  water storage. Default: ``"outflow:snow_holding"`` (the HBV holding capacity
  CWH). ``None`` disables the liquid water retention (melt water then leaves
  the snowpack directly).
* ``snow_refreezing_process``: refreezing process of the retained liquid
  water. Default: ``"refreeze:degree_day"`` (the HBV refreezing coefficient
  CFR). ``None`` disables refreezing. Requires a snow water retention process.
* ``rain_to_snowpack`` (default ``True``): route the rain to the snowpack
  liquid water storage instead of the ground, as in the original HBV snow
  routine. Requires a snow water retention process.
* ``snow_rain_process``: rain/snow partitioning method. Default: ``None``,
  i.e. ``"snow_rain:linear"``, which matches the HBV-96 linear transition over
  TT ± TTI/2 (see :ref:`rain/snow partitioning <snow-rain-partitioning>`).
* ``snow_redistribution``: optional snow redistribution process
  (e.g., ``'transport:snow_slide'``).
  See the :ref:`snow redistribution section <snow-redistribution-params>`.
* ``snow_sublimation_process``: optional snow sublimation process removing snow
  water equivalent directly to the atmosphere (``'sublimation:constant'`` or
  ``'sublimation:pet'``). Default ``None``.
  See the :ref:`snow sublimation section <snow-sublimation>`.


Parameters
^^^^^^^^^^^

The parameters are exposed under their literature names (as aliases).

**Precipitation (snow/rain transition)**

The linear rain/snow transition parameters ``prec_t_start`` and ``prec_t_end``
are the same as in :ref:`GSM-Socont <gsm-socont>`; together they correspond to
the HBV-96 transition interval TT ± TTI/2.

**Snow routine**

* ``cfmax`` *(mm/d/°C, no default, [2, 20])*

  - Degree-day snow melt factor.
  - Full name: ``snowpack:degree_day_factor``.

* ``tt`` *(optional, °C, default: 0, [0, 5])*

  - Threshold/melting temperature.
  - Full name: ``snowpack:melting_temperature``.

* ``cwh`` *(optional, dimensionless, default: 0.1, [0, 0.2])*

  - Liquid water holding capacity of the snowpack, as a fraction of the snow
    water equivalent.
  - Full name: ``snowpack:water_holding_capacity``.

* ``cfr`` *(optional, dimensionless, default: 0.05, [0, 0.1])*

  - Refreezing coefficient of the retained liquid water.
  - Full name: ``snowpack:refreezing_factor``.


**Soil moisture routine**

With a single soil-bearing land cover (or ``share_soil=True``) the aliases below are
used as-is. With several soil-bearing covers and per-class soils (the default), they
take a per-cover suffix instead — ``fc_<cover>``, ``lp_<cover>``, ``beta_<cover>``,
``cevpf_<cover>`` (e.g. ``fc_forest``) — and the full names use the cover's store
(``<cover>_soil_moisture:...``).

.. note::

   A per-class ``fc_<cover>`` is the capacity of the cover's own soil, in mm **over
   the cover**. Each store's capacity and evapotranspiration are scaled by the cover's
   area fraction in the unit, and follow land cover changes, so per-class soils with
   the same parameters behave like a shared soil. The same holds for
   :ref:`PREVAH-UniBE <prevah-unibe>` with ``share_soil=False``.

* ``fc`` *(mm, no default, [0, 3000])*

  - Maximum soil moisture storage capacity.
  - Full name: ``soil_moisture:capacity``.

* ``lp`` *(dimensionless, default: 0.9, [0.3, 1])*

  - Fraction of ``fc`` above which the actual evapotranspiration reaches the
    potential rate.
  - Full name: ``soil_moisture:lp``.

* ``cevpf`` *(optional, dimensionless, default: 1, [0.5, 2])*

  - Evapotranspiration correction factor, scaling the potential evaporation:
    :math:`E_a = \mathrm{cevpf} \cdot \mathrm{PET} \cdot \min(SM/(LP \cdot FC), 1)`.
    Set it per cover (e.g. ``cevpf_forest`` > 1) to give a higher evaporation over
    forests.
  - Full name: ``soil_moisture:et_correction_factor``.

* ``beta`` *(dimensionless, default: 2, [1, 6])*

  - Shape coefficient of the recharge (beta) function.
  - Full name: ``open:beta`` (``<cover>:beta`` in general).


**Response routine**

* ``k_uz`` *(mm^(-alpha)/d, no default, [0.0001, 1])*

  - Response factor of the non-linear upper zone.
  - Full name: ``upper_zone:response_factor``.

* ``alpha``, ``alfa`` *(dimensionless, default: 1, [0, 2])*

  - Non-linearity coefficient of the upper zone runoff (``alfa`` is the SMHI
    spelling). Beyond 2, the upper zone is so stiff that a daily time step
    overshoots it.
  - Full name: ``upper_zone:alpha``.

* ``perc`` *(mm/d, no default, [0, 10])*

  - Constant percolation rate from the upper to the lower zone.
  - Full name: ``upper_zone:percolation_rate``.

* ``cflux`` *(optional, mm/d, default: 0, [0, 3])*

  - Maximum capillary flux from the upper zone back to the soil moisture
    storage.
  - Full name: ``upper_zone:max_capillary_flux``.

* ``k_lz``, ``k4`` *(1/d, no default, [0.0001, 1])*

  - Response factor of the linear lower zone.
  - Full name: ``lower_zone:response_factor``.


**Transformation function**

* ``maxbas`` *(d, default: 1, [1, 10])*

  - Base length of the triangular unit hydrograph.
  - Full name: ``routing:maxbas``.


Pre-defined parameter constraints:

* ``k_lz < k_uz``
* ``a_snow < a_ice`` (only with a ``glacier`` cover)


.. _hbv-land-covers:

Land covers
^^^^^^^^^^^

In addition to the default ``open`` cover (the HBV "open areas" class; the former
``ground`` name is kept as an accepted alias), HBV accepts the land cover types of the
original HBV (``land_cover_types``). Each soil-bearing cover (``open``, ``forest``) has,
by default, its own soil moisture store feeding the shared response routine;
``share_soil=True`` collapses them into one. The soil/recharge parameters are then
exposed per cover (``fc_<cover>``, ``lp_<cover>``, ``beta_<cover>``).

* **forest** — a soil-bearing cover that, when ``forest_interception=True``, intercepts
  rain in a canopy store on the rain path (upstream of the snowpack): the canopy holds
  up to the interception capacity, evaporates at the potential rate, and passes the
  excess as throughfall (snowmelt bypasses the canopy). Interception is **off by
  default**, in which case a ``forest`` cover behaves like a generic soil cover (it can
  still differ from ``open`` through its own per-class soil parameters and ``cevpf``).

  * ``ic`` (or ``ic_<cover>`` with several forests) *(mm, optional, default: 2, [0, 10])*

    - Canopy interception capacity (only with ``forest_interception=True``).
      Full name: ``<cover>_canopy:capacity``.

* **water** — an exclusive open-water cover (a water unit is entirely open water).
  All precipitation enters the open water directly (no snowpack), which evaporates at
  the potential rate, and a linear outflow drains to the outlet. Water units use a
  dedicated no-snow structure variant. (The name ``lake`` is reserved for a future
  distinct cover — a regulated lake or reservoir with its own release rules — and is
  not accepted as a cover type.)

  * ``k_water`` (or ``k_water_<cover>``) *(1/d, no default, [0.0001, 1])*

    - Response factor of the open water's linear outflow.
      Full name: ``<cover>_storage:response_factor``.

* **glacier** — Socont-style glacier handled by the :ref:`glacier module
  <glacier-modules>`: the glacierized area drains its rain + snowmelt and its ice melt
  to two catchment-level linear reservoirs. Parameters ``a_ice`` (ice melt factor),
  ``k_snow`` and ``k_ice`` (reservoir response factors) are as in
  :ref:`GSM-Socont <gsm-socont>`.

At least one soil-bearing cover (``open`` or ``forest``) is required.


Usage example
^^^^^^^^^^^^^

.. code-block:: python

  import hydrobricks as hb
  import hydrobricks.models as models

  hbv = models.HBV96()

  parameters = hbv.generate_parameters()
  parameters.set_values({
    'cfmax': 3, 'tt': 0, 'cwh': 0.1, 'cfr': 0.05,
    'fc': 250, 'lp': 0.9, 'beta': 2,
    'k_uz': 0.2, 'alpha': 1, 'perc': 0.7, 'cflux': 0.5, 'k_lz': 0.05,
    'maxbas': 2.5
  })

  # ... load hydro_units and forcing as for the other models ...

  hbv.setup(
    spatial_structure=hydro_units,
    output_path='path/to/outputs',
    start_date='1981-01-01',
    end_date='2020-12-31'
  )
  hbv.run(parameters=parameters, forcing=forcing)



.. _prevah-unibe:

PREVAH-UniBE
------------

PREVAH (Precipitation-Runoff-EVApotranspiration HRU model, :cite:t:`Viviroli2007b`,
:cite:t:`Gurtz1999`) is an HBV-type conceptual model developed for mountainous
(Alpine) catchments and applied operationally across Switzerland. The hydrobricks
``PrevahUniBE`` class reproduces the University of Bern lineage of the model — the
xPREVAH code base — hence the name; the processes themselves keep the ``prevah``
suffix.

The structure chains the following routines, all resolved per hydro unit
(PREVAH's "hydrotopes"):

* **Snow routine**: rain/snow split over a linear transition with undercatch
  correction factors; melt by the :ref:`radiation-corrected (Hock) melt <melt-models>`
  that PREVAH uses, driven by a potential clear-sky radiation forcing (or by a
  :ref:`seasonal degree-day factor <melt-models>`, CRMFMIN to CRMFMAX); liquid water
  retention (CWH) with PREVAH's melting-day release, refreezing (CRFR) with a seasonal
  factor, and snow evaporation at the albedo-reduced potential rate.
* **Interception**: a canopy store on every non-glacier cover, filled by the
  :ref:`Menzel asymptotic law <interception>` and evaporating at
  :math:`E_P \cdot veg_{cov}`, reduced by the surface albedo under snow.
* **Soil moisture routine**: the incoming water (rain and snowpack outflow) is split
  by the HBV beta function between the soil moisture store (capacity FC) and the
  upper zone; the ET is limited by the CU fraction and reduced by the surface albedo
  under snow. A **single** soil store is shared by the soil-bearing covers, as a
  PREVAH hydrotope carries one soil.
* **Runoff generation**: the upper zone SUZ produces a surface runoff above a storage
  threshold, :math:`Q_0 = k_0 (SUZ - SGRLUZ)`, an interflow :math:`Q_1 = k_1 \cdot SUZ`,
  and a :ref:`percolation gated by the soil moisture <percolation-processes>`.
* **SLOWCOMP groundwater** (:cite:t:`Schwarze1999`): the fast store SLZ1 fills
  asymptotically toward SLZ1MAX with its own baseflow time constant; the excess
  recharge overflows 8/9 into the slow store SLZ2 and 1/9 into the very slow store
  SLZ3 (PREVAH ties the storage time of SLZ3 to nine times that of SLZ1). The
  baseflow is the sum of the three outflows. The wet surfaces (the ``wetland`` covers)
  evaporate from SLZ1.
* **Aggregation**: as in the PREVAH model core, there is no channel routing — the
  catchment discharge is the area-weighted aggregation of the unit outflows.

PREVAH's storage times are expressed in hours; the hydrobricks response factors are
their daily reciprocals, :math:`k = 24 / K_h` (e.g. K0H = 20 h gives
:math:`k_0 = 1.2` d\ :sup:`-1`).

That mapping is exact rather than approximate, and it dictates the solver. PREVAH's
storage coefficients are themselves *exponential decay factors*: the model computes
:math:`k_{\mathrm{PREVAH}} = 1 - e^{-\Delta t / K_h}` once at initialization and
then applies it as a plain multiplier, so an outflow written :math:`k_{\mathrm{PREVAH}}
\cdot S` is really the analytical solution of the linear reservoir over the sub-step
(:cite:t:`Viviroli2007b`, Eq. 4.5-5 and 4.5-10). A linear reservoir integrated
analytically with :math:`k = 24 / K_h` decays over a day by exactly
:math:`e^{-24 / K_h}` — the same value. ``PrevahUniBE`` therefore defaults to the
``analytic_linear`` :ref:`solver <solvers>`, which reproduces those coefficients
exactly; the other solvers only approximate them. The remaining difference is the
sub-step structure: PREVAH adds the inflow at the start of each sub-step (six a day,
or hourly in the gridded version), where the solver spreads it over the whole step.

* **Spatial structure**: distributed or semi-distributed (hydrological units)
* **Time step**: daily, or shorter (see
  :ref:`computation time step <computation-time-step>`); the parameters of the original
  are calibrated for a daily step

The defaults are PREVAH's own processes, and they expect the inputs PREVAH works with:

* a **potential clear-sky radiation** forcing (``solar_radiation``) for the Hock melt.
  It can be computed from a DEM with
  :ref:`the potential radiation <potential-solar-radiation>` of the preprocessing
  module, or directly by a :ref:`project file <project-files-radiation>`. A run
  without it stops with an error; select ``snow_melt_process="melt:degree_day_seasonal"``
  to do without;
* a **vapour-density Hamon PET** (``forcing.compute_pet(method="Hamon_vapor_density",
  ...)``, see :ref:`potential evapotranspiration <pet>`): the snow evaporation has no
  parameter to absorb a PET of another magnitude, and pyet's default Hamon runs about
  1.5 times hotter;
* the **monthly vegetation tables** of the cover classes (see
  :ref:`cover classes <prevah-cover-classes>`), which are applied automatically to
  the covers named after a PREVAH cover class. A cover with a generic name
  (``open``, ``forest``) keeps constant canopy parameters until
  ``apply_cover_parameters`` is called for it.

Each process can be swapped for a simpler one through the options below.


Specific options
^^^^^^^^^^^^^^^^^

* ``snow_melt_process``: melt model; see :ref:`melt models <melt-models>`. Default:
  ``"melt:temperature_index"``, PREVAH's radiation-corrected (Hock) melt, which
  requires the potential clear-sky radiation forcing. ``"melt:degree_day_seasonal"``
  gives PREVAH's seasonal sine between CRMFMIN and CRMFMAX, with no radiation needed.
* ``snow_water_retention_process``: outflow process of the snowpack liquid water
  storage. Default: ``"outflow:snow_holding_prevah"`` (the CWH holding capacity with
  PREVAH's melting-day release and CEXLIQ graded release);
  ``"outflow:snow_holding"`` keeps the plain holding capacity. ``None`` disables the
  retention.
* ``snow_refreezing_process``: refreezing process of the retained liquid water.
  Default: ``"refreeze:degree_day_seasonal"`` (its own seasonal factor, so it works
  with any melt process); ``"refreeze:degree_day"`` reads the factor of a degree-day
  melt process. ``None`` disables refreezing.
* ``rain_to_snowpack`` (default ``True``): route the rain to the snowpack liquid water
  storage, as in the PREVAH snow routine.
* ``snow_sublimation_process``: snow evaporation. Default: ``"sublimation:prevah"``,
  the parameter-free, albedo-driven evaporation of PREVAH; ``"sublimation:pet"``
  evaporates a fixed fraction of the PET.
* ``snow_rain_process``: rain/snow partitioning. Default ``None``, i.e.
  ``"snow_rain:linear"``, PREVAH's transition over TGR ± TTRANS.
* ``snow_redistribution``: optional snow redistribution process.
* ``share_soil`` (default ``True``): share a single soil moisture store across the
  soil-bearing land covers. With ``share_soil=False`` each cover gets its own store,
  with its own ``fc_<cover>`` and ``lp_<cover>``, as PREVAH parameterizes the soil per
  cover class; the percolation is then gated by their area-weighted mean
  saturation, and the snow-albedo reduction of ``et:prevah`` is read from the
  cover owning the store rather than from the whole hydro unit.
  ``fc_<cover>`` is the capacity of the cover's own soil, in mm over the
  cover's area. Each store represents its cover's area, so in each hydro unit its
  capacity and its evapotranspiration are scaled by the cover's area fraction, read
  live so that land cover changes apply during the run. A cover absent from a unit
  therefore holds no soil there and does not affect its percolation. This suits both
  a discretization giving each unit a single cover class (a PREVAH hydrotope) and units
  mixing several covers.
* ``forest_interception`` (default ``True``): enable the canopy interception;
  ``False`` disables it unless ``interception_covers`` names covers explicitly.
* ``interception_covers`` (default ``None``: every cover but the glaciers, as PREVAH
  intercepts on every hydrotope): names of the covers to equip with a canopy store.
* ``canopy_interception_process``: throughfall process of the canopy. Default:
  ``"interception:menzel"``; ``"outflow:threshold"`` gives a simpler fill-then-spill
  store.
* ``canopy_et_process``: canopy evaporation. Default ``"et:open_water_prevah"``
  (the potential rate with the snow-albedo reduction, scaled by the
  ``canopy_et_factor``, PREVAH's ``veg_cov``); ``"et:open_water"`` evaporates at the
  plain potential rate.
* ``soil_et_process``: soil evapotranspiration. Default ``"et:prevah"`` (the HBV
  limitation with PREVAH's snow-albedo reduction, which suppresses the soil ET under
  snow); ``"et:hbv"`` is the plain HBV limitation.
* ``wet_et_from_groundwater`` (default ``True``): add PREVAH's
  :ref:`wet-surface evaporation <et-wet-surface-prevah>`, drawn from the SLZ1
  groundwater store at the potential rate times the wet share of the unit (the area
  of its ``wetland`` covers times their ``wet_fraction``). It is only added when the
  model has a wetland cover.
* ``glacier_infinite_storage`` (default ``True``): treat the glacier ice as an infinite
  store (only relevant with a ``glacier`` cover).
* ``glacier_module`` (default ``"prevah"``): glacier formulation; see
  :ref:`glacier modules <glacier-modules>`.
* ``firn_to_groundwater`` (default ``True``): route the firn melt reservoir into the
  groundwater store SLZ1 instead of the outlet.


Parameters
^^^^^^^^^^^

The parameters are exposed under their PREVAH names (as aliases).

**Precipitation (snow/rain transition)**

``prec_t_start`` and ``prec_t_end`` are the linear transition bounds, corresponding to
TGR − TTRANS and TGR + TTRANS; ``rfcf`` and ``sfcf`` are the rain and snow correction
factors (PREVAH's cf_rain / cf_snow). See
:ref:`precipitation correction <precipitation-correction>`.

**Snow routine**

* ``melt_factor`` (alias ``mf``) *(mm/d/°C, no default, [0, 12])*

  - Temperature factor of the radiation-corrected melt (PREVAH CSNOMF), shared by the
    snow and the glacier ice.
  - Full name: ``type:snowpack,type:glacier:melt_factor``.

* ``r_snow`` *(m²/W·mm/d/°C, no default, [0, 1])*

  - Radiation coefficient of the snow melt (PREVAH CASNO).
  - Full name: ``snowpack:radiation_coefficient``.

* ``a_snow_min`` (alias ``crmfmin``) and ``a_snow_max`` (alias ``crmfmax``) replace
  ``melt_factor`` and ``r_snow`` with ``snow_melt_process="melt:degree_day_seasonal"``
  *(mm/d/°C, no default, [0.5, 6] and [1.5, 12])*

  - Winter minimum and summer maximum of the seasonal snow melt factor.
  - Full names: ``snowpack:degree_day_factor_min``, ``snowpack:degree_day_factor_max``.

* ``melt_t_snow`` *(optional, °C, default: 0, [-3, 5])*

  - Melting temperature (PREVAH T0).
  - Full name: ``snowpack:melting_temperature``.

* ``cwh`` (alias ``whc``) *(optional, dimensionless, default: 0.1, [0, 0.2])*

  - Liquid water holding capacity of the snowpack, as a fraction of the SWE.
  - Full name: ``snowpack:water_holding_capacity``.

* ``holding_melt_t`` *(optional, °C, default: 0, [-5, 5])*

  - Temperature above which the liquid water retention collapses (the melting-day
    release).
  - Full name: ``snowpack:melting_temperature`` (of the retention process).

* ``cexliq`` *(optional, dimensionless, default: 0, [0, 5])*

  - Exponent of the graded release of the fresh melt (PREVAH CEXLIQ); 0 gives the
    plain collapse.
  - Full name: ``snowpack:liquid_release_exponent``.

* ``cfr`` *(optional, dimensionless, default: 0.05, [0, 0.1])*

  - Refreezing coefficient.
  - Full name: ``snowpack:refreezing_factor``.

* ``cfr_ddf_min``, ``cfr_ddf_max`` *(optional, mm/d/°C, defaults: 2 and 6, [0, 12])*
  and ``cfr_melt_t`` *(optional, °C, default: 0, [-5, 5])*

  - Seasonal degree-day factor and melting temperature of the refreezing (PREVAH
    TMFMIN, TMFMAX and T0).
  - Full names: ``snowpack:degree_day_factor_min``, ``snowpack:degree_day_factor_max``,
    ``snowpack:melting_temperature`` (of the refreezing process).

* ``sublimation_pet_factor`` *(optional, dimensionless, default: 0.2, [0, 1])*

  - Fraction of the PET evaporated from the snowpack, only with
    ``snow_sublimation_process='sublimation:pet'`` (the default
    ``'sublimation:prevah'`` has no parameter).
  - Full name: ``snowpack:sublimation_pet_factor``.

**Interception**

* ``ic`` (or ``ic_<cover>`` with several canopies) *(optional, mm, default: 2, [0, 10])*

  - Canopy interception capacity (PREVAH's :math:`si_{\max} \cdot veg_{cov}`, usually
    set monthly).
  - Full name: ``<cover>_canopy:capacity``.

* ``canopy_et_factor`` (or ``canopy_et_factor_<cover>``) *(optional, dimensionless,
  default: 1, [0, 1.5])*

  - Vegetation cover fraction scaling the canopy evaporation (only with
    ``canopy_et_process='et:open_water_prevah'``; usually set monthly).
  - Full name: ``<cover>_canopy:et_factor``.

**Soil moisture routine**

* ``fc`` *(mm, no default, [0, 3000])*

  - Plant-available soil moisture storage capacity. Often set per unit from a soil map
    with a :ref:`spatial parameter <spatial-parameters>`. With ``share_soil=False``
    the alias takes a per-cover suffix instead (``fc_<cover>``, and likewise
    ``lp_<cover>``).
  - Full name: ``soil_moisture:capacity`` (``<cover>_soil_moisture:capacity`` with
    per-cover stores).

* ``lp`` (alias ``cu``) *(dimensionless, no default, [0.3, 1])*

  - Fraction of ``fc`` above which the actual ET reaches the potential rate.
  - Full name: ``soil_moisture:lp``.

* ``cevpf`` *(optional, dimensionless, default: 1, [0.5, 2])*

  - Evapotranspiration correction factor.
  - Full name: ``soil_moisture:et_correction_factor``.

* ``albedo_land`` *(optional, dimensionless, default: 0.2, [0, 0.4])*

  - Albedo of the snow-free ground in the snow-albedo reduction of the soil ET
    (0.2 makes the reduction neutral without snow).
  - Full name: ``soil_moisture:albedo_land``.

* ``beta_<cover>`` *(dimensionless, no default, [0.3, 6])*

  - Shape coefficient of the beta recharge function (PREVAH CBETA), per soil-bearing
    cover. With a single cover the alias is ``beta``.
  - Full name: ``<cover>:beta``.

**Runoff generation (upper zone)**

* ``k0`` *(1/d, no default, [0.0001, 1])*

  - Surface runoff response factor (= 24 / K0H).
  - Full name: ``upper_zone:response_factor_threshold``.

* ``sgrluz`` *(mm, no default, [0, 100])*

  - Upper zone storage threshold above which surface runoff is generated.
  - Full name: ``upper_zone:threshold``.

* ``k1`` *(1/d, no default, [0.0001, 1])*

  - Interflow response factor (= 24 / K1H).
  - Full name: ``upper_zone:response_factor``.

* ``cperc`` *(mm/d, no default, [0, 10])*

  - Maximum percolation rate to the groundwater.
  - Full name: ``upper_zone:percolation_rate``.

* ``cu_perc`` *(optional, dimensionless, default: 0.7, [0, 0.9])*

  - Soil moisture fraction below which the percolation stops. PREVAH uses the same
    value as ``cu``.
  - Full name: ``upper_zone:threshold_fraction``.

**SLOWCOMP groundwater**

* ``k_gw1``, ``k_gw2``, ``k_gw3`` *(1/d, no default, [0.0001, 1])*

  - Response factors of the fast, slow and very slow stores (= 24 / CG1H, 24 / K2H and
    24 / CG3H, with CG3H = 9 × CG1H).
  - Full names: ``slz1:response_factor``, ``slz2:response_factor``,
    ``slz3:response_factor``.

* ``slz1max`` *(optional, mm, default: 100, [0, 1000])*

  - Maximum content of the fast baseflow store SLZ1, bounding its asymptotic fill.
  - Full name: ``slz1:max_content``.

**Land-cover specific**

* ``wet_fraction`` (or ``wet_fraction_<cover>``) *(optional, dimensionless,
  default: 0.8889, [0, 1])*

  - Fraction of a ``wetland`` cover's input routed directly to the groundwater
    (PREVAH's wet surfaces: 0.7 on wetlands, 0.9 on open water); the rest goes through
    the soil routine.
  - Full name: ``<cover>:split_fraction``.

* ``wet_et_factor`` *(optional, dimensionless, default: 1, [0, 1.5])*

  - Overall scaling of the wet-surface evaporation, whose rate already follows the
    wetland area and its ``wet_fraction`` (only with a wetland cover).
  - Full name: ``slz1:et_factor``.

* ``r_ice`` (or ``r_ice_<cover>`` with several glacier covers), ``k_ice``, ``k_snow``,
  ``k_firn`` — the radiation coefficient of the ice melt (above ``r_snow``) and the
  reservoir response factors, only with a ``glacier`` cover; the seasonal melt uses
  ``a_ice_min`` / ``a_ice_max`` instead of ``r_ice``. ``lag_snow``, ``lag_ice`` and
  ``lag_firn`` *(optional, d, defaults: 2/24, 1/24 and 0, [0, 1])* are the
  translation times following the three reservoirs. See
  :ref:`glacier modules <glacier-modules>`.

* ``kwper`` and ``perc_const`` *(optional, per unit)* — the hydraulic-conductivity
  factor of the percolation and the share of the unit percolating at a constant rate
  (built-up and rock hydrotopes); see
  :ref:`percolation:prevah <percolation-processes>`. Set them with
  ``model.apply_cover_percolation(parameters, hydro_units, cover_class, awc,
  soil_depth, conductivity=None)``. The per-unit ``awc``, ``soil_depth`` and
  ``conductivity`` come from the soil maps through
  :ref:`extract_soil_properties <unit-properties-from-rasters>`.

Pre-defined parameter constraints (the response cascade must slow down with depth):

* ``k1 < k0``
* ``k_gw1 < k1``
* ``k_gw2 < k_gw1``
* ``k_gw3 < k_gw2``


Land covers
^^^^^^^^^^^

``PrevahUniBE`` accepts ``open``, ``forest``, ``wetland`` and ``glacier`` covers (plus
the generic soil covers ``urban`` and ``rock``, available in every model). At least one
soil-bearing cover is required, and all of them share the single soil moisture store.

* **open**, **forest** — soil-bearing covers feeding the beta split, each carrying a
  canopy interception store by default.
* **wetland** — a wet surface: the ``wet_fraction`` share of its input recharges the
  groundwater store SLZ1 directly, the rest passing through the soil routine, and the
  same share of its area evaporates from SLZ1.
* **glacier** — handled by the :ref:`PREVAH glacier module <glacier-modules>`, with the
  ice and firn covers split at the equilibrium line.


.. _prevah-cover-classes:

Cover classes
^^^^^^^^^^^^^

.. note::

   A **land cover** is a named cover of a hydro unit, with an area fraction in each
   unit. Covers differ either by their **type** (``open``, ``forest``, ``glacier``,
   ...), which decides what the model builds for them, or only by their
   **parameters** — ``pasture`` and ``bush`` are both ``open`` and run the same
   routines, but carry different monthly values. A **cover class** is an entry of
   an external land cover classification, such as PREVAH's 22 classes below, used
   to look up those parameters; it is finer-grained than a type, and a cover is
   usually named after the class it stands for.

The original PREVAH carries a fixed table of cover classes: water, built-up, coniferous /
deciduous / mixed forest, cereals, pasture, bush, firn, bare ice, rock, fruits,
vegetables, wheat, alpine vegetation, wetlands, rough pasture, sub-alpine and alpine
meadow, bare soil vegetation, corn and grapes.

Only **six** of them carry distinct physics — water, built-up, firn, bare ice, rock
and wetlands — and those are the hydrobricks land cover types of the same name
(``water``, ``urban``, ``glacier``, ``rock``, ``wetland``). Every other cover class runs
the same snow, soil and runoff routines and differs *only* through monthly tables of
vegetation properties. They therefore need no dedicated cover type: declare them as
ordinary land covers under their own name, typed ``open`` or ``forest``, and give each
its own monthly parameters.

Those tables (maximal interception storage, vegetation cover fraction, rooting depth,
albedo, leaf area index and the land-cover capacity overrides) live in
:mod:`hydrobricks.land_covers` as ``PREVAH_COVER_*``, where any model can use them,
and ``PrevahUniBE`` applies them:

.. code-block:: python

    import hydrobricks.models as models
    from hydrobricks.land_covers import PREVAH_COVER_TYPES

    covers = ["coniferous_forest", "pasture", "wetland"]
    model = models.PrevahUniBE(
        land_cover_names=covers,
        land_cover_types=[PREVAH_COVER_TYPES[c] for c in covers],
        share_soil=False,
    )
    parameters = model.generate_parameters()  # the tables of the three cover classes
    parameters.set_values(...)

``generate_parameters`` applies the tables to every canopy whose cover is named after
a cover class: the canopy interception capacity is set to
:math:`si_{\max} \cdot veg_{cov}` and, when the canopy uses ``et:open_water_prevah``
(the default), the canopy evaporation factor to :math:`veg_{cov}`, both as
:ref:`monthly parameters <monthly-parameters>`. A cover under another name gets them
from ``apply_cover_parameters``, given the cover class it stands for:

.. code-block:: python

    model.apply_cover_parameters(parameters, "alpine_meadow", cover_name="open")

``PrevahUniBE.cover_field_capacity(cover_class, awc, soil_depth)`` gives the monthly
soil moisture capacity PREVAH derives from a soil map,
:math:`awc \cdot \min(root\_depth + 0.05,\ soil\_depth) \cdot 10`, with the
available water content in [Vol-%] and the depths in [m]. The land cover then overrides
the result as in the original: a fixed capacity where there is no real soil (5 mm
built-up, 3 mm rock, 0.1 mm glacier) and a minimum elsewhere (2500 mm open water, 10 mm
on the vegetated covers).

That capacity varies in space and through the year at once, which
``apply_cover_field_capacity`` sets up in one call — it builds the per-unit monthly
table, stores it as twelve hydro-unit properties and binds the parameter to them as a
:ref:`spatial monthly parameter <spatial-monthly-parameters>`:

.. code-block:: python

    model.apply_cover_field_capacity(
        parameters, hydro_units, cover_classes,  # one cover class per hydro unit
        available_water_content=awc,         # [Vol-%], one value per hydro unit
        soil_depth=soil_depth,               # [m], one value per hydro unit
    )

A PREVAH hydrotope carries a single cover class, so the cover class is given per
hydro unit here; a single name applies to all of them. A per-unit value times a
shared monthly shape would not do: the units can carry different cover classes,
hence different rooting-depth curves, and each unit's own soil depth caps that
depth from above while the minimum capacity holds it up from below, so the shape
of the year differs from unit to unit.

Whether the capacity actually moves through the year depends on the cover classes in play:
only the crops of the table root deeper in summer, and where none of them occurs the
capacity is constant and a plain :ref:`spatial parameter <spatial-parameters>` would do
as well.

The tables are keyed by cover class name, following the hydrobricks conventions
(``urban``, ``wetland``, ``glacier_ice`` / ``glacier_firn``, the latter two matching
:ref:`the ELA split <glacier-cover-init>`); PREVAH's own class numbers are not used.

A land cover often aggregates several cover classes — a single ``forest`` cover standing
for coniferous, deciduous and mixed stands, say. Give it the cover class that represents
the mixture: the dominant one where one dominates, and otherwise the one whose
vegetation cover is closest to the area-weighted mean of the mixture, since
``veg_cov`` scales the canopy evaporation and therefore drives most of the effect.
``examples/advanced/prevah_ticino.py`` works this through on a real dataset.

Reproducing the original PREVAH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The defaults are the processes that reproduce the original point by point, so the
model needs no option to do so:

.. code-block:: python

    model = models.PrevahUniBE(land_cover_names=covers, land_cover_types=covers)

together with the vapour-density Hamon PET used by PREVAH
(``forcing.compute_pet(method="Hamon_vapor_density", ...)``, see
:ref:`potential evapotranspiration <pet>`), the monthly vegetation tables
(``ic`` = :math:`si_{\max} \cdot veg_{cov}`, ``canopy_et_factor`` =
:math:`veg_{cov}`, see :ref:`cover classes <prevah-cover-classes>`) and the potential
clear-sky radiation of each unit for the radiation-corrected (Hock) melt of the
control file. The refreezing brings its own seasonal factor, since there is no
degree-day melt to read it from.

The soil moisture limitation follows the control file too: the Hamon
evapotranspiration method selects the PREVAH branch that evaporates the soil at the
potential rate, so the CU limit is set to ~0 rather than to its calibrated value.

``examples/advanced/prevah_ticino.py`` runs that configuration on the
Ticino-Bellinzona test catchment (570 hydrotopes, daily step, 1984-2000), building
the soil moisture capacity of each hydrotope from its own soil and cover class. With the
parameters of the original taken as they are — **nothing is calibrated in
hydrobricks** — it reproduces the discharge of the Fortran PREVAH with a
Nash-Sutcliffe efficiency of about 0.985. The example also scores against the gauged
discharge of the Ticino at Bellinzona, where both models land around 0.79.
Because the parameters belong to the original, they are only consistent with the
original's process set.

The following components of the original are **not** reproduced:

* the dynamic contributing-area (soil-topographic index) surface runoff store. It is
  present in the PREVAH code lineages — both the hydrotope-based xPREVAH and the
  gridded FORHYCS implement it identically — but in none of the published model
  descriptions, and both codes disable it for catchments above 100 km²;
* the runoff concentration and flood routing modules (single linear storage and
  translation elements), which are outside the PREVAH model core;
* the optional karst outflow of the upper zone (:math:`Q_3 = k_3 \cdot SUZ` in the
  gridded PREVAH). Being a plain linear reservoir outflow, it can be added to the
  upper zone through a :ref:`custom structure <custom-structures>` if needed;
* the memory of the percolation rate within a day: once the soil saturates, xPREVAH
  keeps the rate of its previous sub-step, where hydrobricks applies the full rate;
* the alternative melt (energy balance, wind index) and PET (Penman-Monteith, Turc,
  Wendling) formulations, the last of which are covered by the
  :ref:`PET methods <pet>` of the forcing module.


.. _custom-structures:

Custom structures
-----------------

A model structure can be declared entirely as data — the bricks (stores and
land covers), their processes, and the fluxes routing the water between bricks
or to the outlet — in a YAML file (or an equivalent dict) consumed by
``hb.models.CustomModel``:

.. code-block:: yaml

   name: my_model

   options:
     snow_melt_process: melt:degree_day

   bricks:
     open:                        # a land cover (must match land_cover_names)
       kind: land_cover
       processes:
         infiltration: {kind: infiltration:socont, target: slow_reservoir}
         runoff: {kind: outflow:rest, target: surface_runoff}
     slow_reservoir:
       kind: storage              # attached to each hydro unit by default
       parameters: {capacity: 200}
       processes:
         et: {kind: et:socont}    # ET needs no target (to the atmosphere)
         outflow: {kind: outflow:linear, target: outlet}
         overflow: {kind: overflow, target: outlet}
     surface_runoff:
       kind: storage
       processes:
         runoff: {kind: outflow:linear, target: outlet}

   aliases:
     slow_reservoir:capacity: A
     slow_reservoir:response_factor: k_slow
     surface_runoff:response_factor: k_quick

   constraints:
     - [k_slow, "<", k_quick]

.. code-block:: python

   model = models.CustomModel('my_structure.yaml')
   model.print_structure()
   parameters = model.generate_parameters()

The rain/snow splitters and one snowpack per land cover are generated from the
``options`` (the same snow options every model supports), so the declared
bricks start where the snow routine ends. The rules:

* **Bricks** attach to each hydro unit by default; use ``attach_to:
  subbasin`` for catchment-level stores (``sub_basin`` is still accepted). ``kind: land_cover`` selects a
  declared land cover (the name must match the model's ``land_cover_names``);
  other kinds (e.g. ``storage``) create new stores. Fixed brick properties go
  in ``parameters`` (e.g. ``{capacity: 200}``); ``computed_directly: true``
  marks a brick as explicitly computed (outside the ODE solver). ``area_of:
  <land cover>`` makes a store represent that cover's area rather than the whole
  unit (e.g. one soil store per cover, fed by it): its ``capacity`` is then the
  cover's own, and the capacity and the evapotranspiration of the store are scaled
  by the cover's live area fraction in each unit.
* **Processes** withdraw water from their brick: the ``kind`` selects the
  formulation (see the :ref:`processes page <processes>`), and its
  calibratable parameters are generated from it — ``generate_parameters()``,
  calibration and :ref:`project files <project-files>` work exactly as for
  the pre-built models. ``aliases`` gives the generated parameters friendly
  names, and ``constraints`` declares relationships enforced during
  calibration.
* **Fluxes** are the process outputs: ``target`` routes to a declared brick,
  a generated one (e.g. ``<cover>_snowpack``) or ``outlet``; ``targets`` (a
  list) fans out to several bricks. ET and sublimation processes take no
  target (the water leaves to the atmosphere). Declare the bricks in flow
  order: fluxes must point to bricks declared **later** in the file (water
  flows forward through the solver), and ``instantaneous: true`` transfers
  within the same time step (required for same-brick loops). ``log: true``
  records a flux for the output files.

In a project file, point the ``model`` section at the structure instead of a
pre-built name:

.. code-block:: yaml

   model:
     structure: my_structure.yaml

A complete example (replicating GSM-Socont as an illustration) is available
in the `examples directory
<https://github.com/hydrobricks/hydrobricks/tree/main/examples/basics>`_
(``custom_structure.yaml`` and ``run_custom_structure.py``).
