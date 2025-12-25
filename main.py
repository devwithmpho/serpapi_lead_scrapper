from serpapi import GoogleSearch
import os, time
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

from utils import clean_number
from utils import clean_url
from utils import create_session

load_dotenv()
api_key = os.getenv("SERPAPI_KEY")

niche = input("Enter niche: ")

while niche == "":
    niche = input("Enter niche: ")

all_results = []
start = 0
MAX_START = 100

while start < MAX_START:
    params = {
        "q": niche,
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

### Cleaning business data
details = []

session = create_session()

clean_start = time.time()

for place in all_results:
    title = place.get("title")
    phone = clean_number(place.get("phone"))
    website = clean_url(place.get("website"), session)

    details.append([title, phone, website])

clean_end = time.time()
clean_time_elapsed = round((clean_end - clean_start) / 60, 2)

print(f"Total time elapsed from cleaning: {clean_time_elapsed} minutes")

##### saving data to a csv file

# csv file name
now = datetime.now()
file_timestamp = now.strftime("%Y-%m-%d_%H-%M")
filename = f"lead_data_{niche.lower}_{file_timestamp}.csv"

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
df_cleaned = df_cleaned.dropna()

# send to csv
df_cleaned.to_csv(file_path, header=False, index=False)