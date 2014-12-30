# MAZU - MALWARE REPOSITORY WITH SOCIAL SHARING FEATURE

[![Build Status](https://travis-ci.org/PwnDoRa/mazu.svg?branch=master)](https://travis-ci.org/PwnDoRa/mazu)

## INSTALLATION PREREQUISITES

- python 2.7
- django
- mongodb
- libmagic

## INSTALLATION

### Ubuntu

```
$ git clone https://github.com/PwnDoRa/mazu
$ cd mazu
$ chmod +x deploy_mazu.sh
$ ./deploy_mazu.sh
```

## USAGE

### Start mazu service

```
$ cd mazu
$ chmod +x start_mazu.sh
$ ./start_mazu.sh 
```

### Type in ip and port
```
-= RUNNING Mazu =-
==> Here we go...
  > Migrating celery database...
  > Initializing database...
  > Starting web service...
  > Type in IP address that binds mazu to : 127.0.0.1
  > Type in port number that runs mazu :8000
  > Starting celery worker...
```

## Now Mazu service is running on 127.0.0.1:8000 !
