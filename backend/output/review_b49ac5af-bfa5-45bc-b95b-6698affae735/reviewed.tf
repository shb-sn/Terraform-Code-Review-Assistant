terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "environment" {
  default = "dev"
}

resource "aws_s3_bucket" "app_bucket" {
  bucket = "my-test-terraform-bucket-12345"

  tags = {
    Name        = "My App Bucket"
    Environment = "dev"
  }
}

resource "aws_s3_bucket_public_access_block" "app_bucket_public_access" {
  bucket = aws_s3_bucket.app_bucket.id

  block_public_acls = true
            block_public_policy = true
            ignore_public_acls = true
            restrict_public_buckets = true
  block_public_acls = true
            block_public_policy = true
            ignore_public_acls = true
            restrict_public_buckets = true
  block_public_acls = true
            block_public_policy = true
            ignore_public_acls = true
            restrict_public_buckets = true
  block_public_acls = true
            block_public_policy = true
            ignore_public_acls = true
            restrict_public_buckets = true
}

resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = var.instance_type

  tags = {
    Name = "WebServer"
  }
}

resource "aws_security_group" "web_sg" {
  name = "web-security-group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/24"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  database_password = var.db_password
  api_key = var.api_key
}

output "instance_ip" {
  value = aws_instance.web_server.public_ip
}