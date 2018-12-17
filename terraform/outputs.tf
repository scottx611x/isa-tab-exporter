output "api_gateway_deployment_invoke_url" {
  value = "${var.domain_name != "example.com" ? var.domain_name : module.api_gateway.api_gateway_deployment_invoke_url}${module.api_gateway.api_gateway_resource_path}"
}
