.. _getting-started:

Getting started
===============

Hydrobricks is distributed through PyPi and can be installed using pip:

.. code-block:: python

   pip install hydrobricks

Use an older version of Python (e.g., 3.11) to ensure package compatibility.

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
   parameters.set_values({'A': 458, 'a_snow': 1.8, 'k_slow_1': 0.9, 'k_slow_2': 0.8,
                          'k_quick': 1, 'percol': 9.8})

   # Hydro units
   hydro_units = hb.HydroUnits()
   hydro_units.load_from_csv(
       'path/to/elevation_bands.csv', column_elevation='elevation', column_area='area')

   # Meteo data
   forcing = hb.Forcing(hydro_units)
   forcing.load_station_data_from_csv(
       'path/to/meteo.csv', column_time='Date', time_format='%d/%m/%Y',
       content={'precipitation': 'precip(mm/day)', 'temperature': 'temp(C)',
                'pet': 'pet_sim(mm/day)'})
   ref_elevation = 1250  # Reference altitude for the meteo data
   forcing.spatialize_from_station_data(
       variable='temperature', ref_elevation=ref_elevation, gradient=-0.6)
   forcing.correct_station_data(variable='precipitation', correction_factor=0.75)
   forcing.spatialize_from_station_data(
       variable='precipitation', ref_elevation=ref_elevation, gradient=0.05)
   forcing.compute_pet(method='Hamon', use=['t', 'lat'], lat=47.3)

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
   obs_ts = obs.data[0]
   nse = socont.eval('nse', obs_ts)
   kge_2012 = socont.eval('kge_2012', obs_ts)

   print(f"nse = {nse:.3f}, kge_2012 = {kge_2012:.3f}")
