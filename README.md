# MAZU - with ipython inside
## Malware Repository with social sharing feature
##  

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
[NotebookApp] Using existing profile dir: u'/home/kippo/.ipython/profile_nbserver'
[NotebookApp] The IPython Notebook is running at: http://127.0.0.1:8888
[NotebookApp] Use Control-C to stop this server and shut down all kernels.

```

### Now you can use ipython notebook to interact with mazu on 127.0.0.1:8888 !
