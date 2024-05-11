#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries and modules
import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute().parent))
from datetime import datetime
from fuzzywuzzy import fuzz
import json
import pandas as pd
import numpy as np
import re
import os
import requests
import ast
import random
from time import sleep
import html
from bs4 import BeautifulSoup
from tqdm import tqdm
tqdm.pandas()
import anthropic
from functions import sleep_random, parse_links, instagram_fetch_post_text, fetch_geocode, extract_locations

# Configuration of API keys
google_geocode_api_key = ''  # Google Geocode API key
anthropic_api_key = ''  # Anthropic API key

# Paths setup
out_path = 'files/'  # Default output directory
telegram_results_json_path = 'path_to_telegram_result.json'  # Update this with your actual path from the Telegram JSON export

# Ensure the output directory exists
if not os.path.exists(out_path):
    os.makedirs(out_path)
out_path = os.path.abspath(out_path)

# Initialize the Anthropoic API client
client = anthropic.Anthropic(api_key=anthropic_api_key)

# Load and clean the JSON exported from Telegram
results = pd.read_json(telegram_results_json_path, orient='records')
results['links'] = results['messages'].apply(parse_links)  # Extract links from messages
# Clean URLs by removing Instagram tracking parameters -- ?igshid=
results['links'] = results['links'].apply(lambda x: [re.sub(r'\?igshid=.*', '', link) for link in x])
results['links'] = results['links'].apply(lambda x: list(set(x)))  # Remove duplicate links
results = results.drop_duplicates(subset=['links'])  # Drop duplicate messages
results = results[results['links'].map(len) > 0]  # Keep only messages with links
links_list = results['links'].tolist()
links_list = [item for sublist in links_list for item in sublist]  # Flatten list of lists
links_list = list(dict.fromkeys(links_list))  # Remove duplicates from flat list

# Fetch post text from Instagram links
parsed_list = []
for url in tqdm(links_list):  # Progress bar for visual feedback
    post_dict = instagram_fetch_post_text(url)
    parsed_list.append({'url': url, 'post_text': post_dict})
    sleep_random(3, 5)  # Random sleep to mimic human interaction and avoid rate limits

parsed_list = [x for x in parsed_list if x['post_text']]  # Filter out empty posts

# Extract and geocode locations from the post texts
locations = []
for post in tqdm(parsed_list):
    sleep(1)  # Sleep to pace requests
    extracted_locs = extract_locations(client, post['post_text'], 3)
    if extracted_locs:
        for loc in extracted_locs:
            try:
                if loc['city_town'] != loc['place']:
                    address_string = loc['place'] + ', ' + loc['city_town'] + ', ' + loc['state'] + ', ' + loc['country']
                else:
                    address_string = loc['city_town'] + ', ' + loc['state'] + ', ' + loc['country']
                results = fetch_geocode(address_string, google_geocode_api_key)
                results = results['results'][0]

                locations.append({
                    'url': post['url'],
                    'post': post['post_text'],
                    'extracted_loc': loc,
                    'geocoded': results,
                    'latitude': results['geometry']['location']['lat'],
                    'longitude': results['geometry']['location']['lng'],
                })
            except Exception as e:
                print(f"Error fetching geocode: {e}")
                continue

# Convert list of locations to a DataFrame
parsed_df = pd.DataFrame(locations)
parsed_df = pd.concat([parsed_df.drop(['extracted_loc'], axis=1), parsed_df['extracted_loc'].apply(pd.Series)], axis=1)
parsed_df['post'] = parsed_df['post'].apply(lambda x: f'``{x}``')  # In case excel has issues opening the CSV due to posts column

# Export the data to CSV and JSON formats
out_file_path = out_path + '/' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv'
parsed_df.to_csv(out_file_path, encoding='utf-8-sig', index=False)

locations_json = out_path + '/' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.json'
with open(locations_json, 'w') as f:
    json.dump(locations, f)
