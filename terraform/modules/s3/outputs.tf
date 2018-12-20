output "lambda_zip_s3_object_key" {
  value = "${aws_s3_bucket_object.isatab-exporter-lambda-zip.key}"
}

output "lambda_zip_hash" {
  value = "${data.archive_file.lambda_zip.output_base64sha256}"
}

output "s3_bucket" {
  value = "${aws_s3_bucket.isatab-exporter-bucket.bucket}"
}
