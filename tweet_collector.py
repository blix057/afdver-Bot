import logging
import time
from typing import List, Dict
from datetime import datetime
from twitter_client import TwitterClient
from content_analyzer import ContentAnalyzer
from config import AFD_ACCOUNTS, CONSTITUTIONAL_KEYWORDS, SEARCH_SETTINGS
from db import LinkStore

class TweetCollector:
    """
    Collects and analyzes tweets from AfD accounts and searches for constitutional concerns
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.twitter_client = TwitterClient()
        self.content_analyzer = ContentAnalyzer()
        self.accounts = AFD_ACCOUNTS
        self.search_settings = SEARCH_SETTINGS
        # Initialize DB link store if configured
        try:
            self.link_store = LinkStore()
        except Exception as e:
            self.logger.warning(f"LinkStore disabled (no MongoDB configured): {e}")
            self.link_store = None
        
    def collect_from_accounts(self) -> List[Dict]:
        """
        Collect tweets from all configured AfD accounts
        
        Returns:
            List of flagged tweets with analysis
        """
        all_flagged_tweets = []
        successful_accounts = 0
        failed_accounts = 0
        
        self.logger.info(f"Starting collection from {len(self.accounts)} AfD accounts")
        
        for account in self.accounts:
            try:
                self.logger.info(f"Collecting tweets from @{account}")
                
                # Get tweets from this account
                tweets = self.twitter_client.search_tweets_by_user(
                    username=account,
                    max_results=self.search_settings['max_tweets_per_account'],
                    days_back=self.search_settings['days_back']
                )
                
                if not tweets:
                    self.logger.warning(f"No tweets found for @{account}")
                    continue
                
                self.logger.info(f"Found {len(tweets)} tweets from @{account}")
                
                # Analyze tweets for constitutional concerns
                flagged_tweets = self.content_analyzer.batch_analyze_tweets(tweets)
                
                if flagged_tweets:
                    self.logger.info(f"Flagged {len(flagged_tweets)} tweets from @{account}")
                    
                    # Add account information to each flagged tweet
                    for tweet_analysis in flagged_tweets:
                        tweet_analysis['source_account'] = account
                        tweet_analysis['collection_method'] = 'account_search'
                    
                    all_flagged_tweets.extend(flagged_tweets)
                    
                    # Store links in DB (de-duplicated across users)
                    if self.link_store:
                        new_links = 0
                        for ta in flagged_tweets:
                            new_links += self.link_store.store_from_tweet_analysis(ta)
                        self.logger.info(f"Stored {new_links} new links from @{account}")
                else:
                    self.logger.info(f"No problematic tweets found for @{account}")
                
                successful_accounts += 1
                
                # Rate limiting: small delay between accounts
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error collecting tweets from @{account}: {e}")
                failed_accounts += 1
                continue
        
        self.logger.info(f"Collection complete: {successful_accounts} successful, {failed_accounts} failed")
        self.logger.info(f"Total flagged tweets: {len(all_flagged_tweets)}")
        
        return all_flagged_tweets
    
    def collect_by_keywords(self, max_results_per_keyword: int = 50) -> List[Dict]:
        """
        Search for tweets containing constitutional keywords
        
        Args:
            max_results_per_keyword: Maximum tweets to collect per keyword
            
        Returns:
            List of flagged tweets with analysis
        """
        all_flagged_tweets = []
        successful_keywords = 0
        failed_keywords = 0
        
        # Limit to most important keywords to avoid rate limits
        priority_keywords = CONSTITUTIONAL_KEYWORDS[:20]  # First 20 keywords
        
        self.logger.info(f"Starting keyword search for {len(priority_keywords)} terms")
        
        for keyword in priority_keywords:
            try:
                self.logger.info(f"Searching for keyword: '{keyword}'")
                
                # Build search query
                query = f"{keyword} lang:de -is:retweet"
                
                # Search tweets
                tweets = self.twitter_client.search_tweets_by_keyword(
                    query=query,
                    max_results=max_results_per_keyword,
                    days_back=self.search_settings['days_back']
                )
                
                if not tweets:
                    self.logger.info(f"No tweets found for '{keyword}'")
                    continue
                
                self.logger.info(f"Found {len(tweets)} tweets for '{keyword}'")
                
                # Analyze tweets
                flagged_tweets = self.content_analyzer.batch_analyze_tweets(tweets)
                
                if flagged_tweets:
                    self.logger.info(f"Flagged {len(flagged_tweets)} tweets for '{keyword}'")
                    
                    # Add keyword information
                    for tweet_analysis in flagged_tweets:
                        tweet_analysis['search_keyword'] = keyword
                        tweet_analysis['collection_method'] = 'keyword_search'
                    
                    all_flagged_tweets.extend(flagged_tweets)
                    
                    # Store links in DB (de-duplicated across users)
                    if self.link_store:
                        new_links = 0
                        for ta in flagged_tweets:
                            new_links += self.link_store.store_from_tweet_analysis(ta)
                        self.logger.info(f"Stored {new_links} new links for keyword '{keyword}'")
                
                successful_keywords += 1
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error searching for keyword '{keyword}': {e}")
                failed_keywords += 1
                continue
        
        self.logger.info(f"Keyword search complete: {successful_keywords} successful, {failed_keywords} failed")
        self.logger.info(f"Total flagged tweets from keywords: {len(all_flagged_tweets)}")
        
        return all_flagged_tweets
    
    def full_collection(self) -> Dict:
        """
        Perform complete collection from both accounts and keywords
        
        Returns:
            Dictionary with all results and summary
        """
        self.logger.info("Starting full AfD tweet collection")
        collection_start = datetime.utcnow()
        
        # Collect from accounts
        account_tweets = self.collect_from_accounts()
        
        # Collect by keywords
        keyword_tweets = self.collect_by_keywords()
        
        # Combine and deduplicate
        all_tweets = account_tweets + keyword_tweets
        deduplicated_tweets = self._deduplicate_tweets(all_tweets)
        
        # Sort by severity (highest first)
        deduplicated_tweets.sort(key=lambda x: x['severity_score'], reverse=True)
        
        # Generate summary
        summary = self.content_analyzer.generate_summary(deduplicated_tweets)
        
        collection_end = datetime.utcnow()
        collection_duration = (collection_end - collection_start).total_seconds()
        
        results = {
            'collection_timestamp': collection_start,
            'collection_duration_seconds': collection_duration,
            'flagged_tweets': deduplicated_tweets,
            'summary': summary,
            'collection_stats': {
                'accounts_searched': len(self.accounts),
                'tweets_from_accounts': len(account_tweets),
                'tweets_from_keywords': len(keyword_tweets),
                'total_before_dedup': len(all_tweets),
                'total_after_dedup': len(deduplicated_tweets)
            }
        }
        
        self.logger.info(f"Full collection complete in {collection_duration:.1f} seconds")
        self.logger.info(f"Final result: {len(deduplicated_tweets)} unique flagged tweets")
        
        return results
    
    def _deduplicate_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """
        Remove duplicate tweets based on tweet ID
        
        Args:
            tweets: List of tweet analyses
            
        Returns:
            Deduplicated list
        """
        seen_ids = set()
        deduplicated = []
        
        for tweet in tweets:
            tweet_id = tweet['tweet_id']
            if tweet_id not in seen_ids:
                seen_ids.add(tweet_id)
                deduplicated.append(tweet)
            else:
                self.logger.debug(f"Removing duplicate tweet {tweet_id}")
        
        removed_count = len(tweets) - len(deduplicated)
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} duplicate tweets")
        
        return deduplicated
