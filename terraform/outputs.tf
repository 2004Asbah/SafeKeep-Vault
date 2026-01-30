output "s3_bucket_name" {
  description = "The name of the created S3 bucket"
  value       = aws_s3_bucket.vault.bucket
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.image_processor.function_name
}
