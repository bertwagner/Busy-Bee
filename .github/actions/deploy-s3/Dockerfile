FROM python:3.8-alpine

RUN pip install --quiet --no-cache-dir awscli==1.18.39

# COPY entrypoint.sh /entrypoint.sh
ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]