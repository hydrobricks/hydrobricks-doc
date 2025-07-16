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
:doc:`altroclima_preprocessing`


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


Outputs
--------

Hydrobricks produces a variety of outputs stored in automatically created folders.

See detailed output descriptions here:  
:doc:`altroclima_outputs`
