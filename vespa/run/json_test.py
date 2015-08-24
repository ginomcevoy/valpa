""" Simulate a submission that is read and converted to JSON. """

import json
from pprint import pprint

def dump_submission_json():
    exp1 = {'name' : 'parpac-nc32-cpv2-idf8-psNONE',
            'cluster' : 'nc32-cpv2-idf8-psNONE',
            'application' : 'parpac',
            'start' : '2015-08-24 10:05:00',
            'finished' : True,
            'deployed' : True,
            'deploymentError' : ''}
    
    exp2 = {'name' : 'parpac-nc32-cpv4-idf8-psNONE',
            'cluster' : 'nc32-cpv2-idf8-psNONE',
            'application' : 'parpac',
            'start' : '2015-08-24 10:30:00',
            'finished' : True,
            'deployed' : False,
            'deploymentError' : 'kvm-pbs03-04 timeout'}
    
    exp3 = {'name' : 'parpac-nc32-cpv8-idf8-psNONE',
            'cluster' : 'nc32-cpv2-idf8-psNONE',
            'application' : 'parpac',
            'start' : '2015-08-24 10:35:00',
            'finished' : False,
            'deployed' : False,
            'deploymentError' : ''}
    
    exp4 = {'name' : 'parpac-nc32-cpv2-idf4-psNONE',
            'cluster' : 'nc32-cpv2-idf8-psNONE',
            'application' : 'parpac',
            'start' : '',
            'finished' : False,
            'deployed' : False,
            'deploymentError' : ''}
    
    submission = { 'submission' : 'parpac-place-32.xml',
                   'submitted' : '2015-08-24 10:00:00',
                   'description' : 'Parpac with 32 nodes under different placements',
                   'experiments' : [exp1, exp2, exp3, exp4]
                  }
    
    return json.dumps(submission, indent=4)

def read_submission_json():
    with open('submission.json') as submission_file:    
        submission = json.load(submission_file)
        
    return submission

if __name__ == "__main__":
    #submission = dump_submission_json()
    submission = read_submission_json()
    pprint(submission)