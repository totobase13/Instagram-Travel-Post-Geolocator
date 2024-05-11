#!/usr/bin/env python
# coding: utf-8

# Imports
from time import sleep
import random
import re
import requests
import html
from bs4 import BeautifulSoup
import anthropic
import ast


# Function to sleep for a random duration between min and max seconds
def sleep_random(min, max):
    sleep(random.uniform(min, max))


# Function to extract all URLs from the given text
def parse_links(text):
    links = re.findall(r'(https?://[^\s]+)', str(text))
    return links


# Function to clean text by removing user mentions and special characters
def clean_text(text):
    text = re.sub(r'@\w+', '', text)  # Remove handles (user mentions) starting with '@'
    text = re.sub(r'[^\w\s]', '', text)  # Remove all special characters
    return text.strip()  # Remove leading/trailing spaces


# Function to fetch and extract post text from an Instagram URL
def instagram_fetch_post_text(url):
    payload, headers = {}, {}
    response = requests.request("GET", url, headers=headers, data=payload)
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        og_title_tag = soup.find('meta', property='og:title')
        if og_title_tag:
            post_text = og_title_tag.get('content')
            post_text = html.unescape(post_text)  # Convert HTML entities to text
        else:
            post_text = ''
    except Exception as e:
        print(f"Error fetching post text: {e}")
        post_text = ''
    return post_text


# Function to fetch geolocation data for a given address using Google Maps API
def fetch_geocode(location, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={api_key}"  # Construct the request URL
    response = requests.get(url)  # Send the GET request
    return response.json()  # Return the JSON response


# Function to extract location data from text using Anthropic API client
def extract_locations(client, text_input, attempts):
    attempts = 0
    while attempts < 2:
        try:
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0,
                system="extract all places. only return json no explainer. do not return duplicates. returning a machine-readable json format. Here are two examples of the format to return. \n\nExample 1:\n[{\"city_town\": \"Boston\", \"state\": \"Massachusetts\", \"country\": \"United States\", \"place\": \"Charles River\"}, {\"city_town\": \"Dubai\", \"state\": \"\", \"country\": \"United Arab Emirates\", \"place\": \"Al Serkal Arts District\"}...]\nExample 2:\n[{\"city_town\": \"Atlanta\", \"state\": \"Georgia\", \"country\": \"United States\", \"place\": \"Atlanta Zoo\"}...]",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": text_input
                            }
                        ]
                    }
                ]
            )

            message_response = message.content[0].text
            message_response = ast.literal_eval(message_response)
            return message_response
        except Exception as e:
            print(f"Error: {e}")
            attempts += 1

    return None
