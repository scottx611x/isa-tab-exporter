#!/usr/local/bin/bash

# install lambda's python requirements
docker run -it -v "$PWD/lambda_function":/lambda_build_dir \
    scottx611x/aws-linux-python-3.6 \
    /usr/bin/pip-3.6 install -r /lambda_build_dir/requirements.txt -t /lambda_build_dir/__python_reqs__

# initialize Terraform and apply infrastructure changes
cd terraform
terraform init
terraform apply -auto-approve
cd ..