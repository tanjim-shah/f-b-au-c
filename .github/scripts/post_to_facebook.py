# #!/usr/bin/env python3
# # .github/scripts/post_to_facebook.py

# import os
# import json
# import time
# import requests
# import csv
# import random
# from datetime import datetime, timedelta

# # Configure files and settings
# PENDING_POSTS_FILE = "data/pending_posts.csv"
# FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
# FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

# def read_pending_posts():
#     """Read pending posts from CSV file"""
#     posts = []
#     if not os.path.exists(PENDING_POSTS_FILE):
#         print(f"Pending posts file {PENDING_POSTS_FILE} not found.")
#         return posts
    
#     try:
#         with open(PENDING_POSTS_FILE, 'r', newline='', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 # Only include posts that haven't been posted yet
#                 if row['posted'].lower() == 'false':
#                     posts.append(row)
        
#         print(f"Found {len(posts)} pending posts")
#         return posts
#     except Exception as e:
#         print(f"Error reading pending posts: {e}")
#         return []

# def update_pending_posts(posts):
#     """Update the pending posts CSV file"""
#     try:
#         if not os.path.exists(PENDING_POSTS_FILE):
#             print(f"Pending posts file {PENDING_POSTS_FILE} not found.")
#             return False
        
#         # Read all posts first (including header)
#         all_rows = []
#         with open(PENDING_POSTS_FILE, 'r', newline='', encoding='utf-8') as f:
#             reader = csv.reader(f)
#             all_rows = list(reader)
        
#         if not all_rows:
#             print("Pending posts file is empty.")
#             return False
        
#         # Create a dictionary of posts to update by URL
#         update_dict = {}
#         for post in posts:
#             update_dict[post['url']] = post
        
#         # Update rows that match the URLs
#         for i in range(1, len(all_rows)):  # Skip header row
#             if len(all_rows[i]) >= 3:  # Make sure row has enough columns
#                 url = all_rows[i][0]  # URL is in first column
#                 if url in update_dict:
#                     all_rows[i][3] = update_dict[url]['posted']  # 'posted' column
#                     all_rows[i][4] = update_dict[url]['posted_time']  # 'posted_time' column
        
#         # Write all rows back to the file
#         with open(PENDING_POSTS_FILE, 'w', newline='', encoding='utf-8') as f:
#             writer = csv.writer(f)
#             writer.writerows(all_rows)
        
#         print(f"Successfully updated {len(posts)} posts in pending posts file")
#         return True
#     except Exception as e:
#         print(f"Error updating pending posts: {e}")
#         return False

# def post_to_facebook(post_content, link):
#     """Post content to Facebook Page"""
#     if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
#         print("Facebook credentials not set. Skipping posting.")
#         return False
    
#     url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed"
    
#     params = {
#         'message': post_content,
#         'link': link,
#         'access_token': FACEBOOK_ACCESS_TOKEN
#     }
    
#     try:
#         print(f"Posting to Facebook: {link}")
#         response = requests.post(url, params=params)
        
#         if response.status_code == 200:
#             post_id = response.json().get('id')
#             print(f"Successfully posted to Facebook. Post ID: {post_id}")
#             return True
#         else:
#             print(f"Failed to post to Facebook. Response: {response.text}")
#             return False
#     except Exception as e:
#         print(f"Error posting to Facebook: {e}")
#         return False

# def main():
#     print(f"Starting Facebook posting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
#     # Read pending posts
#     pending_posts = read_pending_posts()
    
#     if not pending_posts:
#         print("No pending posts found. Exiting.")
#         return
    
#     # Select one post to publish
#     selected_post = random.choice(pending_posts)
#     print(f"Selected post for URL: {selected_post['url']}")
    
#     # Post to Facebook
#     success = post_to_facebook(selected_post['post_content'], selected_post['url'])
    
#     if success:
#         # Update post status
#         selected_post['posted'] = 'True'
#         selected_post['posted_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
#         # Update CSV file
#         update_pending_posts([selected_post])
    
#     print(f"Facebook posting completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
# .github/scripts/post_to_facebook.py

import os
import json
import time
import requests
import csv
import random
from datetime import datetime, timedelta

# Configure files and settings
PENDING_POSTS_FILE = "data/pending_posts.csv"
POST_DETAILS_FILE = "data/post_details.json"  # New file to store post details
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

def read_pending_posts():
    """Read pending posts from CSV file"""
    posts = []
    if not os.path.exists(PENDING_POSTS_FILE):
        print(f"Pending posts file {PENDING_POSTS_FILE} not found.")
        return posts
    
    try:
        with open(PENDING_POSTS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Only include posts that haven't been posted yet
                if row['posted'].lower() == 'false':
                    posts.append(row)
        
        print(f"Found {len(posts)} pending posts")
        return posts
    except Exception as e:
        print(f"Error reading pending posts: {e}")
        return []

def update_pending_posts(posts):
    """Update the pending posts CSV file"""
    try:
        if not os.path.exists(PENDING_POSTS_FILE):
            print(f"Pending posts file {PENDING_POSTS_FILE} not found.")
            return False
        
        # Read all posts first (including header)
        all_rows = []
        with open(PENDING_POSTS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            all_rows = list(reader)
        
        if not all_rows:
            print("Pending posts file is empty.")
            return False
        
        # Create a dictionary of posts to update by URL
        update_dict = {}
        for post in posts:
            update_dict[post['url']] = post
        
        # Update rows that match the URLs
        for i in range(1, len(all_rows)):  # Skip header row
            if len(all_rows[i]) >= 3:  # Make sure row has enough columns
                url = all_rows[i][0]  # URL is in first column
                if url in update_dict:
                    all_rows[i][3] = update_dict[url]['posted']  # 'posted' column
                    all_rows[i][4] = update_dict[url]['posted_time']  # 'posted_time' column
        
        # Write all rows back to the file
        with open(PENDING_POSTS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(all_rows)
        
        print(f"Successfully updated {len(posts)} posts in pending posts file")
        return True
    except Exception as e:
        print(f"Error updating pending posts: {e}")
        return False

def save_post_details(details):
    """Save post details to a JSON file for use in email notifications"""
    try:
        os.makedirs(os.path.dirname(POST_DETAILS_FILE), exist_ok=True)
        with open(POST_DETAILS_FILE, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=2)
        print(f"Post details saved to {POST_DETAILS_FILE}")
        
        # Also output to GitHub Actions environment for use in workflow
        with open(os.environ.get('GITHUB_ENV', ''), 'a') as env_file:
            for key, value in details.items():
                env_file.write(f"POST_{key.upper()}={value}\n")
        print("Post details added to GitHub environment variables")
        
        return True
    except Exception as e:
        print(f"Error saving post details: {e}")
        return False

def post_to_facebook(post_content, link):
    """Post content to Facebook Page"""
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        print("Facebook credentials not set. Skipping posting.")
        return False, {}
    
    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed"
    
    params = {
        'message': post_content,
        'link': link,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    
    try:
        print(f"Posting to Facebook: {link}")
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get('id')
            print(f"Successfully posted to Facebook. Post ID: {post_id}")
            
            # Get page details for post URL construction
            page_response = requests.get(
                f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}",
                params={'fields': 'username', 'access_token': FACEBOOK_ACCESS_TOKEN}
            )
            
            post_details = {
                'post_id': post_id,
                'blog_url': link,
                'post_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'success'
            }
            
            # If we can get the page username, construct the post URL
            if page_response.status_code == 200:
                page_data = page_response.json()
                username = page_data.get('username')
                if username and post_id:
                    # Extract the numeric part of the post_id (after the underscore)
                    if '_' in post_id:
                        numeric_id = post_id.split('_')[1]
                        post_url = f"https://www.facebook.com/{username}/posts/{numeric_id}"
                        post_details['post_url'] = post_url
            
            # Save post details to file
            save_post_details(post_details)
            
            return True, post_details
        else:
            error_details = {
                'blog_url': link,
                'error': response.text,
                'status': 'failed',
                'post_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_post_details(error_details)
            print(f"Failed to post to Facebook. Response: {response.text}")
            return False, error_details
    except Exception as e:
        error_details = {
            'blog_url': link,
            'error': str(e),
            'status': 'failed',
            'post_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_post_details(error_details)
        print(f"Error posting to Facebook: {e}")
        return False, error_details

def main():
    print(f"Starting Facebook posting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Read pending posts
    pending_posts = read_pending_posts()
    
    if not pending_posts:
        print("No pending posts found. Exiting.")
        return
    
    # Select one post to publish
    selected_post = random.choice(pending_posts)
    print(f"Selected post for URL: {selected_post['url']}")
    
    # Post to Facebook
    success, post_details = post_to_facebook(selected_post['post_content'], selected_post['url'])
    
    if success:
        # Update post status
        selected_post['posted'] = 'True'
        selected_post['posted_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update CSV file
        update_pending_posts([selected_post])
    
    print(f"Facebook posting completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()