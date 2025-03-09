# Reddit Content Remover

This script allows you to delete all your Reddit posts and comments. It uses the Reddit API through PRAW to safely and efficiently delete your content while respecting Reddit's rate limits. The script uses OAuth2 authentication for enhanced security.

## Setup

1. First, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a Reddit API application:
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app..."
   - Select "script" as the application type
   - Fill in the name and description
   - For redirect uri, use `http://localhost:8080` (important!)
   - Click "create app"

3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and fill in your credentials:
   - `REDDIT_CLIENT_ID`: The string under the app name
   - `REDDIT_CLIENT_SECRET`: The string labeled "secret"
   - `REDDIT_USER_AGENT`: A unique identifier for your script (can use the example provided)

## Usage

1. Run the script:
   ```bash
   python reddit_content_remover.py
   ```

2. The script will:
   - Open your default web browser for Reddit OAuth2 authorization
   - Ask you to log in to Reddit (if not already logged in)
   - Request permission to access your account
   - After authorization, return to the script automatically
   - Present options to delete:
     1. Posts only
     2. Comments only
     3. Both posts and comments
   - Ask for confirmation before proceeding with deletion
   - Show each item as it's being deleted
   - Print a summary when complete

## Safety Features

- OAuth2 authentication (more secure than password-based auth)
- Confirmation prompt before deletion
- 2-second delay between deletions to respect rate limits
- Error handling for individual items
- Detailed logging of deleted content
- Preview of comments before deletion
- Summary of deleted items at the end

## Note

This script will permanently delete your selected Reddit content. This action cannot be undone. Make sure you want to proceed before confirming the deletion. 