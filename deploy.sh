#!/bin/bash

./docker_context/install-lambda-reqs.sh $PWD/lambda_function

# initialize Terraform and apply infrastructure changes
cd terraform
terraform init -input=false
terraform workspace select production
terraform apply -auto-approve \
    -var "acm_certificate_arn=$ACM_CERTIFICATE_ARN" \
    -var "domain_name=isa-tab-exporter.aws.stemcellcommons.org" \
    -var "hosted_zone_id=$ROUTE_53_HOSTED_ZONE_ID" \
    -var "api_gateway_stage_name=production"
cd ..
