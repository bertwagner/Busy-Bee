#!/bin/sh 

set -e

configure_aws_credentials() {
	aws configure set aws_access_key_id "${AWS_ACCESS_KEY_ID}"
    aws configure set aws_secret_access_key "${AWS_SECRET_ACCESS_KEY}"
    aws configure set default.region "${AWS_REGION}"
}

install_dependencies() {
	echo "Installing and zipping dependencies..."
	mkdir python
	# pip install --target=python -r "Lambda/${LAMBDA_NAME}/requirements.txt"
}

zip_files() {
	echo "Copying Lambda scripts into depedencies folder"
	cp -R "Lambda/${LAMBDA_NAME}" python/
	echo "Zipping everything up"
	zip -r lambda_function.zip python
}

deploy_to_lambda() {
	echo "Deploying the code to AWS Lambda"
	aws lambda update-function-code --function-name "${LAMBDA_NAME}" --zip-file fileb://lambda_function.zip
}

deploy_lambda_function() {
    configure_aws_credentials
	install_dependencies
	zip_files
	deploy_to_lambda
}


deploy_lambda_function