// Zip up python code & reqs into what will get run in the lambda
data "archive_file" "lambda_zip" {
    type        = "zip"
    source_dir  = "${var.lambda_dir}"
    output_path = "lambda.zip"
}

resource "aws_lambda_function" "isatab_exporter_lambda" {
  filename         = "${data.archive_file.lambda_zip.output_path}"
  function_name    = "isatab-exporter"
  role             = "${var.iam_role_arn}"
  handler          = "isa-tab-exporter.post_handler"
  source_code_hash = "${base64sha256(file(data.archive_file.lambda_zip.output_path))}"
  runtime          = "python3.6"
}

resource "aws_lambda_permission" "api_gateway_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.isatab_exporter_lambda.arn}"
  principal     = "apigateway.amazonaws.com"

  source_arn = "${var.api_gateway_rest_api_execution_arn}/*/POST/isa-tab-export"
}