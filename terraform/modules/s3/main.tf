resource "aws_s3_bucket" "isatab-exporter-bucket" {
  bucket = "isatab-exporter-bucket"
  acl    = "private"
}
