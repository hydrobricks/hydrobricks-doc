.. _upgrade:

Upgrade guide
=============

v0.7 to v0.8
------------

No breaking changes.

New features:

* GR4J daily rainfall-runoff model added (see :ref:`GR4J <gr4j>`).
* CemaNeige snow model and rain/snow splitter added
  (see :ref:`processes page <processes>`).
* Simple area-scaling glacier evolution method added
  (see :ref:`area-scaling <glacier_evolution_area_scaling>`).


v0.6 to v0.7
------------

No breaking changes.


v0.5 to v0.6
------------

Breaking changes in the ``Forcing`` class:

* ``load_from_csv()`` was renamed to ``load_station_data_from_csv()``.
* ``define_spatialization()`` was renamed to ``spatialize_from_station_data()``
  and is now reserved for spatialization from station data.
* ``correct_station_data()`` was added for applying correction factors to raw
  station data.
* ``spatialize_from_gridded_data()`` was added for loading from gridded NetCDF
  files.
* ``compute_pet()`` was added and uses the pyet package.
* Operations are no longer applied immediately. They are queued and applied
  automatically before the model run or before saving to a NetCDF file (via
  ``apply_operations()``, called internally).

Other changes:

* The ``Catchment`` class is now part of the main ``hydrobricks`` module
  (previously in a submodule).


v0.4 to v0.5
------------

Breaking change:

* Hyphens replaced with underscores in all component names. Any land cover or
  model component name must use underscores instead of hyphens
  (e.g., ``glacier_ice`` instead of ``glacier-ice``,
  ``slow_reservoir`` instead of ``slow-reservoir``).
