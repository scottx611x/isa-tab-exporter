output "api_gateway_deployment_execution_arn" {
  value = "${module.api_gateway.aws_api_gateway_rest_api_execution_arn}"
}

output "api_gateway_deployment_invoke_url" {
  value = "${module.api_gateway.api_gateway_deployment_invoke_url}"
}