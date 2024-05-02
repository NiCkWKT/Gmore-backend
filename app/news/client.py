import boto3
from news.config import settings
from loguru import logger

# Create a session with the AWS credentials
# session = boto3.Session(
#     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#     region_name=settings.AWS_REGION_NAME,
# )
#
# logger.info(f"Current AWS Region {settings.AWS_REGION_NAME}")

# Create clients for different AWS services
dynamodb = boto3.client("dynamodb")
