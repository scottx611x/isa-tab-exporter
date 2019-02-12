#!/usr/bin/env bash

API_GATEWAY_DEPLOYMENT_URL=$1

ISA_JSON=$(cat ../../test_data/isa_json/BII-S-7.json)


# -O, --remote-name   Write output to a file named as the remote file
#  -J, --remote-header-name Use the header-provided filename
curl -X POST -O -J ${API_GATEWAY_DEPLOYMENT_URL} \
    -d @- <<CURL_DATA
{
  "isatab_filename": "BII-S-7",
  "isatab_contents": ${ISA_JSON}
}
CURL_DATA

if [ ! -f ./BII-S-7.zip ]; then
    echo "BII-S-7.zip not found!"
    exit 1
else
    echo "Deploy successful"
    rm ./BII-S-7.zip
    exit 0
fi