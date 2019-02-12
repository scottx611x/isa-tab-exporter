resource "aws_api_gateway_rest_api" "isatab_exporter_api" {
  name        = "${var.resource_name_prefix}isatab_exporter_api"
  description = "ISA_Tab Exporter API"
}

resource "aws_api_gateway_resource" "isatab_exporter_resource" {
  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  parent_id   = "${aws_api_gateway_rest_api.isatab_exporter_api.root_resource_id}"

  path_part = "isa_tab_export"
}

resource "aws_api_gateway_method" "isatab_exporter_method" {
  rest_api_id   = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  resource_id   = "${aws_api_gateway_resource.isatab_exporter_resource.id}"
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "isatab_exporter_integration" {
  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  resource_id = "${aws_api_gateway_method.isatab_exporter_method.resource_id}"
  http_method = "${aws_api_gateway_method.isatab_exporter_method.http_method}"

  # Proxy incoming POST requests to our lambda function
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${var.lambda_function_invoke_arn}"
}

resource "aws_api_gateway_method_response" "200" {
  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  resource_id = "${aws_api_gateway_resource.isatab_exporter_resource.id}"
  http_method = "${aws_api_gateway_method.isatab_exporter_method.http_method}"
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "isatab_exporter_integration_post_response_200" {
  depends_on = [
    "aws_api_gateway_integration.isatab_exporter_integration",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  resource_id = "${aws_api_gateway_method.isatab_exporter_method.resource_id}"
  http_method = "${aws_api_gateway_method.isatab_exporter_method.http_method}"
  status_code = "${aws_api_gateway_method_response.200.status_code}"

  # This doesn't do anything, just needed different values than the default for each aws_api_gateway_integration_response.selection_pattern
  selection_pattern = "Ok"
}

resource "aws_api_gateway_method_response" "400" {
  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  resource_id = "${aws_api_gateway_resource.isatab_exporter_resource.id}"
  http_method = "${aws_api_gateway_method.isatab_exporter_method.http_method}"
  status_code = "400"
}

resource "aws_api_gateway_integration_response" "isatab_exporter_integration_post_response_400" {
  depends_on = [
    "aws_api_gateway_integration.isatab_exporter_integration",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  resource_id = "${aws_api_gateway_method.isatab_exporter_method.resource_id}"
  http_method = "${aws_api_gateway_method.isatab_exporter_method.http_method}"
  status_code = "${aws_api_gateway_method_response.400.status_code}"

  # This doesn't do anything, just needed different values than the default for each aws_api_gateway_integration_response.selection_pattern
  selection_pattern = "Bad Request"
}

resource "aws_api_gateway_method_response" "500" {
  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  resource_id = "${aws_api_gateway_resource.isatab_exporter_resource.id}"
  http_method = "${aws_api_gateway_method.isatab_exporter_method.http_method}"
  status_code = "500"
}

resource "aws_api_gateway_integration_response" "isatab_exporter_integration_post_response_500" {
  depends_on = [
    "aws_api_gateway_integration.isatab_exporter_integration",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  resource_id = "${aws_api_gateway_method.isatab_exporter_method.resource_id}"
  http_method = "${aws_api_gateway_method.isatab_exporter_method.http_method}"
  status_code = "${aws_api_gateway_method_response.500.status_code}"

  # This doesn't do anything, just needed different values than the default for each aws_api_gateway_integration_response.selection_pattern
  selection_pattern = "Unexpected Error"
}

resource "aws_api_gateway_deployment" "isatab_exporter_deployment" {
  depends_on = [
    "aws_api_gateway_method.isatab_exporter_method",
    "aws_api_gateway_integration.isatab_exporter_integration",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  stage_name  = "${var.api_gateway_stage_name}"
}

resource "aws_api_gateway_domain_name" "isatab_exporter_domain_name" {
  certificate_arn = "${var.acm_certificate_arn}"
  domain_name     = "${var.domain_name}"

  count = "${var.use_custom_domain ? 1 : 0}"
}

resource "aws_api_gateway_base_path_mapping" "isatab_exporter_base_path_mapping" {
  api_id      = "${aws_api_gateway_rest_api.isatab_exporter_api.id}"
  stage_name  = "${var.api_gateway_stage_name}"
  domain_name = "${var.domain_name}"

  count = "${var.use_custom_domain ? 1 : 0}"

  depends_on = ["aws_api_gateway_domain_name.isatab_exporter_domain_name"]
}
