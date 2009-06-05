#!/usr/bin/env python


"""

********************************************
:mod:`ruffus.task` -- Overview
********************************************

.. moduleauthor:: Leo Goodstadt <ruffus@llew.org.uk>


============================
Decorator syntax:
============================

    Pipelined tasks are created by "decorating" a function with the following syntax::
    
        def func_a():
            pass
            
        @follows(func_a)
        def func_b ():
            pass
                
    
    Each task is a single function which is applied one or more times to a list of parameters
    (typically input files to produce a list of output files).
    
    Each of these is a separate, independent job (sharing the same code) which can be
    run in parallel.
        

============================
Running the pipeline
============================
    To run the pipeline::
    
            pipeline_run(target_tasks, forcedtorun_tasks = [], multiprocess = 1, 
                            logger = stderr_logger,
                            gnu_make_maximal_rebuild_mode  = True,
                            cleanup_log = "../cleanup.log")

            pipeline_cleanup(cleanup_log = "../cleanup.log")
        
        

           
    

"""
__version__ = '0.9.1'


import os,sys,copy, multiprocessing
# add self to search path for testing
if __name__ == '__main__':
    exe_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
    sys.path.append(os.path.abspath(os.path.join(exe_path,"..", "python_modules")))
    myname = os.path.split(sys.argv[0])[1]
    myname = os.path.splitext(myname)[0];
else:
    myname = __name__


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   imports        


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
import logging
import sys, os
import os.path
import re
import operator
import sys
from collections import defaultdict
from graph import *
from print_dependencies import *
import types

# use simplejson in place of json for python < 2.6
try:
    import json
except ImportError:
    import simplejson
    json = simplejson


dumps = json.dumps
from multiprocessing import Pool
import traceback


def is_str(arg):
    return issubclass(arg.__class__, str)

def non_str_sequence (arg):
    """
    Whether arg is a sequence.
    We treat a string however as a singleton not as a sequence
    """
    if issubclass(arg.__class__, str) or issubclass(arg.__class__, unicode):
        return False
    try:
        test = iter(arg)
        return True
    except TypeError:
        return False
    
def ioparam_to_str(io):
    if io == None:
        return ""
    elif is_str(io):
        return "'" + io + "'"
    else:
        return ", ".join("'%s'" % s for s in io)


    
def die_error(Msg):
    """
    Standard way of dying after a fatal error
    """
    print_error (Msg)
    sys.exit()

def print_error (Msg):
    """
    Standard way of printing error
    """
    sys.stderr.write("\nError:\n    %s\n" % Msg)
    
   



   
       
#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   needs_update_func

#       functions which are called to see if a job needs to be updated
#
#   Each task is a series of parallel jobs
#           each of which has the following pseudo-code
# 
#   for param in param_generator_func():
#       if needs_update_func(*param):
#           job_wrapper(*param)
# 
#   N.B. param_generator_func yields iterators of *sequences*
#   if you are generating single parameters, turn them into lists:
#   
#       for a in alist:
#           yield (a,)
#
#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
#_________________________________________________________________________________________

#   needs_update_check_modify_time

#_________________________________________________________________________________________
def check_input_files_exist (input, *other):
    """
    Clunky hack to make sure input files exists right before 
        job is called for better error messages
    """

    # missing file means always build                
    if input == None:
        return
    if is_str(input):
        if not os.path.exists(input):
            raise MissingInputFileError("No way to run job: Input file ['%s'] does not exist" % input)
    else:
        for f in input:
            if not os.path.exists(f):
                raise MissingInputFileError("No way to run job: Input file ['%s'] does not exist" % f)


def needs_update_check_modify_time (i, o, *other):
    """
    Given input and output files
        see if all exist and whether output files are later than input files
        Each can be None, "file1" or ["file1", "file2", "file3"]
        None means always make
        
    """
    # missing output file
    if o == None or (non_str_sequence(o)  and len(o) == 0):
        return True

    # missing file means always build                
    for io in (i, o):
        if io == None:
            continue
        if is_str(io):
            if not os.path.exists(io):
                return True
        else:
            for f in io:
                if not os.path.exists(f):
                    return True

    #
    #   missing input -> build if absent
    # 
    if i == None or len(i) == 0:
        return False
    
    
    #
    #   get sorted modified times for all input and output files 
    #
    file_times = [[], []]                                    
    for index, io in enumerate((i, o)):
        if is_str(io):
            file_times[index].append(os.path.getmtime(io))
        else:
            for f in io:
                file_times[index].append(os.path.getmtime(f))
        file_times[index].sort()

    # 
    #   update if any input file >= (more recent) output fifle
    #
    if max(file_times[0]) >= min(file_times[1]):
        return True
    return False

#_________________________________________________________________________________________

#   needs_update_check_directory_missing 

#       N.B. throws exception if this is an ordinary file, not a directory


#_________________________________________________________________________________________
def needs_update_check_directory_missing (dirs):
    """
    Called per directory:
        Does it exist?
        Is it an ordinary file not a directory? (throw exception
    """
    for d in dirs:
        #print >>sys.stderr, "check directory missing %d " % os.path.exists(d)
        if not os.path.exists(d):
            return True
        if not os.path.isdir(d):
            raise error_not_a_directory("%s already exists but as a file, not a directory" % d )
    return False

    
    
    
    
    
class t_black_hole_logger:
    """
    Does nothing!
    """
    def info (self, message):
        pass
    def debug (self, message):
        pass
    

class t_stderr_logger:
    """
    Everything to stderr
    """
    def info (self, message):
        print >>sys.stderr, message
    def debug (self, message):
         print >>sys.stderr, message
    
    
black_hole_logger = t_black_hole_logger()
stderr_logger     = t_stderr_logger()
    
    
    
    
    
    
    
    
    
    
#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   param_factories

#       makes python generators which yield parameters for
#
#           A) needs_update_func 
#           B) job_wrapper

#       Each task is a series of parallel jobs
#           each of which has the following pseudo-code
# 
#       for param in param_generator_func():
#           if needs_update_func(*param):
#               act_func(*param)
#
#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#_________________________________________________________________________________________

#   glob_regex_io_param_factory                                                                        

#      iterable list of input / output files from
       
#                1) glob/filelist
#                2) regex
#                3) input_filename_str (optional)
#                4) output_filename_str
#_________________________________________________________________________________________
import glob    
def glob_regex_io_param_factory (glob_str_or_list, matching_regex, *parameters):
    """
    Factory for functions which in turn
        yield tuples of input_file_name, output_file_name                                     
                                                                                                   
    Usage:
                                         
    1.::
    
        param_func = glob_regex_io_param_factory("/etc/*",          # glob                                  
                                                 "(file_)(\d+)",    # which match this regex                
                                                 "input_file_\2",   # pattern to generate input file names    
                                                 "output_file_\2")  # pattern to generate output file names  
                                                 
    or                                                                                                 
    2.::
    
        param_func = glob_regex_io_param_factory("/etc/*",         # glob                                  
                                                 "(file_)(\d+)",   # which match this regex                
                                                 None,             # use originals as input file names     
                                                 "output_file_\2") # pattern to generate output file names   

    or 
    3.::
    
        param_func = glob_regex_io_param_factory(file_list,        # list of files
                                                 "(file_)(\d+)",   # which match this regex                
                                                 None,             # use originals as input file names     
                                                 "output_file_\2") # pattern to generate output file names   
    
        for i, o in param_func():                                                                          
            print " input file name = " , i                                                                
            print "output file name = " , o                                                                
                                                                                                       
                                                                                                       
    ..Note::
        1. `param_func` has to be called each time
        2. `glob` is called each time.
           So do not expect the file lists in `param_func()` to be the same for each invocation
        3. A "deepcopy" of the file list is saved
           So do not expect to modify your copy of the original list and expect changes
           to the input/export files
        
    
    """
    parameters = list(parameters)
    if len(parameters) == 0:
        raise task_FilesreArgumentsError("Missing arguments @files_re for job " + 
                                        dumps([glob_str_or_list, matching_regex] + parameters))
    
    
    regex = re.compile(matching_regex)

    # make (expensive) copy so that changes to the original sequence don't confuse us
    parameters = copy.deepcopy(parameters)

    
    # if the input file term is missing, just use the original
    class pass_thru:
        pass
    if len(parameters) == 1:
        parameters.insert(0, pass_thru())

            
    #
    #   make copy of file list? 
    #
    if not is_str(glob_str_or_list):
        glob_str_or_list = copy.deepcopy(glob_str_or_list)

    def iterator ():
        #
        #   glob or file list? 
        #
        if is_str(glob_str_or_list):
            filenames = sorted(glob.glob(glob_str_or_list))
        else:
            filenames = sorted(glob_str_or_list)
            
            
        
        for starting_file_name in filenames:
            #
            #   regular expression has to match 
            #
            if not regex.search(starting_file_name):
                continue

            job_param = []
            for p in parameters:
                if isinstance(p, pass_thru):
                    job_param.append(starting_file_name)
                elif is_str(p):
                    job_param.append(regex.sub(p, starting_file_name))
                elif non_str_sequence (p):
                    nested_params = []
                    for pp in p:
                        if is_str(pp):
                            nested_params.append(regex.sub(pp, starting_file_name))
                        else:
                            nested_params.append(pp)
                    job_param.append(nested_params)
                else:
                    job_param.append(p)
            
            yield job_param
                
        ##  
        ##   If there is no input_filename_str
        ##       use original file names as the input files
        ##   
        ##   Only proceed if regex matches filename
        ##       (any_changes != 0)
        ##           
        ## 
        #if input_filename_str == None:
        #    for input_file_name in filenames:
        #        (output_file_name, any_changes) = regex.subn(output_filename_str, input_file_name)
        #        if not any_changes:
        #            continue
        #        yield (input_file_name, output_file_name)
        #else:
        #    for filename in filenames:
        #        (input_file_name, any_changes) = regex.subn(input_filename_str, filename)
        #        if not any_changes:
        #            continue
        #        output_file_name = regex.sub(output_filename_str, filename)
        #        yield (input_file_name, output_file_name)

    return iterator
    
#_________________________________________________________________________________________

#   file_list_io_param_factory 

#       iterates through a list of input output files

#
#       orig_args = ["input", "output", 1, 2, ...] 
#       orig_args = [None,    "output", 1, 2, ...] 
#       orig_args = [
#                       ["input0",               "output0",                1, 2, ...]
#                       [["input1a", "input1b"], "output1",                1, 2, ...]
#                       ["input2",               ["output2a", "output2b"], 1, 2, ...]
#                       ["input3",               "output3",                1, 2, ...]
#                   ] 
#       
#       N.B. There is not much checking of parameters up front
#_________________________________________________________________________________________
def check_file_list_io_param (params):
    """
    Helper function for file_list_io_param_factory
    Checks there are input and output files specified for each job
    """
    if not len(params):
        return
    
        
    try:
        for job_param in params:
            if len(job_param) < 2:
                raise task_FilesArgumentsError("Missing input or output files for job " + 
                                                dumps(job_param))
            if list(job_param[0:2]) == [None, None]:
                raise task_FilesArgumentsError("Either the input or output file " + 
                                                "must be defined for job "                +
                                                dumps(job_param))
            for file_param in job_param[0:2]:
                # 
                #   check that i/o files are sequences of strings or strings
                #
                if file_param == None:
                    continue
                if is_str(file_param):
                    continue
                if non_str_sequence(file_param):
                    for f in file_param:
                        if not is_str(f):
                            break
                    else:
                        continue
                raise task_FilesArgumentsError("Input or output files must be a string or " + 
                                                    "a collection of strings: "              +
                                                    dumps(job_param))
    except TypeError:
        message = ("Enclosing brackets are needed even if you are "
                                            "only supplying parameters for a single job: "     +
                                            dumps(params))
        raise task_FilesArgumentsError(message)
    
def file_list_io_param_factory (orig_args):
    """
    Factory for functions which 
        yield tuples of input_file_name, output_file_name                            
        
    Examples of orig_args:

    1.::
        
        orig_args = "input1", "output1", any_other_parameters1, ...       # files for job 1 
    
    2.::
        
        orig_args = None,     "output1", any_other_parameters2, ...       # files for job 1 
    
    3.::
    
        orig_args = [                                                               
                      ["input0",               "output0",                ...] # files for job 1
                      [["input1a", "input1b"], "output1",                ...] # files for job 2 
                      ["input2",               ["output2a", "output2b"], ...] # files for job 3 
                      ["input3",               "output3",                ...] # files for job 4 
                    ]                                                                 


    Usage:

        param_func = file_list_io_param_factory(orig_args)
        
        for params in param_func():                                                                          
            i,o = params[0:2]
            print " input file name = " , i                                                                
            print "output file name = " , o                                                                


    ..Note::
    
        1. Each job requires input/output file names
        2. Input/output file names can be a string, a list of strings or None
        3. Either Input or output file name must be non-None
        
    """
    # multiple jobs with input/output parameters etc.
    if len(orig_args) > 1:
        params = copy.deepcopy([list(orig_args)])
    else:
        params = copy.deepcopy(orig_args[0])

    check_file_list_io_param(params)
      

    def iterator():
        for job_param in params:
            #print >> sys.stderr, dumps(job_param, indent=4)
            yield job_param
    return iterator

#_________________________________________________________________________________________

#   args_param_factory

#       iterates through supplied list 
#_________________________________________________________________________________________
def args_param_factory (orig_args):
    """
so that::
    
        @parallel('a', 'b', 'c') 
        def task_func (A, B, C):
            pass

and::
   
        parameters=[
                     ['a', 'b', 'c'],        # first job
                   ]        
        @parallel(parameters) 
        def task_func (A, B, C):
            pass

both call::
    
            task_func(A='a', B = 'b', C = 'c')
    """
    # multiple jobs with input/output parameters etc.
    if len(orig_args) > 1:
        params = copy.deepcopy([list(orig_args)])
    else:
        params = copy.deepcopy(orig_args[0])

    def iterator():
        for job_param in params:
            #print >> sys.stderr, dumps(job_param, indent=4)
            yield job_param
    return iterator

    
    
    
    
    
    
#_________________________________________________________________________________________

#   touch_file_factory

#_________________________________________________________________________________________
def _touch_file_factory (orig_args, register_cleanup):
    """
    Creates function, which when called, will touch files
    """
    file_names = orig_args
    if is_str (orig_args):
        file_names = [orig_args]
    else:
        # make copy so when original is modifies, we don't get confused!
        file_names = list(orig_args)
        
    def do_touch_file ():
        for f  in file_names:
            if not os.path.exists(f):
                open(f, 'w')
            else:
                os.utime(f, None)
            register_cleanup(f, "touch")
    return do_touch_file
        
    
    
    
    
    
    
        
        
#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   Exceptions


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

class error_task(Exception):
    def __init__(self, *errmsg):
        Exception.__init__(self, *errmsg)
        self.task = ""
    def __str__(self):
        return self.task + " ".join(map(str, self.args))
    def specify_task (self, task, additional_msg):
        task_name = task._name.replace('__main__.', '')
        if task._action_type != task.action_mkdir:
            task_name = "'def %s(...):'" % (task_name)
        self.task = "\n\n" + additional_msg + " for\n%s\n" % task_name

class RethrownJobError(error_task):
    """
    Wrap up one or more exceptions rethrown across process boundaries
    
        See multiprocessor.Server.handle_request/serve_client for an analogous function
    """
    def __init__(self, job_exceptions):
        Exception.__init__(self, job_exceptions)
        self.args = job_exceptions
    def __str__(self):
        message = ["\nOriginal exception%s:\n" % ("s" if len(self.args) > 1 else "")]
        #
        #   For each exception:
        #       turn original exception stack message into an indented string
        #
        for i, (job_name, exception_name, exception_value, exception_stack) in enumerate(self.args):
            message += ("\nException #%d\n" % (i + 1) +
                        "%s: %s\nfor %s\n\n%s\n" % 
                            (exception_name, exception_value, job_name, exception_stack) )
        return (self.task + "".join(message)).replace("\n", "\n    ")
        
class task_FilesArgumentsError(error_task):
    pass
class task_FilesreArgumentsError(error_task):
    pass
class JobSignalledBreak(error_task):
    pass
class MissingInputFileError(error_task):
    pass
class PostTaskArgumentError(error_task):
    pass

            
class error_making_directory(error_task):
    pass
class error_duplicate_task_name(error_task):
    pass
class error_decorator_args(error_task):
    pass
class error_task_name_lookup_failed(error_task):
    pass
class error_task_decorator_takes_no_args(error_task):
    pass
class error_function_is_not_a_task(error_task):
    pass
class error_circular_dependencies(error_task):
    pass
class error_not_a_directory(error_task):
    pass
class error_missing_output(error_task):
    pass
class error_job_signalled_interrupt(error_task):
    pass

        

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   task_decorator

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
class task_decorator(object):
    """
        Adds task to the "pipeline_task" attribute of this function but
        otherwise leaves function untouched
    """
    def __init__(self, *decoratorArgs):
        """
            saves decorator arguments
        """
        self.args = decoratorArgs

    def __call__(self, func):
        """
            calls func in task with the same name as the class
        """
        # add task as attribute of this function
        if not hasattr(func, "pipeline_task"):
            func.pipeline_task = _task.create_task(func)


        # call the method called  
        #   "task.task_decorator" 
        #   where "task_decorator" is the name of this class
        decorator_function_name = "task_" + self.__class__.__name__
        task_decorator_function = getattr(func.pipeline_task, decorator_function_name)
        task_decorator_function(self.args)

        #
        #   don't change the function so we can call it unaltered
        # 
        return func



class follows(task_decorator):
    """
    **@follows** (parent_task1, "module_X.parent_task2")

        Takes a list of tasks which have to be run *before* this function
        Dependencies can be quoted or unquoted function names.
        Quoted function names allow dependencies to be added before the function is defined

        Functions in other modules need to be fully qualified


        For convenience, ``mkdir`` can be used to specify 
        directories which need to be created (if they don't exist) before
        the task is run.

        e.g::
            
            @follows(task_x, mkdir("/output/directory") ...)
    """
    pass
    
class files(task_decorator):
    """
    **@files** ([[job1.input, job1.output, job1.optional_extra_parameters], ...])
    
    **@files** (input_file, output_file, optional_extra_parameters)

    **@files** (custom_function)

    The first two parameters in each set represent the input and output of the each job.
    Only out of date jobs will be run.
    By default, this is by checking input/output file timestamps.
    (On some file systems, timestamps have a resolution in seconds.)

    The input and output files for each job can be 
        * A single file name
        * A list of files
        * ``None``
    
    If the input file is ``None``, the job will run if any output file is missing.
    
    If the output file is ``None``, the job will always run.
    
    If any of the output files is missing, the job will run.
    
    If any of the input files is missing when the job is run, a
    ``MissingInputFileError`` exception will be raised.
        
    Example::

        from ruffus import *
        parameters = [
                            [ 'a.1', 'a.2', 'A file'], # 1st job
                            [ 'b.1', 'b.2', 'B file'], # 2nd job
                      ]

        @files(parameters)
        def parallel_io_task(infile, outfile, text):
            infile_text = open(infile).read()
            f = open(outfile, "w").write(infile_text + "\\n" + text)

        pipeline_run([parallel_io_task])


    Parameters can be generated on the fly as well.
    Example::

        from ruffus import *
        def generate_parameters_on_the_fly():
            parameters = [
                                ['input_file1', 'output_file1', 1, 2], # 1st job
                                ['input_file2', 'output_file2', 3, 4], # 2nd job
                                ['input_file3', 'output_file3', 5, 6], # 3rd job
                         ]
            for job_parameters in parameters:
                yield job_parameters

        @files(generate_parameters_on_the_fly)
        def parallel_io_task(input_file, output_file, param1, param2):
            sys.stderr.write("    Parallel task %s: " % name)
            sys.stderr.write("%d + %d = %d\\n" % (param1, param2, param1 + param2))
        
        pipeline_run([parallel_task])
"""
    pass
    

class files_re(task_decorator):
    """
    **@files_re** (glob/file_list, matching_regex, output_file)
    
    **@files_re** (glob/file_list, matching_regex, input_file, output_file, [extra_parameters,...] )

    Generates a list of i/o files for each job in the task:
    Only out of date jobs will be run (See @files).
    
    #. ``matching_regex`` is a python regular expression.
    #. The first parameter are input file(s)
    #. The second parameter are output file(s)

    These are used to check if jobs are up to date.
    
    All parameters can be:
    
        #. ``None``
        #. A string
        #. A sequence of strings
        #. Anything else
    
    Strings and sequences of strings will be treated as regular expression substitution
    patterns, using matches from ``matching_regex``.
    
    See python `regular expression (re) <http://docs.python.org/library/re.html>`_ 
    documentation for details of the syntax
   
    `None` and all other types of objects are passed through unchanged.
        
        
    Operation:    

        1) For each file in the ``glob`` (See `glob <http://docs.python.org/library/glob.html>`_) 
           results or ``file_list``.
        2) Discard all file names those which don't matching ``matching_regex``
        3) Generate parameters using regular expression pattern substitution
       
    Example::
    
        from ruffus import *
        #
        #   convert all files ending in ".1" into files ending in ".2"
        #
        @files_re('*.1', '(.*).1', r'\\1.2')
        def task_re(infile, outfile):
            open(outfile, "w").write(open(infile).read() + "\\nconverted\\n")
        
        pipeline_run([task_re])
   
       
"""
    pass
class check_if_uptodate(task_decorator):
    """
    **@check_if_uptodate** (dependency_checking_func)
    
    Checks to see if a job is up to date, and needs to be run.
    dependency_checking_func() needs to handle the same number of parameters as the
    task function
    
    These two examples, using automatic and manual dependency checking produce
    the same output.
    Example 1: Automatic::

        from ruffus import *
        @files(None, "a.1")
        def create_if_necessary(input_file, output_file):
            open(output_file, "w")
                    
        pipeline_run([create_if_necessary])


    Could be rewritten as::
    Example 2: Manual::
        
        from ruffus import *
        import os
        def check_file_exists(input_file, output_file):
            return not os.path.exists(output_file)
        
        @parallel([[None, "a.1"]])
        @check_if_uptodate(check_file_exists)
        def create_if_necessary(input_file, output_file):
            open(output_file, "w")
        
        pipeline_run([create_if_necessary])
        
    Both produce the same output::
    
        Task = create_if_necessary
            Job = [null, "a.1"] completed
        

    """
    pass

class parallel(task_decorator):
    """
**@parallel** ([[job1_params, ...], [job2_params, ...]...])

**@parallel** (parameter_generating_func)

    The task function will be called iteratively 
    with each set of parameters (possibly in parallel)

    No dependency checking is carried out.
    
    Example::
    
        from ruffus import *
        parameters = [
                         ['A', 1, 2], # 1st job
                         ['B', 3, 4], # 2nd job
                         ['C', 5, 6], # 3rd job
                     ]
        @parallel(parameters)                                                     
        def parallel_task(name, param1, param2):                                  
            sys.stderr.write("    Parallel task %s: " % name)                     
            sys.stderr.write("%d + %d = %d\\n" % (param1, param2, param1 + param2))
        
        pipeline_run([parallel_task])

        
    """
    pass
class posttask(task_decorator):
    """
    Calls functions to signal the completion of each task::
    
        from ruffus import *
        
        def task_finished():
            print "hooray"
            
        @posttask(task_finished)
        @files(None, "a.1")
        def create_if_necessary(input_file, output_file):
            open(output_file, "w")
                    
        pipeline_run([create_if_necessary])

    .. note::

        The function(s) provided to ``@posttask`` will be called if the ruffus passes 
        through a task, even if none of its jobs are run because they are up-to-date.
        This happens when a upstream task is out-of-date, and the execution passes through
        this point in the pipeline
        

    If ``touch_file`` is specified, the enclosed files(s) will be ``touch``\ -ed::

        from ruffus import *

        @posttask(touch_file("task_completed.flag"))
        @files(None, "a.1")
        def create_if_necessary(input_file, output_file):
            open(output_file, "w")

        pipeline_run([create_if_necessary])
    """
    pass
     
        
        
        

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   special marker used by follows

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
class mkdir(object):
    def __init__ (self, *args):
        self.args = args

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   special marker used by post_task

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
class touch_file(object):
    def __init__ (self, *args):
        self.args = args
        
#8888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#       job descriptors

#           given parameters, returns string describing job
#           main use in error logging

#8888888888888888888888888888888888888888888888888888888888888888888888888888888888888
def generic_job_descriptor (param):
    if param in ([], None):
        return "Job"
    else:
        return "Job = %s" % dumps(param)

def io_files_job_descriptor (param):
    # input, output
    extra_param = "" if len(param) == 2 else ", " + dumps(param[2:])[1:-1]
    return "Job = [%s -> %s%s]" % (dumps(param[0]), dumps(param[1]), extra_param)

def mkdir_job_descriptor (param):
    # input, output and parameters
    return "Make directory %s" % (dumps(param))


#8888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#       job wrappers
#           registers files/directories for cleanup    

#8888888888888888888888888888888888888888888888888888888888888888888888888888888888888
#_________________________________________________________________________________________

#   generic job wrapper

#_________________________________________________________________________________________
def job_wrapper_generic(param, user_defined_work_func, register_cleanup):
    """
    run func
    """
    assert(user_defined_work_func)
    return user_defined_work_func(*param)

#_________________________________________________________________________________________

#   job wrapper for all that deal with i/o files

#_________________________________________________________________________________________
def job_wrapper_io_files(param, user_defined_work_func, register_cleanup):
    """
    run func on any i/o if not up to date
    """
    assert(user_defined_work_func)

    ret_val = user_defined_work_func(*param)
    if ret_val == False:
        return False

    i,o = param[0:2]

    #
    # register output file for cleanup
    #
    if o == None:
        return
    elif is_str(o):
        register_cleanup(o, "file")
    else:
        for f in o:
            register_cleanup(f, "file")


#_________________________________________________________________________________________

#   job wrapper for mkdir

#_________________________________________________________________________________________
def job_wrapper_mkdir(param, user_defined_work_func, register_cleanup):
    """
    make directories if not exists
    """
    #
    #   Just in case, extra check because some other makedirs might be subpath 
    #       of this directory
    #   Should not be necessary because of "sorted" in task_mkdir
    #   
    #
    for d in param[0]:
        if not os.path.exists(d):
            os.makedirs(d)
            register_cleanup(d, "makedirs")


        
#_________________________________________________________________________________________

#   multiprocess_callback 
# 
#_________________________________________________________________________________________
def run_pooled_job_without_exceptions (process_parameters):
    """
    handles running jobs in parallel
    Make sure exceptions are caught here: 
        Otherwise, these will kill the thread/process
        return any exceptions which will be rethrown at the other end:
        See RethrownJobError /  run_all_jobs_in_task
    """
    
    (param, job_descriptor, needs_update_func, job_wrapper, 
        user_defined_work_func, do_log, force_rerun) = process_parameters
    
    if do_log:
        job_name = job_descriptor(param)
    else:
        job_name = None
    
    try:
        # don't run if up to date
        if not force_rerun and needs_update_func:
            if not needs_update_func (*param):
                return False, job_name
                
            #    Clunky hack to make sure input files exists right before 
            #        job is called for better error messages
            if needs_update_func == needs_update_check_modify_time:
                check_input_files_exist (*param)


        # if user return false, halt job
        if job_wrapper(param, user_defined_work_func, register_cleanup) == False:
            raise JobSignalledBreak("%s returned False" % job_descriptor(param))
        return None, job_name
    except:
        #   Wrap up one or more exceptions rethrown across process boundaries
        #   
        #       See multiprocessor.Server.handle_request/serve_client for an analogous function
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        exception_stack  = traceback.format_exc(exceptionTraceback)
        exception_name   = exceptionType.__module__ + '.' + exceptionType.__name__
        exception_value  = str(exceptionValue)
        return (job_descriptor(param), exception_name, exception_value, exception_stack)
        


#_________________________________________________________________________________________

#   register_cleanup

#       to do

#_________________________________________________________________________________________
def register_cleanup (file_name, operation):
    pass
#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   _task

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
class _task (node):
    """
    pipeline task
    """

    action_names = ["unspecified",
                    "task",
                    "task_files_re",
                    "task_files_func",
                    "task_files",
                    "task_mkdir",
                    "task_parallel",
                    ]
    action_unspecified      = 0
    action_task             = 1
    action_task_files_re    = 2
    action_task_files_func  = 3
    action_task_files       = 4
    action_mkdir            = 5
    action_parallel         = 6

    #_________________________________________________________________________________________

    #   create_task / __init__

    #_________________________________________________________________________________________
    @staticmethod
    def create_task(func):
        """
        Create task if the name as not been previously specified
        Note that the task function may not have been created yet.
        This allows us to create tasks and dependencies out of order
        """
        func_name   = func.__name__
        module_name = func.__module__
        task_name   = module_name + "." + func_name
    
        # Link to existing dependency if task name has previously been specified
        if node.is_node(task_name):
            t = node.lookup_node_from_name(task_name)
            if t.user_defined_work_func != None:
                raise error_duplicate_task_name("Same task name %s specified multiple times in the same module" % task_name)
        #   otherwise create new
        else:
            t = _task(module_name, func_name)

        t.set_action_type (_task.action_task)
        t.user_defined_work_func = func
        assert(t._name == task_name)
        t._description           = func.__doc__ or ""
        t._description = t._description.strip()

        return t


    #_________________________________________________________________________________________

    #   __init__

    #_________________________________________________________________________________________
    def __init__ (self, module_name, func_name):
        """
        Does nothing because this might just be a dependency.
        If it does not get initialised by a real task 
            (a task is depending on an unknown function/task), 
            throw an exception when running the pipeline

        """
        self._module_name = module_name
        self._func_name   = func_name
        
        node.__init__ (self, module_name + "." + func_name)
        self._action_type  = _task.action_unspecified
        
        
        
        self.param_generator_func   = None
        self.needs_update_func      = None
        self.job_wrapper            = job_wrapper_generic
        
        # 
        self.job_descriptor         = generic_job_descriptor

        # function which is decorated and does the actual work
        self.user_defined_work_func = None
        
        # functions which will be called when task completes
        self.post_task_functions    = []
                
        
        
    #_________________________________________________________________________________________

    #   set_action_type

    #_________________________________________________________________________________________
    def set_action_type (self, new_action_type):
        """
        Save how this task 
            1) tests whether it is up-to-date and 
            2) handles input/output files

        Checks that the task has not been defined with conflicting actions    
            
        """
        if self._action_type not in (_task.action_unspecified, _task.action_task):
            old_action = _task.action_names[self.action_type]
            new_action = _task.action_names[new_action_type]
            actions = " and ".join(list(set((old_action, new_action))))
            raise error_decorator_args(("Duplicate task names: Task/function %s has been " +
                                        "specified more than once (%s) ") % 
                                        (self._name, actions))
        self._action_type = new_action_type
        #
        #   DEBUGG
        # 
        self._action_type_desc = _task.action_names[new_action_type]


    #_________________________________________________________________________________________

    #   printout

    #_________________________________________________________________________________________
    def printout (self, stream, force_rerun, long_winded=False, indent = 4):
        """
        Print out all jobs for this task
        """
        indent_str = ' ' * indent
        
        task_name = self._name.replace("__main__.", "")
        stream.write("Task = " + task_name + ("    >>Forced to rerun<<\n" if force_rerun else "\n"))
        if long_winded:
            stream.write(indent_str + '"' + self._description + '"\n')

        #
        #   No parameters: just call task function 
        #
        if self.param_generator_func == None:
            stream.write(indent_str + self._name + "()\n")
        else:
            for param in self.param_generator_func():
                uptodate = '   '
                if self.needs_update_func and not self.needs_update_func (*param):
                    uptodate = "U: "
                stream.write(indent_str + uptodate + self.job_descriptor(param) + "\n")

        stream.write("\n")

    

    #_________________________________________________________________________________________

    #   run_all_jobs_in_task

    #_________________________________________________________________________________________
    def run_all_jobs_in_task(self, logger, pool, poolsize, force_rerun):
        """
        Run all jobs for this task
        """
            
        task_name = self._name.replace("__main__.", "")
        logger.info("Task = " + task_name + (": Forced to rerun" if force_rerun else ""))
        if len(self._description):
            logger.debug("    " + self._description)

        # 
        # append all functions and arguments to a list
        # 
        # pass to pool if multiprocess otherwise to single task
        # 
        # Catch exceptions before pool
        
        job_parameters = list()
            
            
        assert(self.job_wrapper)
        import pickle
        
        #
        #   No parameters: just call task function 
        #
        if self.param_generator_func == None:
            job_parameters.append(([], self.job_descriptor, self.needs_update_func, 
                                    self.job_wrapper, self.user_defined_work_func,
                                    logger != None, force_rerun))
        else:    
            for param in self.param_generator_func():
                job_parameters.append((param, self.job_descriptor, self.needs_update_func, 
                                        self.job_wrapper, self.user_defined_work_func,
                                        logger != None, force_rerun))


        if pool:
            # run in parallel
            imap_unordered_it = pool.imap_unordered(run_pooled_job_without_exceptions, job_parameters)
            mapped_results = imap_unordered_it
        else:
            mapped_results = map(run_pooled_job_without_exceptions, job_parameters)
        return_values = list()
        
        for results in mapped_results:
            if results[0] == False:
                if logger:
                    logger.debug("    %s unnecessary: already up to date" % results[1])
            elif results[0] == None:
                if logger:
                    logger.debug("    %s completed" % results[1])
            else:
                #
                #   too many errors: break
                #
                return_values.append(results)
                if ("JobSignalledBreak" in results[1]  or
                    len(return_values) >= poolsize):
                    break
            
        if len(return_values):
            errt = RethrownJobError(return_values)
            errt.specify_task(self, "Exceptions running jobs")
            raise errt
        
        # run post task functions
        for f in self.post_task_functions:
            f()
        return True
        
        

    #_____________________________________________________________________________________

    #   signal
    # 
    #       returns whether up to date
    # 
    #_____________________________________________________________________________________
    def signal (self):
        """
        If up to date: signal = true
        If true, depth first search will not pass through this node
        """
        try:
            #
            #   Always needs update if no way to check if up to date
            #
            if self.needs_update_func == None:
                return False
                
            #
            #   if no parameters, just return the results of needs update
            # 
            if self.param_generator_func == None:
                return not self.needs_update_func()
            else:
                #
                #   return not up to date if ANY jobs needs update
                # 
                for param in self.param_generator_func():
                    if self.needs_update_func (*param):
                        return False
                return True
                
        # rethrow exception after adding task name
        except error_task, inst:
            inst.specify_task(self, "Exceptions in dependency checking")
            raise


        
        

        

            
            
            
            
            
            
            
            
            
            
            
            
    #8888888888888888888888888888888888888888888888888888888888888888888888888888888888888

    #       task handlers
    
    #         sets 
    #               1) action_type
    #               2) param_generator_func
    #               3) needs_update_func
    #               4) job wrapper


    #8888888888888888888888888888888888888888888888888888888888888888888888888888888888888
        
    #_________________________________________________________________________________________

    #   task_files

    #_________________________________________________________________________________________
    def task_files (self, orig_args):
        """
        calls user function in parallel
            with either each of a list of parameters
            or using parameters generated by a custom function
            
            In the parameter list,
                The first two items of each set of parameters must 
                be input/output files or lists of files or Null
        """
        
        self.needs_update_func    = self.needs_update_func or needs_update_check_modify_time
        self.job_wrapper          = job_wrapper_io_files
        self.job_descriptor       = io_files_job_descriptor

        #   Use parameters generated by a custom function
        if len(orig_args) == 1 and type(orig_args[0]) == types.FunctionType:
            self.set_action_type (_task.action_task_files_func)
            self.param_generator_func = orig_args[0]

        #   Use parameters in supplied list
        else:
            self.set_action_type (_task.action_task_files)
            self.param_generator_func = file_list_io_param_factory (orig_args)

    #_________________________________________________________________________________________

    #   task_parallel

    #_________________________________________________________________________________________
    def task_parallel (self, orig_args):
        """
        calls user function in parallel
            with either each of a list of parameters
            or using parameters generated by a custom function
        """
        self.set_action_type (_task.action_parallel)

        #   unmodified from __init__
        # 
        # self.needs_update_func      = None
        # self.job_wrapper          = job_wrapper_generic
        # self.job_descriptor       = io_files_job_descriptor

        

        # no passed: single call
        if len(orig_args) == 0:
            self.param_generator_func = None
            
        # custom function will generate params 
        elif type(orig_args[0]) == types.FunctionType:
            self.param_generator_func = orig_args[0]
            
        # list of  params 
        else:
            self.param_generator_func = args_param_factory(orig_args)
            


    #_________________________________________________________________________________________

    #   task_files_re

    #_________________________________________________________________________________________
    def task_files_re (self, orig_args):
        """
        calls user function in parallel
            with input_files, output_files, parameters
            These needed to be generated on the fly by 
                getting all file names in the supplied list/glob pattern
            There are two variations:

            1)    inputfiles = all files in glob which match the regular expression
                  outputfile = generated from the replacement string

            2)    inputfiles = all files in glob which match the regular expression and
                                          generated from the "from" replacement string
                  outputfiles = all files in glob which match the regular expression and
                                          generated from the "to" replacement string
        """
        self.set_action_type (_task.action_task_files_re)
        self.param_generator_func = glob_regex_io_param_factory (*orig_args)
        self.needs_update_func    = self.needs_update_func or needs_update_check_modify_time
        self.job_wrapper          = job_wrapper_io_files
        self.job_descriptor       = io_files_job_descriptor

    

    #_________________________________________________________________________________________

    #   task_mkdir
    
    #       only called within task_follow

    #_________________________________________________________________________________________
    def task_mkdir (self, orig_args):
        """
        list of directory names or a single argument which is aa list of directory names
        Creates directory if missing
        """
        #   jump through hoops 
        #   all directories created in one job to avoid race conditions
        #    so we are converting [a,b,c] into [   [[a, b,c]]   ]
        self.set_action_type (_task.action_mkdir)
        param_func                = args_param_factory([[[sorted(orig_args)]]])
        
        #print >>sys.stderr, dumps(list(param_func()), indent = 4)
        
        self.param_generator_func = param_func
        self._description         = "Make directories (%s)" % ", ".join(orig_args)
        self.needs_update_func    = self.needs_update_func or needs_update_check_directory_missing
        self.job_wrapper          = job_wrapper_mkdir
        self.job_descriptor       = mkdir_job_descriptor

        # doesn't have a real function
        #  use job_wrapper just so it is not None
        self.user_defined_work_func = self.job_wrapper
        
        

        
        
        
    #8888888888888888888888888888888888888888888888888888888888888888888888888888888888888

    #   Other task handlers



    #8888888888888888888888888888888888888888888888888888888888888888888888888888888888888
        
        
        
        
    
                
    #_________________________________________________________________________________________

    #   task_follows

    #_________________________________________________________________________________________
    def task_follows (self, args):
        """
        Saved decorator arguments should be:
                (string/task,...)
        """
        cnt_task_mkdir      = 0
        for arg in args:
            if is_str(arg):
                if node.is_node(arg):
                    arg = node.lookup_node_from_name(arg)
                elif node.is_node("__main__." + arg):
                    arg = node.lookup_node_from_name("__main__." + arg)
                else:    
                    #
                    #   if no module: use same module as task
                    #
                    names = arg.rsplit(".", 2)
                    if len(names) == 1:
                        arg = _task(self._module_name, arg)
                    else:
                        arg = _task(*names)
                self.add_child(arg)
                
        
            elif isinstance(arg, mkdir):
                cnt_task_mkdir += 1
                # give unique name to this instance of mkdir
                new_node = _task(self._module_name, self._name + "_mkdir_%d" % cnt_task_mkdir)
                self.add_child(new_node)
                new_node.task_mkdir(arg.args)

                
                
                
            # add task as attribute of this function
            else:
                if type(arg) != types.FunctionType:
                    raise error_decorator_args("Dependencies must be functions or function names in " +
                                                "@task_follows %s:\n[%s]" %
                                                (self._name, str(arg)))
                    
                # add task as attribute of this function
                if not hasattr(arg, "pipeline_task"):
                    arg.pipeline_task = _task.create_task(arg)
                self.add_child(arg.pipeline_task)

            
            
            
            
    #_________________________________________________________________________________________

    #   task_check_if_uptodate

    #_________________________________________________________________________________________
    def task_check_if_uptodate (self, args):
        """
        Saved decorator arguments should be:
                a function which takes the appropriate number of arguments for each job
        """
        if len(args) != 1 or type(args[0]) != types.FunctionType:
            raise error_decorator_args("Expecting a single function in  " +
                                                "@task_check_if_uptodate %s:\n[%s]" %
                                                (self._name, str(args)))
        self.needs_update_func        = args[0]
        


    #_________________________________________________________________________________________

    #   task_check_if_uptodate

    #_________________________________________________________________________________________
    def task_posttask(self, args):
        """
        Saved decorator arguments should be:
                one or more functions which will be called if the task completes
        """
        for arg in args:
            if isinstance(arg, touch_file):
                self.post_task_functions.append(_touch_file_factory (arg.args, register_cleanup))
            elif type(arg) == types.FunctionType:
                self.post_task_functions.append(arg)
            else:
                raise PostTaskArgumentError("Expecting simple functions or touch_file in  " +
                                                "@posttask(...)\n Task = %s" %
                                                (self._name))

        
        

            
            
            


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   Functions


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
#_________________________________________________________________________________________

#   link_task_names_to_functions

#_________________________________________________________________________________________
def link_task_names_to_functions ():
    """
    Make sure all tasks in dependency list are linked to real functions
        Call this before running anything else
    """
    
    for n in node._all_nodes:
        if n.user_defined_work_func == None:
            display_task_name = n._name.replace("__main__.", "")
            dependent_display_task_name = n._inward[0]._name.replace("__main__.", "")
            if n._module_name in sys.modules:
                module = sys.modules[n._module_name]
                if hasattr(module, n._func_name):
                    n.user_defined_work_func = getattr(module, n._func_name)
                else:
                    raise error_decorator_args(("Module '%s' has no function '%s' in " +
                                                "\n@task_follows('%s')\ndef %s...") %
                                        (n._module_name, n._func_name, display_task_name, dependent_display_task_name))
            else:        
                raise error_decorator_args("Module '%s' not found in " +
                                        "\n@task_follows('%s')\ndef %s..." %
                                (n._module_name, display_task_name, dependent_display_task_name))
    

#_________________________________________________________________________________________

#   task_names_to_tasks

#_________________________________________________________________________________________
def task_names_to_tasks (task_description, task_names):
    """
    Given a list of task names, look up the corresponding tasks
    Will just pass through if the task_name is already a task
    """
    
    #
    #   In case we are given a single item instead of a list
    #
    if is_str(task_names) or type(task_names) == types.FunctionType:
        task_names = [task_names]

    task_nodes = []
    for task_name in task_names:

        # Is this already a function, don't do mapping if already is task
        if type(task_name) == types.FunctionType:
            if task_name.pipeline_task:
                task_nodes.append(task_name.pipeline_task)
                continue
            else:
                # blow up for unwrapped function
                raise error_function_is_not_a_task("Function %s is not a pipelined task" % 
                                                    task_name.__name__)
            
        # assumes is some kind of string
        if not node.is_node(task_name):
            if  node.is_node("__main__." + task_name):
                task_nodes.append(node.lookup_node_from_name("__main__." + task_name))
            else:
                die_error("%s task %s not a pipelined task " % (
                                                        task_description, task_name))
        else:
            task_nodes.append(node.lookup_node_from_name(task_name))
    return task_nodes


#_________________________________________________________________________________________

#   pipeline_printout_in_dot_format

#_________________________________________________________________________________________
def pipeline_printout_graph (stream, 
                             output_format,
                             target_tasks, 
                             forcedtorun_tasks              = [], 
                             draw_vertically                = True, 
                             ignore_upstream_of_target      = False,
                             skip_uptodate_tasks            = False,
                             gnu_make_maximal_rebuild_mode  = True,
                             test_all_task_for_update       = True,
                             no_key_legend                  = False):
    """
    print out pipeline dependencies in various formats

    :param stream: where to print to
    :type stream: file-like object with ``write()`` function
    :param output_format: ["dot", "jpg", "svg", "ps", "png"]. All but the first depends on the `dot <http://www.graphviz.org>`_ program. 
    :param target_tasks: targets task functions which will be run if they are out-of-date.
    :param forcedtorun_tasks: task functions which will be run whether or not they are out-of-date.
    :param draw_vertically: Top to bottom instead of left to right.
    :param ignore_upstream_of_target: Don't draw upstream tasks of targets. 
    :param skip_uptodate_tasks: Don't draw up-to-date tasks if possible. 
    :param gnu_make_maximal_rebuild_mode: Defaults to re-running *all* out-of-date tasks. Runs minimal
                                          set to build targets if set to ``True``. Use with caution.
    :param test_all_task_for_update: Ask all task functions if they are up-to-date.
    :param no_key_legend: Don't draw key/legend for graph. 
    
    """
    

    link_task_names_to_functions ()
    
    #
    #   target jobs
    #     
    target_tasks        = task_names_to_tasks ("Target", target_tasks)
    forcedtorun_tasks   = task_names_to_tasks ("Forced to run", forcedtorun_tasks)
    

    graph_printout (  stream, 
                          output_format,
                          target_tasks, 
                          forcedtorun_tasks,
                          draw_vertically,
                          ignore_upstream_of_target,
                          skip_uptodate_tasks,
                          gnu_make_maximal_rebuild_mode,
                          test_all_task_for_update,
                          no_key_legend)

    

    
#_________________________________________________________________________________________

#   pipeline_run

#_________________________________________________________________________________________
def pipeline_run(target_tasks, forcedtorun_tasks = [], multiprocess = 1, logger = stderr_logger, 
                                    gnu_make_maximal_rebuild_mode  = True):
    """
    Run pipelines.
    
    :param target_tasks: targets task functions which will be run if they are out-of-date
    :param forcedtorun_tasks: task functions which will be run whether or not they are out-of-date
    :param multiprocess: The number of concurrent jobs
    :param logger: Where progress will be logged. Defaults to stderr output. 
    :type logger: `logging <http://docs.python.org/library/logging.html>`_ objects
    :param gnu_make_maximal_rebuild_mode: Defaults to re-running *all* out-of-date tasks. Runs minimal
                                          set to build targets if set to ``True``. Use with caution. 

   
    """
    
    


    link_task_names_to_functions ()
    #
    #   target jobs
    #     
    target_tasks = task_names_to_tasks ("Target", target_tasks)
    forcedtorun_tasks = task_names_to_tasks ("Forced to run", forcedtorun_tasks)
    (topological_sorted,
    self_terminated_nodes,
    dag_violating_edges,
    dag_violating_nodes) = topologically_sorted_nodes(  target_tasks, forcedtorun_tasks, 
                                                        gnu_make_maximal_rebuild_mode)

    if len(dag_violating_nodes):
        dag_violating_tasks = ", ".join(t._name for t in dag_violating_nodes)
        
        e = error_circular_dependencies("Circular dependencies found in the "
                                        "pipeline involving one or more of (%s)" %
                                            (dag_violating_tasks))
        raise e

    #
    #   whether using multiprocessing
    #   
    pool = Pool(multiprocess) if multiprocess > 1 else None

    for task in topological_sorted:
        if not task.run_all_jobs_in_task(logger, pool, multiprocess, task in forcedtorun_tasks):
            break

#_________________________________________________________________________________________

#   pipeline_printout

#_________________________________________________________________________________________
def pipeline_printout(output_stream, target_tasks, forcedtorun_tasks = [], long_winded=False, indent = 4,
                                    gnu_make_maximal_rebuild_mode  = True,
                                    test_all_task_for_update        = True):
    """
    Printouts the parts of the pipeline which will be run

    Because the parameters of some jobs depend on the results of previous tasks, this function
    produces only the current snap-shot of task jobs. In particular, tasks which generate 
    variable number of inputs into following tasks will not produce the full range of jobs. 
    
    :param output_stream: where to print to
    :type output_stream: file-like object with ``write()`` function
    :param target_tasks: targets task functions which will be run if they are out-of-date
    :param forcedtorun_tasks: task functions which will be run whether or not they are out-of-date
    :param long_winded: More verbose output
    :param indent: How much indentation for pretty format. 
    :param gnu_make_maximal_rebuild_mode: Defaults to re-running *all* out-of-date tasks. Runs minimal
                                          set to build targets if set to ``True``. Use with caution.
    :param test_all_task_for_update: Ask all task functions if they are up-to-date 
    """

    link_task_names_to_functions ()

    #
    #   target jobs
    #     
    target_tasks = task_names_to_tasks ("Target", target_tasks)
    forcedtorun_tasks = task_names_to_tasks ("Forced to run", forcedtorun_tasks)
    (topological_sorted,
    self_terminated_nodes,
    dag_violating_edges,
    dag_violating_nodes) = topologically_sorted_nodes(target_tasks, forcedtorun_tasks, 
                                                        gnu_make_maximal_rebuild_mode,
                                                        test_all_task_for_update)


    if len(dag_violating_nodes):
        dag_violating_tasks = ", ".join(t._name for t in dag_violating_nodes)

        e = error_circular_dependencies("Circular dependencies found in the "
                                        "pipeline involving one or more of (%s)" %
                                            (dag_violating_tasks))
        raise e

    for task in topological_sorted:
        task.printout(output_stream, task in forcedtorun_tasks, long_winded, indent)


#   use high resolution timestamps where available            
#       default in python 2.5 and greater
#   N.B. File modify times / stat values have 1 second precision for many file systems
#       and may not be accurate to boot, especially over the network.
os.stat_float_times(True)
