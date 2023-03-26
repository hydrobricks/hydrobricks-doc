.. _calibration:

Calibration
===========

Calibration/analysis using SPOTPY
---------------------------------

The calibration and sensitivity analyses are performed by the
`SPOTPY package <https://spotpy.readthedocs.io/en/latest/>`_.
The links to SPOTPY are provided by hydrobricks so that it can be used directly.

As we might not want to calibrate all parameters, those that can change have to
be specified in the ``parameters`` instance (see :ref:`parameters <parameters>`):

.. code-block:: python

   parameters.allow_changing = ['a_snow', 'k_quick', 'A', 'k_slow_1', 'percol',
                                'k_slow_2', 'precip_corr_factor']

Then, an instance of the SPOTPY setup can be created by providing the
:ref:`model instance <model-instance>`, the :ref:`parameters <parameters>`, the
:ref:`forcing <forcing-data>`, the observation time series, a warmup duration (in days),
and the objective function to use:

.. code-block:: python

   spot_setup = hb.SpotpySetup(socont, parameters, forcing, obs, warmup=365,
                               obj_func='mse')

SPOTPY only maximizes the metric value.
Thus, when the metric needs to be minimized, we need to invert the objective function:

.. code-block:: python

   spot_setup = hb.SpotpySetup(socont, parameters, forcing, obs, warmup=365,
                               obj_func='kge_2012', invert_obj_func=True)

Once the setup defined, one can use any
`SPOTPY algorithm <https://spotpy.readthedocs.io/en/latest/Algorithm_guide/>`_.
For example, an optimization using the SCE-UA algorithm can be performed:

.. code-block:: python

   # Select number of maximum repetitions and run spotpy
   sampler = spotpy.algorithms.sceua(spot_setup, dbname='socont_SCEUA', dbformat='csv')
   max_rep = 10000
   sampler.sample(max_rep)

Similarly, a Monte-Carlo analysis can be performed:

.. code-block:: python

   sampler = spotpy.algorithms.mc(spot_setup, dbname='socont_MC', dbformat='csv',
                                  save_sim=False)
   sampler.sample(10000)

Then, the SPOTPY results can be loaded for analysis:

.. code-block:: python

   # Load the results
   results = sampler.getdata()

   # Plot parameter interaction
   spotpy.analyser.plot_parameterInteraction(results)
   plt.tight_layout()
   plt.show()

   # Plot posterior parameter distribution
   posterior = spotpy.analyser.get_posterior(results, percentage=10)
   spotpy.analyser.plot_parameterInteraction(posterior)
   plt.tight_layout()
   plt.show()

Prior distributions
-------------------

The default prior distribution is a uniform distribution in the range provided by the
min/max parameter values.
The prior distribution can be changed before the calibration/analysis using the
``set_prior()`` function on the ``parameters`` instance:

.. code-block:: python

   parameters.set_prior('a_snow', spotpy.parameter.Normal(mean=4, stddev=2))

Prebuild parameter distribution functions provided by SPOTPY: Uniform, Normal,
logNormal, Chisquare, Exponential, Gamma, Wald, Weilbull.