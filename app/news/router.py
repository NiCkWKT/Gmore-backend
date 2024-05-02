import boto3
import traceback
from loguru import logger
from fastapi import APIRouter, status
from news.database import NewsDatabase
from news.service import get_news_list

router = APIRouter()

dynamodb = boto3.resource("dynamodb")
news = NewsDatabase(dynamodb)

categories = ["sports", "entertainment", "tech", "business"]


@router.get("/news", status_code=status.HTTP_200_OK)
def get_news(category: str):
    response = {"success": False, "message": "", "data": []}

    try:
        news_list = get_news_list(category)

        logger.debug(f"There is/are {len(news_list)} news")
        logger.debug(f"News: {news_list}")

        if len(news_list) == 0:
            response["message"] = "No available news"

        response["success"] = True
        response["message"] = f"There is/are {len(news_list)} news"
        response["data"] = news_list
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        response["message"] = e
    finally:
        return response
