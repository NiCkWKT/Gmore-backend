import os
import boto3
import traceback
import google.generativeai as genai
from loguru import logger
from fastapi import APIRouter, status, File, UploadFile
from news.database import NewsDatabase
from news.service import get_news_list, get_news_by_id
from news.util import split_summary
from PIL import Image

router = APIRouter()

dynamodb = boto3.resource("dynamodb")
news = NewsDatabase(dynamodb)

categories = ["sports", "entertainment", "tech", "business"]

model = genai.GenerativeModel("gemini-pro-vision")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


@router.get("/news/{news_id}", status_code=status.HTTP_200_OK)
def get_single_news(news_id: str):
    response = {"success": False, "message": "", "data": {}}

    try:
        news_item = get_news_by_id(news_id)

        logger.debug(f"News data: {news_item}")

        response["success"] = True
        response["message"] = "News found"
        response["data"] = news_item
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        response["message"] = e
    finally:
        return response


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


@router.post("/ocr", status_code=status.HTTP_200_OK)
def upload_image(image: UploadFile = File(...)):
    response = {"success": False, "message": "", "data": []}
    prompt = """
    You are a news article summarizer. Given an image contain news article, provide a concise 3-bullet point summary.
    Each bullet point should be a complete sentence and should not exceed 100 characters.
    Bullet points should be separated by @@@@. The response should be plain text without any format.

    To summarize the article, focus on extracting the most important and newsworthy information, key facts, events, or conclusions. Keep each bullet point concise but informative.

    Please summarize the following news article using the provided structure:
    """

    try:
        img = Image.open(image.file)
        resp = model.generate_content([prompt, img])
        logger.debug(f"Gemini response: {resp}")

        lines = split_summary(resp.text)

        response["success"] = True
        response["message"] = ""
        response["data"] = lines
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        response["message"] = e
    finally:
        return response
