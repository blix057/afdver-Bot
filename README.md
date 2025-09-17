# AfD Twitter Monitoring Bot

An automated system for monitoring Alternative für Deutschland (AfD) social media content for potential constitutional concerns based on Article 21(2) of the German Basic Law.

## Overview

This bot monitors official AfD Twitter accounts at federal and state levels, analyzing public content for keywords and patterns that may indicate constitutional concerns. The analysis is based on Germany's legal framework for party bans and generates structured reports for further review.

## Legal Disclaimer

⚠️ **IMPORTANT**: This is an automated analysis tool for research and informational purposes only. It does not constitute legal evidence or professional legal assessment. Only the Federal Constitutional Court of Germany can determine party unconstitutionality.

## Features

- **Account Monitoring**: Tracks tweets from official AfD accounts at federal and state levels
- **Keyword Analysis**: Searches for constitutionally relevant terms and phrases
- **Severity Scoring**: Assigns severity scores based on content analysis
- **Content Categorization**: Groups findings into constitutional concern categories
- **Comprehensive Reports**: Generates detailed text reports with links and summaries
- **Rate Limiting**: Respects Twitter API rate limits and terms of service
- **Ethical Constraints**: Built with transparency and legal compliance in mind

## Requirements

- Python 3.8 or higher
- Twitter API v2 access (Bearer Token + OAuth 1.0a credentials)
- Required Python packages (see `requirements.txt`)
- Optional: MongoDB Atlas account (for shared, de-duplicated link storage)

## Setup

### 1. Twitter API Access

How to get a Twitter (X) API key:
1. Go to https://developer.twitter.com and sign in.
2. Apply for a developer account and create a Project + App.
3. In your App, generate:
   - API Key and API Secret
   - Bearer Token
   - Access Token and Access Token Secret
4. Copy these into your .env file as shown below.

You need Twitter API credentials:

1. Apply for Twitter API access at [developer.twitter.com](https://developer.twitter.com)
2. Create a new app and generate:
   - Bearer Token
   - API Key and Secret
   - Access Token and Secret

### 2. Install Dependencies

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Edit `.env` and add your Twitter API credentials (and optionally MongoDB):
```env
# Twitter
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# MongoDB (optional but recommended for collaborative de-duplication)
# Example (MongoDB Atlas): mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority
MONGODB_URI=your_mongodb_connection_uri_here
```

## Usage

If MongoDB is configured (MONGODB_URI set), URLs from flagged tweets will be stored de-duplicated in the database. If not, the bot still runs and outputs a local report.

### Basic Usage

Run full analysis (accounts + keywords):
```bash
python main.py
```

### Command Line Options

- `--accounts-only`: Only search AfD accounts (skip keyword search)
- `--keywords-only`: Only search by keywords (skip account search)
- `--output-dir PATH`: Directory to save reports (default: ./reports)
- `--verbose`: Enable verbose logging
- `--dry-run`: Perform analysis without generating report

MongoDB is automatically detected from MONGODB_URI. No extra flags needed.

- `--accounts-only`: Only search AfD accounts (skip keyword search)
- `--keywords-only`: Only search by keywords (skip account search)  
- `--output-dir PATH`: Directory to save reports (default: ./reports)
- `--verbose`: Enable verbose logging
- `--dry-run`: Perform analysis without generating report

### Examples

```bash
# Full analysis with verbose logging
python main.py --verbose

# Only search AfD accounts
python main.py --accounts-only

# Only search by keywords
python main.py --keywords-only

# Dry run to test without generating report
python main.py --dry-run

# Save reports to custom directory
python main.py --output-dir /path/to/reports
```

## Output

The bot generates comprehensive text reports including:

- **Executive Summary**: Overview of findings and statistics
- **Detailed Findings**: Individual tweets with analysis and URLs
- **Statistical Analysis**: Collection metrics and patterns
- **Methodology**: Explanation of analysis methods
- **Legal Context**: Relevant constitutional law information

Reports are saved as timestamped text files in the `reports/` directory.

## Configuration

Key configuration files:

- `config.py`: AfD accounts list and constitutional keywords
- `requirements.txt`: Python dependencies
- `.env`: Twitter API credentials (create from template)

### Monitored Accounts

The bot monitors these official AfD accounts:

**Federal Level:**
- @AfD (main party account)
- @Alice_Weidel (party leader)
- @Tino_Chrupalla (party leader)
- @AfDimBundestag (parliamentary group)

**State Level:**
All 16 German states' official AfD accounts

### Analysis Keywords

Keywords are based on constitutional concerns from Article 21(2) GG:
- Threats to democratic basic order
- Anti-constitutional rhetoric
- Historical revisionism
- Violence promotion
- Hate speech patterns

## Technical Details

### De-duplication and Collaboration

- When MongoDB is configured, every URL found in flagged tweets is extracted and stored once in the shared database.
- A unique index on the URL ensures the same link is never stored twice, even across machines/users.
- This lets multiple users run the bot and contribute to a common evidence set without duplicates.
- MongoDB is optional; the bot still runs and generates local reports without it.

### Architecture

- `twitter_client.py`: Twitter API interface with rate limiting
- `content_analyzer.py`: Keyword matching and severity scoring
- `tweet_collector.py`: Orchestrates data collection from accounts/keywords
- `report_generator.py`: Formats findings into structured reports
- `main.py`: Command-line interface and execution logic
- `config.py`: Configuration data (accounts, keywords, settings)

### Rate Limiting

The bot includes comprehensive rate limiting to comply with Twitter's API terms:
- Automatic retry with exponential backoff
- Configurable delays between requests
- Respects API quotas and limits

### Ethical Considerations

- Only analyzes publicly available content
- Transparent methodology and limitations
- Clear disclaimers about automated analysis
- Respects platform terms of service
- Focuses on constitutional law compliance

## Logging

Logs are saved to the `logs/` directory with timestamps. Use `--verbose` for detailed debugging information.

## Troubleshooting

### Common Issues

1. **"Missing Twitter API credentials"**
   - Ensure your `.env` file exists and contains valid credentials
   - Check that all required environment variables are set

2. **Rate limit errors**
   - The bot handles rate limits automatically
   - Consider reducing search parameters if issues persist

3. **No tweets found**
   - Check that the monitored accounts are still active
   - Verify your API access permissions

### Support

This is a research tool. For technical issues:
1. Check the logs in the `logs/` directory
2. Verify your Twitter API credentials and permissions
3. Ensure all dependencies are installed correctly

## Legal Framework

Based on Article 21(2) of the German Basic Law (Grundgesetz):

> "Parties that, by reason of their aims or the behavior of their members, seek to undermine or abolish the free democratic basic order or to endanger the existence of the Federal Republic of Germany shall be unconstitutional."

The analysis focuses on identifying content that may indicate:
1. Active opposition to democratic principles
2. Plans to undermine constitutional order
3. Sufficient weight to pose a real threat to democracy

## Disclaimer

This tool is provided for research and educational purposes. Users are responsible for:
- Compliance with applicable laws and regulations
- Proper interpretation of automated analysis results
- Verification of findings through appropriate legal channels
- Respecting privacy and data protection requirements

The automated analysis may contain false positives and should not be used as the sole basis for any legal or political decisions.