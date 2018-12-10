output "s3_bucket" {
  value = "${aws_s3_bucket.isatab-exporter-bucket.bucket}"
}
