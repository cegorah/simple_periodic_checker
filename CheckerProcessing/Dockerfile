from python:3.8.3-alpine
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev curl wget iproute2 vim sudo libffi-dev openssl-dev bash
RUN adduser --disabled-password --shell /bin/sh proc_app
RUN echo "proc_app ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /home/proc_app/
COPY . /home/proc_app
RUN chown -R proc_app:proc_app /home/proc_app
WORKDIR /home/proc_app/
RUN pip3 install --upgrade pip
RUN pip3 install -e .[tests]
RUN pip3 install --no-cache-dir -r ./src/requirements.txt
WORKDIR /home/proc_app/src/ProcessingServer
USER proc_app
ENTRYPOINT ./consumer_server.py