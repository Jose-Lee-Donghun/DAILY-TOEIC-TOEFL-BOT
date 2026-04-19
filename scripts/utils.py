import json
import os
import requests
from datetime import date


def get_day_number():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    start_date = date.fromisoformat(config['start_date'])
    today = date.today()
    day_number = (today - start_date).days + 1
    return day_number


def load_content(day_number):
    content_path = os.path.join(
        os.path.dirname(__file__), '..', 'content', f'day_{day_number:03d}.json'
    )
    with open(content_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def send_slack(webhook_url, text):
    response = requests.post(webhook_url, json={'text': text})
    if response.status_code != 200:
        raise ValueError(f"Slack error {response.status_code}: {response.text}")
    return response.status_code
