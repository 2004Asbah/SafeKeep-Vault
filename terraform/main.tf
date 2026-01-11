# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

# Create the S3 Bucket for the NGO Vault
resource "aws_s3_bucket" "vault" {
  bucket = "safekeep-ngo-vault-${random_id.id.hex}"
  
  tags = {
    Project     = "SafeKeep"
    Environment = "Production"
    Owner       = "NGO-Admin"
  }
}

# 🔒 SECURITY: Block all public access to keep NGO data safe
resource "aws_s3_bucket_public_access_block" "vault_lockdown" {
  bucket                  = aws_s3_bucket.vault.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 💰 COST SAVING: Lifecycle Rule
resource "aws_s3_bucket_lifecycle_configuration" "vault_lifecycle" {
  bucket = aws_s3_bucket.vault.id

  rule {
    id     = "archive-policy"
    status = "Enabled"

    # Move files to GLACIER (90% cheaper) after 30 days
    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }
}

# Helper to make the bucket name unique
resource "random_id" "id" {
  byte_length = 4
}