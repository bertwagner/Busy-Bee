FROM python:3.8-alpine

RUN pip install --quiet --no-cache-dir awscli==2.0.7

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]