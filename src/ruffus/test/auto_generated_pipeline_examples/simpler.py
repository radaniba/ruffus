#!/usr/bin/env python2.5
"""

    test_tasks.py

"""


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   options        


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

from optparse import OptionParser
import sys, os
import os.path
import StringIO

# add self to search path for testing
exe_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
if __name__ == '__main__':
    module_name = os.path.split(sys.argv[0])[1]
    module_name = os.path.splitext(module_name)[0];
else:
    module_name = __name__

# graph, task etc are one directory down
if __name__ == '__main__':
    sys.path.append("/net/cpp-group/Leo/inprogress/pipeline/installation/src/ruffus")



parser = OptionParser(version="%prog 1.0")
parser.add_option("-t", "--target_tasks", dest="target_tasks",
                  action="append",
                  default = list(),
                  metavar="JOBNAME", 
                  type="string",
                  help="Target task(s) of pipeline.")
parser.add_option("-f", "--forced_tasks", dest="forced_tasks",
                  action="append",
                  default = list(),
                  metavar="JOBNAME", 
                  type="string",
                  help="Pipeline task(s) which will be included even if they are up to date.")
parser.add_option("-j", "--jobs", dest="jobs",
                  default=5,
                  metavar="jobs", 
                  type="int",
                  help="Specifies  the number of jobs (commands) to run simultaneously.")
parser.add_option("-v", "--verbose", dest = "verbose",
                  action="count", default=0,
                  help="Print more verbose messages for each additional verbose level.")
parser.add_option("-d", "--dependency", dest="dependency_file",
                  default="simple.svg",
                  metavar="FILE", 
                  type="string",
                  help="Print a dependency graph of the pipeline that would be executed "
                        "to FILE, but do not execute it.")
parser.add_option("-F", "--dependency_graph_format", dest="dependency_graph_format",
                  metavar="FORMAT", 
                  type="string",
                  default = 'svg',
                  help="format of dependency graph file. Can be 'ps' (PostScript), "+
                  "'svg' 'svgz' (Structured Vector Graphics), " +
                  "'png' 'gif' (bitmap  graphics) etc ")
parser.add_option("-n", "--just_print", dest="just_print",
                    action="store_true", default=False,
                    help="Print a description of the jobs that would be executed, "
                        "but do not execute them.")
parser.add_option("-M", "--minimal_rebuild_mode", dest="minimal_rebuild_mode",
                    action="store_true", default=False,
                    help="Rebuild a minimum of tasks necessary for the target. "
                    "Ignore upstream out of date tasks if intervening tasks are fine.")
parser.add_option("-K", "--no_key_legend_in_graph", dest="no_key_legend_in_graph",
                    action="store_true", default=False,
                    help="Do not print out legend and key for dependency graph.")
parser.add_option("-H", "--draw_graph_horizontally", dest="draw_horizontally",
                    action="store_true", default=False,
                    help="Draw horizontal dependency graph.")

parameters = [  
                ]







#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   imports        


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

import StringIO
import re
import operator
import sys
from collections import defaultdict

from graph import *
from task import *
import task
from print_dependencies import *
# use simplejson in place of json for python < 2.6
try:
    import json
except ImportError:
    import simplejson
    json = simplejson

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   Functions


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

def create_custom_file_func(params):
    """
    creates function which can be used as input to @files_func
    """
    def cust_func ():
        for job_param in params:
            yield job_param
    return cust_func
    
    
def is_job_uptodate (infiles, outfiles, *extra_params):
    """
    assumes first two parameters are files, checks if they are up to date
    """
    return task.needs_update_check_modify_time (infiles, outfiles, *extra_params)
    
    
    
def test_post_task_function ():
    print "Hooray"

import time
def test_job_io(infiles, outfiles, extra_params):
    """
    cat input files content to output files
        after writing out job parameters
    """
    # dump parameters
    params = (infiles, outfiles) + extra_params
    sys.stdout.write('    job = %s\n' % json.dumps(params))

    
        
    if isinstance(infiles, str):
        infiles = [infiles]
    elif infiles == None:
        infiles = []
    if isinstance(outfiles, str):
        outfiles = [outfiles]
    output_text = list()
    for f in infiles:
        output_text.append(open(f).read())
    output_text = "".join(sorted(output_text))
    output_text += json.dumps(infiles) + " -> " + json.dumps(outfiles) + "\n"
    for f in outfiles:
        open(f, "w").write(output_text)
    time.sleep(1)


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   Main logic


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888





# get help string
f =StringIO.StringIO()
parser.print_help(f)
helpstr = f.getvalue()
(options, remaining_args) = parser.parse_args()





#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   Tasks


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888


#
#    task1
#
@files(None, 'a.1')
def task1(infiles, outfiles, *extra_params):
    """
    First task
    """
    test_job_io(infiles, outfiles, extra_params)



#
#    task2
#
@files_re('*.1', '(.*).1', r'\1.1', r'\1.2')
@follows(task1)
def task2(infiles, outfiles, *extra_params):
    """
    Second task
    """
    test_job_io(infiles, outfiles, extra_params)



#
#    task3
#
@files_re('*.1', '(.*).1', r'\1.2', r'\1.3')
@follows(task2)
def task3(infiles, outfiles, *extra_params):
    """
    Third task
    """
    test_job_io(infiles, outfiles, extra_params)



#
#    task4
#
@files_re('*.1', '(.*).1', r'\1.3', r'\1.4')
@follows(task3)
def task4(infiles, outfiles, *extra_params):
    """
    Fourth task
    """
    test_job_io(infiles, outfiles, extra_params)



        
if options.just_print:
    pipeline_printout(sys.stdout, options.target_tasks, options.forced_tasks, 
                        long_winded=True, 
                        gnu_make_maximal_rebuild_mode = not options.minimal_rebuild_mode)

elif options.dependency_file:
    pipeline_printout_graph (     open(options.dependency_file, "w"),
                         options.dependency_graph_format,
                         options.target_tasks, 
                         options.forced_tasks,
                         draw_vertically = not options.draw_horizontally,
                         gnu_make_maximal_rebuild_mode  = not options.minimal_rebuild_mode,
                         no_key_legend  = options.no_key_legend_in_graph)
else:    
    pipeline_run(options.target_tasks, options.forced_tasks, multiprocess = options.jobs, 
                    gnu_make_maximal_rebuild_mode  = not options.minimal_rebuild_mode)
    
