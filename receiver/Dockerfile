FROM ubuntu:18.04

LABEL maintainer="kbyin2@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip


WORKDIR /app
COPY ./* /app


RUN pip3 install -r requirements.txt


ENTRYPOINT ["python3"]

CMD ["app.py"]