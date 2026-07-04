variable "aws_region" {
  default = "us-east-1"
}

variable "instance_type" {
  default = "t3.medium"
}

variable "worker_count" {
  default = 2
}

variable "key_name" {
  description = "EC2 SSH key pair name"
}