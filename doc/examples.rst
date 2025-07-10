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
    
    - In the “Clipped (extent)” window save the Clipped are with a “name.tif” (really important to add the ".tif" at the end of the name, Figure 3)

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
    
    - Layer  Create Layer  New Shapefile Layer
    
    - Specify the name (example TR_outlet_EPSG2056) and save it in the folder “Outlet_locations_on_dhm25”
    
    - Geometry type “Point” and EPSG:2056
    
    - Right-click on the newly created Layer  Toggle Editing  Add point feature 
    
    - Click on the point where there is the water intake

Sixth step: 
    Extract coordinates of the Outlet Point
    
    - Right-click on the new Outlet.shp ➔ Open Attribute table ➔ Open Field Calculator
    
    - In the middle panel, select Geometry ➔ Double-click on $x ➔ Set Output field name to “X-coord”, and Output field type to “Decimal number (real)”. Do the same for Y

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



Step 2: Train the Model
-----------------------

The training script uses the output from `load_data.py`.

.. literalinclude:: ../examples/workflow/train_model.py
   :language: python
   :caption: examples/workflow/train_model.py
   :linenos:


