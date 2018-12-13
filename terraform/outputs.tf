output "api_gateway_deployment_invoke_url" {
  value = "${module.api_gateway.api_gateway_deployment_invoke_url}${module.api_gateway.api_gateway_resource_path}"
}
