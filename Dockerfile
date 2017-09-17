FROM python:3.6

MAINTAINER AHAPX
MAINTAINER anarchy.b@gmail.com

COPY src /bot

RUN pip install -U pip
RUN pip install -r /bot/requirements.txt

VOLUME /bot/
WORKDIR /bot/

CMD python main.py
