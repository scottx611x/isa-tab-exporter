#!/bin/bash

./docker_context/install-lambda-reqs.sh $PWD/lambda_function

# initialize Terraform and apply infrastructure changes
cd terraform
terraform init
terraform apply -auto-approve
cd ..