import praw
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import webbrowser
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Extract code from callback URL
        query_components = parse_qs(urlparse(self.path).query)
        
        if 'code' in query_components:
            self.server.oauth_code = query_components['code'][0]
            self.wfile.write(b"Authorization successful! You can close this window.")
        else:
            self.wfile.write(b"Authorization failed! Please try again.")
        
    def log_message(self, format, *args):
        # Suppress log messages
        return

def get_oauth_code():
    """Start local server and get OAuth code"""
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    server.oauth_code = None
    
    # Only handle one request
    server.handle_request()
    
    return server.oauth_code

def setup_reddit():
    """
    Set up and return Reddit instance using OAuth2
    """
    load_dotenv()  # Load environment variables from .env file
    
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        redirect_uri="http://localhost:8080",
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    
    # Generate the authorization URL
    scopes = ['identity', 'history', 'edit']
    auth_url = reddit.auth.url(scopes, 'uniquestate')
    
    print("\nPlease authorize the application:")
    print(f"\n{auth_url}\n")
    
    # Open the authorization URL in default browser
    webbrowser.open(auth_url)
    
    # Wait for the callback
    print("Waiting for authorization...")
    oauth_code = get_oauth_code()
    
    if not oauth_code:
        raise Exception("Failed to get authorization code")
    
    # Exchange the code for a refresh token
    refresh_token = reddit.auth.authorize(oauth_code)
    
    print("\nAuthorization successful!")
    return reddit

def delete_all_posts(reddit, limit=None):
    """
    Delete all posts from the authenticated user's account
    
    Args:
        reddit: authenticated praw.Reddit instance
        limit: maximum number of posts to delete (None for all posts)
    """
    user = reddit.user.me()
    deleted_count = 0
    
    print(f"\nStarting post deletion process for user: {user.name}")
    
    # Get all submissions by the user
    for submission in user.submissions.new(limit=limit):
        try:
            # Print post information
            print(f"Deleting post: {submission.title}")
            print(f"Posted on: {datetime.fromtimestamp(submission.created_utc)}")
            print(f"Score: {submission.score}")
            print("-" * 50)
            
            # Delete the submission
            submission.delete()
            deleted_count += 1
            
            # Sleep to avoid hitting rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"Error deleting post: {str(e)}")
            continue
    
    print(f"\nPost deletion complete! Deleted {deleted_count} posts.")
    return deleted_count

def delete_all_comments(reddit, limit=None):
    """
    Delete all comments from the authenticated user's account
    
    Args:
        reddit: authenticated praw.Reddit instance
        limit: maximum number of comments to delete (None for all comments)
    """
    user = reddit.user.me()
    deleted_count = 0
    
    print(f"\nStarting comment deletion process for user: {user.name}")
    
    # Get all comments by the user
    for comment in user.comments.new(limit=limit):
        try:
            # Print comment information
            preview = comment.body[:100] + "..." if len(comment.body) > 100 else comment.body
            print(f"Deleting comment: {preview}")
            print(f"Posted on: {datetime.fromtimestamp(comment.created_utc)}")
            print(f"Score: {comment.score}")
            print("-" * 50)
            
            # Delete the comment
            comment.delete()
            deleted_count += 1
            
            # Sleep to avoid hitting rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"Error deleting comment: {str(e)}")
            continue
    
    print(f"\nComment deletion complete! Deleted {deleted_count} comments.")
    return deleted_count

def main():
    try:
        # Set up Reddit instance
        reddit = setup_reddit()
        username = reddit.user.me().name
        
        # Ask what to delete
        print("\nWhat would you like to delete?")
        print("1. Posts only")
        print("2. Comments only")
        print("3. Both posts and comments")
        choice = input("Enter your choice (1/2/3): ")
        
        if choice not in ['1', '2', '3']:
            print("Invalid choice. Exiting.")
            return
        
        # Confirm before deletion
        what_to_delete = {
            '1': "posts",
            '2': "comments",
            '3': "posts and comments"
        }[choice]
        
        confirm = input(f"\nThis will delete ALL {what_to_delete} for user {username}. Are you sure? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Deletion cancelled.")
            return
        
        posts_deleted = 0
        comments_deleted = 0
        
        # Perform deletions based on choice
        if choice in ['1', '3']:
            posts_deleted = delete_all_posts(reddit)
        
        if choice in ['2', '3']:
            comments_deleted = delete_all_comments(reddit)
        
        # Print final summary
        print("\nDeletion Summary:")
        if choice in ['1', '3']:
            print(f"Posts deleted: {posts_deleted}")
        if choice in ['2', '3']:
            print(f"Comments deleted: {comments_deleted}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 