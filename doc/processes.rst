.. _processes:

Processes
=========


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


Degree-day model (degree_day)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


Aspect-based degree-day model (degree_day_aspect)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extends the standard degree-day model by assigning different degree-day factors
to north-, south-, and east/west-facing slopes. Sun-exposed south-facing slopes
receive more radiation and melt faster for the same air temperature; this model
captures that effect without explicitly computing radiation. It requires the
catchment to be discretized by elevation and aspect. Use this model when aspect
strongly differentiates melt rates across the catchment.


Radiation-enhanced temperature-index model (temperature_index)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


CemaNeige snowmelt model (cemaneige)
"""""""""""""""""""""""""""""""""""""

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


.. _snow-rain-splitters:

Rain/snow partitioning
-----------------------

Precipitation is partitioned into rain and snow before entering the melt model.
Two splitters are available, controlled by the ``snow_rain_process`` option.


Temperature-threshold splitter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default splitter applies a linear transition between pure snow and pure rain
over a user-defined temperature range:

* Below ``prec_t_start`` (default 0 °C): all precipitation falls as snow.
* Above ``prec_t_end`` (default 2 °C): all precipitation falls as rain.
* Between the two thresholds: the snow fraction decreases linearly.

Both thresholds are optional calibration parameters. This splitter is used by
default in GSM-Socont and in GR4J with the ``'melt:degree_day'`` option.


CemaNeige rain/snow splitter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CemaNeige splitter (:cite:t:`Valery2014`) determines the solid fraction from the
daily temperature range rather than a fixed threshold:

.. math::

   f_{\mathrm{solid}} = \max\!\left(0,\; \min\!\left(1,\; \frac{T_{\max} - T_{\mathrm{mean}}}{T_{\max} - T_{\min}}\right)\right)

The temperature range :math:`[T_{\min},\, T_{\max}]` depends on elevation:

* **At elevations ≥ 1500 m**: fixed values :math:`T_{\min} = -1\ °C` and
  :math:`T_{\max} = 3\ °C` are used — no additional forcing variables are needed.
* **At elevations < 1500 m**: :math:`T_{\min}` and :math:`T_{\max}` are read
  from the daily ``temperature_min`` and ``temperature_max`` forcing variables.

The splitter has no calibrated parameters. It is selected automatically when
``snow_melt_process='melt:cemaneige'`` in GR4J.


.. _evapotranspiration:

Evapotranspiration
------------------

Two ET formulations are available. The one used depends on the model.


Socont ET (et:socont)
^^^^^^^^^^^^^^^^^^^^^^

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


GR4J ET (et:gr4j)
^^^^^^^^^^^^^^^^^^

Used internally by :ref:`GR4J <gr4j>`; not user-configurable. Follows the GR4J
formulation of :cite:t:`Perrin2003`. Before computing ET, a zero-capacity interception
step neutralises precipitation against PET: if P > E\ :sub:`P`, the excess
precipitation P\ :sub:`n` = P − E\ :sub:`P` passes on and E\ :sub:`n` = 0; if
P ≤ E\ :sub:`P`, the net evaporative demand is E\ :sub:`n` = E\ :sub:`P` − P.
Actual ET is then withdrawn from the production store:

.. math::

   E_s = S \cdot \frac{2 - S/X_1}{1 + (1 - S/X_1) \tanh(E_n/X_1)} \tanh(E_n/X_1)

where :math:`X_1` is the production store capacity and :math:`S` is the current
store content. No calibrated parameters beyond :math:`X_1`.


.. _infiltration-processes:

Infiltration
------------

Socont infiltration (infiltration:socont)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used in :ref:`GSM-Socont <gsm-socont>` for the ground land cover. Water
infiltrates into the slow reservoir at a rate that decreases quadratically as
the reservoir fills (:cite:t:`Schaefli2005`):

.. math::

   \mathrm{Inf}(t) = S(t) \left(1 - \left(\frac{S(t)}{S_{\max}}\right)^2\right)

where :math:`S(t)` is the current water content and :math:`S_{\max}` is the
maximum capacity. When the reservoir is empty, all incoming water infiltrates;
when full, infiltration is zero and the remainder becomes surface runoff. No
calibrated parameters.

GR4J uses a separate ``infiltration:gr4j`` formulation internally; it is not
user-configurable.


.. _percolation-processes:

Percolation
-----------

Constant percolation (percolation:constant)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

:ref:`GR4J <gr4j>` uses an internal non-linear percolation
(``percolation:gr4j``) that increases with production-store filling and is not
user-configurable.


.. _runoff-processes:

Surface runoff / Quick flow
---------------------------

Two formulations control how water leaves the surface runoff storage
in :ref:`GSM-Socont <gsm-socont>`. The choice is made via the ``surface_runoff``
option at model instantiation.


Socont runoff (runoff:socont)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Use this formulation when the non-linear response of overland flow to slope is
important. It is the original Socont parameterisation.


Linear storage runoff (outflow:linear)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alternative (``surface_runoff="linear_storage"``). Replaces the Manning-based
formulation with a simple linear reservoir:

.. math::

   Q_{\mathrm{quick}}(t) = k_{\mathrm{quick}} \cdot S(t)

Parameters:

* ``k_quick``: response factor [d\ :sup:`-1`], range [0.05, 1].
  Full name: ``surface_runoff:response_factor``.

Use this formulation when slope data are unavailable or when a simpler quick-flow
representation is preferred.


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
   glacier meltwater directly to the basin-level lumped storages.

**Rest-direct outflow** (``outflow:rest_direct``)
   Routes whatever water remains after all other processes have been applied.
   No parameters. Used for surface runoff in the Socont ground land cover
   (water not infiltrated becomes runoff) and in GR4J (net precipitation not
   captured by the production store passes directly to routing).

