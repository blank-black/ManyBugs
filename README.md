# ManyBugs


## Pre requirement installation

```
$ pip3 install --upgrade bugzoo
$ pip3 install --upgrade docker
```

## Run Manybugs and Semu together in container 

- Running with single version
```
$ python3 build_bugzoo.py -n semu/manybugs:php-2011-01-18-95388b7cda-b9b1fb1827
```

- Running with versions list in file (default: target.txt)
```
$ python3 build_bugzoo.py --read-file
```

## Run original Manybugs or genprog container
- Running with single version
```
$ python3 manybugs_verification.py -n semu/manybugs:php-2011-01-18-95388b7cda-b9b1fb1827
```

- Running with versions list in file (default: target.txt)
```
$ python3 manybugs_verification.py --read-file
```

- Running genprog container
1. Run something using manybugs_verification.py for Manybugs
2. Run `$ docker images`
3. Find squareslab/genprog and the image id
4. Run `$ docker run -it --name {name} -v {path}:/data {image id from step 3} /bin/bash` 