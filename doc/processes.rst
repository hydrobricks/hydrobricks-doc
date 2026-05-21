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

Degree-day model (degree_day; TI)
"""""""""""""""""""""""""""""""""

This is the classic temperature-index model where melt depends solely on air 
temperature above a threshold (see equation above). It is used with HRUs defined
as evenly spaced elevation bands. It is simple.

Aspect-based degree-day model (degree_day_aspect; ATI)
""""""""""""""""""""""""""""""""""""""""""""""""""""""

The aspect-based temperature-index model refines the standard TI approach by
accounting for topographic aspect. The study area is discretized into aspect
classes (e.g., north, south, east/west), and each receives a different 
degree-day factor:

- Enhances spatial realism of melt estimation.
- Reflects directional differences in solar exposure.
- Suitable for mountainous terrain with varied aspect.

Temperarature index model (temperature_index; HTI)
""""""""""""""""""""""""""""""""""""""""""""""""""

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

Radiation is calculated using:

.. math::

   I_{\mathrm{pot}} = I_0 \left( \frac{R_m}{R} \right)^2 \Psi_a^{\left( \frac{P}{P_0 \mathrm{cos}(Z)} \right)} \mathrm{cos}(\theta)

where:

- :math:`I_0` is the solar constant (1368 W m⁻²),
- :math:`\left( R_m/R \right)^2` is the Earth's orbit's eccentricity correction factor,
- :math:`R`, :math:`R_m` are the instantaneous and the mean Sun-Earth distances,
- :math:`\Psi_a` is the mean atmospheric clear-sky transmissivity,
- :math:`P`, :math:`P_0` are the local and the mean sea-level atmospheric pressures,
- :math:`R`, :math:`R_m` are Sun–Earth distances,
- :math:`Z` is the local zenith angle,
- :math:`\theta` is the angle of incidence between the normal to the grid slope and the solar beam.

Radiation is calculated every 15 minutes and aggregated daily to accurately
reflect diurnal variation and terrain shading.

This model offers:

- Direct representation of irradiation effects on melt.
- Improved accuracy in catchments influenced by shadows and aspect.
- More complexity, requiring solar radiation computation at sub-daily time steps.

**HTI** is recommended for its physical realism, especially when snow and glacier
melt dominate runoff processes. **TI** provides a practical simple option when 
radiation data is too long to compute. For more details, refer to Argentin2025_.

References
----------

.. [Argentin2025] Argentin, A.-L., Horton, P., Schaefli, B., Shokory, J., Pitscheider, F., Repnik, L., Gianini, M., Bizzi, S., Lane, S. N., & Comiti, F. (2025). Scale dependency in modeling nivo-glacial hydrological systems: The case of the Arolla basin, Switzerland. Hydrology and Earth System Sciences, 29(6), 1725–1748. https://doi.org/10.5194/hess-29-1725-2025
.. [Hock1999] Hock, R. (1999). A distributed temperature-index ice- and snowmelt model including potential direct solar radiation. Journal of Glaciology, 45(149), 101–111. https://doi.org/10.3189/s0022143000003087
.. [Rango1995] Rango, A., & Martinec, J. (1995). Revisiting The Degree‐Day Method For Snowmelt Computations. JAWRA Journal of the American Water Resources Association, 31(4), 657–669. https://doi.org/10.1111/j.1752-1688.1995.tb03392.x
