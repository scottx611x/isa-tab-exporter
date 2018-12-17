resource "aws_api_gateway_rest_api" "isatab-exporter-api" {
  name        = "isatab-exporter-api"
  description = "ISA-Tab Exporter API"
}

resource "aws_api_gateway_resource" "isatab-exporter-resource" {
  rest_api_id = "${aws_api_gateway_rest_api.isatab-exporter-api.id}"
  parent_id   = "${aws_api_gateway_rest_api.isatab-exporter-api.root_resource_id}"
  path_part   = "isa-tab-export"
}

resource "aws_api_gateway_method" "isatab-exporter-method" {
  rest_api_id   = "${aws_api_gateway_rest_api.isatab-exporter-api.id}"
  resource_id   = "${aws_api_gateway_resource.isatab-exporter-resource.id}"
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "isatab-exporter-integration" {
  rest_api_id = "${aws_api_gateway_rest_api.isatab-exporter-api.id}"
  resource_id = "${aws_api_gateway_method.isatab-exporter-method.resource_id}"
  http_method = "${aws_api_gateway_method.isatab-exporter-method.http_method}"

  # Proxy incoming POST requests to our lambda function
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${var.lambda_function_invoke_arn}"
}

resource "aws_api_gateway_method_response" "200" {
  rest_api_id = "${aws_api_gateway_rest_api.isatab-exporter-api.id}"
  resource_id = "${aws_api_gateway_resource.isatab-exporter-resource.id}"
  http_method = "${aws_api_gateway_method.isatab-exporter-method.http_method}"
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "isatab-exporter-integration-post-response" {
  depends_on = [
    "aws_api_gateway_integration.isatab-exporter-integration",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.isatab-exporter-api.id}"
  resource_id = "${aws_api_gateway_method.isatab-exporter-method.resource_id}"
  http_method = "${aws_api_gateway_method.isatab-exporter-method.http_method}"
  status_code = "${aws_api_gateway_method_response.200.status_code}"
}

resource "aws_api_gateway_deployment" "isatab-exporter-deployment" {
  depends_on = [
    "aws_api_gateway_method.isatab-exporter-method",
    "aws_api_gateway_integration.isatab-exporter-integration",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.isatab-exporter-api.id}"
  stage_name  = "${var.api_gateway_stage_name}"
}

resource "aws_api_gateway_domain_name" "isatab-exporter-domain-name" {
  certificate_arn = "${var.acm_certificate_arn}"
  domain_name     = "${var.domain_name}"

  count = "${var.use_custom_domain ? 1 : 0}"
}

resource "aws_api_gateway_base_path_mapping" "isatab-exporter-base-path-mapping" {
  api_id      = "${aws_api_gateway_rest_api.isatab-exporter-api.id}"
  stage_name  = "${var.api_gateway_stage_name}"
  domain_name = "${var.domain_name}"

  count = "${var.use_custom_domain ? 1 : 0}"

  depends_on = ["aws_api_gateway_domain_name.isatab-exporter-domain-name"]
}
