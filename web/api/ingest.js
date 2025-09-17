import { MongoClient } from "mongodb";

let client;
const rateLimitMap = new Map(); // Simple in-memory rate limiting

async function getClient() {
  if (!process.env.MONGODB_URI) {
    throw new Error("MONGODB_URI not set");
  }
  if (!client) {
    client = new MongoClient(process.env.MONGODB_URI);
    await client.connect();
  }
  return client;
}

function checkRateLimit(botId, maxRequests = 100, windowMs = 3600000) {
  // 100 requests per hour per bot by default
  const now = Date.now();
  const windowStart = now - windowMs;
  
  if (!rateLimitMap.has(botId)) {
    rateLimitMap.set(botId, []);
  }
  
  const requests = rateLimitMap.get(botId);
  // Remove old requests outside the window
  const validRequests = requests.filter(time => time > windowStart);
  
  if (validRequests.length >= maxRequests) {
    return false; // Rate limited
  }
  
  // Add current request
  validRequests.push(now);
  rateLimitMap.set(botId, validRequests);
  return true;
}

const URL_REGEX = /https?:\/\/\S+/gi;

export default async function handler(req, res) {
  try {
    if (req.method !== "POST") {
      return res.status(405).json({ error: "Method not allowed" });
    }

    // Extract bot ID from auth token or use IP as fallback
    const auth = req.headers["authorization"] || "";
    if (!auth.startsWith("Bearer ")) {
      return res.status(401).json({ error: "Bearer token required" });
    }
    
    const token = auth.slice(7);
    const botId = token.split('.')[0] || req.ip || 'anonymous'; // Use first part of token as bot ID
    
    // Rate limiting
    if (!checkRateLimit(botId)) {
      return res.status(429).json({ error: "Rate limit exceeded" });
    }

    // Validate token (simple check - in production you'd want proper JWT or database lookup)
    const validTokens = (process.env.VALID_TOKENS || '').split(',').filter(t => t.trim());
    if (!validTokens.includes(token)) {
      return res.status(401).json({ error: "Invalid token" });
    }

    const body = req.body || {};
    
    // Validate required fields
    if (!body.tweet_text || !body.tweet_id) {
      return res.status(400).json({ error: "Missing required fields: tweet_text, tweet_id" });
    }

    const tweetText = body.tweet_text;
    const urls = (tweetText.match(URL_REGEX) || []).map((u) => u.replace(/[.,);\]"']+$/g, ""));
    
    if (!urls.length) {
      return res.status(200).json({ 
        success: true,
        inserted: 0, 
        message: "No URLs found in tweet" 
      });
    }

    const dbName = process.env.MONGODB_DB || "afdver_bot";
    const colName = process.env.MONGODB_COLLECTION || "links";

    const mongo = await getClient();
    const db = mongo.db(dbName);
    const col = db.collection(colName);

    // Ensure indexes
    try { 
      await col.createIndex({ url: 1 }, { unique: true });
      await col.createIndex({ tweet_id: 1 });
      await col.createIndex({ created_at: -1 });
      await col.createIndex({ severity_score: -1 });
    } catch (e) {
      console.warn('Index creation warning:', e.message);
    }

    let inserted = 0;
    let updated = 0;
    const now = new Date();

    // Process each unique URL
    for (const url of Array.from(new Set(urls))) {
      const metadata = {
        tweet_id: body.tweet_id,
        author_id: body.author_id,
        created_at: body.created_at ? new Date(body.created_at) : null,
        severity_score: body.severity_score || 0,
        categories: body.categories || [],
        matched_keywords: body.matched_keywords || [],
        source_account: body.source_account,
        collection_method: body.collection_method || 'api_upload',
        tweet_text: tweetText,
        bot_id: botId,
        updated_at: now,
      };

      const result = await col.updateOne(
        { url },
        { 
          $setOnInsert: { 
            url, 
            created_at: now,
            first_seen_bot: botId
          }, 
          $set: metadata,
          $addToSet: {
            seen_by_bots: botId
          }
        },
        { upsert: true }
      );
      
      if (result.upsertedId) {
        inserted += 1;
      } else if (result.modifiedCount > 0) {
        updated += 1;
      }
    }

    return res.status(200).json({ 
      success: true,
      inserted, 
      updated,
      processed_urls: urls.length,
      bot_id: botId
    });
    
  } catch (e) {
    console.error("/api/ingest error", e);
    return res.status(500).json({ 
      error: "Server error",
      message: process.env.NODE_ENV === 'development' ? e.message : 'Internal server error'
    });
  }
}
