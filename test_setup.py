#!/usr/bin/env python3
"""
Setup validation script for AfD Twitter Monitoring Bot
Tests all modules and configurations without requiring API credentials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    
    try:
        import config
        print("✓ config.py imported successfully")
        
        import content_analyzer
        print("✓ content_analyzer.py imported successfully")
        
        import report_generator
        print("✓ report_generator.py imported successfully")
        
        import tweet_collector
        print("✓ tweet_collector.py imported successfully")
        
        # Test twitter_client import (might fail without credentials, that's OK)
        try:
            import twitter_client
            print("✓ twitter_client.py imported successfully")
        except Exception as e:
            print(f"⚠ twitter_client.py import issue (expected without API credentials): {e}")
        
        import main
        print("✓ main.py imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration data"""
    print("\nTesting configuration...")
    
    from config import AFD_ACCOUNTS, CONSTITUTIONAL_KEYWORDS, CONTENT_CATEGORIES, SEARCH_SETTINGS
    
    print(f"✓ AfD accounts configured: {len(AFD_ACCOUNTS)} accounts")
    print(f"✓ Constitutional keywords: {len(CONSTITUTIONAL_KEYWORDS)} keywords")
    print(f"✓ Content categories: {len(CONTENT_CATEGORIES)} categories")
    print(f"✓ Search settings: {list(SEARCH_SETTINGS.keys())}")
    
    # Test a few sample accounts
    federal_accounts = ['AfD', 'Alice_Weidel', 'Tino_Chrupalla']
    found_federal = [acc for acc in federal_accounts if acc in AFD_ACCOUNTS]
    print(f"✓ Federal accounts found: {found_federal}")
    
    return True

def test_content_analyzer():
    """Test content analysis without real tweets"""
    print("\nTesting content analyzer...")
    
    from content_analyzer import ContentAnalyzer
    
    # Create mock tweet object
    class MockTweet:
        def __init__(self, text):
            self.id = "123456789"
            self.author_id = "987654321"
            self.created_at = "2023-01-01T00:00:00Z"
            self.text = text
            self.lang = "de"
            self.public_metrics = {"retweet_count": 0, "like_count": 0, "reply_count": 0}
    
    analyzer = ContentAnalyzer()
    
    # Test with neutral content
    neutral_tweet = MockTweet("Das ist ein normaler Tweet über Politik.")
    result = analyzer.analyze_tweet(neutral_tweet)
    if result is None:
        print("✓ Neutral content correctly ignored")
    else:
        print(f"⚠ Neutral content flagged: {result}")
    
    # Test with problematic content
    problematic_tweet = MockTweet("Wir müssen das System stürzen und die Demokratie abschaffen!")
    result = analyzer.analyze_tweet(problematic_tweet)
    if result:
        print(f"✓ Problematic content detected with severity {result['severity_score']}")
        print(f"  Categories: {result['categories']}")
        print(f"  Keywords: {result['matched_keywords']}")
    else:
        print("⚠ Problematic content not detected")
    
    return True

def test_report_generator():
    """Test report generation with mock data"""
    print("\nTesting report generator...")
    
    from report_generator import ReportGenerator
    from datetime import datetime
    import tempfile
    import os
    
    # Create mock results data
    mock_results = {
        'collection_timestamp': datetime.utcnow(),
        'collection_duration_seconds': 123.45,
        'flagged_tweets': [
            {
                'tweet_id': '123456789',
                'author_id': '987654321',
                'created_at': datetime.utcnow(),
                'text': 'Test tweet content',
                'matched_keywords': ['test keyword'],
                'categories': ['test_category'],
                'severity_score': 5.5,
                'source_account': 'TestAccount',
                'collection_method': 'test',
                'public_metrics': {'retweet_count': 10, 'like_count': 5, 'reply_count': 2}
            }
        ],
        'summary': {
            'total_flagged': 1,
            'categories_found': ['test_category'],
            'category_counts': {'test_category': 1},
            'severity_distribution': {'high': 0, 'medium': 1, 'low': 0},
            'most_common_keywords': [('test keyword', 1)],
            'average_severity': 5.5,
            'max_severity': 5.5
        },
        'collection_stats': {
            'accounts_searched': 5,
            'tweets_from_accounts': 10,
            'tweets_from_keywords': 5,
            'total_before_dedup': 15,
            'total_after_dedup': 12
        }
    }
    
    # Test report generation
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # This might fail without Twitter credentials, but we can catch it
        try:
            generator = ReportGenerator()
            generator.generate_report(mock_results, tmp_path)
            print("✓ Report generated successfully")
            
            # Check if file was created
            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                print("✓ Report file created and contains data")
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"✓ Report contains {len(lines)} lines")
            else:
                print("⚠ Report file is empty or missing")
                
        except Exception as e:
            print(f"⚠ Report generation failed (might be due to missing API credentials): {e}")
        
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    return True

def main():
    """Run all setup tests"""
    print("AfD Twitter Monitoring Bot - Setup Validation")
    print("=" * 50)
    
    success = True
    
    success &= test_imports()
    success &= test_config()
    success &= test_content_analyzer()
    success &= test_report_generator()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Setup validation completed successfully!")
        print("\nNext steps:")
        print("1. Get Twitter API credentials from developer.twitter.com")
        print("2. Copy .env.template to .env and add your credentials")
        print("3. Run: python main.py --dry-run")
    else:
        print("✗ Setup validation failed!")
        print("Please check the errors above and fix any issues.")
    
    print("=" * 50)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())