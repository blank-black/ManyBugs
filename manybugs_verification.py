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
    parser.add_argument("--name", "-n", dest='name',
                        default='', help='run single version name')
    parser.add_argument("--work-path", "-path", dest='work_path',
                        default='.')
    parser.add_argument("--script-name", "-script", dest='script_name',
                        default='run.py', help='in docker script, default run.py')
    parser.add_argument("--print-to-screen", action='store_true', default=False,
                        help='if print log to screen, default false')
    parser.add_argument("--read-file", action='store_true', default=False,
                        help='if read target versions from file, default false')
    parser.add_argument("--file-name", dest='file_name', default='target.txt',
                        help='name of reading from file')

    args = parser.parse_args()
    global WORK_PATH
    WORK_PATH = os.path.abspath(args.work_path)
    global SCRIPT_NAME
    SCRIPT_NAME = args.script_name
    global PRINT_TO_SCREEN
    PRINT_TO_SCREEN = args.print_to_screen
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
        time.sleep(3)
        os.chdir(WORK_PATH)
        if name:
            run_single_version(name, WORK_PATH, SCRIPT_NAME, PRINT_TO_SCREEN)
        elif READ_FILE:
            run_from_file()
        else:
            print('Use single version or run from target files!')
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

        err = os.system('pipenv run bugzoo source add manybugs https://github.com/squaresLab/ManyBugs')
        if err != 0:
            print('bugzoo source add ManyBugs error')
            # return 1

        err = os.system('pipenv run bugzoo source add genprog https://github.com/squaresLab/genprog-code')
        if err != 0:
            print('bugzoo source add genprog error')
            # return 1

        err = os.system('pipenv run bugzoo tool build genprog')
        if err != 0:
            print('bugzoo tool build error')
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
            if not os.path.isdir(os.path.join(WORK_PATH, 'build_log')):
                os.system('mkdir ' + os.path.join(WORK_PATH, 'build_log'))
            if not PRINT_TO_SCREEN:
                os.system('pipenv run bugzoo bug build ' + name + ' > ' + os.path.join(WORK_PATH, 'build_log', name + '.log 2>&1'))
            else:
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


def run_from_file():
    name_list = []
    os.chdir(WORK_PATH)
    print('run from file start!')
    try:
        for line in open(TARGET_FILE_NAME, 'r'):
            name_list.append((line.strip('\n'), WORK_PATH, SCRIPT_NAME, PRINT_TO_SCREEN))
        p = multiprocessing.Pool(MAX_CORE)
        p.starmap(run_single_version, name_list)
    except Exception as e:
        print('run_from_file Err: ' + str(e))

    print('run from file end!')


def run_single_version(name, work_path, script_name, print_to_screen):
    global WORK_PATH
    WORK_PATH = work_path
    global SCRIPT_NAME
    SCRIPT_NAME = script_name
    global PRINT_TO_SCREEN
    PRINT_TO_SCREEN = print_to_screen
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
                    print('name:' + name)
                    print('container_id:' + container_id)
                    print('Build success! Please use: $ docker exec -it ' + container_id + ' /bin/bash')
                    print('to get into the ' + name + ' container!')
                    break
                except Exception as e:
                    print('run_single_version Err : ' + str(e))


if __name__ == "__main__":
    main()