#!/usr/bin/env bash

API_GATEWAY_DEPLOYMENT_URL=$1
ISA_TAB_NAME="BII-S-7"

ISA_JSON=$(cat ../../test_data/isa_json/${ISA_TAB_NAME}.json)

# Make a POST request to the API Gateway deployment containing valid ISA-JSON
# -O, --remote-name   Write output to a file named as the remote file
#  -J, --remote-header-name Use the header-provided filename
curl -X POST -O -J ${API_GATEWAY_DEPLOYMENT_URL} \
    -d @- <<CURL_DATA
{
  "isatab_filename": "${ISA_TAB_NAME}",
  "isatab_contents": ${ISA_JSON}
}
CURL_DATA

sleep 5

echo "Running end-to-end test against: ${API_GATEWAY_DEPLOYMENT_URL}"

# Fail the build if we didn't receive the expected ISA-Archive in return
if [ ! -f ${ISA_TAB_NAME}.zip ]; then
    echo "${ISA_TAB_NAME}.zip not found!"
    echo "End-to-end test against: ${API_GATEWAY_DEPLOYMENT_URL} failed"
    exit 1
else
    echo "End-to-end test against: ${API_GATEWAY_DEPLOYMENT_URL} succeeded"
    rm ${ISA_TAB_NAME}.zip
    exit 0
fi