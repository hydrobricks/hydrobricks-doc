.. _getting-started:

Getting started
===============

Hydrobricks is distributed through PyPi and can be installed using pip:

.. code-block:: python

   pip install hydrobricks

Some code examples are provided in the
`python/examples directory of the repo <https://github.com/hydrobricks/hydrobricks/tree/main/python/examples>`_.
The `tests <https://github.com/hydrobricks/hydrobricks/tree/main/python/tests>`_
can also be a useful resource to understand the behaviour of some functions.

Here is a minimum example:

.. code-block:: python

   import hydrobricks as hb
   import hydrobricks.models as models

   # Model structure
   socont = models.Socont(soil_storage_nb=2, surface_runoff="linear_storage",
                          record_all=False)

   # Parameters
   parameters = socont.generate_parameters()
   # TODO: parameters.set_values({'A': 100, 'k_slow': 0.01, 'a_snow': 5, ...})

   # Hydro units
   hydro_units = hb.HydroUnits()
   hydro_units.load_from_csv(
       'path/to/elevation_bands.csv', area_unit='m2', column_elevation='elevation',
       column_area='area')

   # Meteo data
   forcing = hb.Forcing(hydro_units)
   forcing.load_from_csv(
       'path/to/meteo.csv', column_time='Date', time_format='%d/%m/%Y',
       content={'precipitation': 'precip(mm/day)', 'temperature': 'temp(C)',
                'pet': 'pet_sim(mm/day)'})
   ref_elevation = 1250  # Reference altitude for the meteo data
   forcing.spatialize_temperature(ref_elevation, -0.6)
   forcing.spatialize_pet()
   forcing.spatialize_precipitation(ref_elevation=ref_elevation, gradient=0.05,
                                    correction_factor=0.85)

   # Obs data
   obs = hb.Observations()
   obs.load_from_csv('path/to/discharge.csv', column_time='Date', time_format='%d/%m/%Y',
                     content={'discharge': 'Discharge (mm/d)'})

   # Model setup
   socont.setup(spatial_structure=hydro_units, output_path=str('path/to/outputs'),
                start_date='1981-01-01', end_date='2020-12-31')

   # Initialize and run the model
   socont.initialize_state_variables(parameters=parameters, forcing=forcing)
   socont.run(parameters=parameters, forcing=forcing)

   # Get outlet discharge time series
   sim_ts = socont.get_outlet_discharge()

   # Evaluate
   obs_ts = obs.data_raw[0]
   nse = socont.eval('nse', obs_ts)
   kge_2012 = socont.eval('kge_2012', obs_ts)
