Hydrobricks documentation
==========================

**A modular framework for building, calibrating and comparing conceptual
hydrological models.**

Hydrobricks assembles hydrological models from reusable components: storages,
land covers, snowpacks and glaciers (the *bricks*), the processes acting on
them, and the fluxes connecting them. The established models it ships with
(Socont, GR4J, GR6J, HBV, PREVAH) are built from the same components, so they
share one numerical core and one workflow. Changing a single process or
comparing whole model structures then becomes a matter of configuration rather
than a new code base. The computation engine is written in C++ and driven from
Python, which handles data preparation, model configuration and calibration.

The available models are described on the :ref:`models page<models>`.
The main building blocks of the framework are explained on the
:ref:`basics page<basics>`.
Additional resources contributed by the community are listed on the
:ref:`resources page<resources>`.

If you use hydrobricks in your work, please cite it:
`doi:10.5281/zenodo.7139899 <https://doi.org/10.5281/zenodo.7139899>`_
(this DOI always points to the latest release; the citation metadata is in
`CITATION.cff <https://github.com/hydrobricks/hydrobricks/blob/main/CITATION.cff>`_).


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   doc/getting-started
   doc/project-files
   doc/study-files
   doc/basics
   doc/models
   doc/processes
   doc/solvers
   doc/parameters
   doc/forcing
   doc/preprocessing
   doc/advanced
   doc/resources
   doc/upgrade
   doc/references
   api/modules
