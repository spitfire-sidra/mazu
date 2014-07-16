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
$ cp settings/production.example.py settings/production.py
```

Add a secret key in `settings/production.py`, like this:

```
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^v_m6li36$7*px46xw$)a(^&8_)sdfakfjkagu12-8=239r823ls**'
```

## USAGE

### start web server

```
$ cd mazu
$ ./manage.py runserver 127.0.0.1:8000
```

### start celery worker

1. start mongodb server first

2. start celery worker 

```
$ ./manage.py celery worker --app mazu --beat
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

