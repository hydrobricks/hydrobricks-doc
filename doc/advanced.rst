.. _advanced:

Advanced features
=================

Land cover evolution
--------------------

The land cover types in hydrobricks are defined by the user 
(see the :ref:`hydro units section <spatial-structure>`).
Each hydro unit is thus internally defined by a total area and fractional land
covers. These land covers can have a dynamic evolution. This evolution can be
externally driven or internally computed.

Hydrobricks offers the following options:

1. Evolution set through csv file
2. Evolution computed from shapefiles
3. Evolution computed from shapefiles and delta-h method
4. Evolution computed from ice thickness and delta-h method

The definition of a land cover evolution does not replace the original 
definition of the hydro units, which need to be also provided to the function.
The areas provided in the definition of the hydro units are the starting point
of the model, and these changes will be enforced in due time. However, if some
changes are defined for dates prior to the start of the modelling period, these
changes will also be applied.

The two last options are specific to glacier land covers. They do not handle
debris covers on glaciers.

.. _first-option:

Evolution set through csv file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One can provide the model with a timeseries of dates and new land cover areas, such as:

.. code-block:: python

   changes = actions.ActionLandCoverChange()
   changes.load_from_csv(
       '/path/to/surface_changes_glacier_debris.csv',
       hydro_units, area_unit='km2', match_with='elevation'
   )
   model.add_action(changes)

The function ``changes.load_from_csv()`` can be called multiple times for different files.
The corresponding csv file must contain the name of the land cover to change on the
first row (for example here ``glacier_debris``), the dates of these changes on the
second row, and then the change time series.
These changes list all hydro units that need to change; those that do not need to
change should not be listed in the file.
There are two ways to identify the hydro units: by elevation
(``match_with='elevation'``) or by ID (``match_with='id'``).
In the following example, these changes start with the unit elevation and contain the
time series of the area (here in km2) for every date given above.

.. code-block:: text
   :caption: Example of a csv file containing a land cover evolution.

   bands,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris,glacier_debris
   ,01/08/2020,01/08/2025,01/08/2030,01/08/2035,01/08/2040,01/08/2045,01/08/2050,01/08/2055,01/08/2060,01/08/2065,01/08/2070,01/08/2075,01/08/2080,01/08/2085,01/08/2090,01/08/2095,01/08/2100
   4274,0.013,0.003,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
   4310,0.019,0.009,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
   4346,0.052,0.042,0.032,0.022,0.012,0.002,0,0,0,0,0,0,0,0,0,0,0
   4382,0.072,0.062,0.052,0.042,0.032,0.022,0.012,0.002,0,0,0,0,0,0,0,0,0
   4418,0.129,0.119,0.109,0.099,0.089,0.079,0.069,0.059,0.049,0.039,0.029,0.019,0.009,0,0,0,0
   4454,0.252,0.242,0.232,0.222,0.212,0.202,0.192,0.182,0.172,0.162,0.152,0.142,0.132,0.122,0.112,0.102,0.092
   4490,0.288,0.278,0.268,0.258,0.248,0.238,0.228,0.218,0.208,0.198,0.188,0.178,0.168,0.158,0.148,0.138,0.128
   4526,0.341,0.331,0.321,0.311,0.301,0.291,0.281,0.271,0.261,0.251,0.241,0.231,0.221,0.211,0.201,0.191,0.181
   4562,0.613,0.603,0.593,0.583,0.573,0.563,0.553,0.543,0.533,0.523,0.513,0.503,0.493,0.483,0.473,0.463,0.453
   4598,0.648,0.638,0.628,0.618,0.608,0.598,0.588,0.578,0.568,0.558,0.548,0.538,0.528,0.518,0.508,0.498,0.488
   4634,0.618,0.608,0.598,0.588,0.578,0.568,0.558,0.548,0.538,0.528,0.518,0.508,0.498,0.488,0.478,0.468,0.458
   4670,0.478,0.468,0.458,0.448,0.438,0.428,0.418,0.408,0.398,0.388,0.378,0.368,0.358,0.348,0.338,0.328,0.318
   4706,0.306,0.296,0.286,0.276,0.266,0.256,0.246,0.236,0.226,0.216,0.206,0.196,0.186,0.176,0.166,0.156,0.146
   4742,0.338,0.328,0.318,0.308,0.298,0.288,0.278,0.268,0.258,0.248,0.238,0.228,0.218,0.208,0.198,0.188,0.178
   4778,0.199,0.189,0.179,0.169,0.159,0.149,0.139,0.129,0.119,0.109,0.099,0.089,0.079,0.069,0.059,0.049,0.039
   4814,0.105,0.095,0.085,0.075,0.065,0.055,0.045,0.035,0.025,0.015,0.005,0,0,0,0,0,0
   4850,0.051,0.041,0.031,0.021,0.011,0.001,0,0,0,0,0,0,0,0,0,0,0
   4886,0.019,0.009,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
   4922,0.008,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
   4958,0.003,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0

There is no need to specify the corresponding changes in the generic ``ground`` land
cover as it will be automatically computed to preserve the total hydro unit area.


.. _second-option:

Evolution computed from shapefiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One can provide the model with a timeseries of dates and shapefiles, such as:

.. code-block:: python

   times = ['2008-01-01', '2010-01-01', '2016-01-01']
   ice_glaciers = ['/path/to/Glacier_ice_2008.shp',
   		   '/path/to/Glacier_ice_2010.shp', 
   		   '/path/to/Glacier_ice_2016.shp']
   debris_glaciers = ['/path/to/Glacier_debris_2008.shp',
   		      '/path/to/Glacier_debris_2010.shp', 
   		      '/path/to/Glacier_debris_2016.shp']
   changes, changes_df = actions.ActionLandCoverChange.create_action_for_glaciers(
       study_area, times, ice_glaciers, debris_glaciers, 
       with_debris=True, method='raster', interpolate_yearly=True)
   model.add_action(changes)

This method also creates a dataframe that can then be exported as csv files, and
reloaded in if needed using the :ref:`first option <first-option>`:

.. code-block:: python

   changes_df[0].to_csv('/path/to/surface_changes_glacier_ice.csv', index=False)
   changes_df[1].to_csv('/path/to/surface_changes_glacier_debris.csv', index=False)
   changes_df[2].to_csv('/path/to/surface_changes_ground.csv', index=False)
   
And the hydrological units can also separately be initialized using the
following lines:

.. code-block:: python

   hyd_units.initialize_from_land_cover_change('glacier_ice', changes_df[0])
   hyd_units.initialize_from_land_cover_change('glacier_debris', changes_df[1])

Tips and tricks
"""""""""""""""

If information about land cover evolution is only available for a date after
the beginning of the simulation period, it is possible to assume a constant
land cover by duplicating the first data and assigning it the simulation 
begining date. This evolution, is of course, debatable...

For example:

.. code-block:: python

   times = ['2005-01-01', '2008-01-01', '2010-01-01', '2016-01-01']
   ice_glaciers = ['/path/to/Glacier_ice_2008.shp',
                   '/path/to/Glacier_ice_2008.shp',
   		   '/path/to/Glacier_ice_2010.shp', 
   		   '/path/to/Glacier_ice_2016.shp']
   debris_glaciers = ['/path/to/Glacier_debris_2008.shp',
                      '/path/to/Glacier_debris_2008.shp',
   		      '/path/to/Glacier_debris_2010.shp', 
   		      '/path/to/Glacier_debris_2016.shp']


.. _third-option:

Evolution computed from shapefiles and delta-h method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The delta-h method from Huss et al. (2010), implemented by Seibert et al. (2018) is also available in Hydrobricks.
A contrario to the two first methods, in the delta-h approach the glacial evolution is not forced from the outside but decided by the modeled melt of the glacier.
Hydrobricks compute the amount the glacier melted in the year, and retrieves the corresponding glacier area from the lookup table.
This makes this method and the following most appropriate for future discharge modeling or past discharge data when no glacier extent timeseries are available, whereas the two first methods are most appropriate when glacier timeseries of glacier extents are available.

We recommend 10 glacier elevation bands per HRU elevation band.

.. code-block:: python

   elev_distance = 40 # 40 m HRU elevation band
   study_area = catchment.Catchment(outline='path/to/watershed/shapefile.shp')
   glacier_evolution = preprocessing.GlacierEvolutionDeltaH()
   glacier_df = glacier_evolution.compute_initial_ice_thickness(
   	study_area, ice_thickness = glacier_thickness,
   	elevation_bands_distance = elev_distance / 10)
   glacier_evolution.compute_lookup_table(update_width=False)
   
The glacier lookup table ``glacier_evolution`` can then be linked to Hydrobricks.
At the beginning of October, the hydrological model will sum up all the glacier
mass loss that occurred during the hydrological year and will modify the land
cover according to the areas stored in the glacier lookup table: 
   
.. code-block:: python
    
   changes = actions.ActionGlacierEvolutionDeltaH()
   changes.load_from(glacier_evolution, land_cover='glacier',
                     update_month='October')

This method also creates a dataframe that can then be exported as csv files, and
reloaded in if needed using the :ref:`first option <first-option>`:

.. code-block:: python

   glacier_df.to_csv('/path/to/surface_changes_glacier.csv', index=False)
            
The glacier lookup table can be saved as a csv file:

.. code-block:: python
            
   glacier_evolution.save_as_csv('/path/to/results/folder/')
   
   

.. _fourth-option:

Evolution computed from ice thickness and delta-h method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



References
""""""""""

- Seibert, J., Vis, M., Kohn, I., Weiler, M., & Stahl, K. (2018). Technical note: Representing glacier geometry changes in a semi-distributed hydrological model. Hydrology and Earth System Sciences.
- Huss, M., Jouvet, G., Farinotti, D., & Bauder, A. (2010). Future high-mountain hydrology: A new parameterization of glacier retreat. Hydrology and Earth System Sciences.

Note: Options and compatibility with radiation/aspect discretization
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

- 
- 
- 



.. _glacier-thickness-options:
   
Glacier thickness-related options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The glacier evolution methods require appropriate configuration of the following two options:

    ``glacier_infinite_storage``: Boolean flag indicating whether glaciers have unlimited thickness (i.e., no thinning due to melt).

    ``snow_ice_transformation``: Rate at which snow transforms into ice, expressed in mm/day. The default value is 0.002 mm/day.

These options must be set depending on the method used for glacier evolution:

    For methods 1 and 2 (:ref:`CSV input <first-option>` or 
    :ref:`shapefile input <second-option>`), the computation only takes into
    account the area, and not the ice thickness. As such:

    .. code-block:: python

        glacier_infinite_storage = True
        snow_ice_transformation = False

    For methods 3 and 4 (:ref:`shapefiles with delta-h <third-option>` or 
    :ref:`ice thickness with delta-h <fourth-option>`), the computation relies
    on the ice thickness to compute the area. As such:
	
    .. code-block:: python
    
        glacier_infinite_storage = False
        snow_ice_transformation = True

They are specified during model initialization:

.. code-block:: python

   socont = models.Socont(...,
                          glacier_infinite_storage = glacier_infinite_storage,
                          snow_ice_transformation = snow_ice_transformation)
                          
                          
.. _snow-redistribution:
   
Snow redistribution option
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: images/without_snow_redistribution.png
   :alt: Snow height without snow redistribution
   :figwidth: 40%
   :align: center
   
.. figure:: images/with_snow_redistribution.png
   :alt: Snow height with snow redistribution
   :figwidth: 40%
   :align: center

Hydrobricks supports a snow redistribution mechanism based on the SnowSlide
algorithm (Bernhardt & Schulz, 2010). This option simulates gravitational snow
transport and can help improve snow distribution modeling across elevation 
bands and avoid 'snow towers'.

Default example:

.. code-block:: python

   socont = models.Socont(soil_storage_nb = 2,
   			  snow_redistribution = 'transport:snow_slide')

In addition, you must provide a connectivity CSV file describing the lateral
redistribution pathways between hydro units:

.. code-block:: python

   hydro_units.set_connectivity(/path/to/connectivity.csv)

Resources:
    
    `Working example implementation <https://github.com/hydrobricks/hydrobricks/blob/feature/glacier-evolution/python/examples/basics/snow_redistribution.py>`_
    
    `Script to compute the connectivity CSV <https://github.com/hydrobricks/hydrobricks/blob/main/python/examples/preprocessing/compute_lateral_connectivity.py>`_


References
""""""""""

- Bernhardt, M., & Schulz, K. (2010). SnowSlide: A simple routine for calculating gravitational snow transport. Geophysical Research Letters.



