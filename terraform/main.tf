# Configure the AWS Provider
provider "aws" {
  region = "eu-north-1"
}

# 1. Create the S3 Bucket for the NGO Vault
resource "aws_s3_bucket" "vault" {
  bucket = "safekeep-ngo-vault-${random_id.id.hex}"
  
  tags = {
    Project     = "SafeKeep"
    Environment = "Production"
    Owner       = "NGO-Admin"
  }
}

# Helper to make the bucket name unique
resource "random_id" "id" {
  byte_length = 4
}

# 2. SECURITY: Block all public access
resource "aws_s3_bucket_public_access_block" "vault_lockdown" {
  bucket                  = aws_s3_bucket.vault.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 3. COST SAVING: Lifecycle Rule
resource "aws_s3_bucket_lifecycle_configuration" "vault_lifecycle" {
  bucket = aws_s3_bucket.vault.id

  rule {
    id     = "archive-policy"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }
}

# 4. IAM Role for Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "safekeep_lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# 5. IAM Policy (S3 Access)
resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "safekeep_lambda_s3_policy"
  role = aws_iam_role.lambda_exec_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.vault.arn}/*" # FIXED: Matches nickname above
      },
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# 6. The Lambda Function
resource "aws_lambda_function" "image_processor" {
  filename      = "lambda_function_payload.zip"
  function_name = "safekeep-image-processor"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30

  #layers = ["arn:aws:lambda:eu-north-1:770693421928:layer:Klayers-p311-Pillow:4"] 
}

# 7. S3 Permission to invoke Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.image_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.vault.arn # FIXED: Matches nickname above
}

# 8. S3 Trigger
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.vault.id # FIXED: Matches nickname above

  lambda_function {
    lambda_function_arn = aws_lambda_function.image_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "incoming/"
  }
  depends_on = [aws_lambda_permission.allow_s3]
}