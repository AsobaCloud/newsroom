#!/bin/bash

# Deploy news scraper as AWS Lambda function
set -e

FUNCTION_NAME="news-scraper"
ROLE_NAME="news-scraper-role"
POLICY_NAME="news-scraper-policy"

echo "🚀 Deploying news scraper as Lambda function..."

# Create IAM role for Lambda
echo "📋 Creating IAM role..."
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' 2>/dev/null || echo "Role already exists"

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create custom policy for S3 access
echo "📋 Creating S3 access policy..."
aws iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::news-collection-website",
                    "arn:aws:s3:::news-collection-website/*"
                ]
            }
        ]
    }' 2>/dev/null || echo "Policy already exists"

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Attach custom policy to role
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/$POLICY_NAME

# Wait for role to be ready
echo "⏳ Waiting for IAM role to be ready..."
sleep 10

# Create deployment package
echo "📦 Creating deployment package..."
mkdir -p lambda_package
cp lambda_news_scraper.py lambda_package/
cp lambda_wrapper.py lambda_package/
cp news_scraper.py lambda_package/
cp article_tagger.py lambda_package/

# Install dependencies
pip3 install -r requirements.txt -t lambda_package/

# Create zip file
cd lambda_package
zip -r ../news-scraper.zip .
cd ..

# Deploy Lambda function
echo "🚀 Deploying Lambda function..."
aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.9 \
    --role arn:aws:iam::${ACCOUNT_ID}:role/$ROLE_NAME \
    --handler lambda_news_scraper.lambda_handler \
    --zip-file fileb://news-scraper.zip \
    --timeout 900 \
    --memory-size 512 \
    --description "Daily news scraper for newsroom website" 2>/dev/null || \
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://news-scraper.zip

# Update function configuration if it already exists
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --timeout 900 \
    --memory-size 512

echo "✅ Lambda function deployed successfully!"

# Create EventBridge rule for daily execution at 11PM Central
echo "⏰ Setting up daily schedule..."
aws events put-rule \
    --name "news-scraper-daily" \
    --schedule-expression "cron(0 23 * * ? *)" \
    --description "Trigger news scraper daily at 11PM Central" \
    --state ENABLED

# Add Lambda permission for EventBridge
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id "allow-eventbridge" \
    --action "lambda:InvokeFunction" \
    --principal events.amazonaws.com \
    --source-arn "arn:aws:events:us-east-1:${ACCOUNT_ID}:rule/news-scraper-daily"

# Add Lambda target to EventBridge rule
aws events put-targets \
    --rule "news-scraper-daily" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:${ACCOUNT_ID}:function:$FUNCTION_NAME"

echo "✅ Daily schedule configured for 11PM Central Time!"
echo "📊 Function ARN: arn:aws:lambda:us-east-1:${ACCOUNT_ID}:function:$FUNCTION_NAME"

# Cleanup
rm -rf lambda_package news-scraper.zip

echo "🎉 Deployment complete! Your news scraper will run daily at 11PM Central Time."