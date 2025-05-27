#!/usr/bin/env python3
# .github/scripts/generate_facebook_posts.py

import os
import json
import time
import requests
import csv
import random
from datetime import datetime, timedelta
from google import genai
from google.genai import types
import csv

# Configure files and settings
URLS_FILE = "data/urls.txt"
PROCESSED_URLS_FILE = "data/processed_urls.txt"
PENDING_POSTS_FILE = "data/pending_posts.csv"
URLS_PER_RUN = 50

# Ensure directories exist
os.makedirs(os.path.dirname(URLS_FILE), exist_ok=True)
os.makedirs(os.path.dirname(PROCESSED_URLS_FILE), exist_ok=True)
os.makedirs(os.path.dirname(PENDING_POSTS_FILE), exist_ok=True)

def read_urls_from_file(filename=URLS_FILE):
    """Read all URLs from the file"""
    try:
        urls = []
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url and not url.startswith('#'):  # Skip empty lines and comments
                        urls.append(url)
        else:
            print(f"URLs file {filename} not found. Creating new file.")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8'):
                pass
        return urls
    except Exception as e:
        print(f"Error reading URLs from file: {e}")
        return []

def write_urls_to_file(urls, filename=URLS_FILE):
    """Write URLs back to the file"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(f"{url}\n")
        return True
    except Exception as e:
        print(f"Error writing URLs to file: {e}")
        return False

def append_processed_urls(urls, filename=PROCESSED_URLS_FILE):
    """Append processed URLs to the processed file with timestamps"""
    try:
        # Create file if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Determine header based on file existence
        file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0
        
        with open(filename, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Write header if it's a new file
            if not file_exists:
                f.write("# Processed URLs Log\n")
                f.write("# Format: [TIMESTAMP] URL\n\n")
            
            f.write(f"## Batch processed on {timestamp}\n")
            for url in urls:
                f.write(f"[{timestamp}] {url}\n")
            f.write("\n")  # Add a blank line between batches
        return True
    except Exception as e:
        print(f"Error appending to processed URLs file: {e}")
        return False

def save_to_pending_posts(posts, filename=PENDING_POSTS_FILE):
    """Save generated posts to CSV file for posting later"""
    try:
        # Check if file exists to determine if we need to write header
        file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0
        
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header if it's a new file
            if not file_exists:
                writer.writerow(['url', 'post_content', 'generated_time', 'posted', 'posted_time'])
            
            # Write posts
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for url, content in posts:
                writer.writerow([url, content, timestamp, 'False', ''])
        
        print(f"Successfully saved {len(posts)} posts to pending posts file")
        return True
    except Exception as e:
        print(f"Error saving to pending posts file: {e}")
        return False

def create_post_prompt(url):
    """Create prompt for generating Facebook post"""
    return f"""Create an engaging Facebook post for the article at this URL: {url}

Guidelines for the post:
1. Keep it concise (maximum 2-3 short paragraphs)
2. Start with an attention-grabbing question or statement
3. Include a brief description of what people will learn 
4. End with a clear call-to-action to click the link
5. Make the tone conversational and friendly
6. Don't use asterisk or emojis.
7. Focus on the practical benefits for the reader
8. Don't use clickbait phrases like "You won't believe..." or "This will shock you..."

The post should be directly ready to publish on Facebook with the link included at the end.
"""

def generate_facebook_post(prompt):
    """Generate Facebook post content using Gemini API"""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemma-3-27b-it"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_output_tokens=300,
        response_mime_type="text/plain",
    )
    
    try:
        print(f"Generating Facebook post...")
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        if response.text:
            print("Post generation successful")
            return response.text
        return "No content generated"
    except Exception as e:
        print(f"Error generating post: {e}")
        return f"Error generating post: {e}"

def main():
    print(f"Starting Facebook post generation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get URLs for this run
    all_urls = read_urls_from_file()
    print(f"Found {len(all_urls)} total URLs")
    
    # Select URLs for this run (up to URLS_PER_RUN)
    urls_to_process = all_urls[:URLS_PER_RUN]
    print(f"Selected {len(urls_to_process)} URLs for processing in this run")
    
    if not urls_to_process:
        print("No URLs to process. Exiting.")
        return
    
    generated_posts = []
    successful_urls = []
    
    for i, url in enumerate(urls_to_process, 1):
        print(f"\n{'='*50}\nProcessing URL #{i}: {url}\n{'='*50}")
        
        try:
            # Create prompt
            prompt = create_post_prompt(url)
            
            # Generate post
            post_content = generate_facebook_post(prompt)
            if post_content.startswith("Error"):
                print("Post generation failed, skipping to next URL")
                continue
            
            # Add to successful list
            generated_posts.append((url, post_content))
            successful_urls.append(url)
            print(f"Successfully generated post for: {url}")
            print(f"Post content preview: {post_content[:100]}...")
            
        except Exception as e:
            print(f"Error processing URL '{url}': {e}")
            continue
        
        # Add a small delay between requests
        if i < len(urls_to_process):
            sleep_time = random.randint(2, 5)
            print(f"Waiting {sleep_time} seconds before next URL...")
            time.sleep(sleep_time)
    
    # Save generated posts to pending file
    if generated_posts:
        save_to_pending_posts(generated_posts)
    
    # Update URL files
    if successful_urls:
        # Remove processed URLs from the original file
        remaining_urls = [url for url in all_urls if url not in successful_urls]
        write_urls_to_file(remaining_urls)
        
        # Add processed URLs to the processed file
        append_processed_urls(successful_urls)
        
        print(f"Updated URL files: removed {len(successful_urls)} processed URLs")
    
    print(f"Facebook post generation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Generated {len(generated_posts)} posts out of {len(urls_to_process)} URLs")

if __name__ == "__main__":
    main()