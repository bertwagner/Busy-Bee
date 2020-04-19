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
	pip install --target=python -r "Lambda/${LAMBDA_NAME}/requirements.txt"
}

zip_files() {
	echo "Copying Lambda scripts into depedencies folder"
	cp *.publish_dependencies_as_layer /python
	Echo "Zipping everything up"
	zip -r lambda_funcion.zip ./python
}

deploy_to_lambda() {
	echo "Deploying the code to AWS Lambda"
	aws lambda update-function-code --function-name "${LAMBDA_NAME}" --zip-file fileb://lambda_function.zip
}

# # publish_dependencies_as_layer(){
# # 	echo "Publishing dependencies as a layer..."
# # 	local result=$(aws lambda publish-layer-version --layer-name "${INPUT_LAMBDA_LAYER_ARN}" --zip-file fileb://dependencies.zip)
# # 	LAYER_VERSION=$(jq '.Version' <<< "$result")
# # 	rm -rf python
# # 	rm dependencies.zip
# # }

# # publish_function_code(){
# # 	echo "Deploying the code itself..."
# # 	zip -r code.zip . -x \*.git\*
# # 	aws lambda update-function-code --function-name "${INPUT_LAMBDA_FUNCTION_NAME}" --zip-file fileb://code.zip
# # }

# # update_function_layers(){
# # 	echo "Using the layer in the function..."
# # 	aws lambda update-function-configuration --function-name "${INPUT_LAMBDA_FUNCTION_NAME}" --layers "${INPUT_LAMBDA_LAYER_ARN}:${LAYER_VERSION}"
# # }

deploy_lambda_function() {
    configure_aws_credentials
	install_dependencies
	zip_files
	deploy_to_lambda
}


deploy_lambda_function