provider "aws" {
  region  = "us-east-1"
  profile = "scottx611x@gmail.com"
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
  source                               = "./modules/lambda"
  iam_role_arn                         = "${module.iam.iam_role_arn}"
  api_gateway_rest_api_execution_arn = "${module.api_gateway.aws_api_gateway_rest_api_execution_arn}"
  api_gateway_resource_path            = "${module.api_gateway.api_gateway_resource_path}"
}
