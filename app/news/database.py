from loguru import logger
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key


class NewsDatabase:
    def __init__(self, dyn_resource):
        self.dyn_resource = dyn_resource
        self.table = dyn_resource.Table("gmore")

    def query_news_by_category(self, category):
        try:
            response = self.table.query(
                IndexName="category-published_at-index",
                KeyConditionExpression=Key("category").eq(category)
                & Key("published_at").gte("2024-04-20T19:45:05.000000Z"),
                ScanIndexForward=False,  # Sort decending
            )
        except ClientError as err:
            logger.error(
                "Couldn't query for %s news. Here's why: %s: %s",
                category,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Items"]

    def get_news_by_id(self, news_id):
        try:
            response = self.table.query(
                KeyConditionExpression=Key("PK").eq(f"NEWS#{news_id}")
            )
            logger.debug(f"Query response: {response}")
        except ClientError as err:
            logger.error(
                "Couldn't get news with ID %s. Here's why: %s: %s",
                news_id,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Items"][0]
