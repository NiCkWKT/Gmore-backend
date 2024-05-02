import boto3
import traceback
from typing import List
from loguru import logger
from news.database import NewsDatabase
from news.schemas import News


dynamodb = boto3.resource("dynamodb")
news_db = NewsDatabase(dynamodb)

categories = ["sports", "entertainment", "tech", "business"]


def get_news_list(category: str) -> List[News]:
    news_list = []

    try:
        if category not in categories:
            err_msg = f"No such category. Available categories {categories}"
            logger.error(err_msg)
            raise Exception(err_msg)

        news_data = news_db.query_news_by_category(category)

        logger.debug(f"There is/are {len(news_data)} news")
        logger.debug(f"Raw news data: {news_data}")

        for news in news_data:
            news_item = {}
            news_item["id"] = news["PK"].split("#")[1]
            news_item["title"] = news["title"]
            news_item["published_at"] = news["published_at"]
            news_item["image_url"] = news["image_url"]
            news_item["source"] = news["source"]
            news_item["source_url"] = news["url"]
            news_item["category"] = news["category"]
            news_item["summary"] = news["summary"]
            news_list.append(news_item)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    finally:
        return news_list
