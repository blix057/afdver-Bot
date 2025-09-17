# 🤖 AfD Twitter Bot - Centralized Setup Guide

This guide explains how to deploy and configure the centralized AfD Twitter Bot system, where multiple bot instances upload their collected data to a shared Vercel-hosted backend with MongoDB storage.

## Architecture Overview

```
┌─────────────────┐    HTTP POST    ┌──────────────────┐
│   Bot Instance  ├────────────────►│  Vercel Backend  │
│   (User 1)      │                 │                  │
└─────────────────┘                 │  - Ingest API    │
                                    │  - Dashboard     │    ┌─────────────┐
┌─────────────────┐    HTTP POST    │  - Admin Panel   ├────┤  MongoDB    │
│   Bot Instance  ├────────────────►│                  │    │  Atlas      │
│   (User 2)      │                 │  Rate Limiting   │    └─────────────┘
└─────────────────┘                 │  Deduplication   │
                                    └──────────────────┘
┌─────────────────┐    HTTP POST    
│   Bot Instance  ├────────────────►│
│   (User 3)      │                 
└─────────────────┘                 
```

**Benefits:**
- ✅ No direct MongoDB access required for bot operators
- ✅ Centralized data collection and deduplication  
- ✅ Network connectivity issues solved
- ✅ Easy bot registration and management
- ✅ Shared web dashboard for all collected data

## 📋 Prerequisites

- **MongoDB Atlas Account** (free tier works)
- **Vercel Account** (free tier works)
- **Twitter Developer Account** (for bot operators)

---

## 🚀 Step 1: MongoDB Atlas Setup

### 1.1 Create MongoDB Cluster
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create account and new cluster (free tier M0)
3. Create database user with read/write permissions
4. Set Network Access to "Allow access from anywhere" (0.0.0.0/0)
5. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`

### 1.2 Database Structure
The system will automatically create these collections:
- `links` - Collected URLs with metadata
- `registered_bots` - Bot registration and tracking

---

## 🌐 Step 2: Vercel Deployment

### 2.1 Deploy the Application
```bash
cd /Users/paul/Files/vsc_projekte/twitter_bot/web
vercel --prod
```

### 2.2 Configure Environment Variables
In Vercel dashboard, add these environment variables:

```env
# MongoDB Connection
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=afdver_bot
MONGODB_COLLECTION=links

# Admin Access
ADMIN_SECRET=your_super_secret_admin_token_here

# Bot Authentication (initially empty, will be populated)
VALID_TOKENS=
```

### 2.3 Test Deployment
- Visit: `https://your-app.vercel.app/` - Dashboard
- Visit: `https://your-app.vercel.app/admin.html` - Admin Panel

---

## 🔧 Step 3: Bot Registration System

### 3.1 Register First Bot
1. Go to `https://your-app.vercel.app/admin.html`
2. Login with your `ADMIN_SECRET`
3. Register a new bot:
   - **Bot Name**: `PaulBot`
   - **Owner**: `paul@example.com`
   - **Description**: `Paul's development instance`

### 3.2 Update Valid Tokens
Copy the generated token and update Vercel environment variable:
```env
VALID_TOKENS=paulbot.a1b2c3d4e5f6...
```

For multiple bots, use comma-separated tokens:
```env
VALID_TOKENS=paulbot.abc123,unibot.def456,testbot.ghi789
```

---

## 💻 Step 4: Bot Configuration

### 4.1 Update Bot Environment
Each bot operator needs to update their `.env` file:

```env
# Twitter API Credentials (unchanged)
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# Centralized HTTP Ingest (NEW - REQUIRED)
INGEST_URL=https://your-vercel-app.vercel.app/api/ingest
INGEST_TOKEN=your_registered_bot_token_here
```

### 4.2 Remove MongoDB Dependencies
Bot operators no longer need:
- ❌ `MONGODB_URI`
- ❌ `MONGODB_DB` 
- ❌ `MONGODB_COLLECTION`
- ❌ Local MongoDB setup
- ❌ Network troubleshooting

### 4.3 Test Bot Connection
```bash
python main.py --dry-run --verbose
```

Look for log messages like:
```
INFO - HTTP ingest configured for https://your-app.vercel.app/api/ingest
INFO - Stored 3 new links from @afd_account
```

---

## 📊 Step 5: Dashboard Access

### 5.1 Public Dashboard
- **URL**: `https://your-app.vercel.app/`
- **Features**: View all collected links, statistics, filtering
- **Access**: Public (no authentication required)

### 5.2 Admin Panel  
- **URL**: `https://your-app.vercel.app/admin.html`
- **Features**: Register bots, manage tokens
- **Access**: Admin authentication required

---

## 🔒 Security Considerations

### 5.1 Token Management
- Each bot gets a unique token
- Tokens include bot ID prefix for tracking
- Rate limiting: 100 requests/hour per bot
- Invalid tokens are rejected

### 5.2 Admin Access
- Admin panel protected by `ADMIN_SECRET`
- Only admins can register new bots
- Bot tokens must be manually added to `VALID_TOKENS`

### 5.3 Data Protection
- MongoDB uses authentication
- HTTPS for all API endpoints
- No sensitive data in bot logs

---

## 🛠️ Maintenance

### Adding New Bots
1. Admin registers bot via `/admin.html`
2. Admin adds token to Vercel `VALID_TOKENS` 
3. Bot operator configures `.env` with token
4. Bot starts uploading data automatically

### Monitoring
- Dashboard shows active bot count
- Statistics updated every 5 minutes
- Check Vercel function logs for errors

### Troubleshooting
- **Bot can't connect**: Check `INGEST_URL` and `INGEST_TOKEN`
- **401 Unauthorized**: Token not in `VALID_TOKENS` or invalid
- **429 Rate limited**: Bot making too many requests
- **500 Server error**: Check Vercel logs, MongoDB connection

---

## 📈 Scaling

The system can handle:
- **Unlimited bots** (with proper rate limiting)
- **High throughput** (Vercel serverless functions auto-scale)
- **Large datasets** (MongoDB Atlas scales with usage)

For high-volume scenarios, consider:
- Increase rate limits in `ingest.js`
- Use MongoDB connection pooling
- Add Redis for caching statistics
- Implement batch upload endpoints

---

## 🎯 Migration from Direct MongoDB

For existing bot operators using direct MongoDB:

### Old Setup (Remove):
```env
MONGODB_URI=mongodb+srv://...
MONGODB_DB=afdver_bot
MONGODB_COLLECTION=links
```

### New Setup (Add):
```env
INGEST_URL=https://your-vercel-app.vercel.app/api/ingest
INGEST_TOKEN=your_registered_bot_token
```

The bot code automatically detects the HTTP configuration and stops trying MongoDB connections.

---

## 📞 Support

For issues:
1. Check bot logs with `--verbose` flag
2. Verify token in Vercel `VALID_TOKENS`
3. Test endpoint: `curl -H "Authorization: Bearer TOKEN" https://your-app.vercel.app/api/ingest`
4. Check Vercel function logs

---

## ✅ Quick Verification Checklist

- [ ] MongoDB Atlas cluster created and accessible
- [ ] Vercel app deployed with environment variables
- [ ] Admin panel accessible with `ADMIN_SECRET`
- [ ] First bot registered and token added to `VALID_TOKENS`
- [ ] Bot configured with `INGEST_URL` and `INGEST_TOKEN`
- [ ] Test run successful with `--dry-run --verbose`
- [ ] Dashboard shows collected links and statistics
- [ ] Multiple bots can upload simultaneously

🎉 **System Ready!** All bots now upload to your centralized collection system.