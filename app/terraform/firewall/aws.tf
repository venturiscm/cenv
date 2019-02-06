
provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region = "${var.region}"
}

resource "aws_security_group" "firewall" {
  name = "${var.name}"
  vpc_id = "${var.vpc_id}"
  
  tags = {
    Name = "cenv-network"
  }
}