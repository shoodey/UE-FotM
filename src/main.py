import os
import time

import requests
import schedule
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

unreal_store_url = "https://www.unrealengine.com/marketplace/en-US/assets?tag=4910"
thumbnail_url = "https://cdn-icons-png.flaticon.com/512/4712/4712109.png"


# Scrape UE's store page and fetch free of the month asset data
# These include: title, author, and original price
def scrape(url):
    response = requests.get(url)
    page = BeautifulSoup(response.content, "html.parser")
    free_assets = page.find_all("div", class_="asset-container catalog asset-full")

    # Stores the parsed asset data
    asset_data = []

    for free_asset in free_assets:
        title = free_asset.find("h3").text.strip()
        author = free_asset.find("div", class_="creator").text.strip()
        original_price = free_asset.find(
            "span", class_="asset-discount-price"
        ).text.strip()

        asset_data.append(
            {"title": title, "author": author, "original_price": original_price}
        )

    return asset_data


# Sends a webhook POST request to Discord
def send_webhook(url, data):
    description = ""

    for asset in data:
        description += "**" + asset["title"] + "**" + "\n"
        description += "*by " + asset["author"] + "*"
        description += "\t ~~" + asset["original_price"] + "~~"
        description += "\n\n"

    requests.post(
        url,
        json={
            "type": "rich",
            "username": "Unreal Engine - Free of the Month",
            "avatar_url": thumbnail_url,
            "embeds": [
                {
                    "title": "Free of the Month",
                    "url": unreal_store_url,
                    "description": description,
                    "thumbnail": {
                        "url": thumbnail_url,
                    },
                    "color": 16777215,
                }
            ],
        },
    )


# The job to be executed on a schedule
def run():
    # Only run on the first Tuesday of every month
    if time.strftime("%d") > 7:
        return

    asset_data = scrape(unreal_store_url)
    send_webhook(os.getenv("DISCORD_WEBHOOK_URL"), asset_data)


# Main function
# Schedules the job to run every Tuesday at 9:00 AM
def main():
    schedule.every().tuesday.at("9:00").do(run)
    while True:
        schedule.run_pending()
        time.sleep(1)
    run()
