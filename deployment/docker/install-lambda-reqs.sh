#!/bin/bash
# Usage ./install-lambda-reqs.sh <absolute_path_to_lambda_function_directory>


# install lambda's python requirements
docker run -it -v "$1":/lambda_build_dir \
    scottx611x/aws-linux-python-3.6 \
        /usr/bin/pip-3.6 install \
        -r /lambda_build_dir/requirements.txt \
        -t /lambda_build_dir/__python_reqs__