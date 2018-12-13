resource "aws_s3_bucket" "isatab-exporter-bucket" {
  bucket = "isatab-exporter-bucket"
  acl    = "private"

  versioning {
    enabled = true
  }
}

// Zip up python code & reqs into what will get run in the lambda
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${var.local_lambda_dir}"
  output_path = "${var.lambda_zip_name}"
}

resource "aws_s3_bucket_object" "isatab-exporter-lambda-zip" {
  bucket = "${aws_s3_bucket.isatab-exporter-bucket.bucket}"
  key    = "${var.lambda_zip_name}"
  source = "${data.archive_file.lambda_zip.output_path}"
  etag   = "${md5(file(data.archive_file.lambda_zip.output_path))}"
}
