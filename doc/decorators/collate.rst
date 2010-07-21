.. include:: ../global.inc
.. _decorators.collate:
.. index:: 
    pair: @collate; Syntax

See :ref:`Decorators <decorators>` for more decorators

########################
@collate
########################

.. |tasks_or_file_names| replace:: `tasks_or_file_names`
.. _tasks_or_file_names: `decorators.collate.tasks_or_file_names`_
.. |extra_parameters| replace:: `extra_parameters`
.. _extra_parameters: `decorators.collate.extra_parameters`_
.. |output_pattern| replace:: `output_pattern`
.. _output_pattern: `decorators.collate.output_pattern`_
.. |matching_regex| replace:: `matching_regex`
.. _matching_regex: `decorators.collate.matching_regex`_


***********************************************************************************************************************************************************
*@collate* ( |tasks_or_file_names|_, :ref:`regex<decorators.regex>`\ *(*\ |matching_regex|_\ *)*\ , |output_pattern|_, [|extra_parameters|_,...] ) 
***********************************************************************************************************************************************************
    **Purpose:**
        Groups / collates sets of input files, each into a separate summary. 
        
        Only out of date tasks (comparing input and output files) will be run
        
    **Example**:
        ``regex(r".*(\..+)"), "\1.summary"`` creates a separate summary file for each suffix::

            animal_files = "a.fish", "b.fish", "c.mammals", "d.mammals"
            # summarise by file suffix:
            @collate(animal_files, regex(r"\.(.+)$"),  r'\1.summary')
            def summarize(infiles, summary_file):
                pass
    
    **Parameters:**
                
                
.. _decorators.collate.tasks_or_file_names:

    * *tasks_or_file_names*
       can be a:

       #.  Task / list of tasks (as in the example above).
            File names are taken from the output of the specified task(s)
       #.  (Nested) list of file name strings.
            File names containing ``*[]?`` will be expanded as a |glob|_.
             E.g.:``"a.*" => "a.1", "a.2"``
           
                
.. _decorators.collate.matching_regex:

    * *matching_regex*
       is a python regular expression string, which must be wrapped in
       a :ref:`regex<decorators.regex>` indicator object
       See python `regular expression (re) <http://docs.python.org/library/re.html>`_ 
       documentation for details of regular expression syntax
                
.. _decorators.collate.output_pattern:

    * *output_pattern*
        Specifies the resulting output file name(s).
                
.. _decorators.collate.extra_parameters:

    * *extra_parameters*
        Any extra parameters are passed verbatim to the task function

    #. *outputs* and optional extra parameters are passed to the functions after regular expression
       substitution in any strings. Non-string values are passed through unchanged.
    #. Each collate job consists of input files which are aggregated by regular expression substitution
       to a single set of output / extra parameter matches
    #. In the above cases, ``a.fish`` and ``b.fish`` both produce ``fish.summary`` after regular
       expression subsitution, and are collated into a single job:
       ``["a.fish", "b.fish" -> "fish.summary"]``
       while ``c.mammals``, ``d.mammals`` both produce ``mammals.summary``, are collated in a separate job:
       ``["c.mammals", "d.mammals" -> "mammals.summary"]``
       
    **Example2**:
    
        Suppose we had the following files::
        
            cows.mammals.animal
            horses.mammals.animal
            sheep.mammals.animal
            
            snake.reptile.animal
            lizard.reptile.animal
            crocodile.reptile.animal
            
            pufferfish.fish.animal
        
        and we wanted to end up with three different resulting output::
        
            cow.mammals.animal
            horse.mammals.animal
            sheep.mammals.animal
                -> mammals.results
            
            snake.reptile.animal
            lizard.reptile.animal
            crocodile.reptile.animal
                -> reptile.results
            
            pufferfish.fish.animal
                -> fish.results
    
        This is the ``@collate`` code required::
    
            animals = [     "cows.mammals.animal", 
                            "horses.mammals.animal", 
                            "sheep.mammals.animal", 
                            "snake.reptile.animal", 
                            "lizard.reptile.animal", 
                            "crocodile.reptile.animal", 
                            "pufferfish.fish.animal"]
    
            @collate(animals, regex(r"(.+)\.(.+)\.animal"),  r"\2.results")
            # \1 = species [cow, horse]
            # \2 = phylogenetics group [mammals, reptile, fish]
            def summarize_animals_into_groups(species_file, result_file):
                " ... more code here"
                pass



See :ref:`@merge <decorators.merge>` for an alternative way to summarise files.       
