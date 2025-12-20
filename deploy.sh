#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_BACKEND="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ai-commerce-backend"
ECR_RECOMMENDER="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ai-commerce-recommender"
S3_BUCKET="ai-commerce-frontend-production"

echo "🚀 Starting deployment..."

# 1. Build and push backend
echo "📦 Building backend Docker image..."
cd backend
docker build -t ai-commerce-backend:latest .
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_BACKEND}
docker tag ai-commerce-backend:latest ${ECR_BACKEND}:latest
docker push ${ECR_BACKEND}:latest
cd ..

# 2. Build and push recommender
echo "📦 Building recommender Docker image..."
cd recommender
docker build -t ai-commerce-recommender:latest .
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_RECOMMENDER}
docker tag ai-commerce-recommender:latest ${ECR_RECOMMENDER}:latest
docker push ${ECR_RECOMMENDER}:latest
cd ..

# 3. Build and deploy frontend
echo "🎨 Building frontend..."
cd frontend
npm ci
npm run build
echo "☁️  Uploading to S3..."
aws s3 sync dist/ s3://${S3_BUCKET}/ --delete
echo "🔄 Invalidating CloudFront cache..."
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[?DomainName=='${S3_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com']].Id" --output text)
aws cloudfront create-invalidation --distribution-id ${DISTRIBUTION_ID} --paths "/*"
cd ..

echo "✅ Deployment complete!"