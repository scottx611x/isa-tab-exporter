# isa-tab-exporter/deployment/scripts

The following scripts are used in our CI/CD pipeline to deploy the isa-tab-exporter infrastructure, and run end to end tests against live deployments.

### [deploy.sh](deploy.sh):
- Deploys production infrastructure on `master` branch builds
- Deploys non-production infrastructure on `non-master` branch builds and destroys the deployment upon build completion

### [deployment_test.sh](deployment_test.sh):
- Runs an end-to-end test by POSTing valid ISA-JSON to the live API Gateway deployment ensuring that the expected ISA Archive is downloaded

### [lint_format_validate.sh](lint_format_validate.sh)
- Lints Python code
- Formats Python and Terraform code
- Validates Terraform code