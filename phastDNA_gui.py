import flask
import time
import subprocess
import mmap
import datetime
from pathlib import Path
from threading import Thread
from collections import defaultdict


app = flask.Flask(__name__, template_folder=".")

current_task_file = ''
ptrs = defaultdict(dict)
# tasks = {}


# def run_wrapper(task_name):
#     with open(f"{task_name}.log", "w") as f:
#         cmd = subprocess.Popen(['python', 'dummyscript.py', '-l', task_name], stdout=f)
    # subprocess.Popen(['python', 'dummyscript.py', '-l', task_name, ">", f"{task_name}.log"], shell=True)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route("/task", methods=['GET', 'POST'])
def test_f():
    if flask.request.method == 'POST':
        # req_data = flask.request.get_json(force=True)
        data = flask.request.form

        # name_prefix = "train" if 'loss' in data else "predict"
        # task_name = f'{name_prefix}_{datetime.datetime.now():%Y_%m_%d_%H_%M_%S%z}'
        output_dir = Path(data["output_path"])
        output_dir.mkdir(parents=True, exist_ok=True)
        # task_name = f'{data["output_path"]}%PHastDNA.log'
        # print(output_dir.name)
        task_name = f'{output_dir.name}%PHastDNA.log'
        task_file_obj = open(f'{data["output_path"]}/PHastDNA.log', 'a')
        task_file_obj.write(" ")
        task_file_obj.close()
        # print(data)
        global current_task_file
        global ptr
        current_task_file = task_name
        ptr = 0

        ptrs[task_name]['ptr'] = 0
        ptrs[task_name]['path'] = f'{data["output_path"]}/PHastDNA.log'

        # tasks[task_name] = {}
        # print(task_name)
        # print("Run test_f")
        # run_thread = Thread(target=run_wrapper, args=task_name)
        # run_thread.start()
        # time.sleep(3)
        # cmd = subprocess.Popen(['ping', 'google.com', '-t'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # cmd = subprocess.Popen(['ping', 'google.com', '-t'], shell=True)
        # stdout, error = cmd.communicate()
        # for line in cmd.stdout:
        #     print(line)

        # cmd = subprocess.Popen(['python', 'dummyscript.py', '-l', task_name, ">", f"{task_name}.log"], shell=True)
        # with open(f"{task_name}.log", "w") as f:
        # cmd = subprocess.Popen(['python', 'dummyscript.py', '-l', task_name])
        cmd = subprocess.Popen(['python', 'phastdna.py', '-O', data["output_path"], '-H', data["host_path"], '-V', data["virus_path"], '-e', '1', '-p', '1', '-i', '2', '--filter', data["filter"]])
        print(data)
        # subprocess.Popen(['python', 'dummyscript.py', '-l', task_name], stdout=f)
        return flask.render_template('task.html', task_name=task_name)
        # return subprocess.check_output(['ping', 'google.com', '-t'])


@app.route("/test/<id>")
def get_status(id):
    # global ptr
    print(ptrs)

    # if id not in ptrs:
    #     ptrs[id] = 0

    ptr = ptrs[id]['ptr']
    status = 1
    # id_filename = id.replace('%', '/')
    # print(id_filename)
    with open(ptrs[id]['path'], "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)
        
        if ptr == 0:
            logs = str(mm[::], 'utf-8')
            ptr = len(mm)
            ptrs[id]['ptr'] = ptr
            return flask.jsonify({'content': logs, 'status': status})

        logs = str(mm[ptr:], 'utf-8')
        ptr = len(mm)

        if 'finished' in logs:
            status = 0

        if 'Traceback' in logs:
            status = -1

        ptrs[id]['ptr'] = ptr
        # print(logs)
    return flask.jsonify({'content': logs, 'status': status})


if __name__ == '__main__':
    app.run(debug=True)
