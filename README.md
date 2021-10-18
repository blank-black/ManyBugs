# ManyBugs


## Pre requirement installation

```
$ pip3 install --upgrade bugzoo
$ pip3 install --upgrade docker
```

## Run

- Running with single version
```
$ python3 build_bugzoo.py -n semu/manybugs:php-2011-01-18-95388b7cda-b9b1fb1827
```

- Running with versions list in file (default: target.txt)
```
$ python3 build_bugzoo.py --read-file
```

