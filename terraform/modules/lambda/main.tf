//Note: This is a workaround required due to the S3 upload of the Lambda .zip
//taking enough time for it not to be available when creating the lambda function.
// See: https://github.com/hashicorp/terraform/issues/16983#issuecomment-434141081
resource "null_resource" "lambda_zip_upload_workaround" {
  triggers {
    lambda_zip_s3_object = "${var.lambda_zip_s3_object}"
  }
}

resource "aws_lambda_function" "isatab_exporter_lambda" {
  depends_on = ["null_resource.lambda_zip_upload_workaround"]

  function_name    = "isatab-exporter"
  role             = "${var.iam_role_arn}"
  handler          = "isa_tab_exporter.post_handler"
  source_code_hash = "${var.lambda_zip_hash}"
  runtime          = "python3.6"
  s3_bucket        = "${var.s3_bucket}"
  s3_key           = "${var.lambda_zip_name}"
  timeout          = 30
  memory_size      = 256
}

resource "aws_lambda_permission" "api_gateway_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.isatab_exporter_lambda.arn}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_gateway_rest_api_execution_arn}/*/POST${var.api_gateway_resource_path}"
}
