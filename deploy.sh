#!/usr/local/bin/bash

# install lambda's python requirements
pip install -r lambda_function/requirements.txt -t lambda_function/_python_requirements_


# initialize Terraform and apply infrastructure changes
cd terraform
terraform init
terraform apply -auto-approve
cd ..