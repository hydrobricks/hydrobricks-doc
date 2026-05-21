.. _processes:

Processes
=========


.. _melt-models:

Melt Models
-----------

Three melt models are currently available in **Hydrobricks** to simulate snow and 
glacier melt processes. These models are designed to address varying spatial 
complexity and are suited for high-elevation catchments with limited observational
data.

Available melt models:
  
* **degree_day**: classical temperature-index model (TI)
* **degree_day_aspect**: aspect-based temperature-index model (ATI)
* **temperature_index**: Hock’s temperature-index model (HTI)

The melt model is specified when instantiating the :code:`Socont` hydrological 
model. For example:

.. code-block:: python

    melt_model = "melt:degree_day"  # "melt:degree_day", "melt:degree_day_aspect", or "melt:temperature_index"
    socont = Socont(soil_storage_nb=2, 
                    surface_runoff="linear_storage",
                    snow_melt_process=melt_model)

Model descriptions
^^^^^^^^^^^^^^^^^^

Melt processes in snow- and glacier-dominated catchments are typically modeled 
using temperature-index (TI) approaches due to limited availability of detailed
energy balance data. The general form (Rango1995_) of a 
temperature-index melt model is:

.. math::

   M_{\mathrm{TI}}(t) = 
    \begin{cases}
        a_j(T_a(t) - T_T) & : T_a(t) > T_T \mathrm{~~~with~} j \in \mathrm{snow, ice}\\
        0 & : T_a(t) \leq T_T
    \end{cases}

where:

- :math:`M_{\mathrm{TI}}(t)` is the melt rate at time step :math:`t` (mm d⁻¹),
- :math:`a_j` is the degree-day factor for ice or snow (mm d⁻¹ °C⁻¹),
- :math:`T_a` is the air temperature (°C),
- :math:`T_T` is the threshold melt temperature (°C).

**1. degree_day (TI model)**

This is the classic temperature-index model where melt depends solely on air 
temperature above a threshold (see equation above). It is used with HRUs defined
as evenly spaced elevation bands. It is simple.

**2. degree_day_aspect (ATI model)**

The aspect-based temperature-index model refines the standard TI approach by
accounting for topographic aspect. The study area is discretized into aspect
classes (e.g., north, south, east/west), and each receives a different 
degree-day factor:

- Enhances spatial realism of melt estimation.
- Reflects directional differences in solar exposure.
- Suitable for mountainous terrain with varied aspect.

**3. temperature_index (HTI model)**

This model, based on Hock1999_, incorporates **potential clear-sky direct 
solar radiation** to improve melt estimates:

.. math::

    M_{\mathrm{HTI}}(t) = 
        \begin{cases}
            (m + r_j I_{\mathrm{pot}})(T_a(t) - T_T) & : T_a(t) > T_T \mathrm{~~~with~} j \in \mathrm{snow, ice}\\
            0 & : T_a(t) \leq T_T
        \end{cases}

where:

- :math:`M_{\mathrm{HTI}}` is the melt rate (mm d⁻¹),
- :math:`m` is the melt factor common to both ice and snow (mm d⁻¹ °C⁻¹),,
- :math:`r_j` is the radiation factor for ice or snow (mm d⁻¹ °C⁻¹ m² W⁻¹),
- :math:`I_{pot}` is the potential clear-sky direct solar radiation (W m⁻²),
- :math:`T_a` is the air temperature (°C),
- :math:`T_T` is the threshold melt temperature (°C).

This model offers:

- Direct representation of irradiation effects on melt.
- Improved accuracy in catchments influenced by shadows and aspect.
- More complexity, requiring solar radiation computation at sub-daily time steps.

**HTI** is recommended for its physical realism, especially when snow and glacier
melt dominate runoff processes. **TI** provides a practical simple option when 
radiation data is too long to compute. For more details, refer to Argentin2025_.
