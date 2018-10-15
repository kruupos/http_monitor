FROM python:3.7

LABEL authors="kruupos"

# -- Install Pipenv:
RUN pip3 install pipenv

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# -- Install Application into container:
RUN set -ex && mkdir /usr/src/app

WORKDIR /usr/src/app

# -- Adding Pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# -- Install dependencies:
RUN pipenv install --deploy --system --ignore-pipfile

# -- Create access.log file
RUN touch /var/log/access.log
