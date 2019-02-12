output "aws_api_gateway_rest_api_execution_arn" {
  value = "${aws_api_gateway_rest_api.isatab_exporter_api.execution_arn}"
}

output "api_gateway_deployment_invoke_url" {
  value = "${aws_api_gateway_deployment.isatab_exporter_deployment.invoke_url}"
}

output "api_gateway_resource_path" {
  value = "${aws_api_gateway_resource.isatab_exporter_resource.path}"
}

output "cloudfront_domain_name" {
  value = "${ join(" ", aws_api_gateway_domain_name.isatab_exporter_domain_name.*.cloudfront_domain_name) }"
}

output "cloudfront_zone_id" {
  value = "${ join(" ", aws_api_gateway_domain_name.isatab_exporter_domain_name.*.cloudfront_zone_id) }"
}
