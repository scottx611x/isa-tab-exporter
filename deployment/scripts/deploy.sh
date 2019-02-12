#!/bin/bash

./docker_context/install-lambda-reqs.sh $PWD/lambda_function

# initialize Terraform and apply infrastructure changes
cd deployment/terraform
terraform init -input=false

if [ "$TRAVIS_BRANCH" = "master" -a "$TRAVIS_PULL_REQUEST" = "false" ]; then
    terraform workspace select production
    terraform apply -auto-approve \
        -var "acm_certificate_arn=$ACM_CERTIFICATE_ARN" \
        -var "domain_name=isa-tab-exporter.aws.stemcellcommons.org" \
        -var "hosted_zone_id=$ROUTE_53_HOSTED_ZONE_ID" \
        -var "api_gateway_stage_name=production"
fi

if [ "$TRAVIS_BRANCH" != "master" ]; then
    terraform workspace select development
    terraform apply -auto-approve
fi

API_GATEWAY_INVOKE_URL=$(terraform output -json | jq --raw-output '.api_gateway_deployment_invoke_url.value')

if [ "$TRAVIS_BRANCH" != "master" ]; then
    # Run an end-to-end test with the current API Gateway deployment
    ../scripts/deployment_test.sh ${API_GATEWAY_INVOKE_URL}

    # Cleanup after non-production deployments
    terraform destroy --auto-approve;
fi

cd ..

