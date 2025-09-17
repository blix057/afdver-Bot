#!/usr/bin/env python3
"""
AfD Twitter Monitoring Bot
Automated analysis of AfD social media content for constitutional concerns

Usage:
    python main.py [options]

Options:
    --accounts-only    : Only search AfD accounts (skip keyword search)
    --keywords-only    : Only search by keywords (skip account search)
    --output-dir PATH  : Directory to save reports (default: ./reports)
    --verbose          : Enable verbose logging
    --dry-run          : Perform analysis without generating report
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Import our modules
from tweet_collector import TweetCollector
from report_generator import ReportGenerator

def setup_logging(verbose: bool = False):
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/afd_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = [
        'TWITTER_BEARER_TOKEN',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease create a .env file with your Twitter API credentials.")
        print("See .env.template for the required format.")
        return False
    
    return True

def main():
    """Main bot execution"""
    parser = argparse.ArgumentParser(
        description="AfD Twitter Monitoring Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--accounts-only', action='store_true',
                       help='Only search AfD accounts (skip keyword search)')
    parser.add_argument('--keywords-only', action='store_true',
                       help='Only search by keywords (skip account search)')
    parser.add_argument('--output-dir', default='./reports',
                       help='Directory to save reports (default: ./reports)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform analysis without generating report')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting AfD Twitter Monitoring Bot")
    
    # Validate environment (Twitter only). MongoDB is optional.
    if not validate_environment():
        sys.exit(1)
    
    # Validate arguments
    if args.accounts_only and args.keywords_only:
        logger.error("Cannot use both --accounts-only and --keywords-only")
        sys.exit(1)
    
    try:
        # Initialize collector
        logger.info("Initializing tweet collector")
        collector = TweetCollector()
        
        # Determine collection method
        if args.accounts_only:
            logger.info("Running accounts-only collection")
            results = {
                'collection_timestamp': datetime.utcnow(),
                'flagged_tweets': collector.collect_from_accounts(),
                'collection_stats': {'accounts_searched': len(collector.accounts)},
                'collection_duration_seconds': 0
            }
            # Generate summary for accounts-only results
            from content_analyzer import ContentAnalyzer
            analyzer = ContentAnalyzer()
            results['summary'] = analyzer.generate_summary(results['flagged_tweets'])
            
        elif args.keywords_only:
            logger.info("Running keywords-only collection")
            results = {
                'collection_timestamp': datetime.utcnow(),
                'flagged_tweets': collector.collect_by_keywords(),
                'collection_stats': {'accounts_searched': 0},
                'collection_duration_seconds': 0
            }
            # Generate summary for keywords-only results
            from content_analyzer import ContentAnalyzer
            analyzer = ContentAnalyzer()
            results['summary'] = analyzer.generate_summary(results['flagged_tweets'])
            
        else:
            logger.info("Running full collection (accounts + keywords)")
            results = collector.full_collection()
        
        # Log results summary
        flagged_count = len(results['flagged_tweets'])
        logger.info(f"Collection complete: {flagged_count} tweets flagged")
        
        if flagged_count > 0:
            max_severity = max(tweet['severity_score'] for tweet in results['flagged_tweets'])
            avg_severity = sum(tweet['severity_score'] for tweet in results['flagged_tweets']) / flagged_count
            logger.info(f"Severity scores - Max: {max_severity:.2f}, Avg: {avg_severity:.2f}")
        
        # Generate report unless dry-run
        if not args.dry_run:
            # Create output directory
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate report filename
            timestamp = results['collection_timestamp'].strftime('%Y%m%d_%H%M%S')
            report_filename = f"afd_analysis_{timestamp}.txt"
            report_path = output_dir / report_filename
            
            # Generate report
            logger.info(f"Generating report: {report_path}")
            report_generator = ReportGenerator()
            report_generator.generate_report(results, str(report_path))
            
            print(f"\n{'='*60}")
            print(f"ANALYSIS COMPLETE")
            print(f"{'='*60}")
            print(f"Flagged tweets: {flagged_count}")
            if flagged_count > 0:
                print(f"Max severity: {max_severity:.2f}/10")
                print(f"Avg severity: {avg_severity:.2f}/10")
            print(f"Report saved: {report_path}")
            print(f"{'='*60}")
            
        else:
            logger.info("Dry-run complete - no report generated")
            print(f"\nDry-run results: {flagged_count} tweets flagged")
    
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        print("\nBot stopped by user")
        
    except Exception as e:
        logger.error(f"Bot failed with error: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)
    
    logger.info("AfD Twitter Monitoring Bot completed")

if __name__ == "__main__":
    main()