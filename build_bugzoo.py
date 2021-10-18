import multiprocessing
import time

import docker
import bugzoo
import os
import argparse
import subprocess
import json

MAX_CORE = 6
PROGRAM = ''
WORK_PATH = ''
SCRIPT_NAME = ''
LOG_DIR = ''
READ_FILE = False
TARGET_FILE_NAME = ''
CLEAN_CONTAINER = False
PRINT_TO_SCREEN = False
rebuild_container = True
check_item = 'buggy_err'
check_value = 'all test passed'
URL = "http://127.0.0.1:8080"


# Need python library: docker + bugzoo installed!
# pip3 install docker
# pip3 install bugzoo


def main():
    parser = argparse.ArgumentParser(add_help=True, usage="")
    # parser.add_argument("--build-bugzoo", action='store_true', default=False)
    parser.add_argument("--max-core", "-core", dest='max_core',
                        default=6)
    parser.add_argument("--name", "-n", dest='name',
                        default='')
    parser.add_argument("--program", "-p", dest='program',
                        default='')
    parser.add_argument("--work-path", "-path", dest='work_path',
                        default='.')
    parser.add_argument("--script-name", "-script", dest='script_name',
                        default='run.py')
    parser.add_argument("--log-dir", "-log", dest='log_dir',
                        default='log')
    parser.add_argument("--delete-container", action='store_true', default=False)
    parser.add_argument("--print-to-screen", action='store_true', default=False)
    parser.add_argument("--read-file", action='store_true', default=False)
    parser.add_argument("--file-name", dest='file_name', default='target.txt')

    args = parser.parse_args()
    global MAX_CORE
    MAX_CORE = int(args.max_core)
    global PROGRAM
    PROGRAM = args.program
    global WORK_PATH
    WORK_PATH = os.path.abspath(args.work_path)
    global SCRIPT_NAME
    SCRIPT_NAME = args.script_name
    global LOG_DIR
    LOG_DIR = args.log_dir
    global PRINT_TO_SCREEN
    PRINT_TO_SCREEN = args.print_to_screen
    global CLEAN_CONTAINER
    CLEAN_CONTAINER = args.delete_container

    if not os.path.isdir(LOG_DIR):
        os.system('mkdir ' + LOG_DIR)
    else:
        LOG_DIR = LOG_DIR + '-' + str(int(time.time()))
        os.system('mkdir ' + LOG_DIR)
    global READ_FILE
    READ_FILE = args.read_file
    global TARGET_FILE_NAME
    TARGET_FILE_NAME = args.file_name
    name = args.name

    try:
        os.chdir(WORK_PATH)
        if not os.path.isdir('BugZoo'):
            run_build_bugzoo()
        os.chdir('BugZoo')

        p = subprocess.Popen(['pipenv', 'run', 'bugzood', '-p', '8080'])
        print('starting bugzoo...')
        # time.sleep(3)
        os.chdir(WORK_PATH)
        if name:
            run_single_version(name, WORK_PATH, SCRIPT_NAME, LOG_DIR, PRINT_TO_SCREEN, CLEAN_CONTAINER)
        elif READ_FILE:
            run_from_file()
        else:
            run_all()
        p.kill()
    except Exception as e:
        print('main Err: ' + str(e))


def run_build_bugzoo():
    try:
        os.system('pip3 install --upgrade pip')
        os.system('pip3 install pipenv')
        os.chdir(WORK_PATH)
        os.system('git clone https://github.com/blank-black/BugZoo')
        os.chdir('Bugzoo')
        err = os.system('pipenv install .')
        if err != 0:
            print('pipenv install error')
            # return 1

        err = os.system('pipenv run bugzoo source add manybugs https://github.com/blank-black/ManyBugs')
        if err != 0:
            print('bugzoo source add ManyBugs error')
            # return 1

        err = os.system('pipenv run bugzoo source add genprog https://github.com/squaresLab/genprog-code')
        if err != 0:
            print('bugzoo source add genprog error')
            # return 1

        # err = os.system('pipenv run bugzoo tool build genprog')
        # if err != 0:
        #     print('bugzoo tool build error')
    except Exception as e:
        print('run_build_bugzoo Err: ' + str(e))
    finally:
        os.chdir(WORK_PATH)


def run_container(name):
    try:
        client = docker.from_env()
        client_bugzoo = bugzoo.Client(URL)
        find_flag = False
        for n in client_bugzoo.bugs:
            if name.split(':')[-1] in client_bugzoo.bugs[n].name.replace(':', '-'):
                name = client_bugzoo.bugs[n].name
                find_flag = True
                break
        if not find_flag:
            print("Can't find bug!")
            return '', ''
        built_flag = False
        image_tag = ''
        for n in [i.tags[0] for i in client.images.list()]:
            if name.split(':')[-1] in n:
                built_flag = True
                image_tag = n
                break
        if not built_flag:
            os.chdir(os.path.join(WORK_PATH, 'BugZoo'))
            os.system('pipenv run bugzoo bug build ' + name)
            os.chdir(WORK_PATH)
            client = docker.from_env()
            for n in [i.tags[0] for i in client.images.list()]:
                if name.split(':')[-1] in n:
                    image_tag = n
                    break
        if not image_tag:
            print("Can't build bug!")
            os.chdir(WORK_PATH)
            return '', ''

        os.chdir(os.path.join(WORK_PATH, 'BugZoo'))
        os.system('pipenv run bugzoo container launch -v ' + WORK_PATH + ':/data ' + name)
        os.chdir(WORK_PATH)
        for i in client.containers.list():
            if image_tag == i.image.tags[0]:
                return name, i.short_id
        print("Can't launch container!")
        return '', ''
    except Exception as e:
        print('run_container Err: ' + str(e))
    finally:
        os.chdir(WORK_PATH)


def run_in_docker(name, container_id):
    os.chdir(WORK_PATH)
    if container_id == '':
        print(name + " no container input!")
        return
    try:
        # print to file
        if not PRINT_TO_SCREEN:
            os.system('docker exec -t ' + container_id
                      + ' /bin/bash -c "cd /experiment && '
                        'cp /data/' + SCRIPT_NAME + ' . && '
                        'python3 ' + SCRIPT_NAME + ' -n ' + name +
                      '" > ' + os.path.join(LOG_DIR, name + '.log') + ' 2>&1')
        # print on screen
        else:
            os.system('docker exec -t ' + container_id
                      + ' /bin/bash -c "cd /experiment && '
                        'cp /data/' + SCRIPT_NAME + ' . && '
                        'python3 ' + SCRIPT_NAME + ' -n ' + name + '" ')
    except Exception as e:
        print('run_in_docker Err: ' + str(e))


def run_all():
    client_bugzoo = bugzoo.Client(URL)
    print('run all start!')
    try:
        p = multiprocessing.Pool(MAX_CORE)
        name_list = []
        for n in client_bugzoo.bugs:
            if not PROGRAM or PROGRAM in client_bugzoo.bugs[n].name:
                name_list.append((client_bugzoo.bugs[n].name, WORK_PATH, SCRIPT_NAME, LOG_DIR, PRINT_TO_SCREEN, CLEAN_CONTAINER))
        p.starmap(run_single_version, name_list)
    except Exception as e:
        print('run_all Err: ' + str(e))
    print('run all end!')


def run_from_file():
    name_list = []
    os.chdir(WORK_PATH)
    print('run from file start!')
    try:
        for line in open(TARGET_FILE_NAME, 'r'):
            name_list.append((line.strip('\n'), WORK_PATH, SCRIPT_NAME, LOG_DIR, PRINT_TO_SCREEN, CLEAN_CONTAINER))
        p = multiprocessing.Pool(MAX_CORE)
        p.starmap(run_single_version, name_list)
    except Exception as e:
        print('run_from_file Err: ' + str(e))

    print('run from file end!')


def run_single_version(name, work_path, script_name, log_dir, print_to_screen, clean_container):
    global WORK_PATH
    WORK_PATH = work_path
    global SCRIPT_NAME
    SCRIPT_NAME = script_name
    global LOG_DIR
    LOG_DIR = log_dir
    global PRINT_TO_SCREEN
    PRINT_TO_SCREEN = print_to_screen
    global CLEAN_CONTAINER
    CLEAN_CONTAINER = clean_container
    client = docker.from_env()
    container_id = ''

    if name and rebuild_container:
        name, container_id = run_container(name)
    if not name:
        print('Can find bug in bugzoo!')
        return 1

    else:
        for container in client.containers.list():
            if name.split(':')[-1] in container.image.tags[0]:
                name = container.image.tags[0].split('/')[-1].replace('-', ':', 1)
                container_id = container.short_id
                try:
                    print(name + ' start')
                    print('name:' + name)
                    print('container_id:' + container_id)
                    run_in_docker(name, container_id)
                    print(name + ' running finish\n')
                    break
                except Exception as e:
                    print('run_single_version Err : ' + str(e))
                finally:
                    if container_id != '' and CLEAN_CONTAINER:
                        os.system('docker stop ' + container_id)
                        os.system('docker rm ' + container_id)
                        print(name + ' clean\n')


if __name__ == "__main__":
    main()
