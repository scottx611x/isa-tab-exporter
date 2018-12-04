#!/usr/local/bin/bash

# install lambda's python requirements
pip install -r lambda/requirements.txt -t lambda/_python_requirements_


# initialize Terraform and apply infrastructure changes
cd terraform
terraform init
terraform apply -auto-approve
cd ..