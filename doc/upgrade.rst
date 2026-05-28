.. _upgrade:

Upgrade guide
=============

Only breaking changes that require attention are listed here. For a complete list of changes, see the
`changelog <https://github.com/hydrobricks/hydrobricks/blob/main/CHANGELOG.md>`_.

v0.7 to v0.8
------------

Breaking change2:

* The minimum Python version is now 3.10.
* Behaviours were renamed as Actions.
* Changing logging labels for content to type-specific labels 
  (``content`` becomes ``water_content``, ``ice`` becomes 
  ``ice_content``, ``snow`` becomes ``snow_content``).
* The extraction of meteorological data from netCDF files (``spatialize_from_gridded_data``) 
  has changed. The function now computes elevation gradients by default for temperature 
  and precipitation. In order to access to the DEM, the class must be initialized with the 
  catchment object (``forcing = hb.Forcing(catchment)``) instead of the hydro units object. 
  This gradient-based interpolation can be disabled with ``apply_data_gradient=False``.
* The functions ``model.is_ok()`` and ``parameters.is_ok()`` have been renamed to ``model.is_valid()`` 
  and ``parameters.are_valid()`` or ``parameters.is_valid()`` respectively.


v0.6 to v0.7
------------

Breaking change:

* The ``isohypse`` option has been renamed to ``equal_intervals`` in the 
  catchment discretization functions.


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
