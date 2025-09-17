import tweepy
import os
import logging
from dotenv import load_dotenv
import time
from typing import Optional

# Load environment variables
load_dotenv()

class TwitterClient:
    """
    Twitter API client with authentication and rate limiting
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api = None
        self.client = None
        self._setup_authentication()
        
    def _setup_authentication(self):
        """Set up Twitter API authentication"""
        try:
            # Get credentials from environment variables
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            
            if not all([bearer_token, api_key, api_secret, access_token, access_token_secret]):
                raise ValueError("Missing Twitter API credentials in environment variables")
            
            # Setup API v2 client (preferred for newer features)
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Setup API v1.1 client (for some features not available in v2)
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Verify credentials
            self._verify_credentials()
            
        except Exception as e:
            self.logger.error(f"Failed to setup Twitter authentication: {e}")
            raise
    
    def _verify_credentials(self):
        """Verify that the API credentials are working"""
        try:
            # Test API v2 client
            me = self.client.get_me()
            self.logger.info(f"Twitter API v2 authenticated as: {me.data.username}")
            
            # Test API v1.1 client
            me_v1 = self.api.verify_credentials()
            self.logger.info(f"Twitter API v1.1 authenticated as: {me_v1.screen_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to verify Twitter credentials: {e}")
            raise
    
    def search_tweets_by_user(self, username: str, max_results: int = 100, days_back: int = 30) -> list:
        """
        Search for recent tweets by a specific user
        
        Args:
            username: Twitter username (without @)
            max_results: Maximum number of tweets to retrieve
            days_back: How many days back to search
            
        Returns:
            List of tweet objects
        """
        try:
            # Get user ID first
            user = self.client.get_user(username=username)
            if not user.data:
                self.logger.warning(f"User {username} not found")
                return []
            
            user_id = user.data.id
            
            # Calculate start time
            from datetime import datetime, timedelta
            start_time = datetime.utcnow() - timedelta(days=days_back)
            
            # Search tweets
            tweets = tweepy.Paginator(
                self.client.get_users_tweets,
                id=user_id,
                max_results=min(max_results, 100),  # API limit is 100 per request
                start_time=start_time,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations', 'lang'],
                expansions=['author_id']
            ).flatten(limit=max_results)
            
            return list(tweets)
            
        except tweepy.TooManyRequests:
            self.logger.warning(f"Rate limit reached while searching tweets for {username}")
            time.sleep(15 * 60)  # Wait 15 minutes
            return []
        except Exception as e:
            self.logger.error(f"Error searching tweets for {username}: {e}")
            return []
    
    def search_tweets_by_keyword(self, query: str, max_results: int = 100, days_back: int = 30) -> list:
        """
        Search for tweets containing specific keywords
        
        Args:
            query: Search query
            max_results: Maximum number of tweets to retrieve
            days_back: How many days back to search
            
        Returns:
            List of tweet objects
        """
        try:
            # Calculate start time
            from datetime import datetime, timedelta
            start_time = datetime.utcnow() - timedelta(days=days_back)
            
            # Search tweets
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                max_results=min(max_results, 100),  # API limit is 100 per request
                start_time=start_time,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations', 'lang'],
                expansions=['author_id']
            ).flatten(limit=max_results)
            
            return list(tweets)
            
        except tweepy.TooManyRequests:
            self.logger.warning(f"Rate limit reached while searching for: {query}")
            time.sleep(15 * 60)  # Wait 15 minutes
            return []
        except Exception as e:
            self.logger.error(f"Error searching tweets for query '{query}': {e}")
            return []
    
    def get_tweet_url(self, tweet) -> str:
        """
        Generate URL for a tweet
        
        Args:
            tweet: Tweet object
            
        Returns:
            Tweet URL string
        """
        # Get author username from includes if available
        author_username = None
        if hasattr(tweet, 'includes') and 'users' in tweet.includes:
            for user in tweet.includes['users']:
                if user.id == tweet.author_id:
                    author_username = user.username
                    break
        
        if not author_username:
            # Fallback: try to get username separately (this uses additional API calls)
            try:
                user = self.client.get_user(id=tweet.author_id)
                author_username = user.data.username
            except:
                author_username = "unknown"
        
        return f"https://twitter.com/{author_username}/status/{tweet.id}"