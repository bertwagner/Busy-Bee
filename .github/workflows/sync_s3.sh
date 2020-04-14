#!/bin/sh
pip install --quiet --no-cache-dir awscli==2.0.7

# Exit immediately upon error
set -e


aws configure --profile busy-bee-app-deployments \
${{secrets.AWS_Access_Key_ID}} \
${{secrets.AWS_Secret_Access_Key}} \
us-east-1 \
text

sh -c "aws s3 sync ${SOURCE_DIR:-.} s3://busy-bee.app/ \
              --profile busy-bee-app-deployments \
              --no-progress ./S3/busy-bee.app $*"

# Clear out credentials after we're done.
# We need to re-run `aws configure` with bogus input instead of
# deleting ~/.aws in case there are other credentials living there.
# https://forums.aws.amazon.com/thread.jspa?threadID=148833
aws configure --profile busy-bee-app-deployments \
null \
null \
null \
text