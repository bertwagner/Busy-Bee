#!/bin/bash

set -e

configure_aws_credentials(){
	aws configure set aws_access_key_id "${AWS_ACCESS_KEY_ID}"
    aws configure set aws_secret_access_key "${AWS_SECRET_ACCESS_KEY}"
    aws configure set default.region "${AWS_REGION}"
}

# install_zip_dependencies(){
# 	echo "Installing and zipping dependencies..."
# 	mkdir python
#     echo "Looking into Directory: ${LAMBDA_DIRECTORY}"
# 	pip install --target=python -r "${LAMBDA_DIRECTORY}/requirements.txt"
# 	zip -r dependencies.zip ./python
# }

# publish_dependencies_as_layer(){
# 	echo "Publishing dependencies as a layer..."
# 	local result=$(aws lambda publish-layer-version --layer-name "${INPUT_LAMBDA_LAYER_ARN}" --zip-file fileb://dependencies.zip)
# 	LAYER_VERSION=$(jq '.Version' <<< "$result")
# 	rm -rf python
# 	rm dependencies.zip
# }

# publish_function_code(){
# 	echo "Deploying the code itself..."
# 	zip -r code.zip . -x \*.git\*
# 	aws lambda update-function-code --function-name "${INPUT_LAMBDA_FUNCTION_NAME}" --zip-file fileb://code.zip
# }

# update_function_layers(){
# 	echo "Using the layer in the function..."
# 	aws lambda update-function-configuration --function-name "${INPUT_LAMBDA_FUNCTION_NAME}" --layers "${INPUT_LAMBDA_LAYER_ARN}:${LAYER_VERSION}"
# }

deploy_lambda_function(){
    configure_aws_credentials
	# install_zip_dependencies
	# publish_dependencies_as_layer
	# publish_function_code
	# update_function_layers
}

printf "TEST TEST BERT TEST"
deploy_lambda_function
echo "Each step completed, check the logs if any error occured."