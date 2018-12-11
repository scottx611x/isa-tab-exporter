locals {
  lambda_zip_name = "lambda_function.zip"
}

resource "aws_lambda_function" "isatab_exporter_lambda" {
  depends_on = ["aws_s3_bucket_object.isatab-exporter-lambda-zip"]

  function_name    = "isatab-exporter"
  role             = "${var.iam_role_arn}"
  handler          = "isa_tab_exporter.post_handler"
  source_code_hash = "${base64sha256(file(data.archive_file.lambda_zip.output_path))}"
  runtime          = "python3.6"
  s3_bucket        = "${var.s3_bucket}"
  s3_key           = "${local.lambda_zip_name}"
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

// Zip up python code & reqs into what will get run in the lambda
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${var.local_lambda_dir}"
  output_path = "${local.lambda_zip_name}"
}

// aws_lambda_function.isatab_exporter_lambda needs to depend on this object existing,
// but the actually .zip upload can take a few seconds causing a race condition.
// This resource should really remain in the s3 module, but I've moved it here for now.
// It seems as though newer versions of TF will allow for specifcying modules resources directly in a `depends_on`
resource "aws_s3_bucket_object" "isatab-exporter-lambda-zip" {
  bucket = "${var.s3_bucket}"
  key    = "${local.lambda_zip_name}"
  source = "${data.archive_file.lambda_zip.output_path}"
  etag   = "${md5(file(data.archive_file.lambda_zip.output_path))}"
}
