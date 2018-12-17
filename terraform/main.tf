provider "aws" {
  region  = "us-east-1"
  profile = "${var.aws_profile_name}"
}

provider "random" {
  version = "~> 2.0"
}

resource "random_string" "s3_bucket_name_random_string" {
  length  = 8
  upper   = false
  special = false
}

module api_gateway {
  source                     = "./modules/api_gateway"
  lambda_function_invoke_arn = "${module.lambda.lambda_function_invoke_arn}"
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
  lambda_zip_name                    = "${var.lambda_zip_name}"
  lambda_zip_s3_object               = "${module.s3.lambda_zip_s3_object}"
  local_lambda_dir                   = "${var.local_lambda_dir}"
  s3_bucket                          = "${module.s3.s3_bucket}"
}

module s3 {
  source           = "./modules/s3"
  lambda_zip_name  = "${var.lambda_zip_name}"
  local_lambda_dir = "${var.local_lambda_dir}"
  s3_bucket_name   = "isatab-exporter-bucket-${random_string.s3_bucket_name_random_string.result}"
}
