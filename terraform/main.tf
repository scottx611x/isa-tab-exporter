terraform {
  backend "s3" {
    bucket               = "isatab-exporter-config"
    key                  = "terraform.tfstate"
    workspace_key_prefix = "sites"
  }
}

provider "aws" {
  region = "${var.aws_region}"
}

provider "random" {
  version = "~> 2.0"
}

resource "random_string" "s3_bucket_name_random_string" {
  length  = 8
  upper   = false
  special = false
}

locals {
  use_custom_domain = "${var.acm_certificate_arn != false && var.domain_name != "example.com"}"
}

module api_gateway {
  source                     = "./modules/api_gateway"
  acm_certificate_arn        = "${var.acm_certificate_arn}"
  api_gateway_stage_name     = "${var.api_gateway_stage_name}"
  domain_name                = "${var.domain_name}"
  lambda_function_invoke_arn = "${module.lambda.lambda_function_invoke_arn}"
  use_custom_domain          = "${local.use_custom_domain}"
}

module cloud_watch {
  source               = "./modules/cloud_watch"
  lambda_function_name = "${module.lambda.lambda_function_name}"
}

module iam {
  source                   = "./modules/iam"
  cloudwatch_log_group_arn = "${module.cloud_watch.cloudwatch_log_group_arn}"
}

module lambda {
  source                             = "./modules/lambda"
  api_gateway_rest_api_execution_arn = "${module.api_gateway.aws_api_gateway_rest_api_execution_arn}"
  api_gateway_resource_path          = "${module.api_gateway.api_gateway_resource_path}"
  iam_role_arn                       = "${module.iam.lambda_iam_role_arn}"
  lambda_zip_hash                    = "${module.s3.lambda_zip_hash}"
  lambda_zip_s3_object_key           = "${module.s3.lambda_zip_s3_object_key}"
  s3_bucket                          = "${module.s3.s3_bucket}"
}

module route53 {
  source                 = "./modules/route53"
  cloudfront_domain_name = "${module.api_gateway.cloudfront_domain_name}"
  cloudfront_zone_id     = "${module.api_gateway.cloudfront_zone_id}"
  domain_name            = "${var.domain_name}"
  hosted_zone_id         = "${var.hosted_zone_id}"
  use_custom_domain      = "${local.use_custom_domain}"
}

module s3 {
  source           = "./modules/s3"
  lambda_zip_name  = "${var.lambda_zip_name}"
  local_lambda_dir = "${var.local_lambda_dir}"
  s3_bucket_name   = "isatab-exporter-bucket-${random_string.s3_bucket_name_random_string.result}"
}
