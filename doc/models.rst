.. _models:

Models
======

The following model structures are currently implemented:

* :ref:`GSM-Socont <gsm-socont>`
* :ref:`GR4J <gr4j>`
* :ref:`GR6J <gr6j>`
* :ref:`HBV-96 <hbv96>`

Beyond the pre-built structures, a model can be defined entirely through a file —
its stores, processes and fluxes declared in a YAML file — with
:ref:`custom structures <custom-structures>`.


Common options
--------------

All models accept the following options at instantiation:

* ``solver``: numerical solver to use; choices are ``heun_explicit`` (default),
  ``runge_kutta``, ``euler_explicit``, and ``analytic_linear``. See the
  :ref:`solvers page <solvers>` for their properties and how to choose.
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

    socont = models.Socont(solver="heun_explicit", record_all=False)


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

Snow redistribution via the SnowSlide method (:cite:t:`Bernhardt2010`) simulates
gravitational downslope transport of snow between hydro units. It is activated by setting
``snow_redistribution="transport:snow_slide"``.

**Snow slide** (``transport:snow_slide``)

* ``snow_slide_coeff`` *(optional, dimensionless, default: 3178.4, [0, 10000])*

  - Coefficient in the snow holding depth equation
    :math:`h_\mathrm{hold} = \mathrm{coeff} \cdot \theta^{\mathrm{exp}}`,
    where :math:`\theta` is the slope in degrees.
  - Full name: ``<snowpack>:coeff``.

* ``snow_slide_exp`` *(optional, dimensionless, default: -1.998, [-5, 0])*

  - Exponent in the snow holding depth equation (see above).
  - Full name: ``<snowpack>:exp``.

* ``snow_slide_min_slope`` *(optional, °, default: 10, [0, 45])*

  - Minimum slope used in the holding depth calculation. Units with a slope below 
    this value are treated as having this minimum slope.
  - Full name: ``<snowpack>:min_slope``.

* ``snow_slide_max_slope`` *(optional, °, default: 75, [45, 90])*

  - Slope above which the minimum snow holding depth is applied directly, regardless 
    of the equation result.
  - Full name: ``<snowpack>:max_slope``.

* ``snow_slide_min_snow_depth`` *(optional, mm, default: 50, [0, 1000])*

  - Minimum snow holding depth applied when the slope exceeds ``snow_slide_max_slope``.
  - Full name: ``<snowpack>:min_snow_holding_depth``.

* ``snow_slide_max_snow_depth`` *(optional, mm, default: 20000, [-1, 50000])*

  - Maximum snow depth allowed to accumulate in a receiving unit (extension to the original
    method). Set to ``-1`` for no limit.
  - Full name: ``<snowpack>:max_snow_depth``.


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
  default, its own soil moisture store (the original HBV land-use formulation);
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

Beyond the default ``open`` cover, HBV supports the HBV land-use classes as land
covers — ``forest``, ``lake`` and ``glacier`` — each with its own behaviour; see
:ref:`HBV land covers <hbv-land-covers>`.

* **Spatial structure**: lumped or semi-lumped (elevation bands)
* **Time step**: daily


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

* ``alpha``, ``alfa`` *(dimensionless, default: 1, [0, 3])*

  - Non-linearity coefficient of the upper zone runoff (``alfa`` is the SMHI
    spelling).
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
``ground`` name is kept as an accepted alias), HBV accepts the HBV land-use classes as
land covers (``land_cover_types``). Each soil-bearing cover (``open``, ``forest``) has,
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

* **lake** — an exclusive open-water cover (a lake unit is entirely lake). All
  precipitation enters the lake directly (no snowpack), the open water evaporates at
  the potential rate, and a linear outflow drains to the outlet. Lake units use a
  dedicated no-snow structure variant.

  * ``k_lake`` (or ``k_lake_<cover>``) *(1/d, no default, [0.0001, 1])*

    - Response factor of the lake's linear outflow.
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
  sub_basin`` for catchment-level stores. ``kind: land_cover`` selects a
  declared land cover (the name must match the model's ``land_cover_names``);
  other kinds (e.g. ``storage``) create new stores. Fixed brick properties go
  in ``parameters`` (e.g. ``{capacity: 200}``); ``computed_directly: true``
  marks a brick as explicitly computed (outside the ODE solver).
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
