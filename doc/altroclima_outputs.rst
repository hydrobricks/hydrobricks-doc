Outputs
=======

The folders where the results are stored are called `OutputFigures` and `Outputs`. These folders are automatically created by Hydrobricks in the same path where the others are stored.

Outputs list:

- **“socont_...”**: Intermediate simulations before the best simulation is identified (e.g., "best_fit_..."). Useful for debugging.
- **“forcing.nc”**: NetCDF with climate inputs (precipitation, temperature, PET, radiation). See: https://hydrobricks.readthedocs.io/en/latest/doc/basics.html#forcing-data
- **“hydrobricks_...log”**: Log files of each simulation run (useful only if Hydrobricks crashes).
- **“unit_ids.tif”**: Distribution of HRUs (by elevation/aspect/radiation). Minimum 10 bands per glacier.
- **“annual_potential_radiation.tif”**: Radiation map. Helps verify radiation class correctness.
- **“change_glacier.csv” & “change_ground.csv”**: HRU area evolution over time, interpolated from data (e.g. GLAMOS: https://www.glamos.ch/en/#/B45-04).
- **“hydro_units.csv”**: Table with HRU properties (elevation, radiation, slope, area, coordinates, etc.).
- **“bootstrapping_stats.csv”**: Evaluation statistics (NSE, KGE) from bootstrapped time series.
- **“best_fit_simulated_discharge_SCEUA…”**: Final flow simulation output using best-fit parameters.
- **“melt:degree_day”**, **“melt:degree_day_aspect”**, **“melt:temperature_index”**: Indicates melt model used (TI, aspect-based, or Hock).
- **Efficiency metrics**: `nse`, `kge_2012`, etc. See: https://hydroerr.readthedocs.io/en/stable/list_of_metrics.html
- **“best_fit_simulation_stats_SCEUA”**: Simulation score (NSE/KGE) and fitted parameters. Also see: https://hydrobricks.readthedocs.io/en/latest/doc/basics.html#parameters
- **“results.nc”**: Main NetCDF output with modeled results.

Output Figures
--------------

Among the figure outputs, the most interesting are the `discharge_SCEUA_melt_degree_day_` plots. These show the simulated vs. observed discharge, often alongside the performance score.
