# MAZU - MALWARE REPOSITORY WITH SOCIAL SHARING FEATURE

[![Build Status](https://travis-ci.org/PwnDoRa/mazu.svg?branch=master)](https://travis-ci.org/PwnDoRa/mazu)

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
$ sudo apt-get install python-dev libxml2-dev libxslt-dev
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

### Initialize database

```
$ cd mazu
$ ./manage.py syncdb
```

### start web server

```
$ ./manage.py runserver 127.0.0.1:8000
```

### start celery worker

1. start mongodb server first

2. start celery worker 

```
$ ./manage.py celery worker --app mazu --beat
```

## Start a broker for sharing samples through hpfeeds (experimental)

### create an user and an broker for testing

```
./manage.py shell
>>> from django.contrib.auth.models import User
>>> from authkey.models import AuthKey
>>> User.objects.create_user('username', 'username@example.com', 'password').save()
>>> usr = User.objects.get(username='username')
>>> AuthKey(owner=usr, ident='ident', secret='secret', pubchans='["chan1"]', subchans='["chan1"]').save()
```

### start a broker

```
vim broker/config.py
python broker/broker.py
```

### publish a message just for fun

#### install hpfeeds on your system:

```
git clone https://github.com/rep/hpfeeds
pip install gevent
cd hpfeeds/cli/
cp ../lib/hpfeeds.py ./
```

#### documentation of hpfeeds-client.py

```
hpfeeds-client
Usage: hpfeeds-client -i ident -s secret --host host -p port -c channel1 [-c channel2, ...] <action> [<data>]

hpfeeds-client: error: You need to give "subscribe" or "publish" as <action>.
```

for example, publish a message on "chan1" can use command line like below:

```
./hpfeeds-client -i ident -s secret --host 127.0.0.1 -p 20000 -c chan1 publish "helloworld"
```

subscribe messages of "chan1" can use command line:

```
./hpfeeds-client -i ident -s secret --host 127.0.0.1 -p 20000 -c chan1 subscribe
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

