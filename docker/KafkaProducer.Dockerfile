FROM python:3.6

WORKDIR /app/
ADD ./producer_server/requirements.txt /app/

RUN pip install -r requirements.txt
VOLUME [ "/usr/local/lib/python3.6/site-packages/", "/app/" ]

