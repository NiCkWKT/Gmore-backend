from loguru import logger
from fastapi import APIRouter, status
from news.client import dynamodb
from news.database import NewsDatabase

router = APIRouter()

news = NewsDatabase(dynamodb)


@router.get("/news", status_code=status.HTTP_200_OK)
def get_news():
    items = news.query_news_by_category("tech")
    logger.debug(f"Type is {type(items)} and length is {len(items)}")
    return items
