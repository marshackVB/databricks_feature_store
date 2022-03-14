terraform {
  required_providers {

    random = {
      source = "hashicorp/random"
      version = "3.1.0"
    }

    aws = {
        source = "hashicorp/aws"
    }


  }
}

provider "aws" {
  region = var.AWS_REGION
}

provider random {}