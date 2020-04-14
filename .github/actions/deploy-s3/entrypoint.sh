#!/bin/sh

set -e

aws configure --profile deploy-s3 <<-EOF > /dev/null 2>&1
${AWS_ACCESS_KEY_ID}
${AWS_SECRET_ACCESS_KEY}
${AWS_REGION}
text
EOF

sh -c "aws s3 sync ${SOURCE_DIR:-.} s3://${AWS_S3_BUCKET} \
              --profile deploy-s3 \
              --no-progress \
              $*"

aws configure --profile deploy-s3 <<-EOF > /dev/null 2>&1
null
null
null
text
EOF