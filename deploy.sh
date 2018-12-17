#!/bin/bash

./docker_context/install-lambda-reqs.sh $PWD

# initialize Terraform and apply infrastructure changes
cd terraform
terraform init
terraform apply -auto-approve
cd ..