from serpapi import GoogleSearch
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import pandas as pd

from utils import clean_number
from utils import clean_website

load_dotenv()
api_key = os.getenv("SERPAPI_KEY")

search_query = input("Enter search: ")

while search_query == "":
    search_query = input("Enter search: ")

all_results = []
start = 0
MAX_START = 100

while start < MAX_START:
    params = {
        "q": search_query,
        "engine": "google_maps",
        "ll": "@-26.0082584,26.8077072,8z",
        "hl": "af",
        "gl": "za",
        "start": start,
        "api_key": api_key
    }

    search = GoogleSearch(params)
    result = search.get_dict()

    local_results = result.get("local_results", [])
    if not local_results:
        break

    all_results.extend(local_results)

    print(f"Fetched {len(local_results)} results at start={start}")

    # pagination check
    pagination = result.get("serpapi_pagination", {})
    if "next" in pagination:
        start += 20
    else:
        break

    time.sleep(1.5)

print(f"Total businesses saved: {len(all_results)}")

details = []

for place in all_results:
    title = place.get("title")
    phone = clean_number(place.get("phone"))
    website = clean_website(place.get("website"))

    details.append([title, phone, website])

##### saving data to a csv file

# csv file name
now = datetime.now()
file_timestamp = now.strftime("%Y-%m-%d_%H-%M")
filename = f"lead_data_{file_timestamp}.csv"

# send csv to reports directory
folder_name = "reports"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

file_path = os.path.join(folder_name, filename)

# cleaning data

df = pd.DataFrame(details)
df.columns = ["Title", "Phone", "Website"]
df_cleaned = df[df["Phone"].notna()]

df_cleaned = df_cleaned.drop_duplicates()
df_cleaned = df_cleaned.fillna("None")

# send to csv
df_cleaned.to_csv(file_path, header=False, index=False)