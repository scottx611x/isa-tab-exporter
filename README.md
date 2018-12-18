# isa-tab-exporter [![Build Status](https://travis-ci.com/scottx611x/isa-tab-exporter.svg?branch=master)](https://travis-ci.com/scottx611x/isa-tab-exporter) [![codecov](https://codecov.io/gh/scottx611x/isa-tab-exporter/branch/master/graph/badge.svg)](https://codecov.io/gh/scottx611x/isa-tab-exporter)

### What?
The aim of `isa-tab-exporter` is to provide the [refinery-platform](https://github.com/refinery-platform/refinery-platform) with a means to utilize the Python3-based [ISA-tools API](https://github.com/ISA-tools/isa-api) while it remains in the land of Python2, but development has been done in a general manner so that anyone facing this same issue could reuse this code.

### How?
`isa-tab-exporter` provides [terraform](https://www.terraform.io/) code that will create/manage AWS infrastructure allowing for POST requests containing valid [ISA-JSON](https://isa-specs.readthedocs.io/en/latest/isajson.html) to be converted into a full blown [ISA-Tab](http://www.dcc.ac.uk/resources/metadata-standards/isa-tab) Archive .zip file and returned to the end user.

Specifically, an API Gateway deployment is created that accepts these POST requests, and proxies said requests to a Lambda function that it triggers which will execute the [ISA-tools API](https://github.com/ISA-tools/isa-api) code to transform the ISA-JSON to a valid ISA-Tab Archive .zip file.

### Pre-Reqs:
- [terraform](https://www.terraform.io/)
- [docker](https://docs.docker.com/)
- `Python 3.6.x`

### Running Tests:
- `pip install -r requirements-test.txt`
- `nosetests`

**Note:** Some of the provided tests are end-to-end tests and are a bit slow.
 Run fast or slow tests in isolation with the following commands:

```bash
# Just the speedy ones
$ nosetests -a '!slow'

# Just the slow ones
$ nosetests -a 'slow'
```

### Deployment:
The `deploy.sh` script will build the Lambda's python reqs using an Amazon Linux docker container, and provision the AWS infrastructure using Terraform.

```bash
$ ./deploy.sh

...

Apply complete! Resources: 16 added, 0 changed, 0 destroyed.

Outputs:

api_gateway_deployment_invoke_url = https://XXXXXXXXX.execute-api.us-east-1.amazonaws.com/development/isa-tab-export
```

See the [terraform-instructions](https://github.com/scottx611x/isa-tab-exporter/tree/master/terraform#isa-tab-exporterterraform) for deployment to custom domain names, among other things.

### CI/CD:
The Terraform code will be run in Travis-CI upon successful `master` branch builds deploying the latest version of the APIGateway/Lambda to the `production` APIGateway stage.

### Example Usage:

**cURL**
```bash
$ curl -X POST \
  -O \ # -O, --remote-name   Write output to a file named as the remote file
  -J \ #  -J, --remote-header-name Use the header-provided filename
  https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/development/isa-tab-export \
  -d '{
    "isatab_filename": "My Cool ISA-Tab",
    "isatab_contents": <Valid ISA-JSON content (Take a peek at test_data/isa_json/*)>
}'

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  4641  100  4604  100    37    767      6  0:00:06  0:00:06 --:--:--  1301
curl: Saved to filename 'My Cool ISA-Tab.zip'
```

**Postman**
![dec-14-2018 13-16-10](https://user-images.githubusercontent.com/5629547/50019956-7c4ce880-ffa2-11e8-87c1-e7b94c4df381.gif)

### Development Notes:
- By default terraform will utilize the credentials from the `default` AWS Profile that is available on the system. `isa-tab-exporter/terraform/terraform.tfvars` can be created with an entry like `aws_profile_name = "<desired_aws_profile_name>"` to override this.

- Currently we are using [`flake8`](https://github.com/PyCQA/flake8) & [`black`](https://github.com/ambv/black) in CI to lint and format our Python code, respectively. These tools can be run outside of CI using the following commands:
  - `black --diff .`
  - `flake8`

---

**Lambda & Triggers**
![screen shot 2018-12-10 at 2 53 16 pm](https://user-images.githubusercontent.com/5629547/49757849-692cd680-fc8b-11e8-833a-f5cd3e45ed1e.png)

**APIGateway Setup**
![screen shot 2018-12-10 at 4 34 03 pm](https://user-images.githubusercontent.com/5629547/49763058-9aac9e80-fc99-11e8-9634-13d85a8093d7.png)
