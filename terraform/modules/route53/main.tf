resource "aws_route53_record" "isa-tab-exporter-route53-record" {
  name    = "${var.domain_name}"
  type    = "A"
  zone_id = "${var.hosted_zone_id}"

  alias {
    evaluate_target_health = false
    name                   = "${var.cloudfront_domain_name}"
    zone_id                = "${var.cloudfront_zone_id}"
  }

  count = "${var.use_custom_domain ? 1 : 0}"
}
