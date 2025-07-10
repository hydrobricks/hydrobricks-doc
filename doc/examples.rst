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

First step: create a SHP file of the outlet location using the map of Switzerland
    Layer à Create Layer à New Shapefile Layer
    Specify the name (example TR_intake_EPSG2056) and save it in the folder “Inatkes_locations”
    Geometry type “Point” and EPSG:2056
    Right-click on the newly created Layer à Toggle Editing à Add point feature
    Click on the point where there is the outlet/water intake

Step 2: Train the Model
-----------------------

The training script uses the output from `load_data.py`.

.. literalinclude:: ../examples/workflow/train_model.py
   :language: python
   :caption: examples/workflow/train_model.py
   :linenos:


