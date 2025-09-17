# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is the **AfD Twitter Monitoring Bot**, a Python application that monitors German political party (AfD) social media content for constitutional concerns based on Article 21(2) of the German Basic Law. The system collects tweets from official accounts and keyword searches, analyzes them for problematic content, and generates detailed reports.

## Architecture

### Core Components

- **`main.py`**: CLI orchestration and main entry point
- **`twitter_client.py`**: Twitter API v2 client with rate limiting and authentication
- **`tweet_collector.py`**: Data collection from accounts and keyword searches
- **`content_analyzer.py`**: Content analysis, keyword matching, and severity scoring
- **`report_generator.py`**: Text report generation with detailed analysis
- **`config.py`**: Configuration for accounts, keywords, and search parameters
- **`db.py`**: MongoDB integration for link storage and deduplication

### Web Components (`web/` directory)

- **`web/index.html`**: Dashboard for viewing collected links
- **`web/admin.html`**: Admin panel for bot registration
- **`web/api/`**: Serverless functions for Vercel deployment
- **`web/package.json`**: Node.js dependencies (primarily MongoDB driver)

### Data Flow

1. **Collection**: Gathers tweets from AfD accounts and keyword searches
2. **Analysis**: Applies constitutional keyword matching and severity scoring
3. **Storage**: Optionally stores extracted links in MongoDB (local or HTTP ingest)
4. **Reporting**: Generates comprehensive text reports with statistics

### Configuration Architecture

- **Environment Variables**: API credentials and database URIs in `.env`
- **Static Configuration**: Account lists and keywords in `config.py`
- **Two Storage Modes**: Direct MongoDB or centralized HTTP ingest

## Common Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.template .env
# Edit .env with your Twitter API credentials
```

### Testing and Validation
```bash
# Validate setup without API calls
python test_setup.py

# Dry run (analysis without report generation)
python main.py --dry-run

# Verbose dry run for debugging
python main.py --dry-run --verbose
```

### Running the Bot
```bash
# Full analysis (accounts + keywords)
python main.py

# Only search AfD accounts
python main.py --accounts-only

# Only search by keywords
python main.py --keywords-only

# Watch mode (continuous collection)
python main.py --watch

# Custom output directory
python main.py --output-dir /custom/path/reports
```

### Web Deployment (Vercel)
```bash
# Deploy web interface
cd web/
vercel --prod

# Local development
cd web/
vercel dev
```

## Key Configuration Files

### Environment Variables (`.env`)
Required Twitter API credentials:
- `TWITTER_BEARER_TOKEN`
- `TWITTER_API_KEY` 
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`

Optional storage configuration:
- `MONGODB_URI` (for direct MongoDB access)
- `INGEST_URL` + `INGEST_TOKEN` (for centralized HTTP ingest)

### Bot Configuration (`config.py`)
- `AFD_ACCOUNTS`: List of monitored Twitter usernames
- `CONSTITUTIONAL_KEYWORDS`: Keywords for constitutional concern detection
- `CONTENT_CATEGORIES`: Categorization system for flagged content
- `SEARCH_SETTINGS`: API limits, time ranges, and polling intervals

## Storage Modes

The system supports two storage architectures:

### Direct MongoDB Mode
- Bot connects directly to MongoDB Atlas or local instance
- Configure `MONGODB_URI` in `.env`
- Individual bot operators manage their own database

### Centralized HTTP Ingest Mode  
- Multiple bots upload to shared Vercel backend
- Configure `INGEST_URL` + `INGEST_TOKEN` in `.env`
- Centralized data collection with bot registration system
- See `CENTRALIZED_SETUP.md` for deployment details

## Important Implementation Details

### Rate Limiting
- Twitter API v2 with `wait_on_rate_limit=True`
- Configurable delays between account searches
- Automatic 15-minute waits on rate limit errors

### Content Analysis Pipeline
1. **Keyword Matching**: Case-insensitive with word boundaries
2. **Categorization**: Maps keywords to constitutional concern categories
3. **Severity Scoring**: 0-10 scale based on keyword count and category weights
4. **Link Extraction**: URLs extracted from flagged tweets for storage

### Report Generation
- Comprehensive text reports with executive summaries
- Statistical analysis and severity distributions
- Legal context and methodology explanations
- Timestamped output in `reports/` directory

## Development Notes

### Dependencies
- **tweepy**: Twitter API v2 client
- **python-dotenv**: Environment variable management
- **pymongo**: MongoDB integration
- **requests**: HTTP client for ingest mode

### Testing Strategy
- `test_setup.py` validates configuration without API calls
- Mock tweet objects for testing content analysis
- Dry-run mode for safe testing with live API

### Logging
- Structured logging to `logs/` directory with timestamps
- Verbose mode for debugging API interactions
- Error handling with detailed stack traces

### Error Handling
- Graceful degradation when API limits reached
- Continues collection even if individual accounts fail
- Optional storage - bot works without database connectivity

## Deployment Considerations

### Local Development
- Use virtual environment for dependency isolation
- Start with `--dry-run` to test without generating reports
- Monitor `logs/` directory for detailed execution traces

### Production Deployment
- Set up MongoDB Atlas or local MongoDB instance
- Consider centralized HTTP ingest for multi-user scenarios
- Use `--watch` mode for continuous monitoring
- Implement proper secret management for API credentials

### Scaling Notes
- Rate limits are per Twitter developer account
- MongoDB can be shared across multiple bot instances
- Vercel serverless functions auto-scale for HTTP ingest mode
- Consider Redis caching for high-volume scenarios