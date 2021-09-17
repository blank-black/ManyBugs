import docker
import bugzoo
import os
import argparse
import json


def main():
    # parser = argparse.ArgumentParser(add_help=True, usage="")
    # parser.add_argument("--number", "-n", dest='num',
    #                     default=0)
    #
    # args = parser.parse_args()
    # num = args.num
    # read_json()
    # run(num)

    url = "http://127.0.0.1:8080"
    client_bugzoo = bugzoo.Client(url)

    finish_list = []
    for line in open('finished.txt', 'r'):
        finish_list.append(line.strip('\n'))
    bug_num = -1

    for name in client_bugzoo.bugs:
        container_id = ''
        bug_num += 1
        if name in finish_list:
            continue

        try:
            print(str(bug_num) + ' start')
            bug = client_bugzoo.bugs[name]
            bug_name = bug.name
            print(bug_name)
            os.system('bugzoo bug build ' + name + ' > log/' + name + '_build.log')
            print(name, file=open('finished.txt', 'a'))
            print(str(bug_num) + ' finish')
        except Exception as e:
            print('Err: ' + str(e))


if __name__ == "__main__":
    main()
