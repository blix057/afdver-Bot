import os
import logging
from typing import Dict, List
from datetime import datetime
from twitter_client import TwitterClient

class ReportGenerator:
    """
    Generates formatted text reports from tweet analysis results
    """
    
    def __init__(self, twitter_client: TwitterClient = None):
        self.logger = logging.getLogger(__name__)
        self.twitter_client = twitter_client or TwitterClient()
        
    def generate_report(self, results: Dict, output_file: str) -> str:
        """
        Generate a comprehensive text report from analysis results
        
        Args:
            results: Results dictionary from TweetCollector.full_collection()
            output_file: Path to output file
            
        Returns:
            Path to the generated report file
        """
        self.logger.info(f"Generating report to {output_file}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write report header
            self._write_header(f, results)
            
            # Write executive summary
            self._write_executive_summary(f, results)
            
            # Write detailed findings
            self._write_detailed_findings(f, results['flagged_tweets'])
            
            # Write statistical analysis
            self._write_statistical_analysis(f, results)
            
            # Write methodology section
            self._write_methodology(f)
            
            # Write legal context
            self._write_legal_context(f)
            
            # Write footer
            self._write_footer(f, results)
        
        self.logger.info(f"Report generated successfully: {output_file}")
        return output_file
    
    def _write_header(self, f, results: Dict):
        """Write report header"""
        f.write("=" * 80 + "\n")
        f.write("AUTOMATED CONSTITUTIONAL ANALYSIS REPORT\n")
        f.write("AfD Twitter Content Monitoring\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Collection Date: {results['collection_timestamp'].strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"Collection Duration: {results['collection_duration_seconds']:.1f} seconds\n\n")
    
    def _write_executive_summary(self, f, results: Dict):
        """Write executive summary section"""
        summary = results['summary']
        stats = results['collection_stats']
        
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 50 + "\n\n")
        
        f.write(f"• Total AfD accounts monitored: {stats['accounts_searched']}\n")
        f.write(f"• Total flagged tweets found: {summary['total_flagged']}\n")
        f.write(f"• Average severity score: {summary['average_severity']}/10\n")
        f.write(f"• Maximum severity score: {summary['max_severity']}/10\n\n")
        
        if summary['total_flagged'] > 0:
            f.write("Severity Distribution:\n")
            f.write(f"  - High (≥6.0): {summary['severity_distribution']['high']} tweets\n")
            f.write(f"  - Medium (3.0-5.9): {summary['severity_distribution']['medium']} tweets\n")
            f.write(f"  - Low (<3.0): {summary['severity_distribution']['low']} tweets\n\n")
            
            f.write("Content Categories Found:\n")
            for category, count in summary['category_counts'].items():
                category_name = category.replace('_', ' ').title()
                f.write(f"  - {category_name}: {count} tweets\n")
            f.write("\n")
            
            if summary['most_common_keywords']:
                f.write("Most Common Constitutional Keywords:\n")
                for keyword, count in summary['most_common_keywords'][:5]:
                    f.write(f"  - '{keyword}': {count} occurrences\n")
                f.write("\n")
        else:
            f.write("No tweets were flagged for constitutional concerns during this monitoring period.\n\n")
    
    def _write_detailed_findings(self, f, flagged_tweets: List[Dict]):
        """Write detailed findings section"""
        f.write("DETAILED FINDINGS\n")
        f.write("-" * 50 + "\n\n")
        
        if not flagged_tweets:
            f.write("No tweets were flagged for constitutional concerns.\n\n")
            return
        
        for i, tweet in enumerate(flagged_tweets[:50], 1):  # Limit to top 50 tweets
            f.write(f"FINDING #{i}\n")
            f.write(f"Severity Score: {tweet['severity_score']}/10\n")
            
            # Get tweet URL
            tweet_url = self._get_tweet_url(tweet)
            f.write(f"Tweet URL: {tweet_url}\n")
            
            f.write(f"Posted: {tweet['created_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            
            if 'source_account' in tweet:
                f.write(f"Account: @{tweet['source_account']}\n")
            
            f.write(f"Collection Method: {tweet.get('collection_method', 'unknown')}\n")
            
            if 'search_keyword' in tweet:
                f.write(f"Triggered by keyword: '{tweet['search_keyword']}'\n")
            
            f.write("\nContent Categories:\n")
            for category in tweet['categories']:
                category_name = category.replace('_', ' ').title()
                f.write(f"  - {category_name}\n")
            
            f.write("\nMatched Keywords:\n")
            for keyword in tweet['matched_keywords']:
                f.write(f"  - '{keyword}'\n")
            
            f.write("\nTweet Text:\n")
            f.write(f'\\"{tweet["text"]}\\"\n')
            
            # Add engagement metrics if available
            if 'public_metrics' in tweet and tweet['public_metrics']:
                metrics = tweet['public_metrics']
                f.write("\nEngagement Metrics:\n")
                f.write(f"  - Retweets: {metrics.get('retweet_count', 'N/A')}\n")
                f.write(f"  - Likes: {metrics.get('like_count', 'N/A')}\n")
                f.write(f"  - Replies: {metrics.get('reply_count', 'N/A')}\n")
            
            f.write("\n" + "=" * 70 + "\n\n")
    
    def _write_statistical_analysis(self, f, results: Dict):
        """Write statistical analysis section"""
        f.write("STATISTICAL ANALYSIS\n")
        f.write("-" * 50 + "\n\n")
        
        stats = results['collection_stats']
        summary = results['summary']
        
        f.write("Collection Statistics:\n")
        f.write(f"  - Accounts successfully searched: {stats['accounts_searched']}\n")
        f.write(f"  - Tweets from account searches: {stats['tweets_from_accounts']}\n")
        f.write(f"  - Tweets from keyword searches: {stats['tweets_from_keywords']}\n")
        f.write(f"  - Total before deduplication: {stats['total_before_dedup']}\n")
        f.write(f"  - Total after deduplication: {stats['total_after_dedup']}\n\n")
        
        if summary['total_flagged'] > 0:
            flagging_rate = (summary['total_flagged'] / max(stats['total_after_dedup'], 1)) * 100
            f.write(f"Flagging Rate: {flagging_rate:.2f}% of collected tweets\n\n")
            
            f.write("Keyword Frequency Analysis:\n")
            for keyword, count in summary['most_common_keywords'][:10]:
                f.write(f"  - '{keyword}': {count} occurrences\n")
            f.write("\n")
        
    def _write_methodology(self, f):
        """Write methodology section"""
        f.write("METHODOLOGY\n")
        f.write("-" * 50 + "\n\n")
        
        f.write("Data Collection:\n")
        f.write("This report was generated through automated analysis of public Twitter content\n")
        f.write("from official Alternative für Deutschland (AfD) party accounts at federal and\n")
        f.write("state levels. The analysis uses the Twitter API to collect recent tweets and\n")
        f.write("searches for specific keywords related to constitutional concerns.\n\n")
        
        f.write("Analysis Criteria:\n")
        f.write("Content is flagged based on keyword matching against terms that may indicate:\n")
        f.write("  - Threats to democratic basic order (Art. 21(2) GG)\n")
        f.write("  - Anti-constitutional rhetoric\n")
        f.write("  - Historical revisionism\n")
        f.write("  - Promotion of violence\n")
        f.write("  - Hate speech patterns\n\n")
        
        f.write("Severity Scoring:\n")
        f.write("Each flagged tweet receives a severity score (0-10) based on:\n")
        f.write("  - Number of matched keywords\n")
        f.write("  - Category of constitutional concern\n")
        f.write("  - Weighted importance of different violation types\n\n")
        
        f.write("Limitations:\n")
        f.write("  - Automated analysis may miss context or nuance\n")
        f.write("  - False positives are possible\n")
        f.write("  - Limited to public Twitter content\n")
        f.write("  - Keyword-based detection has inherent limitations\n\n")
    
    def _write_legal_context(self, f):
        """Write legal context section"""
        f.write("LEGAL CONTEXT\n")
        f.write("-" * 50 + "\n\n")
        
        f.write("Constitutional Basis (Article 21(2) Grundgesetz):\n")
        f.write("'Parties that, by reason of their aims or the behavior of their members,\n")
        f.write("seek to undermine or abolish the free democratic basic order or to\n")
        f.write("endanger the existence of the Federal Republic of Germany shall be\n")
        f.write("unconstitutional.'\n\n")
        
        f.write("Party Ban Requirements:\n")
        f.write("  1. Active, aggressive, and militant stance against democracy\n")
        f.write("  2. Concrete plans to undermine the constitutional order\n")
        f.write("  3. Sufficient weight and significance to pose real threat\n\n")
        
        f.write("Important Note:\n")
        f.write("This automated analysis is for informational purposes only and does not\n")
        f.write("constitute legal evidence or professional legal assessment. Only the\n")
        f.write("Federal Constitutional Court can determine party unconstitutionality.\n\n")
    
    def _write_footer(self, f, results: Dict):
        """Write report footer"""
        f.write("REPORT METADATA\n")
        f.write("-" * 50 + "\n\n")
        
        f.write(f"Generated by: AfD Twitter Monitoring Bot\n")
        f.write(f"Analysis timestamp: {results['collection_timestamp'].isoformat()}\n")
        f.write(f"Report generation: {datetime.utcnow().isoformat()}\n")
        f.write(f"Collection duration: {results['collection_duration_seconds']:.2f}s\n\n")
        
        f.write("Disclaimer:\n")
        f.write("This report contains automated analysis of public social media content.\n")
        f.write("All findings should be verified independently. The analysis is based on\n")
        f.write("publicly available information and constitutional law principles.\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    def _get_tweet_url(self, tweet: Dict) -> str:
        """Get URL for a tweet"""
        try:
            if 'source_account' in tweet:
                return f"https://twitter.com/{tweet['source_account']}/status/{tweet['tweet_id']}"
            else:
                # Try to get username from Twitter API
                user = self.twitter_client.client.get_user(id=tweet['author_id'])
                if user.data:
                    return f"https://twitter.com/{user.data.username}/status/{tweet['tweet_id']}"
                else:
                    return f"https://twitter.com/unknown/status/{tweet['tweet_id']}"
        except:
            return f"https://twitter.com/unknown/status/{tweet['tweet_id']}"