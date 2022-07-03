# Create resources in AWS using Modules
# Author: Somnath Das

module "vpc" {
  source = "../../modules/vpc"
  cidr_block = var.project_cidr
}


output "project_vpc" {
  value = module.vpc.vpc_id
}

