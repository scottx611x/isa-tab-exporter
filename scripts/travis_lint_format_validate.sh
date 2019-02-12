#!/usr/bin/env bash

flake8
black --check --diff .

cd deployment/terraform
terraform fmt -check=true -diff=true
terraform init -backend-config="bucket=$TERRAFORM_STATE_BUCKET" -input=false
terraform validate
cd ..