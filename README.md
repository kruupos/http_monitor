# SNIWI

Sniwi - the kiwi sniffer, is a monitoring tool intended to alert any user on detecting abnormalities with HTTP traffic on his machine.

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

#### Locally, if you have python 3.7 installed

```bash
python3 -m sniwi
```

#### Using docker

```bash
# first build the application, you need to do this only once
docker-compose build
# then launch the app
docker-compose --rm run sniwi
```

Because tty and stdin are set to true in docker-compose, running the app will launch the app directly inside your terminal
