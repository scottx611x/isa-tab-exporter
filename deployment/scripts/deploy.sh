#!/bin/bash

# Build Python requirements for the lambda using an aws-linux based container
./deployment/docker/install-lambda-reqs.sh $PWD/lambda_function

# Initialize terraform using the S3 backend so that Travis builds have
# access to the same workspaces & state files
cd deployment/terraform
terraform init -backend-config="bucket=$TERRAFORM_STATE_BUCKET" -input=false

# Deploy to production on master branch builds
if [ "$TRAVIS_BRANCH" = "master" -a "$TRAVIS_PULL_REQUEST" = "false" ]; then
    terraform workspace select production
    terraform apply -auto-approve \
        -var "acm_certificate_arn=$ACM_CERTIFICATE_ARN" \
        -var "domain_name=isa-tab-exporter.aws.stemcellcommons.org" \
        -var "hosted_zone_id=$ROUTE_53_HOSTED_ZONE_ID" \
        -var "api_gateway_stage_name=production"
fi

# Create a non-production deployment for any non-master branch
if [ "$TRAVIS_BRANCH" != "master" ]; then
    terraform workspace select development
    terraform apply -auto-approve
fi

# Parse out the URL to invoke our deployed Lambda from the terraform output
API_GATEWAY_INVOKE_URL=$(terraform output -json | jq --raw-output '.api_gateway_deployment_invoke_url.value')

if [ "$TRAVIS_BRANCH" != "master" ]; then
    # Run an end-to-end test with the current API Gateway deployment
    ../scripts/deployment_test.sh ${API_GATEWAY_INVOKE_URL}
    DEPLOYMENT_TEST_EXIT_CODE=$?

    if [ ! -z $CONTINUOUS_INTEGRATION ]; then
        # Cleanup test deployment
        terraform destroy --auto-approve;

        # Fail build if we received a non-zero exit code from deployment_test.sh
        [[ ${DEPLOYMENT_TEST_EXIT_CODE} -ne 0 ]] && exit ${DEPLOY_TEST_EXIT_CODE}
    fi
fi

cd ..

exit 0