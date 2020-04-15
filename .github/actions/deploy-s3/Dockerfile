FROM python:3.8-alpine

LABEL "com.github.actions.name"="Deploy S3"
LABEL "com.github.actions.description"="Copy files to S3 bucket"

ENV AWSCLI_VERSION='2.0.7'

RUN pip install --quiet --no-cache-dir awscli==${AWSCLI_VERSION}

ADD entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]