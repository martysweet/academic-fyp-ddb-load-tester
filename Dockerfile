FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install python-dev python-pip -y && \
    apt-get clean

RUN pip install awscli

WORKDIR /tmp/workdir
COPY main.py /tmp/workdir
COPY requirements.txt /tmp/workdir
COPY countries.txt /tmp/workdir

RUN pip install -r requirements.txt

ENTRYPOINT python main.py -t ${STRESS_TYPE} -r ${TABLE_REGION} -n ${TABLE_NAME} -k ${HASH_KEY} -u ${UNITS} -d ${DURATION}