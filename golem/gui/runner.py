import json
import time
import os
import subprocess
import sys

import utils



while True:


	# read tasks
	tasks = None
	with open('tasks.json') as tasks_file:
		tasks = json.load(tasks_file)

	for task in tasks:
		time_span = utils.get_time_span(task['id'])
		if time_span > task['interval']:
			# execute task
			pid = subprocess.Popen([
					sys.executable, 
					'task.py',
					task['id'], 
					task['type'],
					task['url'],
					task['status_code']
					])



	time.sleep(2)