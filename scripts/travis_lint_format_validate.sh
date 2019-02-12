#!/usr/bin/env bash

flake8
black --check --diff .

cd deployment/terraform
terraform fmt -check=true -diff=true
terraform init -input=false
terraform validate
cd ..