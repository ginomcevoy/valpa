""" Facade for the Ansible API. Provides functions to call scripts and playbooks. """

from ansible.playbook import PlayBook
from ansible import callbacks, utils, runner
import json
from sys import stdout

def ansible_playbook(playbook, inventory, forks, verbose):
    """ Calls an Ansible playbook using default callbacks. 
    
    Raises
    ------
    PlaybookError if there was an error in the execution.
    
    """
    # setup playbook with default callbacks
    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
    pb = PlayBook(playbook=playbook, stats=stats, callbacks=playbook_cb,
                  runner_callbacks=runner_cb, host_list = inventory, forks=forks) 
    
    # execute playbook and look for possible errors
    results = pb.run()
    for hostname in results:
        if results[hostname]['failures'] != 0:
            # Found an error during playbook execution, 
            # report deployment failure to the caller
            raise PlaybookError("ERROR: Deployment of VMs failed: {}".format(hostname))

    # Playbook succeeded, inform output
    if verbose > 0:
        print json.dumps(results, sort_keys=True, indent=4, separators=(',', ':'))
        stdout.flush()

def ansible_script(inventory, script_args, forks, verbose):
    """ Calls Ansible runner with the script module. """
      
    theRunner = runner.Runner(host_list=inventory, module_name='script',
                              module_args=script_args, pattern='all',
                              forks=forks)
    out = theRunner.run()
    if verbose > 0:
        print json.dumps(out, sort_keys=True, indent=4, separators=(',', ': '))
        
class PlaybookError(Exception):
    pass