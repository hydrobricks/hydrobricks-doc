.. _processes:

Processes
=========


.. _snow-rain-partitioning:

Rain/snow partitioning
-----------------------

Precipitation is partitioned into rain and snow before entering any store.
Three partitioning methods are available, selected via the ``snow_rain_process`` option.
If ``snow_rain_process`` is not set, the default is ``'snow_rain:linear'``, except
when ``snow_melt_process='melt:cemaneige'``, which automatically selects
``'snow_rain:cemaneige'``.


Linear transition (``snow_rain:linear``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default partitioning applies a linear transition between pure snow and pure rain
over a user-defined temperature range:

* Below ``prec_t_start`` *(optional, °C, default: 0, [-2, 2])*: all precipitation falls as snow.
* Above ``prec_t_end`` *(optional, °C, default: 2, [0, 4])*: all precipitation falls as rain.
* Between the two thresholds: the snow fraction decreases linearly.

This partitioning is used by default in GSM-Socont, in HBV-96 (where it
corresponds to the transition interval TT ± TTI/2), and in GR4J when
``snow_melt_process`` is not ``'melt:cemaneige'``.


Single-threshold (``snow_rain:threshold``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A step-function partitioning with no transition zone. All precipitation is snow at
or below the threshold, and rain above it.

* ``prec_t`` *(optional, °C, default: 0, [-5, 5])*: temperature threshold.
  Full name: ``snow_rain_transition:threshold``.


CemaNeige rain/snow partitioning (``snow_rain:cemaneige``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CemaNeige partitioning (:cite:t:`Valery2014`) has no calibrated parameters. It is
selected automatically when ``snow_melt_process='melt:cemaneige'`` in GR4J. The
equation used depends on elevation.

**At elevations ≥ 1500 m**, the solid fraction is computed from the daily mean
temperature :math:`T_\mathrm{mean}` with fixed bounds of −1 °C and 3 °C:

.. math::

   f_{\mathrm{solid}} = \max\!\left(0,\; \min\!\left(1,\; \frac{3 - T_{\mathrm{mean}}}{4}\right)\right)

No additional forcing variables are needed beyond daily mean temperature.

**At elevations < 1500 m**, the solid fraction is approximated as the fraction of the
day during which temperature is below 0 °C, assuming a linear diurnal cycle between
the daily minimum (:math:`T_\mathrm{min}`) and maximum (:math:`T_\mathrm{max}`):

.. math::

   f_{\mathrm{solid}} = \max\!\left(0,\; \min\!\left(1,\; 1 - \frac{T_{\mathrm{max}}}{T_{\mathrm{max}} - T_{\mathrm{min}}}\right)\right)

The ``temperature_min`` and ``temperature_max`` forcing variables are required for
hydro units below 1500 m.


.. _precipitation-correction:

Precipitation correction
-------------------------

Independently of the rain/snow partitioning method, every model registers a
pair of multiplicative undercatch-correction factors (the HBV RFCF/SFCF) on
its precipitation splitter. They scale the rain and snow amounts *after* the
partitioning, so they can compensate for gauge undercatch without changing
where the rain/snow threshold sits. Both default to 1.0 (no correction) and
are optional.

For snow-bearing models, the splitter (``snow_rain_transition``) carries both
factors and a built-in constraint keeps the snow factor at least as large as
the rain factor (snow undercatch is usually the larger of the two):

.. math::

   P_{\mathrm{rain}}(t) = \mathrm{RCF} \cdot P_{\mathrm{rain}}^{\mathrm{raw}}(t),
   \qquad
   P_{\mathrm{snow}}(t) = \mathrm{SCF} \cdot P_{\mathrm{snow}}^{\mathrm{raw}}(t)

For no-snow models, only the rain-only splitter (``rain``) and its correction
factor are registered.

Parameters:

* ``rain_correction_factor`` (aliases ``rain_corr_factor``, ``rfcf``, ``rcf``)
  *(optional, dimensionless, default: 1.0, [0.7, 1.3])*

  - Multiplicative correction applied to the rain fraction.
  - Full name: ``snow_rain_transition:rain_correction_factor`` (or
    ``rain:rain_correction_factor`` for no-snow models).

* ``snow_correction_factor`` (aliases ``snow_corr_factor``, ``sfcf``, ``scf``)
  *(optional, dimensionless, default: 1.0, [0.8, 1.6])*

  - Multiplicative correction applied to the snow fraction. Not registered for
    no-snow models. Constrained to ``rain_correction_factor <= snow_correction_factor``.
  - Full name: ``snow_rain_transition:snow_correction_factor``.


.. _melt-models:

Melt models
-----------

Five snow and glacier melt models are available in Hydrobricks. They differ
in data requirements and spatial complexity, ranging from a simple temperature
index to a radiation-enhanced approach. Choose based on the available input
data and the catchment characteristics.

Available melt models:

* **degree_day**: classical degree-day model
* **degree_day_aspect**: aspect-based degree-day model
* **degree_day_seasonal**: degree-day model with a seasonally varying factor
* **temperature_index**: Hock's radiation-enhanced temperature-index model
* **cemaneige**: CemaNeige snowmelt model with thermal-state correction

Specify the melt model when instantiating the hydrological model:

.. code-block:: python

   socont = Socont(
      soil_storage_nb=2,
      surface_runoff="linear_storage",
      snow_melt_process="melt:degree_day"
   )

Valid values for ``snow_melt_process``: ``"melt:degree_day"``,
``"melt:degree_day_aspect"``, ``"melt:degree_day_seasonal"``,
``"melt:temperature_index"``, ``"melt:cemaneige"``.


Degree-day model (``degree_day``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Degree-day or temperature-index approaches are widely used in snow- and 
glacier-dominated catchments because they require only air temperature data, 
which is often the most readily available meteorological variable. 
The general form (:cite:t:`Rango1995`) is:

.. math::

   M_{\mathrm{DD}}(t) =
    \begin{cases}
        a_j(T_a(t) - T_T) & : T_a(t) > T_T \quad j \in \{\mathrm{snow,\, ice}\}\\
        0 & : T_a(t) \leq T_T
    \end{cases}

where:

- :math:`M_{\mathrm{DD}}(t)` is the melt rate at time step :math:`t` [mm d⁻¹],
- :math:`a_j` is the degree-day factor for snow or ice [mm d⁻¹ °C⁻¹],
- :math:`T_a` is the air temperature [°C],
- :math:`T_T` is the melt temperature threshold [°C].

This is the simplest option: melt is proportional to the temperature excess above
the threshold, with a single degree-day factor per surface type (snow or ice).
Requires only temperature and elevation band data. Use this model when
computational simplicity or data availability is a priority.

Parameters:

* ``degree_day_factor`` *(mm d⁻¹ °C⁻¹, no default, [2, 20])*

  - Degree-day factor :math:`a_j`. Registered independently per snow- or
    ice-bearing component (e.g. ``snowpack:degree_day_factor``,
    ``glacier:degree_day_factor``), so snow and ice can be calibrated
    separately.

* ``melting_temperature`` *(optional, °C, default: 0, [0, 5])*

  - Melt temperature threshold :math:`T_T`.
  - Full name: ``<component>:melting_temperature``.


Aspect-based degree-day model (``degree_day_aspect``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extends the standard degree-day model by assigning different degree-day factors
to north-, south-, and east/west-facing slopes. Sun-exposed south-facing slopes
receive more radiation and melt faster for the same air temperature; this model
captures that effect without explicitly computing radiation. It requires the
catchment to be discretized by elevation and aspect. Use this model when aspect
strongly differentiates melt rates across the catchment.

Parameters:

* ``degree_day_factor_n`` *(mm d⁻¹ °C⁻¹, no default, [1, 20])*

  - Degree-day factor for north-facing slopes.
  - Full name: ``<component>:degree_day_factor_n``.

* ``degree_day_factor_s`` *(mm d⁻¹ °C⁻¹, no default, [1, 20])*

  - Degree-day factor for south-facing slopes.
  - Full name: ``<component>:degree_day_factor_s``.

* ``degree_day_factor_ew`` *(mm d⁻¹ °C⁻¹, no default, [1, 20])*

  - Degree-day factor for east- and west-facing slopes.
  - Full name: ``<component>:degree_day_factor_ew``.

* ``melting_temperature`` *(optional, °C, default: 0, [0, 5])*

  - Melt temperature threshold :math:`T_T`, shared by all three aspects.
  - Full name: ``<component>:melting_temperature``.


Radiation-enhanced temperature-index model (``temperature_index``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Based on :cite:t:`Hock1999`, this model replaces the fixed degree-day factor with one
that scales with potential clear-sky solar radiation:

.. math::

    M_{\mathrm{HTI}}(t) =
        \begin{cases}
            (m + r_j\, I_{\mathrm{pot}})(T_a(t) - T_T) & : T_a(t) > T_T \quad j \in \{\mathrm{snow,\, ice}\}\\
            0 & : T_a(t) \leq T_T
        \end{cases}

where:

- :math:`m` is a base melt factor common to both ice and snow [mm d⁻¹ °C⁻¹],
- :math:`r_j` is a radiation factor for snow or ice [mm d⁻¹ °C⁻¹ m² W⁻¹],
- :math:`I_{\mathrm{pot}}` is the potential clear-sky direct solar radiation [W m⁻²].

Radiation is computed as:

.. math::

   I_{\mathrm{pot}} = I_0 \left( \frac{R_m}{R} \right)^2 \Psi_a^{\left( \frac{P}{P_0 \cos Z} \right)} \cos\theta

where :math:`I_0` is the solar constant (1368 W m⁻²),
:math:`(R_m/R)^2` is the orbital eccentricity correction,
:math:`\Psi_a` is the mean clear-sky transmissivity,
:math:`P/P_0` is the ratio of local to sea-level atmospheric pressure,
:math:`Z` is the zenith angle, and :math:`\theta` is the angle between
the surface normal and the solar beam. Radiation is computed at 15-minute
intervals and aggregated to daily values to capture diurnal and shading effects.

This model requires the catchment to be discretized by elevation and radiation.
It is the most physically realistic of the three temperature-based variants and
is recommended when snow and glacier melt dominate runoff.
The main trade-off is that computing the radiation field adds some preprocessing time.
See :cite:t:`Argentin2025` for a comparative evaluation of all three models.

Parameters:

* ``melt_factor`` (alias ``hock_melt_factor``) *(mm d⁻¹ °C⁻¹, no default, [0, 12])*

  - Base melt factor :math:`m`, common to ice and snow.
  - Full name: ``<component>:melt_factor``.

* ``radiation_coefficient`` (alias ``hock_radiation_coefficient``)
  *(m² W⁻¹ mm d⁻¹ °C⁻¹, no default, [0, 1])*

  - Radiation factor :math:`r_j`, set independently per snow or ice component.
  - Full name: ``<component>:radiation_coefficient``.

* ``melting_temperature`` (alias ``hock_melting_temperature``)
  *(optional, °C, default: 0, [0, 5])*

  - Melt temperature threshold :math:`T_T`.
  - Full name: ``<component>:melting_temperature``.


CemaNeige snowmelt model (``cemaneige``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CemaNeige model (:cite:t:`Valery2014`) addresses a known weakness of plain degree-day
models: they tend to overestimate melt immediately after cold spells because they
respond instantly to temperature without any memory of prior cold. CemaNeige
adds a **thermal state** variable :math:`e_{TG}` that tracks how cold the
snowpack is. Melt can only occur when the snowpack has fully warmed (i.e.,
:math:`e_{TG} = 0`):

.. math::

   e_{TG}(t) = \min\!\left(0,\; CTG \cdot e_{TG}(t-1) + (1-CTG) \cdot (T_a - T_{melt})\right)

.. math::

   M_{\mathrm{pot}}(t) =
   \begin{cases}
       K_f \cdot (T_a - T_{melt}) & : e_{TG} = 0 \text{ and } T_a > T_{melt} \\
       0 & : \text{otherwise}
   \end{cases}

An additional scaling factor accounts for partial snow cover: when the snow
water equivalent (SWE) is well below the mean annual accumulation :math:`C_n`,
only a fraction of the area is snow-covered and effective melt is reduced:

.. math::

   M(t) = \left(0.9 \cdot \min\!\left(1,\; \frac{SWE}{C_n}\right) + 0.1\right) \cdot M_{\mathrm{pot}}(t)

where :math:`C_n = 0.9 \times \overline{P_{\mathrm{snow}}}` and
:math:`\overline{P_{\mathrm{snow}}}` is the mean annual solid precipitation.
The factor 0.1 ensures a minimum melt rate even at very low SWE.

Parameters:

* ``Kf``: degree-day melt factor [mm d⁻¹ °C⁻¹]
* ``CTG``: cold content weighting factor [−], range [0, 1]. Values close to 1
  give the snowpack a long thermal memory; values near 0 make it respond
  almost instantly to temperature.
* ``Tmelt``: melt temperature threshold [°C]
* ``Cn`` (``mean_annual_snow``): mean annual solid precipitation [mm]

CemaNeige is the recommended snow model for the :ref:`GR4J <gr4j>` model:

.. code-block:: python

   gr4j = models.GR4J(snow_melt_process='melt:cemaneige')


Seasonal degree-day model (``degree_day_seasonal``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The degree-day model of :ref:`PREVAH-UniBE <prevah-unibe>`
(:cite:t:`Viviroli2007b`): the degree-day factor is not constant but follows a
seasonal sine between a winter minimum and a summer maximum, standing in for the
annual cycle of incoming solar radiation (:cite:t:`Braun1985`) without requiring
a radiation field:

.. math::

   a(t) = \frac{a_{\max} + a_{\min}}{2}
          + \frac{a_{\max} - a_{\min}}{2}
            \sin\!\left(\frac{2 \pi (d - 80)}{366}\right)

.. math::

   M(t) =
   \begin{cases}
       a(t) \cdot (T_a(t) - T_{melt}) & : T_a(t) > T_{melt} \\
       0 & : \text{otherwise}
   \end{cases}

where :math:`d` is the day of the year, so the factor is at its mean at the
spring equinox and peaks at the summer solstice. Because it derives from the
degree-day model, it works with the degree-day refreezing, which then uses the
current (seasonal) factor.

Parameters:

* ``a_snow_min`` (alias ``crmfmin``) *(mm/d/°C, no default, [0.5, 6])*

  - Winter minimum of the degree-day factor.
  - Full name: ``snowpack:degree_day_factor_min``.

* ``a_snow_max`` (alias ``crmfmax``) *(mm/d/°C, no default, [1.5, 12])*

  - Summer maximum of the degree-day factor.
  - Full name: ``snowpack:degree_day_factor_max``.

* ``melt_t_snow`` *(optional, °C, default: 0, [-3, 5])*

  - Melt temperature threshold.
  - Full name: ``snowpack:melting_temperature``.

On glacier covers the same process uses ``a_ice_min`` / ``a_ice_max``
(``<cover>:degree_day_factor_min`` / ``_max``).


.. _snow-water-retention:

Snowpack liquid water retention
-------------------------------

By default, melt water leaves the snowpack directly. The HBV snow routine
(:cite:t:`Bergstrom1976`, :cite:t:`Lindstrom1997`) instead retains liquid water
in the snowpack, releases only the excess over a holding capacity, and lets the
retained water refreeze during cold spells. This behaviour is enabled by the
``snow_water_retention_process`` and ``snow_refreezing_process`` options (it is
the default in :ref:`HBV-96 <hbv96>`); the melt process output is then kept in
the snowpack liquid water storage instead of leaving the snowpack.

In addition, the ``rain_to_snowpack`` option routes the rain onto the snowpack
liquid water storage instead of the land cover, as in the original HBV snow
routine. Rain falling on an existing snowpack is then retained (up to the
holding capacity) and exposed to refreezing; when there is no snow, the holding
capacity is zero and the rain passes through to the land cover within the same
time step. This option requires a snow water retention process.


Snow water holding capacity (``outflow:snow_holding``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Releases the liquid water exceeding the snowpack holding capacity, defined as a
fraction CWH of the snow water equivalent:

.. math::

   Q_{\mathrm{out}}(t) = \max\!\left(0,\; W(t) - CWH \cdot SWE(t)\right)

where :math:`W` is the liquid water content of the snowpack [mm] and
:math:`SWE` is the snow water equivalent [mm]. The excess is released within
the time step to the parent land cover. When the snowpack is melted away
(:math:`SWE = 0`), all the liquid water is released.

Parameters:

* ``cwh`` (alias ``whc``) *(optional, dimensionless, default: 0.1, [0, 0.2])*

  - Liquid water holding capacity, as a fraction of the SWE.
  - Full name: ``snowpack:water_holding_capacity``.


Degree-day refreezing (``refreeze:degree_day``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Refreezes the liquid water retained in the snowpack (transfer from the water
storage back to the snow storage) when the temperature drops below the melt
threshold:

.. math::

   R(t) =
   \begin{cases}
       CFR \cdot a_{\mathrm{snow}} \cdot (T_T - T_a(t)) & : T_a(t) < T_T \\
       0 & : T_a(t) \geq T_T
   \end{cases}

where :math:`CFR` is the refreezing coefficient [−], and :math:`a_{\mathrm{snow}}`
(degree-day factor) and :math:`T_T` (melt temperature threshold) are read from
the melt process of the same snowpack, so melt and refreezing stay consistent.
It therefore requires ``snow_melt_process='melt:degree_day'``.

Parameters:

* ``cfr`` *(optional, dimensionless, default: 0.05, [0, 0.1])*

  - Refreezing coefficient.
  - Full name: ``snowpack:refreezing_factor``.


.. _prevah-snow-release:

PREVAH snow water release (``outflow:snow_holding_prevah``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The snowpack liquid water release of :ref:`PREVAH-UniBE <prevah-unibe>`. On cold
days it behaves like ``outflow:snow_holding`` (retention up to
:math:`CWH \cdot SWE`), but on melting days (:math:`T_a > T_{melt}`) the
retention limit collapses to a fraction of the *liquid* content instead of the
snow water equivalent, so the pack flushes most of its retained water:

.. math::

   Q_{\mathrm{out}}(t) =
   \begin{cases}
       \max\!\left(0,\; W(t) - CWH \cdot SWE(t)\right) & : T_a(t) \leq T_{melt} \\
       (1 - CWH) \cdot W(t) + CWH \cdot \mathrm{at}_{sliq} \cdot M(t) & : T_a(t) > T_{melt}
   \end{cases}

On a melting day, :math:`W` is the liquid content after the melt :math:`M` of the
step has been added, and the graded release factor

.. math::

   \mathrm{at}_{sliq} = \min\!\left(1,\;
       \left(\frac{W(t) - M(t)}{CWH \cdot SWE(t)}\right)^{\!CEXLIQ}\right)

lets a growing share of the fresh melt pass straight through as the pack wets up
(PREVAH's CEXLIQ exponent). With the default :math:`CEXLIQ = 0` the factor is 1
and the release reduces to the plain collapse. In deep snowpacks the graded term
is usually negligible.

.. warning::

   Which branch applies is decided from the temperature of the *current step*, and the
   release empties the pack within that step. That is faithful to the formulation, but
   it makes the routine sensitive to the
   :ref:`computation time step <computation-time-step>` in a way the other snow
   processes are not. On a daily step the pack can flush at most once a day, and only
   if the daily mean exceeds the threshold. On an hourly step every warm hour flushes
   it, so a spring day averaging below the threshold but reaching a few degrees in the
   afternoon drains the pack, where the daily run would have held the water and let it
   refreeze overnight.

   The effect is real melt physics rather than a discretization error, but PREVAH's
   calibrated values (CWH, CEXLIQ and the threshold) were fitted to a daily
   application of the rule, so the seasonal timing of the meltwater shifts when the
   same set is run sub-daily with a real diurnal cycle. On the Ticino-Bellinzona
   catchment, an hourly run whose temperature swings 8 °C through the day around an
   unchanged daily mean moves 25 % more water through December to March, and 5.5 %
   less through the freshet of May to July, than the daily run does. What drives it is that
   16 % of the meteo-zone days there sit below the threshold on the daily mean yet rise
   above it for about eight hours.

Parameters:

* ``cwh`` (alias ``whc``) *(optional, dimensionless, default: 0.1, [0, 0.2])*

  - Liquid water holding capacity, as a fraction of the SWE.
  - Full name: ``snowpack:water_holding_capacity``.

* ``holding_melt_t`` *(optional, °C, default: 0, [-5, 5])*

  - Temperature above which the melting-day branch applies.
  - Full name: ``snowpack:melting_temperature``.

* ``cexliq`` *(optional, dimensionless, default: 0, [0, 5])*

  - Exponent of the graded release of the fresh melt.
  - Full name: ``snowpack:liquid_release_exponent``.


Seasonal degree-day refreezing (``refreeze:degree_day_seasonal``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The same refreezing law as ``refreeze:degree_day``, but with its *own* seasonal
degree-day factor and melt threshold instead of reading them from a degree-day
melt process on the same snowpack:

.. math::

   R(t) =
   \begin{cases}
       CFR \cdot a_{\mathrm{cfr}}(t) \cdot (T_T - T_a(t)) & : T_a(t) < T_T \\
       0 & : T_a(t) \geq T_T
   \end{cases}

where :math:`a_{\mathrm{cfr}}(t)` follows the same seasonal sine as the
:ref:`seasonal degree-day melt <melt-models>`. Being self-contained, it works
with any melt process — including ``melt:temperature_index``, which is the
combination used by PREVAH (radiation-corrected melt, seasonal refreezing).

Parameters:

* ``cfr`` *(optional, dimensionless, default: 0.05, [0, 0.1])*

  - Refreezing coefficient.
  - Full name: ``snowpack:refreezing_factor``.

* ``cfr_ddf_min`` *(optional, mm/d/°C, default: 2, [0, 12])*

  - Winter minimum of the refreezing degree-day factor.
  - Full name: ``snowpack:degree_day_factor_min``.

* ``cfr_ddf_max`` *(optional, mm/d/°C, default: 6, [0, 12])*

  - Summer maximum of the refreezing degree-day factor.
  - Full name: ``snowpack:degree_day_factor_max``.

* ``cfr_melt_t`` *(optional, °C, default: 0, [-5, 5])*

  - Temperature below which the retained water refreezes.
  - Full name: ``snowpack:melting_temperature``.


.. _snow-to-ice-transformation-process:

Snow-to-ice transformation
---------------------------

Converts snow accumulated on a glacier land cover into glacier ice (transfer
from the snow container to the ice container of the same brick). It is
important for melt-driven glacier evolution methods (delta-h or area
scaling, see :ref:`glacier-related options <glacier_options>`), which derive
glacier area from tracked ice volume: snow left unconverted at the end of the
accumulation season would otherwise understate the ice thickness. Selected
via the ``snow_ice_transformation`` model option, with the process key as its
value (``None`` disables the transformation, the default).

.. note::

   This is the underlying per-time-step transformation process. It is
   typically paired with the periodic
   :ref:`ActionGlacierSnowToIceTransformation <snow-to-ice-transformation>`
   action, which applies a one-off, end-of-season conversion of the remaining
   snowpack.


Constant-rate transformation (``transform:snow_ice_constant``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Converts snow to ice at a fixed rate whenever snow is present, capped by the
available snow water equivalent:

.. math::

   T(t) = r

where :math:`r` is a constant transformation rate [mm d⁻¹].

Parameters:

* ``snow_ice_transformation_rate`` *(mm d⁻¹, default: 0.5, [0, 10])*

  - Constant snow-to-ice transformation rate :math:`r`.
  - Full name: ``<glacier_component>_snowpack:snow_ice_transformation_rate``.


SWAT-based transformation (``transform:snow_ice_swat``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Scales the transformation rate by the current snow water equivalent and by a
seasonal factor derived from the day of year, following the SWAT model's
glacier accumulation routine:

.. math::

   T(t) = c \left(1 + \sin\!\left(\frac{2\pi (d(t) - d_{\mathrm{ref}})}{365}\right)\right) SWE(t)

where :math:`d(t)` is the day of year, :math:`d_{\mathrm{ref}}` is the day of
year of the start of the local astronomical spring (day 81, March 22, for the
northern hemisphere; day 264, September 21, for the southern hemisphere), and
:math:`c` is the basal accumulation coefficient. The seasonal factor swings
between 0 and 2 over the year, so the effective rate is highest roughly
half a year after :math:`d_{\mathrm{ref}}`.

Parameters:

* ``snow_ice_transformation_basal_acc_coeff`` *(optional, dimensionless, default: 0.0014, [0.001, 0.006])*

  - Basal accumulation coefficient :math:`c` [d⁻¹].
  - Full name: ``<glacier_component>_snowpack:snow_ice_transformation_basal_acc_coeff``.

* ``north_hemisphere`` *(optional, dimensionless, default: 1, [0, 1])*

  - Hemisphere flag: non-zero selects the northern-hemisphere reference day
    (81), zero selects the southern-hemisphere one (264).
  - Full name: ``<glacier_component>_snowpack:north_hemisphere``.


.. _snow-sublimation:

Snow sublimation
----------------

By default, snow leaves a snowpack only as melt water or through lateral
redistribution. In cold, dry, high-radiation or windy environments, however, a
sizeable share of the snow water equivalent is lost directly to the atmosphere by
sublimation — from 0.1 % up to 90 % of snowfall depending on site and weather,
and of the order of 30 % of the annual snow water equivalent in some semiarid
mountains (:cite:t:`Strasser2008`, :cite:t:`Herrero2016`). The optional
``snow_sublimation_process`` model option adds a process on each snowpack that
removes snow water equivalent straight to the atmosphere (the solid-phase analog
of evapotranspiration; it is therefore accounted for as an atmospheric loss in
the water balance).

Valid values for ``snow_sublimation_process``: ``"sublimation:constant"``,
``"sublimation:pet"``, ``"sublimation:prevah"`` (default: ``None``, i.e. no
sublimation).

.. code-block:: python

   socont = Socont(
      snow_sublimation_process="sublimation:pet"
   )

.. note::

   Sublimation is not gated by air temperature the way melt is: it is driven by
   the vapor-pressure deficit, wind and net radiation, and often peaks below 0 °C. 
   The ``sublimation:pet`` option is preferable when the potential evapotranspiration
   is computed from a demand-based method (which already reflects radiation and
   atmospheric humidity); ``sublimation:constant`` is a crude first-order fallback.


Constant-rate sublimation (``sublimation:constant``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Removes snow at a fixed rate whenever snow is present:

.. math::

   S(t) = S_0

where :math:`S_0` is a constant sublimation rate [mm d⁻¹]. The simplest
possible parameterisation (no forcing dependency), a first-order approximation of
the near-steady mean daily surface-sublimation rates reported from field
measurements in mountain snowpacks (:cite:t:`Strasser2008`, :cite:t:`Herrero2016`).

Parameters:

* ``sublimation_rate`` *(optional, [mm d⁻¹], default: 0.1, [0, 2])*

  - Constant sublimation rate.
  - Full name: ``snowpack:sublimation_rate``.


PET-fraction sublimation (``sublimation:pet``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Treats snow sublimation as the cold-surface analog of evaporation, driven by
atmospheric demand ("evapo-sublimation", :cite:t:`Herrero2016`): a fixed fraction
of the potential evapotranspiration is removed from the snowpack:

.. math::

   S(t) = c_S \cdot E_P(t)

where :math:`c_S` is a dimensionless fraction and :math:`E_P` the potential
evapotranspiration [mm d⁻¹]. Requires the ``pet`` forcing.

Parameters:

* ``sublimation_pet_factor`` *(optional, dimensionless, default: 0.2, [0, 1])*

  - Fraction of PET removed as sublimation.
  - Full name: ``snowpack:sublimation_pet_factor``.


PREVAH snow evaporation (``sublimation:prevah``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The snow evaporation of :ref:`PREVAH-UniBE <prevah-unibe>`. Snow evaporates at
the potential rate reduced by the albedo of the snow surface, the reduction
being the ratio of the energy actually absorbed to that absorbed by the
reference surface of the PET formula (albedo 0.2):

.. math::

   S(t) = \frac{1 - \alpha_{\mathrm{snow}}(t)}{0.8} \cdot E_P(t)

The snow albedo is age-dependent (:cite:t:`Rohrer1994`): it is reset by every
snowfall and decays with the age :math:`n` of the surface layer, in days,

.. math::

   \alpha_{\mathrm{snow}}(t) = 0.4 + 0.45 \, e^{-0.15 \, n}

from about 0.85 on fresh snow (little evaporation) down to 0.4 on old snow (a
reduction factor of 0.75). The process has no calibrated parameter; it requires
the ``pet`` forcing. Unlike ``sublimation:pet``, it is served *before* the melt
on the snowpack, as in PREVAH, so it keeps the full potential rate on days when
the melt would otherwise drain the pack.


.. _snow-redistribution-processes:

Snow redistribution
--------------------

Without redistribution, elevation-band models can accumulate unrealistic amounts
of snow at high elevations ("snow towers"). The optional
``snow_redistribution`` model option adds a lateral process that moves excess
snow water equivalent (SWE) downslope, from each hydro unit to its
lower-elevation neighbours, following a connectivity graph (see
:ref:`Catchment connectivity <catchment-connectivity>`). Both methods redistribute
only *excess* snow above a holding capacity, and cap the amount transported per
time step to 1000 mm SWE to avoid unrealistic single-step transfers; the
target's own accumulation is separately capped by ``max_snow_depth``.

Valid values for ``snow_redistribution``: ``"transport:snow_slide"``,
``"transport:snow_redistribution_frey"``,
``"transport:snow_redistribution_frey_dynamic"`` (default: ``None``, i.e. no
redistribution).

.. code-block:: python

   socont = Socont(
      snow_redistribution="transport:snow_slide"
   )


SnowSlide (``transport:snow_slide``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implements the SnowSlide algorithm (:cite:t:`Bernhardt2010`): snow exceeding a
slope-dependent holding capacity slides downslope. The holding capacity
decreases with slope (steeper terrain holds less snow):

.. math::

   h_{\mathrm{hold}} = \mathrm{coeff} \cdot \theta^{\mathrm{exp}}

where :math:`\theta` is the slope in degrees (clamped to ``min_slope`` from
below), converted from metres to a SWE threshold via a fixed snow density. Above
``max_slope``, the holding capacity is set directly to
``min_snow_holding_depth`` instead of following the equation. The excess SWE
above the holding capacity is redistributed to the downslope neighbours.

Parameters:

* ``snow_slide_coeff`` *(optional, dimensionless, default: 3178.4, [0, 10000])*

  - Coefficient in the holding-depth equation.
  - Full name: ``<snowpack>:coeff``.

* ``snow_slide_exp`` *(optional, dimensionless, default: -1.998, [-5, 0])*

  - Exponent in the holding-depth equation.
  - Full name: ``<snowpack>:exp``.

* ``snow_slide_min_slope`` *(optional, °, default: 10, [0, 45])*

  - Minimum slope used in the holding-depth calculation; units with a lower
    slope are treated as having this minimum.
  - Full name: ``<snowpack>:min_slope``.

* ``snow_slide_max_slope`` *(optional, °, default: 75, [45, 90])*

  - Slope above which ``min_snow_holding_depth`` is applied directly, instead
    of the equation.
  - Full name: ``<snowpack>:max_slope``.

* ``snow_slide_min_snow_depth`` *(optional, mm, default: 50, [0, 1000])*

  - Minimum snow holding depth, used as a floor on the equation's result and
    directly above ``max_slope``.
  - Full name: ``<snowpack>:min_snow_holding_depth``.

* ``snow_slide_max_snow_depth`` *(optional, mm, default: 20000, [-1, 50000])*

  - Maximum snow depth allowed to accumulate in a receiving unit (extension to
    the original method). Set to ``-1`` for no limit.
  - Full name: ``<snowpack>:max_snow_depth``.


Frey & Holzmann redistribution (``transport:snow_redistribution_frey``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implements the conceptual model of :cite:t:`Frey2015`: snow above a
land-cover-specific holding capacity is redistributed, scaled by a
distribution coefficient that increases with slope and decreases with snow
density, and by a calibratable correction coefficient:

.. math::

   f_\rho = \frac{\rho_{\max} - \rho}{\rho_{\max}} \, e^{-\rho/\rho_{\max}} \, \frac{\theta}{90},
   \qquad
   \mathrm{redistributed} = \max(SWE - SWE_{\mathrm{hold}},\, 0) \cdot f_\rho \cdot C

where :math:`\rho` is the snow density (a constant parameter in this variant)
and :math:`\theta` is the slope in degrees; :math:`f_\rho = 0` once
:math:`\rho \geq \rho_{\max}` or on flat terrain. The holding capacity
:math:`SWE_{\mathrm{hold}}` is given as a snow depth [mm] and converted to SWE
using the same density :math:`\rho`.

Parameters:

* ``snow_redist_frey_c`` *(optional, dimensionless, default: 1.0, [0, 10])*

  - Correction coefficient :math:`C`.
  - Full name: ``<snowpack>:correction``.

* ``snow_redist_frey_holding_capacity`` *(optional, mm, default: 200, [0, 5000])*

  - Land-cover snow holding capacity :math:`H_v` (snow depth).
  - Full name: ``<snowpack>:snow_holding_capacity``.

* ``snow_redist_frey_rho_max`` *(optional, kg/m³, default: 450, [200, 600])*

  - Maximum snow density :math:`\rho_{\max}`: at or above it, snow no longer
    redistributes.
  - Full name: ``<snowpack>:rho_max``.

* ``snow_redist_frey_snow_density`` *(optional, kg/m³, default: 250, [50, 600])*

  - Constant snow density :math:`\rho`, used for the SWE/depth conversion and
    in :math:`f_\rho`.
  - Full name: ``<snowpack>:snow_density``.

* ``snow_redist_frey_max_snow_depth`` *(optional, mm, default: 20000, [-1, 50000])*

  - Maximum snow depth allowed to accumulate in a receiving unit. Set to
    ``-1`` for no limit.
  - Full name: ``<snowpack>:max_snow_depth``.


Frey & Holzmann redistribution, dynamic density (``transport:snow_redistribution_frey_dynamic``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The same method as above, but the snow density :math:`\rho` evolves over time
instead of staying constant, so drier (less-settled) snow is more mobile.
Requires the ``temperature`` forcing.

At each time step, the tracked density settles toward :math:`\rho_{\max}` at a
fixed rate, and freshly-added SWE (from snowfall or from redistribution
received from other units) is mixed in at a temperature-dependent fresh-snow
density:

.. math::

   \rho_{\mathrm{fresh}} = \rho_{\min} + \left(\rho_{\mathrm{fresh,max}} - \rho_{\min}\right)
   \frac{1 + \tanh_\sigma(T_a)}{2}

where :math:`\tanh_\sigma` is a sigmoid of the air temperature :math:`T_a`,
shaped by ``rho_scale`` and ``t_scale``: colder air yields a fresh-snow density
near :math:`\rho_{\min}`, warmer air near :math:`\rho_{\mathrm{fresh,max}}`.

Parameters: ``snow_redist_frey_dyn_c``, ``snow_redist_frey_dyn_holding_capacity``,
``snow_redist_frey_dyn_rho_max`` and ``snow_redist_frey_dyn_max_snow_depth`` as for
:ref:`transport:snow_redistribution_frey <snow-redistribution-processes>` above
(with the ``_dyn_`` aliases in place of the static-density ones), plus:

* ``snow_redist_frey_dyn_rho_min`` *(optional, kg/m³, default: 100, [50, 300])*

  - Minimum fresh-snow density (coldest end of the sigmoid).
  - Full name: ``<snowpack>:rho_min``.

* ``snow_redist_frey_dyn_rho_fresh_max`` *(optional, kg/m³, default: 300, [100, 500])*

  - Maximum fresh-snow density (warmest end of the sigmoid).
  - Full name: ``<snowpack>:rho_fresh_max``.

* ``snow_redist_frey_dyn_rho_settling`` *(optional, 1/day, default: 0.1, [0, 1])*

  - Rate at which the tracked density settles toward :math:`\rho_{\max}`.
  - Full name: ``<snowpack>:rho_settling``.

* ``snow_redist_frey_dyn_rho_scale`` *(optional, dimensionless, default: 1.2, [0.1, 10])*

  - Slope of the temperature-to-fresh-density sigmoid.
  - Full name: ``<snowpack>:rho_scale``.

* ``snow_redist_frey_dyn_t_scale`` *(optional, °C, default: 1.0, [-5, 5])*

  - Shift of the temperature-to-fresh-density sigmoid.
  - Full name: ``<snowpack>:t_scale``.

Both methods require a slope property on the hydro units and a connectivity
CSV file describing the downslope pathways between hydro units:

.. code-block:: python

   hydro_units.set_connectivity('/path/to/connectivity.csv')


.. _interception:

Interception
------------

GR4J interception (``interception:gr4j``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implements the GR4J zero-capacity interception store (:cite:t:`Perrin2003`), 
which neutralises precipitation against PET before either reaches a store. 
With total precipitation :math:`P` (rain plus snowmelt) and potential 
evapotranspiration :math:`E_P`:

* if :math:`P > E_P`, the amount :math:`E_P` is sent to the atmosphere, the net
  precipitation :math:`P_n = P - E_P` is passed on, and the net evaporative
  demand is :math:`E_n = 0`;
* if :math:`P \le E_P`, the amount :math:`P` is sent to the atmosphere and the
  net evaporative demand :math:`E_n = E_P - P` is published for the downstream
  production-store ET.

The remaining net precipitation :math:`P_n` is then routed to the production
store by an :ref:`outflow:rest <outflow-processes>` (throughfall) process.
Requires the ``pet`` forcing; no calibrated parameters.


Menzel canopy interception (``interception:menzel``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The throughfall process of a canopy interception store, following
:cite:t:`Menzel1997` and used by :ref:`PREVAH-UniBE <prevah-unibe>`. The canopy
fills asymptotically toward its capacity instead of filling completely before
spilling: part of the rain always passes through, and the retained share shrinks
as the store fills. Over a time step receiving a rain depth :math:`P`, the
storage grows from :math:`SI_A` to

.. math::

   SI = SI_A + (SI_{\max} - SI_A)\left(1 - e^{-P / SI_{\max}}\right)

and the remainder :math:`P - (SI - SI_A)` is passed on as throughfall. The store
is emptied by the canopy evaporation process (see
:ref:`evapotranspiration <evapotranspiration>`).

It is a drop-in replacement for the fill-then-spill ``outflow:threshold`` store
and is selected with the ``canopy_interception_process`` option.

Parameters:

* ``ic`` *(optional, mm, default: 2, [0, 10])*

  - Interception capacity :math:`SI_{\max}`. In PREVAH it varies monthly with
    the vegetation (:math:`si_{\max} \cdot veg_{cov}`); it can be set month by
    month with :ref:`monthly parameters <monthly-parameters>`.
  - Full name: ``<cover>_canopy:capacity``.


.. _evapotranspiration:

Evapotranspiration
------------------

Several ET formulations are available. They all convert the potential
evapotranspiration (``pet`` forcing) into actual ET by reducing it as a function
of the storage filling ratio :math:`S(t)/S_{\max}`; they differ only in the shape
of that reduction. The generic ``et:linear``, ``et:power_law`` and
``et:exponential`` reductions can be attached to any storage brick that has a
maximum capacity.


Socont ET (``et:socont``)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Used in :ref:`GSM-Socont <gsm-socont>`. Actual ET is proportional to PET, scaled
by the filling ratio of the reservoir with a square-root exponent (:cite:t:`Schaefli2005`):

.. math::

   E(t) = E_P(t) \left(\frac{S(t)}{S_{\max}}\right)^{0.5}

where:

- :math:`E_P(t)` is the potential evapotranspiration [mm d⁻¹],
- :math:`S(t)` is the current water content of the reservoir [mm],
- :math:`S_{\max}` is the maximum storage capacity [mm].

ET decreases as the reservoir empties; it equals PET when the reservoir is full.
No calibrated parameters. Requires the ``pet`` forcing.


GR4J ET (``et:gr4j``)
^^^^^^^^^^^^^^^^^^^^^

Used internally by :ref:`GR4J <gr4j>`. Withdraws actual evapotranspiration from
the production store to the atmosphere, using the net evaporative demand
:math:`E_n` published by the interception step (:cite:t:`Perrin2003`):

.. math::

   E_s = S \cdot \frac{2 - S/X_1}{1 + (1 - S/X_1) \tanh(E_n/X_1)} \tanh(E_n/X_1)

where :math:`X_1` is the production store capacity and :math:`S` is the store
content after this step's infiltration. No calibrated parameters beyond
:math:`X_1`.


HBV ET (``et:hbv``)
^^^^^^^^^^^^^^^^^^^

Used in :ref:`HBV-96 <hbv96>`. Actual ET is withdrawn from the soil moisture
storage at the (corrected) potential rate when the soil moisture exceeds a
threshold, and decreases linearly below it (:cite:t:`Lindstrom1997`):

.. math::

   E(t) = \mathrm{cevpf} \cdot E_P(t) \cdot \min\!\left(1,\; \frac{SM(t)}{LP \cdot FC}\right)

where:

- :math:`E_P(t)` is the potential evapotranspiration [mm d⁻¹],
- :math:`\mathrm{cevpf}` is the evapotranspiration correction factor [−],
- :math:`SM(t)` is the current soil moisture [mm],
- :math:`FC` is the soil moisture storage capacity [mm],
- :math:`LP` is the fraction of :math:`FC` above which ET reaches the
  potential rate [−].

Requires the ``pet`` forcing.

Parameters:

* ``lp`` *(dimensionless, default: 0.9, [0.3, 1])*

  - ET reduction threshold, as a fraction of :math:`FC`.
  - Full name: ``soil_moisture:lp``.

* ``cevpf`` *(optional, dimensionless, default: 1, [0.5, 2])*

  - Evapotranspiration correction factor, scaling the potential evaporation. Set it
    per cover (e.g. higher for forests) to vary the evaporation by land cover.
  - Full name: ``soil_moisture:et_correction_factor``.


Linear ET (``et:linear``)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Generic parameter-free reduction. Actual ET increases linearly with the filling
ratio and reaches PET when the reservoir is full:

.. math::

   E(t) = E_P(t) \cdot \min\!\left(1,\; \frac{S(t)}{S_{\max}}\right)

where:

- :math:`E_P(t)` is the potential evapotranspiration [mm d⁻¹],
- :math:`S(t)` is the current water content of the reservoir [mm],
- :math:`S_{\max}` is the maximum storage capacity [mm].

No calibrated parameters. Requires the ``pet`` forcing.


Power-law ET (``et:power_law``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generalization of the Socont ET with a calibratable exponent. Actual ET scales
with the filling ratio raised to the ``exponent`` power:

.. math::

   E(t) = E_P(t) \left(\frac{S(t)}{S_{\max}}\right)^{\beta}

where :math:`\beta` is the exponent. It recovers the linear reduction at
:math:`\beta = 1`, the Socont ET at :math:`\beta = 0.5`, and gives convex
(:math:`\beta > 1`) or concave (:math:`\beta < 1`) reductions otherwise.
Requires the ``pet`` forcing.

Parameters:

* ``exponent`` *(dimensionless, default: 0.5, [0.2, 3])*

  - Exponent applied to the filling ratio. Alias: ``et_beta``.


Exponential ET (``et:exponential``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Concave, asymptotic reduction. Actual ET rises steeply when the store is wet and
saturates toward PET as it fills:

.. math::

   E(t) = E_P(t) \left(1 - \exp\!\left(-\alpha \, \frac{S(t)}{S_{\max}}\right)\right)

where :math:`\alpha` controls the curvature: a larger :math:`\alpha` makes ET
approach PET faster as the reservoir fills. Requires the ``pet`` forcing.

Parameters:

* ``alpha`` *(dimensionless, default: 2, [0.5, 10])*

  - Curvature of the reduction curve. Alias: ``et_alpha``.


PREVAH soil ET (``et:prevah``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The HBV soil-moisture limitation of ``et:hbv``, with the albedo reduction of the
potential rate applied by :ref:`PREVAH-UniBE <prevah-unibe>`:

.. math::

   E_a(t) = c_{\mathrm{evpf}} \cdot \frac{1 - \alpha(t)}{0.8} \cdot E_P(t)
            \cdot \min\!\left(1,\; \frac{SM(t)}{LP \cdot FC}\right)

The albedo :math:`\alpha` is the area-weighted mean, over the hydro unit, of the
snow-free ground albedo (``albedo_land``) and the age-dependent snow albedo of
the unit's snowpacks (see ``sublimation:prevah`` above), weighted by the
snow-covered fraction. It is therefore neutral (a factor of 1) when the unit is
snow-free at the default ``albedo_land`` = 0.2, and strongly reduces the soil ET
under snow.

The albedo belongs to the potential rate of the unit, not to any single flux:
PREVAH computes one PET per hydrotope from the albedo of whatever surface the
sun sees, and the interception store, the snowpack and the soil then all draw
on that same reduced rate. The snow evaporation of ``sublimation:prevah`` is
served from the snowpack, but the soil ET is damped under snow all the same —
that damping is PREVAH's only suppression of the soil ET under a snow cover.

A soil store of its own (``share_soil=False``) belongs to a single land cover,
and then reads that cover alone: the albedo is the snow albedo while the cover
holds snow and ``albedo_land`` otherwise, as in a PREVAH hydrotope, so snow
lying on a neighbouring cover no longer damps its evapotranspiration. A shared
store spans several covers and keeps the mean over the unit.

Parameters:

* ``lp`` (alias ``cu``) *(dimensionless, default: 0.9, [0.3, 1])*

  - Fraction of ``fc`` above which the ET reaches the potential rate.
  - Full name: ``soil_moisture:lp``.

* ``albedo_land`` *(optional, dimensionless, default: 0.2, [0, 0.4])*

  - Albedo of the snow-free ground; 0.2 makes the reduction neutral.
  - Full name: ``soil_moisture:albedo_land``.

* ``cevpf`` *(optional, dimensionless, default: 1, [0.5, 2])*

  - Evapotranspiration correction factor.
  - Full name: ``soil_moisture:et_correction_factor``.


PREVAH open-water ET (``et:open_water_prevah``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The open-water evaporation with the same albedo reduction, scaled by a factor
and capped at the content available over the time step:

.. math::

   E_a(t) = \min\!\left(f_{ET} \cdot \frac{1 - \alpha(t)}{0.8} \cdot E_P(t),\;
                        \frac{S(t)}{\Delta t}\right)

:ref:`PREVAH-UniBE <prevah-unibe>` uses it for the canopy interception
evaporation (option ``canopy_et_process``), where :math:`f_{ET}` is the vegetation
cover fraction ``veg_cov`` of the interception module and is typically set monthly.

Parameters:

* ``ow_et_factor`` (``canopy_et_factor`` on a canopy) *(optional,
  dimensionless, default: 1, [0, 1.5])*

  - Fraction of the albedo-reduced potential rate that is evaporated.
  - Full name: ``<component>:et_factor``.

* ``ow_albedo_land`` *(optional, dimensionless, default: 0.2, [0, 0.4])*

  - Albedo of the snow-free ground.
  - Full name: ``<component>:albedo_land``.


.. _et-wet-surface-prevah:

PREVAH wet-surface ET (``et:wet_surface_prevah``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PREVAH evaporates its wet surfaces — the share of a hydrotope that is water or
saturated — from the groundwater, at the potential rate times that share. The process
draws from a groundwater store (SLZ1 in :ref:`PREVAH-UniBE <prevah-unibe>`, option
``wet_et_from_groundwater``) and reads the wet share of the hydro unit from its wetland
land covers, declared as the process *gates*: each contributes its area fraction
:math:`f_c` times its wet fraction :math:`w_c`, the split fraction of the
``outflow:split`` process that routes its input to the groundwater:

.. math::

   E_a(t) = \min\!\left(f_{ET} \cdot \sum_c f_c(t)\, w_c \cdot
                        \frac{1 - \alpha(t)}{0.8} \cdot E_P(t),\;
                        \frac{S(t)}{\Delta t}\right)

with the albedo :math:`\alpha(t)` of the ``et:open_water_prevah`` process above. The
same share thus routes the wetland input to the groundwater and evaporates from it, as
PREVAH's ``wet_surface`` does for both (0.7 on wetlands). A unit without wetland area
evaporates nothing, the rate follows a calibrated ``wet_fraction``, and it tracks the
land cover changes.

Parameters:

* ``wet_et_factor`` *(optional, dimensionless, default: 1, [0, 1.5])*

  - Overall scaling of the wet-surface evaporation.
  - Full name: ``<component>:et_factor``.

* ``wet_albedo_land`` *(optional, dimensionless, default: 0.2, [0, 0.4])*

  - Albedo of the snow-free ground.
  - Full name: ``<component>:albedo_land``.


.. _infiltration-processes:

Infiltration
------------

Socont infiltration (``infiltration:socont``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used in :ref:`GSM-Socont <gsm-socont>` for the open (soil) land cover. Water
infiltrates into the slow reservoir at a rate that decreases quadratically as
the reservoir fills (:cite:t:`Schaefli2005`):

.. math::

   \mathrm{Inf}(t) = S(t) \left(1 - \left(\frac{S(t)}{S_{\max}}\right)^2\right)

where :math:`S(t)` is the current water content and :math:`S_{\max}` is the
maximum capacity. When the reservoir is empty, all incoming water infiltrates;
when full, infiltration is zero and the remainder becomes surface runoff. No
calibrated parameters.

GR4J infiltration (``infiltration:gr4j``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Computes the portion :math:`P_s` of net precipitation :math:`P_n` that enters the
GR4J production store (:cite:t:`Perrin2003`). In the GR4J model this infiltration
term is not applied on its own but as part of the combined
:ref:`production:gr4j <gr4j-production>` step:

.. math::

   P_s = X_1 \left(1 - \left(\frac{S}{X_1}\right)^{\!2}\right)
         \frac{\tanh\!\left(\dfrac{P_n}{X_1}\right)}
              {1 + \dfrac{S}{X_1}\,\tanh\!\left(\dfrac{P_n}{X_1}\right)}

where :math:`X_1` is the production store capacity and :math:`S` is its current
water content. The rate increases with :math:`P_n` and decreases as the store
fills, going to zero when :math:`S = X_1`. No calibrated parameters.


HBV infiltration / beta function (``infiltration:hbv``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used in :ref:`HBV-96 <hbv96>` on each soil-bearing land cover (e.g. open, forest).
The incoming water :math:`P` (rain and snowpack outflow) is split between the soil
moisture
storage and the response routine using the HBV beta function
(:cite:t:`Lindstrom1997`). The infiltrating part is

.. math::

   \mathrm{Inf}(t) = P(t) \left(1 - \left(\frac{SM(t)}{FC}\right)^{\beta}\right)

and the complement, the recharge :math:`P \cdot (SM/FC)^{\beta}`, is routed to
the upper zone by an :ref:`outflow:rest <outflow-processes>` process. When the
soil is dry, all the water infiltrates; when it is at capacity, all the water
becomes recharge.

Parameters:

* ``beta`` *(dimensionless, default: 2, [1, 6])*

  - Shape coefficient of the beta function.
  - Full name: ``open:beta`` (``<cover>:beta`` in general).


.. _percolation-processes:

Percolation
-----------

Constant percolation (``percolation:constant``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Drains water from one reservoir to another at a fixed rate, independent of
storage:

.. math::

   \mathrm{Perc}(t) = r

where :math:`r` is the percolation rate [mm d⁻¹]. Used in
:ref:`GSM-Socont <gsm-socont>` when ``soil_storage_nb=2`` to connect the first
slow reservoir to the baseflow reservoir, and in :ref:`HBV-96 <hbv96>` (PERC)
to connect the upper zone to the lower zone.

Parameters:

* ``percol`` (alias for ``percolation_rate``): constant drainage rate [mm d⁻¹],
  range [0, 10]. Full name: ``slow_reservoir:percolation_rate`` /
  ``upper_zone:percolation_rate`` (alias ``perc``).

GR4J percolation (``percolation:gr4j``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Drains water from the GR4J production store (:cite:t:`Perrin2003`):

.. math::

   \mathrm{Perc} = S \left[1 - \left(1 + \left(\frac{4S}{9\,X_1}\right)^{\!4}\right)^{\!-1/4}\right]

where :math:`S` is the current production-store water content and :math:`X_1` is
its capacity. Percolation increases non-linearly with the filling ratio and goes
to zero when the store is empty. In the GR4J model it is applied as part of the
combined :ref:`production:gr4j <gr4j-production>` step. No calibrated parameters.


PREVAH percolation (``percolation:prevah``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deep percolation of :ref:`PREVAH-UniBE <prevah-unibe>`: a maximum rate gated
by the wetness of the *soil moisture* store, so that nothing percolates from a
dry soil and the full rate is only reached at saturation:

.. math::

   \mathrm{Perc}(t) =
   \begin{cases}
       r & SM(t) \ge FC \\[1ex]
       r \cdot k_w \cdot \dfrac{SM(t)/FC - cu}{1 - cu} & cu \cdot FC < SM(t) < FC \\[2ex]
       0 & SM(t) \le cu \cdot FC
   \end{cases}

where :math:`SM/FC` is the filling ratio of the soil moisture store,
:math:`cu` the fraction below which percolation stops and :math:`k_w` PREVAH's
hydraulic-conductivity factor KWPER, which scales the ramp but, as in the
original, not the rate at saturation. The store that is read is
not the one the process drains: the percolation leaves the upper zone while the
gating state is the soil moisture. This is expressed with the ``gate`` key of a
structure (see :ref:`custom structures <custom-structures>`), which points a
process at a brick that does not receive its flux.

The ``gate`` key also accepts a list of bricks, for a model carrying one soil
moisture store per land cover. The contents and the capacities are then summed
before the ratio is taken, which gives the area-weighted mean saturation of the
hydro unit. A per-cover store is fed by its land cover, whose outgoing fluxes
already carry the cover area fraction, and its capacity is scaled by that same
fraction (the ``area_of`` key), so both are expressed over the whole unit. A cover
with no area in a unit adds neither content nor capacity there and does not affect
the gate.

PREVAH also has a constant branch: a hydrotope percolates at :math:`r \cdot k_w`
whatever its soil moisture when its ET limit is at least its capacity. The ET limit
is taken from the soil map before the land cover forces the capacity, so this
happens on built-up and rock hydrotopes whose soil promises more than their fixed
5 mm or 3 mm. The branch is off under snow (more than 0.1 mm SWE), where the ET limit
above the capacity then stops the percolation altogether. ``perc_const`` is the
share of the unit following it, and the snowpacks listed among the gate bricks tell
its snow-covered part. Both :math:`k_w` and ``perc_const`` vary per unit (and
``perc_const`` per month, with the rooting depth):
``PrevahUniBE.apply_cover_percolation`` sets them from the soil and the cover class,
and ``PrevahUniBE.conductivity_factor`` computes KWPER from a soil conductivity as
xPREVAH does, including its guard that sets it to 1 everywhere as soon as one
hydrotope has no conductivity.

Parameters:

* ``cperc`` *(mm/d, default: 0.1, [0, 10])*

  - Maximum percolation rate.
  - Full name: ``upper_zone:percolation_rate``.

* ``cu_perc`` *(optional, dimensionless, default: 0.7, [0, 0.9])*

  - Soil moisture fraction below which the percolation stops. PREVAH uses the
    same value as the ET limit ``cu``; set both alike for a strict PREVAH
    behaviour.
  - Full name: ``upper_zone:threshold_fraction``.

* ``kwper`` *(optional, dimensionless, default: 1, [0, 10])*

  - Hydraulic-conductivity factor of the percolation (PREVAH's KWPER), usually
    per unit.
  - Full name: ``upper_zone:conductivity_factor``.

* ``perc_const`` *(optional, dimensionless, default: 0, [0, 1])*

  - Share of the unit percolating at the constant rate, usually per unit and
    per month.
  - Full name: ``upper_zone:constant_fraction``.


.. _capillary-processes:

Capillary flux
--------------

HBV capillary transport (``capillary:hbv``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used in :ref:`HBV-96 <hbv96>`. Returns water from the upper zone to the soil
moisture storage, at a rate that increases with the soil moisture deficit
(:cite:t:`Lindstrom1997`):

.. math::

   C(t) = CFLUX \cdot \left(1 - \frac{SM(t)}{FC}\right)

where :math:`CFLUX` is the maximum capillary flux [mm d⁻¹], :math:`SM` is the
soil moisture [mm] and :math:`FC` its capacity [mm]. The flux vanishes when the
soil is at capacity. It is disabled by default (:math:`CFLUX = 0`).

Parameters:

* ``cflux`` *(optional, mm/d, default: 0, [0, 3])*

  - Maximum capillary flux.
  - Full name: ``upper_zone:max_capillary_flux``.


.. _production:

Production
----------

.. _gr4j-production:
   
GR4J production (``production:gr4j``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used internally by :ref:`GR4J <gr4j>`. Applies the complete production-store
update in a single discrete step and routes its output to the unit-hydrograph
input (:cite:t:`Perrin2003`). For a start-of-step store level :math:`S` and net
precipitation :math:`P_n`:

#. **Infiltration** :math:`P_s` fills the store (see :ref:`infiltration:gr4j
   <infiltration-processes>`), raising the level to :math:`S + P_s`.
#. **Evapotranspiration** :math:`E_s` is withdrawn separately by the
   :ref:`et:gr4j <evapotranspiration>` process and sent to the atmosphere.
#. **Percolation** :math:`\mathrm{Perc}` drains the store (see
   :ref:`percolation:gr4j <percolation-processes>`).

The water routed to the unit-hydrograph input is

.. math::

   P_R = (P_n - P_s) + \mathrm{Perc}

i.e. the net precipitation that did not infiltrate plus the percolation leaving
the store. Because GR4J is solved as a discrete model, the production store is
computed directly (no ODE solver), so the per-step update is exact and
solver-independent. No calibrated parameters beyond :math:`X_1`.


.. _runoff-processes:

Surface runoff / Quick flow
---------------------------

Two formulations control how water leaves the surface runoff storage
in :ref:`GSM-Socont <gsm-socont>`. The choice is made via the ``surface_runoff``
option at model instantiation.


Socont runoff (``runoff:socont``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default (``surface_runoff="socont_runoff"``). Models overland flow on an
inclined plane with a linearly varying water depth, following Manning's equation
(:cite:t:`Schaefli2005`):

.. math::

   q = \beta \sqrt{\tan J} \; h^{5/3}

where:

- :math:`\beta` is a runoff coefficient [m\ :sup:`4/3` s\ :sup:`-1`] that
  absorbs Manning's roughness and the plane width,
- :math:`J` is the mean terrain slope [°]; internally converted to m m\ :sup:`-1` via
  :math:`\tan J`,
- :math:`h` is the water depth at the downslope end of the plane [m].

Parameters:

* ``beta``: runoff coefficient [m\ :sup:`4/3` s\ :sup:`-1`], range [100, 30 000].
  Full name: ``surface_runoff:runoff_coefficient``.
* ``J``: mean terrain slope [°], range [0, 90]. Derived from terrain data; not a
  calibration parameter. Full name: ``surface_runoff:slope``.

It is the original Socont parameterisation.


Linear storage runoff (``outflow:linear``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alternative (``surface_runoff="linear_storage"``). Replaces the Manning-based
formulation with a simple linear reservoir:

.. math::

   Q_{\mathrm{quick}}(t) = k_{\mathrm{quick}} \cdot S(t)

Parameters:

* ``k_quick``: response factor [d\ :sup:`-1`], range [0.05, 1].
  Full name: ``surface_runoff:response_factor``.

Use this formulation when a simpler quick-flow representation is preferred.


.. _outflow-processes:

Reservoir outflow
-----------------

The following outflow mechanisms are used by storage bricks across all models.

**Linear outflow** (``outflow:linear``)
   The most common outflow type. Outflow is proportional to the current storage:

   .. math::

      Q(t) = k \cdot S(t)

   Parameter: ``response_factor`` [d\ :sup:`-1`]. Used for the slow reservoirs, glacier
   area storages, the linear quick-flow option, and the HBV-96 lower zone
   (``k_lz``).

**Non-linear outflow** (``runoff:hbv``)
   The :ref:`HBV-96 <hbv96>` upper zone outflow (:cite:t:`Lindstrom1997`).
   Outflow increases non-linearly with the current storage:

   .. math::

      Q_0(t) = k_{uz} \cdot UZ(t)^{\,1+\alpha}

   where :math:`UZ` is the upper zone content [mm]. With :math:`\alpha = 0` it
   reduces to a linear reservoir. Parameters: ``k_uz`` (``response_factor``)
   [mm\ :sup:`-α` d\ :sup:`-1`], range [0.0001, 1], and ``alpha`` (alias
   ``alfa``) [−], default 1, range [0, 3]. Full names:
   ``upper_zone:response_factor``, ``upper_zone:alpha``.

**Overflow** (``outflow:overflow``)
   Releases water instantaneously when storage exceeds its maximum capacity.
   No parameters. Used to prevent the slow reservoir from overfilling.

**Direct outflow** (``outflow:direct``)
   Routes the entire storage content to the target in a single time step.
   No parameters. Used internally in :ref:`GSM-Socont <gsm-socont>` to pass
   glacier meltwater directly to the basin-level lumped storages. Because it
   withdraws the full content, it cannot run in parallel with any other process
   drawing from the same storage; configuration validation rejects such a
   combination (use ``outflow:rest`` instead when several outflows must share a
   store).

**Rest outflow** (``outflow:rest``)
   Routes whatever water remains in the store after all the other (sibling)
   processes have taken their share. It works on both directly-computed and
   solver-handled bricks: on a direct brick the siblings have already withdrawn
   their share, so the remaining content is exactly "the rest"; on a solver
   brick the siblings' current outflow rates are subtracted so the demands sum
   to the available content. It must therefore be declared *after* the other
   withdrawing processes. No parameters. Used for surface runoff in the Socont
   open (soil) land cover (water not infiltrated becomes runoff), in GR4J for
   throughfall (the net precipitation :math:`P_n` passed on to the production
   store), and in HBV-96 for the recharge (the complement of the beta-function
   infiltration, routed to the upper zone).

**Linear outflow above a threshold** (``outflow:linear_threshold``)
   A linear reservoir that only drains the content above a threshold — the
   PREVAH surface runoff :math:`Q_0 = k_0 (SUZ - SGRLUZ)`:

   .. math::

      Q(t) = k \cdot \max\!\left(0,\; S(t) - \theta\right)

   With :math:`\theta = 0` it reduces to ``outflow:linear``. Unlike
   ``outflow:threshold``, which spills the whole excess within the step, the
   excess drains at the reservoir rate. The response being affine in the
   content, the :ref:`analytic solver <solvers>` integrates it exactly (the
   content above the threshold then decays as :math:`e^{-k \Delta t}`, as in
   PREVAH). Parameters: ``k0`` (``response_factor_threshold``)
   [d\ :sup:`-1`], range [0.0001, 1], and ``sgrluz`` (``threshold``) [mm],
   range [0, 100]. The response factor carries a distinct name so the process
   can share a store with an ``outflow:linear`` (the PREVAH upper zone, which
   produces both a surface runoff and an interflow).

**Split outflow** (``outflow:split``)
   Drains the entire storage content within the time step and divides it
   between **two** targets in a fixed proportion:

   .. math::

      Q_1(t) = f \cdot \frac{S(t)}{\Delta t},
      \qquad
      Q_2(t) = (1 - f) \cdot \frac{S(t)}{\Delta t}

   Used for the fixed 8/9 : 1/9 recharge split of the PREVAH SLOWCOMP
   groundwater, and to route a fixed share of a wetland cover's input directly
   to the groundwater. Because it withdraws the full content, it cannot share a
   store with another withdrawing process. Parameter: ``split_fraction``
   *(optional, dimensionless, default: 0.8889, [0, 1])* — the share sent to the
   first target.

**SLOWCOMP overflow** (``outflow:slowcomp``)
   The filling rule of the fast baseflow store of the SLOWCOMP groundwater
   module (:cite:t:`Schwarze1999`), used by :ref:`PREVAH-UniBE <prevah-unibe>`.
   The store fills asymptotically toward its maximum content: it can only
   absorb what it would leak when full, and the excess inflow overflows to the
   slower stores *even when the store is far below its maximum*:

   .. math::

      Q_{\mathrm{over}}(t) = \max\!\left(0,\;
          I(t) - \left(S_{\max} - S(t)\right) \cdot k\right)

   where :math:`I` is the inflow of the step and :math:`k` the response factor
   of the sibling ``outflow:linear`` baseflow of the same store. This diverts
   the recharge peaks (snow melt) to the slow stores, which sustains the
   recession — a plain capacity, which spills only once full, does not. The
   store therefore carries no hard capacity. Parameter: ``slz1max``
   (``max_content``) *(optional, mm, default: 100, [0, 1000])*.


.. _transfer-processes:
.. _routing-processes:

In-catchment transfer
---------------------

GR4J routing (``routing:gr4j``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used internally by :ref:`GR4J <gr4j>`. Transforms the production-store output
:math:`P_R` into discharge through two unit hydrographs, a non-linear routing
store, and a groundwater-exchange term (:cite:t:`Perrin2003`).

The inflow is split 90 % / 10 % between two unit hydrographs:

* **UH1** (S-curve :math:`S\!H_1`, time base :math:`X_4`) feeds the routing store
  and carries :math:`0.9\,P_R`;
* **UH2** (S-curve :math:`S\!H_2`, time base :math:`2X_4`) feeds the direct branch
  and carries :math:`0.1\,P_R`.

The S-curves are

.. math::

   S\!H_1(t) = \left(\frac{t}{X_4}\right)^{5/2}, \quad 0 \le t \le X_4

.. math::

   S\!H_2(t) =
   \begin{cases}
       \tfrac{1}{2}\left(\dfrac{t}{X_4}\right)^{5/2} & 0 \le t \le X_4 \\[2ex]
       1 - \tfrac{1}{2}\left(2 - \dfrac{t}{X_4}\right)^{5/2} & X_4 < t \le 2X_4
   \end{cases}

with :math:`S\!H = 0` below the range and :math:`S\!H = 1` above it; the
unit-hydrograph ordinates are the successive differences of the S-curve.

The groundwater exchange depends on the routing-store filling ratio:

.. math::

   F = X_2 \left(\frac{R}{X_3}\right)^{7/2}

where :math:`R` is the routing-store content. A positive :math:`X_2` imports water
into the catchment; a negative one exports it (a loss). The routing store is
updated with the UH1 output and :math:`F`, then releases

.. math::

   Q_R = R \left[1 - \left(1 + \left(\frac{R}{X_3}\right)^{\!4}\right)^{\!-1/4}\right]

The direct branch yields :math:`Q_D = \max(0,\; \text{UH2 output} + F)`, and the
total discharge is :math:`Q = Q_R + Q_D`.

Parameters:

* ``X2`` (``exchange_factor``): groundwater exchange coefficient [mm d⁻¹],
  default 0. Full name: ``uh_input:exchange_factor``.
* ``X3`` (``routing_capacity``): routing-store capacity [mm], default 90.
  Full name: ``uh_input:routing_capacity``.
* ``X4`` (``uh_base_time``): unit-hydrograph time base [d], default 1.7, must be
  > 0.5. Full name: ``uh_input:uh_base_time``.


GR6J routing (``routing:gr6j``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used internally by :ref:`GR6J <gr6j>`. Extends GR4J routing
(:cite:t:`Pushpalatha2011`) with two changes that improve low-flow simulation:

* a **threshold-based groundwater exchange** (the GR5J form):

  .. math::

     F = X_2 \left(\frac{R}{X_3} - X_5\right)

  where :math:`R` is the routing-store content and :math:`X_5` is a dimensionless
  threshold setting the filling ratio at which the exchange changes sign;

* an additional **exponential routing store** (coefficient :math:`X_6`) in
  parallel to the power routing store.

The UH1 output :math:`Q_9` is split 60 % to the power store and 40 % to the
exponential store; the exchange :math:`F` is added to both stores and to the
direct branch. The power routing store and the direct branch behave as in
:ref:`GR4J routing <routing-processes>`, releasing :math:`Q_R` and :math:`Q_D`.
The exponential store updates as

.. math::

   R_{\mathrm{exp}} \leftarrow R_{\mathrm{exp}} + 0.4\,Q_9 + F

and releases (:cite:t:`Michel2003`; airGR formulation), with
:math:`a = R_{\mathrm{exp}}/X_6` clamped to :math:`[-33, 33]`:

.. math::

   Q_{\mathrm{exp}} =
   \begin{cases}
       R_{\mathrm{exp}} + X_6\,e^{-a} & a > 7 \\[1ex]
       X_6\,e^{a} & a < -7 \\[1ex]
       X_6 \ln\!\left(e^{a} + 1\right) & \text{otherwise}
   \end{cases}

The exponential store may take negative values, which lets it reproduce long,
smooth recessions. The total discharge is
:math:`Q = \max(0,\; Q_R + Q_{\mathrm{exp}} + Q_D)`.

Parameters: ``X2``, ``X3`` and ``X4`` as for :ref:`routing:gr4j
<routing-processes>` (with the threshold exchange replacing the power-law one),
plus

* ``X5`` (``exchange_threshold``): groundwater exchange threshold [−], default 0.
  Full name: ``uh_input:exchange_threshold``.
* ``X6`` (``exp_store_coeff``): exponential store coefficient [mm], default 4,
  must be > 0. Full name: ``uh_input:exp_store_coeff``.


HBV routing / MAXBAS (``routing:hbv``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used in :ref:`HBV-96 <hbv96>`. Smooths the total runoff (upper and lower zone
outflows) with the MAXBAS transformation function, a triangular unit hydrograph
of base length :math:`MAXBAS` [d] (:cite:t:`Lindstrom1997`). The weight
assigned to day :math:`j` after the inflow is the difference of the cumulative
triangular distribution

.. math::

   C(t) =
   \begin{cases}
       2\left(\dfrac{t}{MAXBAS}\right)^{2} & 0 \le t \le \tfrac{MAXBAS}{2} \\[2ex]
       1 - 2\left(1 - \dfrac{t}{MAXBAS}\right)^{2} & \tfrac{MAXBAS}{2} < t \le MAXBAS
   \end{cases}

evaluated at the time-step boundaries: :math:`u_j = C(j) - C(j-1)`. Each
inflow is thus spread over :math:`\lceil MAXBAS \rceil` days with a symmetric,
triangular weighting. With :math:`MAXBAS = 1` the inflow passes through within
the time step.

Parameters:

* ``maxbas`` *(d, default: 1, [1, 10])*

  - Base length of the triangular unit hydrograph.
  - Full name: ``routing:maxbas``.


Translation delay (``routing:delay``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A pure translation: the water reaching the brick leaves it unchanged, a fixed
duration later. It is the translation element that follows each glacier melt
reservoir of the :ref:`PREVAH glacier module <prevah-unibe>`. The delay is a
duration in days, so it shifts the water by the same time at any
:ref:`computation time step <computation-time-step>`. On the grid of steps it is
:math:`d = \text{delay} / \Delta t` steps: the water received during a step is a
block one step long, and shifting it by :math:`d` steps puts a share
:math:`1 - f` of it in step :math:`\lfloor d \rfloor` and :math:`f` in the next,
:math:`f` being the fractional part of :math:`d`. A whole number of steps is
therefore an exact shift, a delay of a few hours on a daily step moves the matching
share of each day's water onto the next day, and a zero delay is transparent.

Parameters:

* ``delay`` *(optional, d, default: 0, [0, 1])*

  - Translation time. The PREVAH glacier module exposes it as ``lag_snow``,
    ``lag_ice`` and ``lag_firn``.
  - Full name: ``<brick>:delay``.


.. _channel-routing:

Channel routing between subbasins
---------------------------------

When the catchment is a :ref:`river network of subbasins <subbasins>`, the water
leaving a subbasin travels along the reach of the downstream subbasin before it
joins that subbasin's own runoff at its outlet. The reach is not a brick: it is an
element of the network working in volumes (m³ per time step), and its scheme is
chosen model-wide with the ``channel_routing`` option (see :ref:`common options
<models>`). The travel time of a reach is its ``length`` (a subbasin property,
in m) divided by the wave ``celerity``, which is either a calibrated parameter or
derived from the channel geometry.

.. note::

   Channel routing is distinct from the in-catchment routing of a model
   structure, the ``routing:*`` processes of the :ref:`in-catchment transfer
   <transfer-processes>` (unit hydrographs, MAXBAS, the translation delay):
   those shape the hydrograph of a subbasin's own runoff, the channel routing
   moves the water from one subbasin outlet to the next.

* ``none`` (default): the inflow reaches the outlet within the same time step.
* ``lag``: a pure translation by the travel time, with the same delivery
  schedule as the :ref:`translation delay <transfer-processes>` process (a whole
  number of steps is an exact shift, a fractional travel time splits the water
  between two consecutive steps).
* ``muskingum``: the Muskingum method,
  :math:`S = K \left[ X I + (1 - X) O \right]`, with :math:`K` the travel time
  and :math:`X` the weighting factor, integrated with the standard coefficients
  :math:`C_0, C_1, C_2` of the time step. The time step is split into sub-steps
  when it exceeds :math:`2K(1-X)` (the upper stability bound), so short reaches
  stay stable; a reach whose travel time is negligible against the step is
  treated as instantaneous. When the step is shorter than :math:`2KX`, the
  first response of the reach is clamped at zero; mass is conserved in all
  cases (the reach storage keeps the balance).
* ``muskingum_cunge``: the same integration, but :math:`K` and :math:`X` are
  recomputed at every time step from the channel geometry and the discharge, so
  neither has to be calibrated. For a wide channel, Manning gives the flow depth
  :math:`h = \left( Q n / (B \sqrt{S_0}) \right)^{3/5}` and the kinematic wave
  celerity :math:`c = \frac{5}{3} \frac{Q}{B h}`, hence :math:`K = L / c`;
  Cunge's weighting factor
  :math:`X = \frac{1}{2} \left( 1 - \frac{Q}{B S_0 c L} \right)` matches the
  numerical diffusion of the scheme to the physical diffusion of the diffusive
  wave. It needs the reach ``slope``, which the
  :ref:`subbasin delineation <subbasin-delineation>` extracts from the DEM.
  Being uncalibrated, it is also the scheme most exposed to the reach ``length``:
  give the delineation a river shapefile so that the length follows the mapped
  river rather than the flow path of the DEM.

A reach longer than the distance the wave travels in one time step cannot be
resolved by a single element: its :math:`X` tends to 0.5, which is pure
translation, and the diffusion of the wave is lost. A Muskingum-Cunge reach is
therefore divided into sub reaches routed in series, short enough to satisfy the
criterion of Ponce and Theurer (1982),

.. math::

   \Delta x \leq \frac{1}{2} \left( c \Delta t +
   \frac{Q}{B S_0 c} \right)

The number of sub reaches is computed once, at the first time step, from the
``reference_discharge`` and not from the discharge of the step: every sub reach
carries its own state, which a changing count would invalidate. The count is
capped at 50 sub reaches, with a warning naming the subbasin — a reach that
needs more is better split into several subbasins, which also gives it its own
runoff. The other schemes are never divided: ``lag`` is exact whatever the
length, and ``muskingum`` takes its :math:`X` from the user rather than from the
grid.

The celerity of ``lag`` and ``muskingum`` is constant by default. A non-zero
``celerity_exponent`` makes it follow the discharge,
:math:`c = c_{ref} \left( Q / Q_{ref} \right)^{b}`, which is the cheap version of
the same idea: Manning gives an exponent of about 0.4 for a wide channel. In every
scheme the celerity is kept within 0.05 and 10 m/s, so a vanishing discharge cannot
give an unbounded travel time.

By default a subbasin's own runoff joins at its outlet with no delay, on the
grounds that its travel time is already represented by the subbasin's own stores.
With ``route_local_runoff`` it travels through **half** of the reach: being
generated along the reach, it covers half of it on average. The two branches are
routed separately and both appear in the reach water balance.

Parameters (component ``channel``):

* ``celerity`` *(m/s, default: 1, [0.1, 5])*

  - Wave celerity at the reference discharge, shared by every reach. Alias:
    ``channel_celerity``. A subbasin's ``celerity`` property overrides it for that
    reach. Unused by ``muskingum_cunge``.
  - Full name: ``channel:celerity``.

* ``celerity_exponent`` *(-, default: 0, [0, 0.8])*

  - Exponent of the discharge in the celerity power law; 0 keeps the celerity
    constant. Alias: ``channel_celerity_exponent``.
  - Full name: ``channel:celerity_exponent``.

* ``reference_discharge`` *(m³/s, default: 1, [0.001, 1000])*

  - The discharge at which the celerity is the one given above. It also sizes the
    sub reaches of Muskingum-Cunge (an index flow, as in HEC-HMS): a larger one
    gives longer sub reaches, hence fewer of them. Alias:
    ``channel_reference_discharge``.
  - Full name: ``channel:reference_discharge``.

* ``width`` *(m, default: 10, [0.5, 500], Muskingum-Cunge only)*

  - Channel width. Alias: ``channel_width``. A subbasin's ``width`` property
    overrides it for that reach.
  - Full name: ``channel:width``.

* ``manning`` *(s/m^(1/3), default: 0.035, [0.01, 0.15], Muskingum-Cunge only)*

  - Manning roughness of the channel. Alias: ``channel_manning``. A subbasin's
    ``manning`` property overrides it for that reach.
  - Full name: ``channel:manning``.

* ``x`` *(-, default: 0.2, [0, 0.5], Muskingum only)*

  - Weighting factor between the inflow and the outflow in the reach storage.
    Alias: ``muskingum_x``. A subbasin's ``muskingum_x`` property overrides it.
  - Full name: ``channel:x``.

Whenever the channel routing is on, the reach values are recorded per subbasin,
in mm over the area drained at its outlet like the ``outlet`` itself:
``reach:inflow`` (the water arriving from upstream), ``reach:outflow`` (what
reaches the outlet after routing) and ``reach:storage`` (in transit), read with
``results.get_subbasin_values('reach:storage', subbasin_id)``. A headwater
subbasin records zeros.

Inspecting the network
~~~~~~~~~~~~~~~~~~~~~~

What the routing actually does with a network is easier to check than to infer.
Once the model is set up, it reports the tree it built, the reach of every
subbasin and the travel times that follow:

.. code-block:: python

   model.print_network()            # a textual report
   model.plot_network('network')    # the tree as a diagram (needs graphviz)
   table = model.get_network_graph().to_dataframe()

The report gives, per subbasin, its local and drained areas, the length and slope
of its reach, its travel time :math:`K` at the reference discharge, the time the
water it releases needs to reach the catchment outlet, and the number of sub
reaches Muskingum-Cunge asked for. It ends with the slowest path through the
network -- the concentration time of the channel system -- and flags what would
otherwise pass unnoticed: a subbasin whose reach has no length (its routing is
instantaneous), a missing slope, or a reach divided into so many sub reaches that
it would be better represented as several subbasins.

Beware that a subbasin's own reach routes what arrives from *upstream*, not what
it sends downstream: the water leaving a subbasin crosses the reaches of the
subbasins below it, which is what the ``time_to_outlet`` column reports.

After a run, the reaches can be audited one by one:

.. code-block:: python

   results.get_reach_water_balance()

which gives, per subbasin and in m³ over the whole run, the volume that entered
the reach, the volume that left it at the outlet, what is still in transit, and
the closure error of the three. A reach conserves mass, so that error is a check
of the routing rather than a diagnostic of the catchment: it should be zero to
the rounding of the results file.

The discharge itself is available in either unit, from a run model or from the
results file:

.. code-block:: python

   model.get_outlet_discharge(units='m3/s')
   model.get_subbasin_discharge(2, units='m3/s')
   results.get_discharge(subbasin_id=2)              # m3/s by default
   results.get_discharge(subbasin_id=2, units='mm')

The model computes in mm per time step over the area drained at each outlet, which
is what the results file stores; the conversion uses that drained area and the
computation time step.
