# isa-tab-exporter/terraform

### Creating the Infrastructure:
- `$ terraform init && terraform apply`

### Destroying the Infrastructure:
- `$ terraform destroy`

### Deploying `isa-tab-exporter` with a custom domain name:
- `$ cp terraform.tfvars.example terraform.tfvars`
- Populate the entries for:
    - `acm_certificate_arn`
    - `domain_name`
    - `hosted_zone_id`
