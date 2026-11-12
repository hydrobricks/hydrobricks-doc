.. _upgrade:

Upgrade guide
=============

Only the changes that require attention are listed here: breaking changes (code or files to
update) and behaviour changes (results that differ, or inputs that are now rejected). For a
complete list of changes, see the
`changelog <https://github.com/hydrobricks/hydrobricks/blob/main/CHANGELOG.md>`_.

v0.9.5 to v0.9.6
----------------

Behaviour changes:

* The ``'quantiles'`` method of ``create_elevation_bands()`` and ``discretize_by()``
  (elevation, slope and radiation) now creates ``number`` classes; it created one
  fewer. Hydro units built with it get one class more than before, so regenerate
  them (and their parameter sets, if they are set per unit).
* ``transport:snow_slide``: the default ``snow_slide_min_snow_depth`` is now 200 mm
  of snow depth (was 50 mm). Runs with the snow slide hold more snow on steep slopes;
  set the parameter to 50 to get the previous behaviour.
* ``melt:temperature_index``: ``radiation_coefficient`` (``r_snow``, ``r_ice``) has a
  maximum of 0.05 (was 1), and ``melt_factor`` a minimum of 0.5 mm/d/°C (was 0).
  Parameter sets with values outside these bounds are now rejected. Socont
  calibrates ``r_snow`` in [0.001, 0.03].
* PREVAH-UniBE: ``k_gw3`` is linked to ``k_gw1 / 9`` and no longer calibrated, and
  ``k0``, ``k1``, ``k_gw1`` and ``k_gw2`` have narrower ranges. A value given to
  ``k_gw3`` is overridden, with a warning; call ``parameters.unlink_parameter('k_gw3')``
  to set it freely. Calibrations of earlier versions are not directly comparable.
* Socont: the constraint ``k_slow_2 < k_slow_1`` is removed and ``beta`` is calibrated
  in log space over [100, 100000]. Add
  ``parameters.define_constraint('k_slow_2', '<', 'k_slow_1')`` to keep the order.

v0.9.4 to v0.9.5
----------------

Behaviour changes:

* Socont's slow reservoir uses ``et:hbv`` by default (was ``et:socont``), which adds
  the parameter ``lp``. Socont results change; use ``preset='original'`` or
  ``soil_et_process='et:socont'`` for the published model.
* ``Forcing.compute_pet(method='Hamon_vapor_density')`` was up to 18 % low in summer.
  The PET, and the results of runs using it, change.
* ``et:prevah`` no longer evaporates where ``lp * fc`` is zero (e.g. bare rock).
* ``snow_correction_factor`` has the range [0.5, 1.5] (was [0.8, 1.6]): values above
  1.5 are now rejected. The constraint ``rain_correction_factor <=
  snow_correction_factor`` is removed.
* ``set_spatial()`` and ``set_spatial_monthly()`` values are range-checked at
  ``setup()``/``run()``; out-of-range values per unit now raise an error.
* Project files and ``Project.calibrate()`` calibrate with ``dds`` by default (was
  ``sceua``); set ``calibration.algorithm: sceua`` to keep the former one. The
  calibration examples are renamed ``calibrate_dds_socont.py`` and
  ``calibrate_dds_socont_parallel.py``.

v0.9.3 to v0.9.4
----------------

Behaviour changes:

* HBV-96: the field capacity ``fc`` is capped at 1000 mm by default (was 3000 mm), and
  ``alpha`` has the range [0, 2] (was [0, 3]). Parameter sets beyond these bounds are
  rejected; widen them with ``parameter_ranges`` if needed.
* Project files: a ``calibration.link`` whose driving parameter range does not lie
  within that of the linked parameter is refused when the project is loaded.
* A change rate that is not a number, or a PET containing NaN (e.g. from crossed Tmin
  and Tmax), now raises an error instead of silently disabling the storage
  constraints of the brick.
* Capped stores with an overflow add the excess to the overflow rate instead of
  replacing it. Results of all solvers can differ slightly.

v0.9.2 to v0.9.3
----------------

Behaviour changes:

* The default solver is ``exponential_euler`` (was ``crank_nicolson``). Models relying
  on the default give slightly different results; pass ``solver='crank_nicolson'`` to
  keep the former one. PREVAH-UniBE and GR4J/GR6J keep their own defaults.
* HBV-96 with per-class soils and PREVAH-UniBE with ``share_soil=False``:
  ``fc_<cover>`` is now the capacity of the cover's own soil (mm over the cover area),
  not a share of the unit's soil. Calibrated values do not carry over.
* Water passed from a land cover or a snowpack to a storage is no longer delayed by
  one time step, which changes the results of all models.
* ``sub_basin`` is spelled ``subbasin`` in the API and the results file (e.g.
  ``attach_to: subbasin``, ``add_subbasin_brick()``); the old spellings are still
  accepted on input. The results file gains a ``subbasins`` dimension
  (``format_version = 2``); hydrobricks still reads the former layout, but scripts
  reading the NetCDF file directly must be updated.

v0.9.1 to v0.9.2
----------------

Breaking changes:

* The minimum Python version is now 3.11 (Python 3.10 reached its end of life in
  October 2026). The ``StrEnum`` back-port is no longer a dependency: the
  standard library has provided ``enum.StrEnum`` since 3.11.
* The HBV open-water land cover ``lake`` is renamed ``water``, and its outflow
  parameter alias ``k_lake`` (or ``k_lake_<cover>``) becomes ``k_water`` (or
  ``k_water_<cover>``). The name ``lake`` is no longer accepted as a cover type: it
  is reserved for a future regulated lake or reservoir cover with its own release
  rules. Rename the cover type in the land cover definitions and the hydro units
  files (``lake`` to ``water``), and the parameter in the parameter sets and
  project files (``k_lake`` to ``k_water``).
* Project files with lateral processes (e.g. ``transport:snow_slide``) must declare
  ``hydro_units.connectivity``; they are rejected otherwise.

v0.9.0 to v0.9.1
----------------

Breaking changes:

* Project-file keys were renamed after the Python API parameters they map to;
  the former keys are rejected as unknown:

  - ``forcing.gridded.<var>.elevation_gradient`` → ``apply_data_gradient``
  - ``forcing.gridded.<var>.crs`` → ``data_crs``
  - ``hydro_units.land_cover_areas`` → ``columns_areas``
  - ``forcing.pet.latitude`` → ``lat``

v0.8 to v0.9
------------

Breaking changes:

* The observation and evaluation classes moved to a new
  ``hydrobricks.evaluation`` subpackage, and the old ``hydrobricks.observations``
  module is gone. The classes stay importable from the top level, so
  ``hb.DischargeObservations``, ``hb.AuxiliaryObservation``,
  ``hb.GlacierMassBalanceObservations``, ``hb.SnowCoverObservations`` and
  ``hb.evaluate`` keep working. Only explicit module imports must be updated:
  replace ``from hydrobricks.observations import ...`` with the top-level access
  (``import hydrobricks as hb`` then ``hb.DischargeObservations``) or with
  ``from hydrobricks.evaluation import DischargeObservations``.
* The discharge observations class ``Observations`` was renamed
  ``DischargeObservations``, and the calibration argument ``obs`` (in
  ``SpotpySetup``) was renamed ``discharge``. Update instantiations
  (``hb.Observations(...)`` becomes ``hb.DischargeObservations(...)``) and the
  calibration setup (``SpotpySetup(..., obs=...)`` becomes
  ``SpotpySetup(..., discharge=...)``).
* The default land cover is now ``open`` instead of ``ground``. The names
  ``ground``, ``generic`` and ``generic_land_cover`` are still accepted as
  aliases, so existing model definitions keep running, but the output labels of
  a default run change from ``ground:*`` to ``open:*`` (e.g. ``ground:outflow``
  becomes ``open:outflow``). Update any post-processing that looks up results by
  these labels, or name the land cover explicitly.


v0.7 to v0.8
------------

Breaking changes:

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
* The count getters were renamed (e.g. ``get_hydro_unit_nb()`` becomes
  ``get_hydro_unit_count()``).
* ``Catchment.calculate_connectivity()``: ``force_connectivity`` is ``False`` by
  default (was ``True``).


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
