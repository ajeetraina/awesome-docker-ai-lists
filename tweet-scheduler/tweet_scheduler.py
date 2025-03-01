#!/usr/bin/env python3
"""
Tweet Scheduler for Kubetools

This script automatically tweets about Kubernetes tools from the kubetools repository
at a specified interval (default: 1 hour).

Requirements:
- tweepy
- PyGithub
- python-dotenv
- pandas
- beautifulsoup4
- markdown

Setup:
1. Create a Twitter Developer account and get API credentials
2. Set the following environment variables:
   - TWITTER_API_KEY
   - TWITTER_API_SECRET
   - TWITTER_ACCESS_TOKEN
   - TWITTER_ACCESS_SECRET
   - GITHUB_TOKEN (optional, for higher API rate limits)

Usage:
python tweet-scheduler.py [--interval HOURS]
"""

import os
import re
import time
import random
import argparse
import logging
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import tweepy
import markdown
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from github import Github

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tweet_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("kubetools-tweet-scheduler")

# Load environment variables
load_dotenv()

# Configuration
REPO_OWNER = "ajeetraina"  # Updated to your forked repository
REPO_NAME = "kubetools"
README_PATH = "README.md"
HISTORY_FILE = "tweet_history.json"
MAX_TWEET_LENGTH = 280  # Twitter character limit

def setup_twitter_api():
    """Set up and return the Twitter API client using credentials from environment variables."""
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    
    if not all([api_key, api_secret, access_token, access_secret]):
        raise ValueError("Twitter API credentials not found. Please set all required environment variables.")
    
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    return tweepy.API(auth)

def get_readme_content():
    """Fetch the README.md content from GitHub repository."""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        g = Github(token)
    else:
        g = Github()
    
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    readme_content = repo.get_contents(README_PATH).decoded_content.decode("utf-8")
    return readme_content

def extract_tools_from_readme(readme_content):
    """Parse the README content and extract all tools with their details."""
    # Convert markdown to HTML
    html = markdown.markdown(readme_content)
    soup = BeautifulSoup(html, 'html.parser')
    
    tools = []
    current_category = None
    
    # Find all h2 elements (category headers) and tables
    h2_elements = soup.find_all('h2')
    
    for h2 in h2_elements:
        # Skip certain categories that don't contain tools
        skip_categories = ["Table of Contents", "Contributors", "Maintainer"]
        if h2.text in skip_categories:
            continue
        
        current_category = h2.text
        
        # Find the table after this h2
        table = h2.find_next('table')
        if not table:
            continue
        
        # Process each row in the table
        rows = table.find_all('tr')
        if len(rows) <= 1:  # Skip if only header row exists
            continue
            
        # Skip header row
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) >= 4:  # Ensure we have all expected columns
                # Extract tool info
                try:
                    tool_name = cells[1].text.strip()
                    
                    # Extract description and URL
                    description_cell = cells[2]
                    
                    # Check if there's a link in the description
                    link = description_cell.find('a')
                    if link:
                        url = link.get('href')
                        # Extract just the description text, not including the URL
                        description = description_cell.text.strip()
                    else:
                        url = None
                        description = description_cell.text.strip()
                    
                    # Extract GitHub popularity indicator if available
                    popularity = cells[3].text.strip()
                    
                    tools.append({
                        "category": current_category,
                        "name": tool_name,
                        "description": description,
                        "url": url,
                        "popularity": popularity
                    })
                except Exception as e:
                    logger.warning(f"Error extracting tool info: {e}")
                    continue
    
    logger.info(f"Extracted {len(tools)} tools from README")
    return tools

def load_tweet_history():
    """Load the history of previously tweeted tools."""
    history_path = Path(HISTORY_FILE)
    if history_path.exists():
        with open(history_path, 'r') as f:
            return json.load(f)
    return {"last_tweeted": None, "tweeted_tools": []}

def save_tweet_history(history):
    """Save the updated tweet history."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def select_tool_to_tweet(tools, history):
    """Select a tool to tweet, prioritizing ones that haven't been tweeted yet."""
    tweeted_tools = set(history["tweeted_tools"])
    
    # Filter out already tweeted tools
    untweeted_tools = [tool for tool in tools if tool["name"] not in tweeted_tools]
    
    if untweeted_tools:
        # Select a random tool from untweeted ones
        selected_tool = random.choice(untweeted_tools)
    else:
        # If all tools have been tweeted, reset and select randomly from all tools
        logger.info("All tools have been tweeted. Resetting selection pool.")
        selected_tool = random.choice(tools)
    
    return selected_tool

def create_tweet_text(tool):
    """Create the tweet text for a selected tool."""
    # Basic information
    tweet = f"🔧 #Kubernetes Tool: {tool['name']} - Category: {tool['category']}\n\n"
    
    # Add description, limiting to fit within tweet length
    description = tool['description']
    # Extract just the tool description without the URL
    description = re.sub(r'\[.*?\]|\(.*?\)', '', description).strip()
    
    # Handle long descriptions
    max_desc_length = MAX_TWEET_LENGTH - len(tweet) - 30  # Allow space for URL and hashtags
    if len(description) > max_desc_length:
        description = description[:max_desc_length-3] + "..."
    
    tweet += description + "\n\n"
    
    # Add URL if available
    if tool['url']:
        tweet += f"{tool['url']}\n\n"
    
    # Add hashtags
    tweet += "#Kubetools #Kubernetes #K8s #CloudNative"
    
    return tweet

def tweet_tool(api, tool):
    """Post a tweet about the selected tool."""
    tweet_text = create_tweet_text(tool)
    
    try:
        api.update_status(tweet_text)
        logger.info(f"Successfully tweeted about {tool['name']}")
        return True
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        return False

def run_scheduler(interval_hours=1):
    """Run the scheduler to tweet at the specified interval."""
    try:
        # Set up Twitter API
        api = setup_twitter_api()
        logger.info("Twitter API initialized successfully")
        
        # Get README content and extract tools
        readme_content = get_readme_content()
        tools = extract_tools_from_readme(readme_content)
        
        if not tools:
            logger.error("No tools extracted from README. Exiting.")
            return
        
        # Load tweet history
        history = load_tweet_history()
        
        while True:
            # Select a tool
            tool = select_tool_to_tweet(tools, history)
            logger.info(f"Selected tool to tweet: {tool['name']}")
            
            # Tweet the tool
            success = tweet_tool(api, tool)
            
            if success:
                # Update history
                if tool["name"] not in history["tweeted_tools"]:
                    history["tweeted_tools"].append(tool["name"])
                history["last_tweeted"] = datetime.now().isoformat()
                save_tweet_history(history)
            
            # Wait for the next interval
            next_tweet_time = datetime.now() + timedelta(hours=interval_hours)
            logger.info(f"Next tweet scheduled for: {next_tweet_time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(interval_hours * 3600)
    
    except Exception as e:
        logger.error(f"Error in scheduler: {e}")

def main():
    """Main function to parse arguments and start the scheduler."""
    parser = argparse.ArgumentParser(description="Tweet scheduler for Kubetools")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between tweets in hours (default: 1)")
    args = parser.parse_args()
    
    logger.info(f"Starting tweet scheduler with interval of {args.interval} hours")
    run_scheduler(interval_hours=args.interval)

if __name__ == "__main__":
    main()
