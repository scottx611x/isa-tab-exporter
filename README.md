# isa-tab-exporter

### What?
The aim of `isa-tab-exporter` is to provide the [refinery-platform](https://github.com/refinery-platform/refinery-platform) with a means to utilize the Python3-based [ISA-tools API](https://github.com/ISA-tools/isa-api) while it remains in the land of Python2.

### How?
`isa-tab-exporter` provides terraform code that will create/manage AWS infrastructure allowing for POST requests containing the [refinery-platform's](https://github.com/refinery-platform/refinery-platform) JSON representation of an ISATab to then be converted into a full blown ISATab .zip file and returned to the end user.

Specifically, an API Gateway deployment is created that accepts these POST requests, and proxies said requests to a Lambda function that it triggers which will execute the [ISA-tools API](https://github.com/ISA-tools/isa-api) code to transform the refinery ISATab JSON to a valid ISATab .zip file.



### Pre-Reqs:
- [Terraform](https://www.terraform.io/)
- Python 3.x


### Running Tests:
- `python lambda/tests.py`

### CI/CD:
The Terraform code will be run in TravisCI upon successful `master` branch builds deploying the latest version of the APIGateway/Lambda.
