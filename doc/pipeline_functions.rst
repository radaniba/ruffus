.. include:: global.inc
.. _pipeline_functions:

See :ref:`Decorators <decorators>` for more decorators

.. |pipeline_run| replace:: `pipeline_run`
.. _pipeline_run: `pipeline_functions.pipeline_run`_
.. |pipeline_printout| replace:: `pipeline_printout`
.. _pipeline_printout: `pipeline_functions.pipeline_printout`_
.. |pipeline_printout_graph| replace:: `pipeline_printout_graph`
.. _pipeline_printout_graph: `pipeline_functions.pipeline_printout_graph`_

.. |pr_target_tasks| replace:: `target_tasks`
.. _pr_target_tasks: `pipeline_functions.pipeline_run.target_tasks`_
.. |pr_forcedtorun_tasks| replace:: `forcedtorun_tasks`
.. _pr_forcedtorun_tasks: `pipeline_functions.pipeline_run.forcedtorun_tasks`_
.. |pr_multiprocess| replace:: `multiprocess`
.. _pr_multiprocess: `pipeline_functions.pipeline_run.multiprocess`_
.. |pr_logger| replace:: `logger`
.. _pr_logger: `pipeline_functions.pipeline_run.logger`_
.. |pr_gnu_make| replace:: `gnu_make_maximal_rebuild_mode`
.. _pr_gnu_make: `pipeline_functions.pipeline_run.gnu_make`_
.. |pr_verbose| replace:: `verbose`
.. _pr_verbose: `pipeline_functions.pipeline_run.verbose`_
.. |pr_runtime_data| replace:: `runtime_data`
.. _pr_runtime_data: `pipeline_functions.pipeline_run.runtime_data`_
.. |pr_one_second_per_job| replace:: `one_second_per_job`
.. _pr_one_second_per_job: `pipeline_functions.pipeline_run.one_second_per_job`_
.. |pr_touch_files_only| replace:: `touch_files_only`
.. _pr_touch_files_only: `pipeline_functions.pipeline_run.touch_files_only`_



.. |pp_output_stream| replace:: `output_stream`
.. _pp_output_stream: `pipeline_functions.pipeline_printout.output_stream`_
.. |pp_target_tasks| replace:: `target_tasks`
.. _pp_target_tasks: `pipeline_functions.pipeline_printout.target_tasks`_
.. |pp_forcedtorun_tasks| replace:: `forcedtorun_tasks`
.. _pp_forcedtorun_tasks: `pipeline_functions.pipeline_printout.forcedtorun_tasks`_
.. |pp_verbose| replace:: `verbose`
.. _pp_verbose: `pipeline_functions.pipeline_printout.verbose`_
.. |pp_indent| replace:: `indent`
.. _pp_indent: `pipeline_functions.pipeline_printout.indent`_
.. |pp_wrap_width| replace:: `wrap_width`
.. _pp_wrap_width: `pipeline_functions.pipeline_printout.wrap_width`_
.. |pp_gnu_make| replace:: `gnu_make_maximal_rebuild_mode`
.. _pp_gnu_make: `pipeline_functions.pipeline_printout.gnu_make`_
.. |pp_runtime_data| replace:: `runtime_data`
.. _pp_runtime_data: `pipeline_functions.pipeline_printout.runtime_data`_




.. |ppg_stream| replace:: `stream`
.. _ppg_stream: `pipeline_functions.pipeline_printout_graph.stream`_
.. |ppg_output_format| replace:: `output_format`
.. _ppg_output_format: `pipeline_functions.pipeline_printout_graph.output_format`_
.. |ppg_target_tasks| replace:: `target_tasks`
.. _ppg_target_tasks: `pipeline_functions.pipeline_printout_graph.target_tasks`_
.. |ppg_forcedtorun_tasks| replace:: `forcedtorun_tasks`
.. _ppg_forcedtorun_tasks: `pipeline_functions.pipeline_printout_graph.forcedtorun_tasks`_
.. |ppg_draw_vertically| replace:: `draw_vertically`
.. _ppg_draw_vertically: `pipeline_functions.pipeline_printout_graph.draw_vertically`_
.. |ppg_ignore_upstream_of_target| replace:: `ignore_upstream_of_target`
.. _ppg_ignore_upstream_of_target: `pipeline_functions.pipeline_printout_graph.ignore_upstream_of_target`_
.. |ppg_skip_uptodate_tasks| replace:: `skip_uptodate_tasks`
.. _ppg_skip_uptodate_tasks: `pipeline_functions.pipeline_printout_graph.skip_uptodate_tasks`_
.. |ppg_gnu_make| replace:: `gnu_make_maximal_rebuild_mode`
.. _ppg_gnu_make: `pipeline_functions.pipeline_printout_graph.gnu_make`_
.. |ppg_test_all_task_for_update| replace:: `test_all_task_for_update`
.. _ppg_test_all_task_for_update: `pipeline_functions.pipeline_printout_graph.test_all_task_for_update`_
.. |ppg_no_key_legend| replace:: `no_key_legend`
.. _ppg_no_key_legend: `pipeline_functions.pipeline_printout_graph.no_key_legend`_
.. |ppg_minimal_key_legend| replace:: `minimal_key_legend`
.. _ppg_minimal_key_legend: `pipeline_functions.pipeline_printout_graph.minimal_key_legend`_
.. |ppg_pipeline_name| replace:: `pipeline_name`
.. _ppg_pipeline_name: `pipeline_functions.pipeline_printout_graph.pipeline_name`_
.. |ppg_user_colour_scheme| replace:: `user_colour_scheme`
.. _ppg_user_colour_scheme: `pipeline_functions.pipeline_printout_graph.user_colour_scheme`_
.. |ppg_size| replace:: `size`
.. _ppg_size: `pipeline_functions.pipeline_printout_graph.size`_
.. |ppg_dpi| replace:: `dpi`
.. _ppg_dpi: `pipeline_functions.pipeline_printout_graph.dpi`_
.. |ppg_runtime_data| replace:: `runtime_data`
.. _ppg_runtime_data: `pipeline_functions.pipeline_printout_graph.runtime_data`_
    
    
    






################################################
Pipeline functions
################################################

    There are only three functions for **Ruffus** pipelines:

        * |pipeline_run|_ executes a pipeline
        * |pipeline_printout|_ prints a list of tasks and jobs which will be run in a pipeline
        * |pipeline_printout_graph|_ prints a schematic flowchart of pipeline tasks in various graphical formats

.. _pipeline_functions.pipeline_run:

.. index:: 
    single: pipeline functions; pipeline_run
    pair: pipeline_run; Run pipeline

**************************************************************************************************************************************************************************************
*pipeline_run*
**************************************************************************************************************************************************************************************
**pipeline_run** ( |pr_target_tasks|_, [ |pr_forcedtorun_tasks|_ = [], |pr_multiprocess|_ = 1, |pr_logger|_ = stderr_logger, |pr_gnu_make|_ = True, |pr_verbose|_ =1], |pr_runtime_data|_ = None, |pr_one_second_per_job|_ = True, |pr_touch_files_only|_ = False)

    **Purpose:**

        Runs all specified pipelined functions if they or any antecedent tasks are 
        incomplete or out-of-date.
        
    **Example**:
        ::

            #
            #   Run task2 whatever its state, and also task1 and antecedents if they are incomplete
            #   Do not log pipeline progress messages to stderr
            #            
            pipeline_run([task1, task2], forcedtorun_tasks = [task2], logger = blackhole_logger)

    **Parameters:**



.. _pipeline_functions.pipeline_run.target_tasks:

    * *target_tasks*
        Pipeline functions and any necessary antecedents (specified implicitly or with :ref:`@follows <decorators.follows>`)
        which should be invoked with the appropriate parameters if they are incomplete or out-of-date.

.. _pipeline_functions.pipeline_run.forcedtorun_tasks:

    * *forcedtorun_tasks*
        Optional. These pipeline functions will be invoked regardless of their state.
        Any antecedents tasks will also be executed if they are out-of-date or incomplete.

.. _pipeline_functions.pipeline_run.multiprocess:

    * *multiprocess*
        Optional. The number of processes which should be dedicated to running in parallel independent 
        tasks and jobs within each task. If ``multiprocess`` is set to 1, the pipeline will
        execute in the main process.
        
.. _pipeline_functions.pipeline_run.logger:

    * *logger*
        For logging messages indicating the progress of the pipeline in terms of tasks and jobs.
        Defaults to outputting to sys.stderr.
        Setting ``logger=blackhole_logger`` will prevent any logging output.

.. _pipeline_functions.pipeline_run.gnu_make:

    * *gnu_make_maximal_rebuild_mode*
        .. warning ::
            This is a dangerous option. Use rarely and with caution

        Optional parameter governing how **Ruffus** determines which part of the pipeline is
        out of date and needs to be re-run. If set to ``False``, **ruffus** will work back
        from the ``target_tasks`` and only execute the pipeline after the first up-to-date
        tasks that it encounters. For example, if there are four tasks:
        
            ::
            
                #  
                #   task1 -> task2 -> task3 -> task4 -> task5
                #
                target_tasks = [task5]
                
        If ``task3()`` is up-to-date, then only ``task4()`` and ``task5()`` will be run.
        This will be the case even if ``task2()`` and ``task1()`` are incomplete.
        
        This allows you to remove all intermediate results produced by ``task1 -> task3``.
        


.. _pipeline_functions.pipeline_run.verbose:

    * *verbose*
        Optional parameter indicating the verbosity of the messages sent to ``logger``:
    
            ::
            
                verbose = 0 : prints nothing
                verbose = 1 : logs warnings and tasks which are not up-to-date and which will be run
                verbose = 2 : logs doc strings for task functions as well
                verbose = 3 : logs job parameters for jobs which are out-of-date
                verbose = 4 : logs list of up-to-date tasks but parameters for out-of-date jobs
                verbose = 5 : logs parameters for all jobs whether up-to-date or not
                verbose = 10: logs messages useful only for debugging ruffus pipeline code


        ``verbose >= 10`` are intended for debugging **Ruffus** by the developers and the details
        are liable to change from release to release
        
.. _pipeline_functions.pipeline_run.runtime_data:

    * *runtime_data*
        Experimental feature for passing data to tasks at run time

.. _pipeline_functions.pipeline_run.one_second_per_job:

    * *one_second_per_job*
        By default, **Ruffus** ensures jobs take a minimum of 1 second to complete, to get around
        coarse grained timestamps in some file systems. This is rarely an issue when many jobs run
        *in parallel*. If your file system has sub-second time stamps, you can turn off this delay
        by setting *one_second_per_job* to ``False``

.. _pipeline_functions.pipeline_run.touch_files_only:

    * *touch_files_only*
        Create or update output files only to simulate the running of the pipeline. 
        Does not invoke real task functions to run jobs. This is most useful to force a 
        pipeline to acknowledge that a particular part is now up-to-date.
        
        This will not work properly if the identities of some files are not known before hand, 
        and depend on run time. In other words, not recommended if ``@split`` or custom parameter generators are being used.


.. _pipeline_functions.pipeline_printout:

.. index:: 
    single: pipeline functions; pipeline_run
    pair: pipeline_printout; Printout simulated run of the pipeline

**********************************************************************************************************************************************************************************************************
*pipeline_printout*
**********************************************************************************************************************************************************************************************************
**pipeline_printout** (|pp_output_stream|_, |pp_target_tasks|_, |pp_forcedtorun_tasks|_ = [], |pp_verbose|_ = 1, |pp_indent|_ = 4, |pp_gnu_make|_ = True, |pp_wrap_width|_ = 100, |pp_runtime_data|_ = None)

    **Purpose:**

        Prints out all the pipelined functions which will be invoked given specified ``target_tasks``
        without actually running the pipeline. Because this is a simulation, some of the job
        parameters may be incorrect. For example, the results of a :ref:`@split<manual.split>`
        operation is not predetermined and will only be known after the pipelined function
        splits up the original data. Parameters of all downstream pipelined functions will
        be changed depending on this initial operation.

    **Example**:
        ::

            #
            #   Simulate running task2 whatever its state, and also task1 and antecedents
            #     if they are incomplete
            #   Print out results to STDOUT
            #            
            pipeline_printout(sys.stdout, [task1, task2], forcedtorun_tasks = [task2], verbose = 1)

    **Parameters:**

.. _pipeline_functions.pipeline_printout.output_stream:

    * *output_stream*
        Where to printout the results of simulating the running of the pipeline.
        
.. _pipeline_functions.pipeline_printout.target_tasks:

    * *target_tasks*
        As in :ref:`pipeline_run<pipeline_functions.pipeline_run>`: Pipeline functions and any necessary antecedents (specified implicitly or with :ref:`@follows <decorators.follows>`)
        which should be invoked with the appropriate parameters if they are incomplete or out-of-date.


.. _pipeline_functions.pipeline_printout.forcedtorun_tasks:

    * *forcedtorun_tasks*
        As in :ref:`pipeline_run<pipeline_functions.pipeline_run>`:These pipeline functions will be invoked regardless of their state.
        Any antecedents tasks will also be executed if they are out-of-date or incomplete.

        
.. _pipeline_functions.pipeline_printout.verbose:

    * *verbose*
        Optional parameter indicating the verbosity of the printout.
        Please do not expect messages to stay constant between release
    
            ::

                verbose = 0 : prints nothing
                verbose = 1 : logs warnings and tasks which are not up-to-date and which will be run
                verbose = 2 : logs doc strings for task functions as well
                verbose = 3 : logs job parameters for jobs which are out-of-date
                verbose = 4 : logs list of up-to-date tasks but parameters for out-of-date jobs
                verbose = 5 : logs parameters for all jobs whether up-to-date or not
                verbose = 10: logs messages useful only for debugging ruffus pipeline code


.. _pipeline_functions.pipeline_printout.indent:

    * *indent*
        Optional parameter governing the indentation when printing out the component job 
        parameters of each task function.


.. _pipeline_functions.pipeline_printout.gnu_make:

    * *gnu_make_maximal_rebuild_mode*
        .. warning ::
            This is a dangerous option. Use rarely and with caution

        See explanation in :ref:`pipeline_run <pipeline_functions.pipeline_run.gnu_make>`.
        
.. _pipeline_functions.pipeline_printout.wrap_width:

    * *wrap_width*
        Optional parameter governing the length of each line before it starts wrapping
        around.


.. _pipeline_functions.pipeline_printout.runtime_data:

    * *runtime_data*
        Experimental feature for passing data to tasks at run time


        
.. _pipeline_functions.pipeline_printout_graph:

.. index:: 
    single: pipeline functions; pipeline_printout_graph
    pair: pipeline_printout_graph; print flowchart representation of pipeline functions



************************************************************************************************************************************************************************************************************************************************************************************
*pipeline_printout_graph*
************************************************************************************************************************************************************************************************************************************************************************************

**pipeline_printout_graph** (|ppg_stream|_, |ppg_output_format|_, |ppg_target_tasks|_, |ppg_forcedtorun_tasks|_ = [], |ppg_ignore_upstream_of_target|_ = False, |ppg_skip_uptodate_tasks|_ = False, |ppg_gnu_make|_ = True, |ppg_test_all_task_for_update|_ = True, |ppg_no_key_legend|_  = False, |ppg_minimal_key_legend|_ = True, |ppg_user_colour_scheme|_ = None, |ppg_pipeline_name|_ = "Pipeline", |ppg_size|_ = (11,8), |ppg_dpi|_ = 120, |ppg_runtime_data|_ = None)

    **Purpose:**

        Prints out flowchart of all the pipelined functions which will be invoked given specified ``target_tasks``
        without actually running the pipeline.

        See :ref:`Flowchart colours <flowchart_colours>` 

    **Example**:
        ::

            pipeline_printout_graph("flowchart.jpg", "jpg", [task1, task16], 
                                        forcedtorun_tasks = [task2], 
                                        no_key_legend = True)

    **Parameters:**

.. _pipeline_functions.pipeline_printout_graph.stream:

    * *stream*
        The file or file-like object to which the flowchart should be printed. 
        If a string is provided, it is assumed that this is the name of the output file
        which will be opened automatically.
        

.. _pipeline_functions.pipeline_printout_graph.output_format:

    * *output_format*
        | If the programme ``dot`` can be found on the executio path, this
          can be any number of `formats <http://www.graphviz.org/doc/info/output.html>`_
          supported by `Graphviz <http://www.graphviz.org/>`_, including, for example,
          ``jpg``, ``png``, ``pdf``, ``svg`` etc.
        | Otherwise, **ruffus** will only output in the `dot <http://en.wikipedia.org/wiki/DOT_language>`_ format, which
          is a plain-text graph description language.
        
.. _pipeline_functions.pipeline_printout_graph.target_tasks:

    * *target_tasks*
        As in :ref:`pipeline_run<pipeline_functions.pipeline_run>`: Pipeline functions and any necessary antecedents (specified implicitly or with :ref:`@follows <decorators.follows>`)
        which should be invoked with the appropriate parameters if they are incomplete or out-of-date.


.. _pipeline_functions.pipeline_printout_graph.forcedtorun_tasks:

    * *forcedtorun_tasks*
        As in :ref:`pipeline_run<pipeline_functions.pipeline_run>`:These pipeline functions will be invoked regardless of their state.
        Any antecedents tasks will also be executed if they are out-of-date or incomplete.
        
.. _pipeline_functions.pipeline_printout_graph.draw_vertically:

    * *draw_vertically*
        Draw flowchart in vertical orientation

.. _pipeline_functions.pipeline_printout_graph.ignore_upstream_of_target:

    * *ignore_upstream_of_target*
        Start drawing flowchart from specified target tasks. Do not draw tasks which are
        downstream (subsequent) to the targets.

.. _pipeline_functions.pipeline_printout_graph.skip_uptodate_tasks:

    * *ignore_upstream_of_target*
        Do not draw up-to-date / completed tasks in the flowchart unless they are 
        lie on the execution path of the pipeline.
        
.. _pipeline_functions.pipeline_printout_graph.gnu_make:

    * *gnu_make_maximal_rebuild_mode*
        .. warning ::
            This is a dangerous option. Use rarely and with caution

        See explanation in :ref:`pipeline_run <pipeline_functions.pipeline_run.gnu_make>`.

.. _pipeline_functions.pipeline_printout_graph.test_all_task_for_update:

    * *test_all_task_for_update*
        | Indicates whether intermediate tasks are out of date or not. Normally **Ruffus** will
          stop checking dependent tasks for completion or whether they are out-of-date once it has
          discovered the maximal extent of the pipeline which has to be run.
        | For displaying the flow of the pipeline, this is hardly very informative. 

.. _pipeline_functions.pipeline_printout_graph.no_key_legend:

    * *no_key_legend*
        Do not include key legend explaining the colour scheme of the flowchart.


.. _pipeline_functions.pipeline_printout_graph.minimal_key_legend:

     * *minimal_key_legend*
        Do not include unused task types in key legend.

.. _pipeline_functions.pipeline_printout_graph.user_colour_scheme:

     * *user_colour_scheme*
        Dictionary specifying colour scheme for flowchart

        | Colours can be names e.g. ``"black"`` or quoted hex e.g. ``'"#F6F4F4"'`` (note extra quotes)
        | Default values will be used unless specified

        .. csv-table::
           :header: "key", "Subkey", ""

           "
           - ``'colour_scheme_index'`` ", "| index of default colour scheme, 
           | 0-7, defaults to 0 unless specified", ""
           "
           - ``'Final target'``
           - ``'Explicitly specified task'``
           - ``'Task to run'``
           - ``'Down stream'``
           - ``'Up-to-date Final target'``
           - ``'Up-to-date task forced to rerun'``
           - ``'Up-to-date task'``
           - ``'Vicious cycle'``                  
           ","
           - ``'fillcolor'``
           - ``'fontcolor'``
           - ``'color'``    
           - ``'dashed'``   = ``0/1``
           ", "Colours / attributes for each task type"
           "
           - ``'Vicious cycle'``
           - ``'Task to run'``
           - ``'Up-to-date'``", "- ``'linecolor'``", "Colours for arrows between tasks"
           "- ``'Pipeline'``",  "- ``'fontcolor'``","Flowchart title colour"
           "- ``'Key'``", "
           - ``'fontcolor'``
           - ``'fillcolor'``", "Legend colours"

        Example:

            Use colour scheme index  = 1
            ::

                pipeline_printout_graph ("flowchart.svg", "svg", [final_task],
                                         user_colour_scheme = {
                                                                "colour_scheme_index" :1,
                                                                "Pipeline"      :{"fontcolor" : '"#FF3232"' },
                                                                "Key"           :{"fontcolor" : "Red",      
                                                                                  "fillcolor" : '"#F6F4F4"' },
                                                                "Task to run"   :{"linecolor" : '"#0044A0"' },
                                                                "Final target"  :{"fillcolor" : '"#EFA03B"',
                                                                                  "fontcolor" : "black",    
                                                                                  "dashed"    : 0           }
                                                               })




.. _pipeline_functions.pipeline_printout_graph.pipeline_name:

     * *pipeline_name*
        Specify title for flowchart

.. _pipeline_functions.pipeline_printout_graph.size:

     * *size*
        Size in inches for flowchart

.. _pipeline_functions.pipeline_printout_graph.dpi:

     * *dpi*
        Resolution in dots per inch. Ignored for svg output

.. _pipeline_functions.pipeline_printout_graph.runtime_data:

     * *runtime_data*
        Experimental feature for passing data to tasks at run time

