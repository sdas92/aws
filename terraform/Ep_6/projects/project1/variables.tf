# Definitions of requried variables for the project
# Author: Somnath Das

variable "project_cidr" {
  description = "The CIDR block for the VPC"
}

variable "project_bucket_name" {
  description = "The S3 bucket name"
}

variable "s3_tags" {
  type = map
}
