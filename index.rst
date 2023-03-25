hydrobricks' documentation
==========================

Hydrobricks is a flexible hydrological modelling framework.
Its core is written in C++ and it has a Python interface.
More specifically, the processes, fluxes and solver are coded in the C++ core,
while data preparation is done with Python.
The objective is to use Python wherever possible, and in particular for data processing,
and C++ where necessary, for performance reasons.

Hydrobricks comes with pre-build model structures, but it aims at allowing structure
definition from the user through the Python API.
The existing model structures can be found under the :ref:`models page<models>`.
The main components of the model are described under the :ref:`basics page<basics>`.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   doc/getting-started
   doc/main-components
   doc/models
   doc/calibration
   api/modules

