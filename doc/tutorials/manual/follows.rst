.. include:: ../../global.inc
.. include:: chapter_numbers.inc

.. _manual.follows:

#################################################################################################
|manual.follows.chapter_num| : `Arranging tasks into a pipeline with` **@follows**
#################################################################################################

    * :ref:`Manual overview <manual>` 
    * :ref:`@follows syntax in detail <decorators.follows>`
    
    .. index:: 
        pair: @follows; Manual


***************************************
**@follows**
***************************************

    The order in which stages or :term:`task`\ s of a pipeline are arranged are set
    explicitly by the :ref:`@follows(...) <decorators.follows>` python decorator:
    
        ::
    
            from ruffus import *
            import sys
            
            def first_task():
                print "First task"
        
            @follows(first_task)
            def second_task():
                print "Second task"
        
            @follows(second_task)
            def final_task():
                print "Final task"

    
    the ``@follows`` decorator indicate that the ``first_task`` function precedes ``second_task`` in 
    the pipeline.


.. note::

    We shall see in :ref:`Chapter 2 <manual.tasks_as_input>` that the order of pipeline :term:`task`\ s can also be inferred implicitly 
    for the following decorators

        * :ref:`@split(...) <manual.split>`
        * :ref:`@transform(...) <manual.transform>`
        * :ref:`@merge(...) <manual.merge>`
        * :ref:`@collate(...) <manual.collate>`

.. index:: 
    pair: pipeline_run; Manual

=====================
Running
=====================

    Now we can run the pipeline by:
        ::
            
            pipeline_run([final_task])
    
    
    Because ``final_task`` depends on ``second_task`` which depends on ``first_task`` , all 
    three functions will be executed in order.
    
.. index:: 
    pair: pipeline_printout_graph; Manual
    pair: pipeline_printout; Manual

    
=====================
Displaying
=====================

    We can see a flowchart of our fledgling pipeline by executing:
        ::
        
            pipeline_printout_graph ( "manual_follows1.png",
                                     "png",
                                     [final_task], 
                                     no_key_legend=True)
        
    producing the following flowchart
    
        .. image:: ../../images/manual_follows1.png
        

    or in text format with:
        ::
        
            pipeline_printout(sys.stdout, [final_task])
        
    which produces the following:
        ::
        
            Task = first_task
            Task = second_task
            Task = final_task

    

.. index:: 
    pair: @follows; referring to functions before they are defined
    pair: @follows; out of order
.. _manual.follows.out_of_order:

***************************************
Defining pipeline tasks out of order
***************************************

    All this assumes that all your pipelined tasks are defined in order.
    (``first_task`` before ``second_task`` before ``final_task``)
    
    | This is usually the most sensible way to arrange your code.

    If you wish to refer to tasks which are not yet defined, you can do so by quoting the function name as a string:

        ::
        
            @follows("second_task")
            def final_task():
                print "Final task"

    You can refer to tasks (functions) in other modules, in which case the full 
    qualified name must be used:

        ::
        
            @follows("other_module.second_task")
            def final_task():
                print "Final task"
    
.. index:: 
    pair: @follows; multiple dependencies
    
.. _manual.follows.multiple_dependencies:

***************************************
Multiple dependencies
***************************************
            
    Each task can depend on more than one antecedent task.
    
    This can be indicated either by stacking ``@follows``:
        ::
        
            @follows(first_task)
            @follows("second_task")
            def final_task():
                ""
    
    
    or in a more concise way:
        ::
        
            @follows(first_task, "second_task")
            def final_task():
                ""
    
.. _manual.follows.mkdir:

.. index:: 
    single: @follows; mkdir (Manual)
    single: mkdir; @follows (Manual)


******************************************************************************
Making directories automatically with :ref:`mkdir <decorators.mkdir>`
******************************************************************************

    A common prerequisite for any computational task, is making sure that the destination
    directories exist. 

    **Ruffus** provides special syntax to support this, using the special 
    :ref:`mkdir <decorators.mkdir>` dependency. For example:

        ::
    
            @follows(first_task, mkdir("output/results/here"))
            def second_task():
                print "Second task"
            
    will make sure that ``output/results/here`` exists before `second_task` is run.
    
    In other words, it will make the ``output/results/here`` directory if it does not exist.



