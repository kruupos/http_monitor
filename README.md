[![Build Status](https://travis-ci.org/kruupos/sniwi.svg?branch=master)](https://travis-ci.org/kruupos/sniwi)

# SNIWI

Sniwi - the kiwi sniffer, is a monitoring tool intended to alert any user by detecting high HTTP traffic appening real-time on a webserver.

```
  __ _
 /  ('>-
 \__/
 L\_
 ```                           


It will simply 'sniff' the [apache logfile](https://httpd.apache.org/docs/2.2/en/logs.html) located in `/var/log/apache.log` and giving you interseting feedback it might have found.

### Requierments

* Python3.7

OR

* Docker
* docker-compose

## Setup

#### 1. Clone this repository. 

```bash
# clone the frontend repository
git clone https://github.com/kruupos/sniwi.git
```

### 2. Run the app

#### Locally, if you have python 3.7 and pipenv installed 

```bash
pipenv shell
python3 -m sniwi
```

#### Using docker

```bash
# first build the docker image, you need to do this only once
docker-compose build
# then launch the app
docker-compose run --rm sniwi # May freeze.
```

Note: if you have docker-for-windows installed you can use

```bash
docker-compose run --rm sniwi_windows
```

it will map the container folder `/var/log` to your current folder.

Because tty and stdin are set to true in docker-compose, running the app will launch the app directly inside your terminal

### Usage

```bash
usage: sniwi [-h] [-f PATH] [-i SECOND] [-a SECOND] [-t SECOND]

optional arguments:
  -h, --help                             show this help message and exit
  -f PATH, --file-path PATH              path of monitoring file
  -i SECOND, --threshold-max-hits SECOND ratio requests/secs to trigger an alert
  -a SECOND, --alert-interval SECOND     interval for alert
  -t SECOND, --traffic-interval SECOND   interval for refreshing traffic information
```

### Unit Tests

Done with `pytest`

#### Using docker (recommanded)

```bash
# first build the docker image, you need to do this only once
docker-compose -f ./docker-compose.test.yml build
# Then run pytest
docker-compose -f ./docker-compose.test.yml run --rm pytest
```

#### Using pytest

```bash
# run pipenv
pipenv shell
# Then run the tests
pytest ./tests -v
```

#### Architecture

### Sniwi

instanciate `ConsoleInterface` and `Sniffer`

Core class of the application, handling all the coroutines created in the main loop with `ayncio`.

3 of them are periodical and are acting like a clock by awaiting themselves with different timer after an asynchrounous sleep.

`tick()`, `alert()` and `traffic()` are responsible to send data to the console interface in order to display up-to-date metrics

`aio_readline` poll and await for new data

### ConsoleInterface

Is responsible for the console, using `urwid` as a library.

### Sniffer

Generate a asynchronous generator to be used by `aio_readline` coro.

Poll new data from file using aiofiles library (support of open witch `asyncio`) in a while loop using `readline()`.

Then, if the data is valid, feed it to `LogParser` to transform it to an useful dictionnary

### LogParser

Responsible for parsing all the incoming requests. It uses `regexp`
