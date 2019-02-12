variable api_gateway_rest_api_execution_arn {}
variable api_gateway_resource_path {}
variable iam_role_arn {}

variable lambda_memory_size {
  # Note: AWS Lambda allocates proportional CPU power, network bandwidth,
  # and disk I/O based off of the specified `memory_size`
  # See `Flexible resource model` here: https://aws.amazon.com/lambda/features/
  default = 3008
}

variable lambda_zip_hash {}
variable lambda_zip_s3_object_key {}
variable resource_name_prefix {}
variable s3_bucket {}
