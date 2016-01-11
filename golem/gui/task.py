import requests
import datetime
import sys
import os
import csv

import utils

def verify_status_code(url, status_code):
    start_time = datetime.datetime.now()
    r = requests.get(url)
    end_time = datetime.datetime.now()
    if r.status_code == int(status_code):
        time_delta = end_time - start_time
        return time_delta.total_seconds()
    else: 
        return -1


def write_result(task_id, result):
    path = os.path.join('results', '{}.csv'.format(task_id))
    with open(path, "ab") as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow([utils.time_to_string(), result])


# main
task_id = sys.argv[1]
test_type = sys.argv[2]
url = sys.argv[3]
status_code = ''
if test_type == 'status':
    status_code = sys.argv[4]

result = verify_status_code(url, status_code)

write_result(task_id, result)


