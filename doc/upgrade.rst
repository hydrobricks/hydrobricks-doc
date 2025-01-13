.. _upgrade:

Upgrade guide
=============

v0.5 to v0.6
------------

Breaking change:

* Many changes in the Forcing class:
    * load_from_csv() was renamed to load_station_data_from_csv().
    * define_spatialization() was renamed to spatialize_from_station_data() and is only meant for spatialization from station data.
    * correct_station_data() was added and is to be used for applying a correction factor, for example.
    * spatialize_from_gridded_data() was added to load data from gridded netCDF files.
    * compute_pet() was added and uses the pyet package.
    * The operations are not performed immediately, but only applied when apply_operations() is called, which is done automatically before the model run or before saving the forcing data to a netcdf file.
* The Catchment class is now part of the main module.


v0.4 to v0.5
------------

Breaking change:

* Removing hyphens for underscores. Any component (including land cover elements) have to use underscores and not hyphens (e.g., glacier_ice instead of glacier-ice, slow_reservoir instead of slow-reservoir).
