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

This partitioning is used by default in GSM-Socont and in GR4J when
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


.. _melt-models:

Melt models
-----------

Four snow and glacier melt models are available in Hydrobricks. They differ
in data requirements and spatial complexity, ranging from a simple temperature
index to a radiation-enhanced approach. Choose based on the available input
data and the catchment characteristics.

Available melt models:

* **degree_day**: classical degree-day model
* **degree_day_aspect**: aspect-based degree-day model
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
``"melt:degree_day_aspect"``, ``"melt:temperature_index"``,
``"melt:cemaneige"``.


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


Aspect-based degree-day model (``degree_day_aspect``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extends the standard degree-day model by assigning different degree-day factors
to north-, south-, and east/west-facing slopes. Sun-exposed south-facing slopes
receive more radiation and melt faster for the same air temperature; this model
captures that effect without explicitly computing radiation. It requires the
catchment to be discretized by elevation and aspect. Use this model when aspect
strongly differentiates melt rates across the catchment.


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


.. _evapotranspiration:

Evapotranspiration
------------------

Two ET formulations are available.


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


.. _infiltration-processes:

Infiltration
------------

Socont infiltration (``infiltration:socont``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used in :ref:`GSM-Socont <gsm-socont>` for the ground land cover. Water
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
slow reservoir to the baseflow reservoir.

Parameters:

* ``percol`` (alias for ``percolation_rate``): constant drainage rate [mm d⁻¹],
  range [0, 10]. Full name: ``slow_reservoir:percolation_rate``.

GR4J percolation (``percolation:gr4j``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Drains water from the GR4J production store (:cite:t:`Perrin2003`):

.. math::

   \mathrm{Perc} = S \left[1 - \left(1 + \left(\frac{4S}{9\,X_1}\right)^{\!4}\right)^{\!-1/4}\right]

where :math:`S` is the current production-store water content and :math:`X_1` is
its capacity. Percolation increases non-linearly with the filling ratio and goes
to zero when the store is empty. In the GR4J model it is applied as part of the
combined :ref:`production:gr4j <gr4j-production>` step. No calibrated parameters.


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


.. _transfer-processes:

Transfer
--------

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


.. _outflow-processes:

Reservoir outflow
-----------------

The following outflow mechanisms are used by storage bricks across all models.

**Linear outflow** (``outflow:linear``)
   The most common outflow type. Outflow is proportional to the current storage:

   .. math::

      Q(t) = k \cdot S(t)

   Parameter: ``response_factor`` [d\ :sup:`-1`]. Used for the slow reservoirs, glacier
   area storages, and the linear quick-flow option.

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
   ground land cover (water not infiltrated becomes runoff) and in GR4J for
   throughfall (the net precipitation :math:`P_n` passed on to the production
   store).

