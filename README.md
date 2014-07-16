# MAZU - MALWARE REPOSITORY WITH SOCIAL SHARING FEATURE

## PREREQUISITE

- python 2.7
- django
- mongodb
- libmagic

## MAC OS X 10.9

If your OS is above MAC OS X 10.9, use the following command first:

```
$ export ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future
```

## INSTALLATION (Ubuntu, MAC OS X)

```
$ sudo apt-get install python-dev libxml2-dev libxslt-d
$ git clone https://github.com/PwnDoRa/mazu
$ cd mazu
$ pip install -r requirements.txt
```

## USAGE

```
$ cd mazu
$ ./manage.py runserver 127.0.0.1:8000
```

## CONTRIBUTE

### TOOLS

- virtualenv
- virtualenvwrapper
- south

```
$ pip install virtualenv
$ pip install virtualenvwrapper
$ pip install south
```

