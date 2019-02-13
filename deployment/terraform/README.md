# isa-tab-exporter/deployment/terraform

### Getting Started:

First, terraform will need to be initialized using the `terraform init` command.

Currently, we are utilizing terraform state files located within an S3 bucket (`isatab-exporter-config`), so the `terraform init` command will end up being:

- `$ terraform init -backend-config="bucket=isatab-exporter-config"`

You should be able to substitute a different bucket name for your own needs.

> **Note**: the `terraform init` command above should only need to be run upon the initial clone of this repo

#### Creating a Terraform workspace:
We utilize terraform workspaces to isolate different infrastructure environment configurations and states.

Run: `$ terraform workspace new <workspace_name>` with a workspace name of your choosing to get started.

#### Creating the Infrastructure:
From this directory you can run the following command to create the necessary infrastructure.
- `$ terraform apply`

#### Destroying the Infrastructure:
- `$ terraform destroy`

#### User-supplied Variables:
- `$ cp terraform.tfvars.example terraform.tfvars`
- Edit/add entries corresponding to variables in the main [`vars.tf`](vars.tf) file

#### Deploying with a custom domain name:
Populate the entries in `terraform.tfvars` with appropriate values for:
- `acm_certificate_arn`
- `api_gateway_stage_name`
- `domain_name`
- `hosted_zone_id`