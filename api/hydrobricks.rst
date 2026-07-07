Components
==========

.. automodule:: hydrobricks

.. _api_project:

Project files
-------------

.. autofunction:: hydrobricks.load_project

.. autoclass:: Project
   :members: run
   :show-inheritance:

.. _api_catchment:

Catchment
---------

.. autoclass:: Catchment
   :members:
   :undoc-members:
   :show-inheritance:

.. _api_hydrounits:

HydroUnits
----------

.. autoclass:: HydroUnits
   :members:
   :undoc-members:
   :show-inheritance:

.. _api_parameterset:

ParameterSet
------------

.. autoclass:: ParameterSet
   :members:
   :undoc-members:
   :show-inheritance:

.. _api_forcing:

Forcing
-------

.. autoclass:: Forcing
   :members:
   :undoc-members:
   :show-inheritance:

Discharge observations
----------------------

.. autoclass:: DischargeObservations
   :members:
   :undoc-members:
   :show-inheritance:

.. _api_periods:

Periods
-------

.. autoclass:: Period
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: Periods
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: hydrobricks.evaluate_periods

Results
-------

.. autoclass:: Results
   :members:
   :undoc-members:
   :show-inheritance:

TimeSeries
----------

.. autoclass:: TimeSeries
   :members:
   :undoc-members:
   :show-inheritance:

StructureGraph
--------------

.. autoclass:: hydrobricks.structure.StructureGraph
   :members:
   :undoc-members:
   :show-inheritance:

Trainer
-------

.. automodule:: hydrobricks.trainer

.. autoclass:: hydrobricks.trainer.SpotpySetup
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: hydrobricks.trainer.calibrate

.. autofunction:: hydrobricks.trainer.calibrate_from_factory

.. autofunction:: hydrobricks.trainer.get_best

.. autofunction:: hydrobricks.trainer.get_results

Evaluation (auxiliary observations)
-----------------------------------

.. automodule:: hydrobricks.evaluation

.. autoclass:: hydrobricks.evaluation.AuxiliaryObservation
   :members:
   :show-inheritance:

.. autoclass:: hydrobricks.evaluation.RecordingRequest
   :members:
   :show-inheritance:

.. autoclass:: hydrobricks.evaluation.GlacierMassBalanceObservations
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: hydrobricks.evaluation.SnowCoverObservations
   :members:
   :undoc-members:
   :show-inheritance:
