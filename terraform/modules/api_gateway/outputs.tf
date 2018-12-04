output "aws_api_gateway_rest_api_execution_arn" {
  value = "${aws_api_gateway_rest_api.isatab-exporter-api.execution_arn}"
}

output "api_gateway_deployment_invoke_url" {
  value = "${aws_api_gateway_deployment.isatab-exporter-deployment.invoke_url}"
}

output "api_gateway_resource_path" {
  value = "${aws_api_gateway_resource.isatab-exporter-resource.path}"
}