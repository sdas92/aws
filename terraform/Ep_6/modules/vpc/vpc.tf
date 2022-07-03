# Module for AWS VPC
# Author: Somnath Das

# Create a VPC
resource "aws_vpc" "vpc" {
  cidr_block = var.cidr_block
}
