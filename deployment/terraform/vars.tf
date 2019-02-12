variable "aws_region" {
  default = "us-east-1"
}

variable "lambda_zip_name" {
  default = "lambda_function.zip"
}

variable "local_lambda_dir" {
  default = "../../lambda_function"
}

// Variables below here are only necessary when using a custom domain name
// for the api gateway deployment
variable "acm_certificate_arn" {
  default = false
}

variable "api_gateway_stage_name" {
  default = "development"
}

variable "domain_name" {
  default = "example.com"
}

variable "hosted_zone_id" {
  default = false
}
