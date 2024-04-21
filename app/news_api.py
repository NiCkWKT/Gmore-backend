import os
import httpx
import orjson
import boto3
import google.generativeai as genai

from newsplease import NewsPlease
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

load_dotenv()


class NewsScraper:
    def __init__(self):
        pass

    def get_news(self, url):
        article = NewsPlease.from_url(url)
        return article.maintext


categories = ["sports", "entertainment", "tech", "business"]

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.0-pro-latest")

prompt = """
You are a news article summarizer. Given a news article, provide a concise 3-bullet point summary.
Each bullet point should be a complete sentence and should not exceed 100 characters.
Bullet points should be separated by @@@@. The response should be plain text without any format.

To summarize the article, focus on extracting the most important and newsworthy information, key facts, events, or conclusions. Keep each bullet point concise but informative.

Please summarize the following news article using the provided structure:
"""

dynamo = boto3.client("dynamodb")


def summarize_news(news_url: str):
    scraper = NewsScraper()
    full_content = scraper.get_news(news_url)
    input = prompt + full_content
    response = model.generate_content(input)
    print("@" * 100)
    print(response.candidates)
    print("@" * 100)
    return response.text, full_content


def upload_string_to_s3(string_data, file_name):
    s3 = boto3.client("s3")
    try:
        s3.put_object(
            Bucket="gmore-news", Key=file_name, Body=string_data.encode("utf-8")
        )
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return False

    return True


def summary_to_dynamo_list(summary):
    points = summary.split("@@@@")
    lines = [line.strip() for line in points]
    lines = [line.strip("\n") for line in lines]
    lines = [line.lstrip("- ") for line in lines]
    dynamo_list = [{"S": line} for line in lines]
    return dynamo_list


def save_json_response_to_file(response, file_name):
    with open("news/" + file_name, "wb") as f:
        json_bytes = orjson.dumps(response)
        f.write(json_bytes)


def save_summary_to_file(summary, file_name):
    with open(file_name, "w") as f:
        f.write(summary)


def read_summary_from_file(file_name):
    with open(file_name, "r") as f:
        return f.read()


def partition_key_exists(table_name, partition_key, partition_key_value):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    try:
        response = table.query(
            TableName=table_name,
            KeyConditionExpression=Key(partition_key).eq(partition_key_value),
        )
        return list(response.get("Items")), bool(response.get("Items"))
    except Exception as e:
        print(f"Error checking partition key: {e}")
        return [], False


def get_news(category, page=1):
    base_url = "https://api.thenewsapi.com/v1/news/"
    top_stories = base_url + "top"
    api_key = os.environ["THE_NEWS_API_KEY"]
    params = {
        "api_token": api_key,
        "locale": "us",
        "limit": 3,
        "categories": category,
        "language": "en",
        "page": page,
    }
    r = httpx.get(top_stories, params=params)
    return r.json()


for category in categories:
    news_data = get_news(category, page=1)
    save_json_response_to_file(news_data, f"{category}_news.json")
    print(f"Processing {category} news")
    for news in news_data["data"]:
        pk = "NEWS#" + news["uuid"]
        sk = "CATEGORY#" + category
        current_news, exists = partition_key_exists("gmore", "PK", pk)
        if not exists:
            print("News not found in DynamoDB")
            print("Summarizing news")
            summary, full_content = summarize_news(news["url"])
            summary_list = summary_to_dynamo_list(summary)
            content_file_name = f"{news['uuid']}.txt"
            success = upload_string_to_s3(full_content, content_file_name)
            if not success:
                print("Failed to upload content to S3")
                break
        else:
            print("News found in DynamoDB")
            news = current_news[0]
            summary_list = [{"S": line} for line in news["summary"]]

        response = dynamo.put_item(
            TableName="gmore",
            Item={
                "PK": {"S": pk},
                "SK": {"S": sk},
                "title": {"S": news["title"]},
                "description": {"S": news["description"]},
                "keywords": {"S": news["keywords"]},
                "snippet": {"S": news["snippet"]},
                "url": {"S": news["url"]},
                "image_url": {"S": news["image_url"]},
                "language": {"S": news["language"]},
                "published_at": {"S": news["published_at"]},
                "source": {"S": news["source"]},
                "category": {"S": category},
                "locale": {"S": news["locale"]},
                "summary": {"L": summary_list},
            },
        )
        print(summary_list)
        print("#" * 100)
