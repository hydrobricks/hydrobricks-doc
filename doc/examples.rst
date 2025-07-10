Examples
========

This page presents examples of workflows to run Hydrobricks.

Simulating discharge under climate change
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first example derives from the AltroClima project that aims to model bedload transport under climate change.
Since it aims at simulating discharge in a range of Swiss and South Tyrolean catchments, it is designed to be
modulable and allow for different catchment inputs.

Step 1: Preprocess the data in QGIS
-----------------------------------

The data preprocessing (outlet, DEM clipping, filling, watershed delineation) is performed in QGIS.

See detailed instructions here:  
:doc:`preprocessing`

.. only:: never
    
    Step that produces the SHP files and .tif files inherent to the basin to be analysed and which 
    will be used by Hydrobricks. This procedure, for the moment, is described to be performed in QGIS. 
    All the following steps will be done with the new Swiss coordinate system EPSG:2056 - CH1903+ / LV95.
    So always make sure that the EPSG is 2056. 

    First step: 
        Create a SHP file of the outlet location using the map of Switzerland

        - Layer ➔ Create Layer ➔ New Shapefile Layer

        - Specify the name (example TR_intake_EPSG2056) and save it in the folder “Inatkes_locations”

        - Geometry type “Point” and EPSG:2056

        - Right-click on the newly created Layer ➔ Toggle Editing ➔ Add point feature

        - Click on the point where there is the outlet/water intake

    Second step: 
        Cut out the study area from the DEM with 10 m resolution (from swissALTIregio). The study area must cover the entire catchment area.
        
        - Load the DEM into QGIS: either by dragging it into the project or by loading it (Layer ➔ Add Layer ➔ Add Raster Layer).
        
        - Cut out the study area: Raster ➔ Extraction ➔ Clip Raster by Extent ➔ in the “Clipping extent” window choose “Draw on Map Canvas” 
        
        - In the “Clipped (extent)” window save the Clipped are with a “name.tif” (really important to add the “.tif” at the end of the name, Figure 3)

    Third step: 
        Fill the sinks of the clipped DEM
        
        - Processing toolbox ➔ SAGA ➔ Fill Sinks (Wang & Liu) 
        
        - Input file: Clipped DEM; Output file: Filled DEM

    Fourth step: 
        Compute the Strahler order of the stream network and generate a polyline of the stream network
        
        - Processing toolbox ➔ SAGA ➔ Terrain analysis ➔ Channels ➔ Channel Network and Drainage Basins
        
        - Input file: Filled DEM ; Output files: “Strahler order” and “Channels”

    Fifth step: 
        Correct manually the location of the outlet point(s) so that they match the stream network. If the location of the water intake (made in step one) is not exactly on the stream network, create a new .shp file that is exactly in the middle of the stream network pixel
        
        - Layer ➔ Create Layer ➔ New Shapefile Layer
        
        - Specify the name (example TR_outlet_EPSG2056) and save it in the folder “Outlet_locations_on_dhm25”
        
        - Geometry type “Point” and EPSG:2056
        
        - Right-click on the newly created Layer ➔ Toggle Editing ➔ Add point feature 
        
        - Click on the point where there is the water intake

    Sixth step: 
        Extract coordinates of the Outlet Point
        
        - Right-click on the new Outlet.shp ➔ Open Attribute table ➔ Open Field Calculator
        
        - In the middle panel, select Geometry ➔ Double-click on $x ➔ Set Output field name to “X-coord”, and Output field type to “Decimal number (real)”. Do the same for Y.

    Seventh step: 
        Generate Watershed of the Stream Network
        
        - Processing Toolbox ➔ SAGA ➔ Terrain Analysis ➔ Hydrology ➔ Upslope Area
        
        - Open the Attribute Table of the “Outlet Point” and copy/paste the X-Y coordinates in the Upslope Area window (Target X and Target Y)
        
        - In “Elevation”: Filled DEM
        
        - In “Method”: [0] Deterministic 8

    Eighth step:  
        Convert the Upslope Area raster to a vector
        
        - Raster ➔ Conversion ➔ Polygonize (Raster to vector)
        
        - In the “Vectorized” window save the Upslope Area are with a “out.shp”
        
        - Save the out.shp file in the folder “Watersheds_on_dhm25”

    Ninth step: 
        Calculate out.shp area
        
        - Open the Attribute Table of the “out” file ➔ Field calculator ➔ and paste “area(transform($geometry, 'EPSG:2056', 'EPSG:2056'))”
        
        - Save the area (integer only) in a .txt file in the folder “Watersheds_on_dhm25”: first line write “Area”, second line the value (without decimals)


Step 2: Install Hydrobricks
----------------------------
If the computer deos not yet have Hydrobricks installed we can make it run with the following steps in the Anaconda prompt:
    
- We create a new environment in which we install all the dependencies needed to run Hydrobricks. Pay attention to using an older version of Python (e.g. Python v3.11) to ensure package compatibility:

.. code-block:: console
    
    conda create -n YOUR_ENVIRONMENT_NAME python=3.11

- Activate the newly created environment for running Hydrobricks. Ensure to activate said environment every time you want to use the model:

.. code-block:: console
        
    conda activate YOUR_ENVIRONMENT_NAME

- If you set up Hydrobricks for the first time in an environment, you need to install the necessary packages using the following line of code in the Anaconda prompt:

.. code-block:: console
        
    pip install numpy pandas matplotlib xarray netCDF4 h5py pyproj rasterio geopandas shapely fiona rioxarray spotpy xarray-spatial pyarrow

- Install Hydrobricks and Spyder:

.. code-block:: console
        
    pip install hydrobricks
    pip install spyder



Step 3: Train the Model
-----------------------

The training script uses the output from `load_data.py`.

.. literalinclude:: ../examples/workflow/train_model.py
   :language: python
   :caption: examples/workflow/train_model.py
   :linenos:


Outputs
--------

The folders where the results are stored are called “OutputFigures” and “Outputs”. These folders are automatically created by Hydrobricks in the same path where the others are stored.

Outputs list: 
    - **“socont_...”** are the files which record all the intermediate simulations before the best simulation (recorded in “best_fit_...”) is identified. Useless, except in the case of debugging. 
    
    - **“forcing.nc”:** Netcdf file containing precipitation, temperature, potential evapotranspiration (PET) and radiation if you run a Hock model. This is a file for Hydrobricks which is only useful in debugging, or to avoid recalculating the forcing each time. More information: https://hydrobricks.readthedocs.io/en/latest/doc/basics.html#forcing-data.
    
    - **“hydrobricks_...log”:** the “.log” files are logs of each simulation run. They will be of no use to you unless Hydrobricks bugs, in which case they may help.
    
    - **“unit_ids.tif”:** contains the distribution of HRUs (hydrological response units). The study area is divided into HRUs by elevation, and depending on the melting model, by aspect or by radiation. This file allows to check that this distribution is correct: sufficient bands of different elevations - a minimum of 10 bands per glacier.
    
    - **“annual_potential_radiation.tif”:** shows the radiation. It allows to check if the radiation categories seem correct (high radiation on the southern flank, 3 categories forming approximately the same % of the surface...). This file is produced only if we use the Hock model! 
    
    - **“change_glacier.csv and change_ground.csv”:** over the years (columns), and for each HRU (rows), the area of the HRU which is either “glacier” or “ground” depending on the file you are looking at. For the moment, this file is created at the start of the simulation by linear interpolation between the years for which we have data (often GLAMOS data: https://www.glamos.ch/en/#/B45-04 ).
    
    - **“hydro_units.csv”:** the HRU. For each HRU, you will find their ID, the fraction of ground, their median elevation, their minimum elevation, their maximum elevation, their median radiation, their min radiation, their max radiation, their mean elevation, their area, their mean slope, their mean aspect, their mean latitude and their mean longitude. As far as these fields are concerned: their median elevation, their minimum elevation, their maximum elevation, their median radiation, their min radiation, their max radiation, these are in fact the criteria used to define the HRUs for this simulation. That's why you have the median and not the average. You'll only find information on radiation if you use the Hock model. For the one with the aspect, you'll find information on the aspect.
    
    - **“bootstrapping_stats.csv”:** the values obtained when we 1) block-bootstrapped the flows by taking one-year blocks to respect the seasonality of the flow in order to create 100 new series, 2) applied the NSE (Nash-Sutcliffe model efficiency criteria) and KGE (Kling-Gupta model efficiency criteria) to each of these series to compare them with the observed flow, 3) averaged these 100 NSE and KGE values (separately). This gives us a reference to know whether the KGE and NSE values obtained from our simulations are good or not.

    - **“best_fit_simulated_discharge_SCEUA…”:** all the files starting with “best_fit_simulated_discharge” are files in which the flow resulting from simulations is saved. “SCEUA” is the name of the convergence algorithm used to obtain the best result (see Argentin et al., 2024).
    
    - **“melt:degree_day”** means that the TI simple melt model has been used
    
    - **“melt:degree_day_aspect”** for the aspect-based melting model
    
    - **“melt:temperature_index”** for the radiation-based melting model (Hock model)

    - Lastly, there is the metric used to compare the results of each run: nse for Nash-Sutcliffe efficiency, kge_2012 for King-Gupta efficiency (2012) etc. The names correspond to those given by Hydroerr (https://hydroerr.readthedocs.io/en/stable/list_of_metrics.html).
    
    - **“best_fit_simulation_stats_SCEUA”:** it shows the simulation score and the associated parameters. The simulation score is in the first line (Minimal objective value). This is the value of the NSE or KGE depending on the metric chosen for the simulation. Below, you'll find the parameters here (https://hydrobricks.readthedocs.io/en/latest/doc/basics.html#parameters ) and in table 2 of Argentin et al., 2024. The number of parameters and the parameters change depending on the font model used.
    
    - **“results.nc”:** a NetCDF file with estimated results inherent to the basin.
https://github.com/ALArgentin/hydrobricks_AltroClima

Outputs Figures
    - Among the figure outputs, the most interesting are the “discharge_SCEUA_melt_degree_day_”. These graphs show the actual observed flow data against the flow data simulated by Hydrobricks, with the value of the function that best describes the actual data. 
