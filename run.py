import argparse
import os


def main():
    parser = argparse.ArgumentParser(add_help=True, usage="")
    parser.add_argument("--name", "-n", dest='name',
                        default=0)
    args = parser.parse_args()
    name = args.name
    sub_path_arr = []

    for line in open('/experiment/manifest.txt', 'r'):
        sub_path_arr.append(line.strip('\n'))
    if 'php' in name:
        os.system('cd /experiment/src && git reset --hard && git clean -fd')
    for sub_path in sub_path_arr:
        os.system('cd /experiment/src && cp ' + sub_path + ' ' + sub_path + '.backup')
        os.system('cd /experiment/src && cp /data/code_dir/' + name + '/' + sub_path.split('/')[-1].split('.')[0]
                  + '_new.c ' + sub_path)
        os.system('cd /experiment/src && cp /data/code_dir/' + name + '/' + 'scope.json '
                  + '/'.join(sub_path.split('/')[:-1]))
    if 'php' in name:
        os.system('cd /experiment/src && cat ../libxml.patch | patch -p0')
        os.system('cd /experiment/src && ./buildconf')
    os.system('cd /experiment/src && CC="wllvm" ./configure')
    os.system('cd /experiment/src && sed -i "s/-O2/-O0/g" Makefile')
    os.system('cd /experiment/src && CC="wllvm" CFLAGS="-c -emit-llvm -g -o -O0" make -j2')

    for sub_path in sub_path_arr:
        # os.system('cd /experiment/src/' + '/'.join(sub_path.split('/')[:-1]) + ' && extract-bc '
        #           + sub_path.split('/')[-1].split('.')[0] + '.o')
        os.system('cd /experiment/src/' + '/'.join(sub_path.split('/')[:-1])
                  + ' && mart -no-compilation .' + sub_path.split('/')[-1].split('.')[0]
                  + '.o.bc')


if __name__ == "__main__":
    main()
