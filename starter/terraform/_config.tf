terraform {
  backend "s3" {
    bucket = "udacity-sre-course1-terraform-seidler"
    key    = "terraform/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = local.tags
  }
}
