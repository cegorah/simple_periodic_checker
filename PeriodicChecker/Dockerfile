from python:3.8.3-alpine
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev curl wget iproute2 vim sudo libffi-dev openssl-dev bash
RUN adduser --disabled-password --shell /bin/sh web_app
RUN echo "web_app ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /home/web_app/
COPY . /home/web_app
RUN chown -R web_app:web_app /home/web_app
WORKDIR /home/web_app/
RUN pip3 install --upgrade pip
RUN pip3 install -e .[tests]
WORKDIR /home/web_app/src
RUN pip3 install --no-cache-dir -r requirements.txt
USER web_app
CMD ["/bin/bash", "/home/web_app/docker_run.sh"]