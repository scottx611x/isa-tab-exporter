output lambda_function_arn {
  value = "${aws_lambda_function.isatab_exporter_lambda.arn}"
}

output lambda_function_invoke_arn {
  value = "${aws_lambda_function.isatab_exporter_lambda.invoke_arn}"
}