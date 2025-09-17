import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from config import CONSTITUTIONAL_KEYWORDS, CONTENT_CATEGORIES

class ContentAnalyzer:
    """
    Analyzes tweet content for potentially constitutional concerns
    Based on Article 21(2) of the German Basic Law
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keywords = CONSTITUTIONAL_KEYWORDS
        self.categories = CONTENT_CATEGORIES
        
    def analyze_tweet(self, tweet) -> Dict:
        """
        Analyze a single tweet for constitutional concerns
        
        Args:
            tweet: Tweet object from Twitter API
            
        Returns:
            Dictionary with analysis results
        """
        if not tweet or not hasattr(tweet, 'text'):
            return None
            
        text = tweet.text.lower()
        
        # Find matching keywords
        matched_keywords = self._find_matching_keywords(text)
        
        if not matched_keywords:
            return None
            
        # Categorize the content
        categories = self._categorize_content(matched_keywords)
        
        # Calculate severity score
        severity_score = self._calculate_severity_score(matched_keywords, categories)
        
        analysis_result = {
            'tweet_id': tweet.id,
            'author_id': tweet.author_id,
            'created_at': tweet.created_at,
            'text': tweet.text,
            'matched_keywords': matched_keywords,
            'categories': categories,
            'severity_score': severity_score,
            'analysis_timestamp': datetime.utcnow(),
            'language': getattr(tweet, 'lang', 'unknown'),
            'public_metrics': getattr(tweet, 'public_metrics', {})
        }
        
        return analysis_result
    
    def _find_matching_keywords(self, text: str) -> List[str]:
        """
        Find constitutional keywords in tweet text
        
        Args:
            text: Tweet text (lowercase)
            
        Returns:
            List of matched keywords
        """
        matched_keywords = []
        
        for keyword in self.keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text):
                matched_keywords.append(keyword)
                self.logger.debug(f"Found keyword '{keyword}' in text")
        
        return matched_keywords
    
    def _categorize_content(self, keywords: List[str]) -> List[str]:
        """
        Categorize content based on matched keywords
        
        Args:
            keywords: List of matched keywords
            
        Returns:
            List of applicable categories
        """
        categories = []
        
        for category, category_keywords in self.categories.items():
            for keyword in keywords:
                if keyword in category_keywords:
                    if category not in categories:
                        categories.append(category)
                    break
                    
        return categories
    
    def _calculate_severity_score(self, keywords: List[str], categories: List[str]) -> float:
        """
        Calculate severity score based on content analysis
        
        Args:
            keywords: Matched keywords
            categories: Content categories
            
        Returns:
            Severity score (0-10, higher is more severe)
        """
        base_score = len(keywords) * 1.0  # Base score from number of keywords
        
        # Category multipliers (based on constitutional severity)
        category_multipliers = {
            'anti_democratic': 3.0,       # Direct threat to democracy
            'violence_promotion': 2.5,     # Promoting violence
            'hate_speech': 2.0,           # Hate speech
            'anti_constitutional': 1.8,    # Anti-constitutional rhetoric
            'historical_revisionism': 1.5  # Holocaust denial, etc.
        }
        
        category_score = 0
        for category in categories:
            multiplier = category_multipliers.get(category, 1.0)
            category_score += multiplier
        
        # Final score calculation
        severity_score = min(base_score * (1 + category_score), 10.0)
        
        return round(severity_score, 2)
    
    def batch_analyze_tweets(self, tweets: List) -> List[Dict]:
        """
        Analyze multiple tweets for constitutional concerns
        
        Args:
            tweets: List of tweet objects
            
        Returns:
            List of analysis results for flagged tweets
        """
        flagged_tweets = []
        
        for tweet in tweets:
            analysis = self.analyze_tweet(tweet)
            if analysis:
                flagged_tweets.append(analysis)
                self.logger.info(f"Flagged tweet {tweet.id} with severity {analysis['severity_score']}")
        
        # Sort by severity score (highest first)
        flagged_tweets.sort(key=lambda x: x['severity_score'], reverse=True)
        
        return flagged_tweets
    
    def generate_summary(self, flagged_tweets: List[Dict]) -> Dict:
        """
        Generate summary statistics for flagged tweets
        
        Args:
            flagged_tweets: List of flagged tweet analyses
            
        Returns:
            Summary dictionary
        """
        if not flagged_tweets:
            return {
                'total_flagged': 0,
                'categories_found': [],
                'severity_distribution': {},
                'most_common_keywords': []
            }
        
        # Count categories
        category_counts = {}
        all_keywords = []
        severity_scores = []
        
        for tweet in flagged_tweets:
            for category in tweet['categories']:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            all_keywords.extend(tweet['matched_keywords'])
            severity_scores.append(tweet['severity_score'])
        
        # Count keyword frequencies
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort keywords by frequency
        most_common_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Severity distribution
        severity_distribution = {
            'low': len([s for s in severity_scores if s < 3]),
            'medium': len([s for s in severity_scores if 3 <= s < 6]),
            'high': len([s for s in severity_scores if s >= 6])
        }
        
        return {
            'total_flagged': len(flagged_tweets),
            'categories_found': list(category_counts.keys()),
            'category_counts': category_counts,
            'severity_distribution': severity_distribution,
            'most_common_keywords': most_common_keywords,
            'average_severity': round(sum(severity_scores) / len(severity_scores), 2) if severity_scores else 0,
            'max_severity': max(severity_scores) if severity_scores else 0
        }