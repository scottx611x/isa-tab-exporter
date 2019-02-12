resource "aws_lambda_function" "isatab_exporter_lambda" {
  function_name    = "${var.resource_name_prefix}isatab_exporter"
  role             = "${var.iam_role_arn}"
  handler          = "lambda_function.api_gateway_post_handler"
  source_code_hash = "${var.lambda_zip_hash}"
  runtime          = "python3.6"
  s3_bucket        = "${var.s3_bucket}"
  s3_key           = "${var.lambda_zip_s3_object_key}"
  timeout          = 20
  memory_size      = "${var.lambda_memory_size}"
  publish          = true
}

resource "aws_lambda_permission" "api_gateway_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.isatab_exporter_lambda.arn}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_gateway_rest_api_execution_arn}/*/POST${var.api_gateway_resource_path}"
}
