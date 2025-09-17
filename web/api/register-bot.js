import { MongoClient } from "mongodb";
import crypto from "crypto";

let client;

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

export default async function handler(req, res) {
  try {
    if (req.method !== "POST") {
      return res.status(405).json({ error: "Method not allowed" });
    }

    // Simple admin authentication
    const adminSecret = process.env.ADMIN_SECRET;
    const auth = req.headers["authorization"] || "";
    
    if (!adminSecret || !auth.startsWith("Bearer ") || auth.slice(7) !== adminSecret) {
      return res.status(401).json({ error: "Admin access required" });
    }

    const { botName, description, owner } = req.body || {};
    
    if (!botName || !owner) {
      return res.status(400).json({ error: "Missing required fields: botName, owner" });
    }

    // Generate unique bot ID and token
    const botId = botName.toLowerCase().replace(/[^a-z0-9]/g, '');
    const tokenSuffix = crypto.randomBytes(16).toString('hex');
    const fullToken = `${botId}.${tokenSuffix}`;
    
    const dbName = process.env.MONGODB_DB || "afdver_bot";
    const mongo = await getClient();
    const db = mongo.db(dbName);
    const botsCol = db.collection('registered_bots');
    
    // Check if bot already exists
    const existingBot = await botsCol.findOne({ botId });
    if (existingBot) {
      return res.status(409).json({ error: "Bot with this name already exists" });
    }
    
    // Create bot record
    const botRecord = {
      botId,
      botName,
      description: description || '',
      owner,
      token: fullToken,
      createdAt: new Date(),
      lastSeen: null,
      isActive: true,
      totalSubmissions: 0,
      lastSubmission: null
    };
    
    await botsCol.insertOne(botRecord);
    
    // Update valid tokens in environment-like storage
    // Note: In production, you'd want a more robust token management system
    const validTokens = process.env.VALID_TOKENS ? process.env.VALID_TOKENS.split(',') : [];
    validTokens.push(fullToken);
    
    // For now, we'll just return the token - in production you'd update your deployment
    
    return res.status(201).json({
      success: true,
      botId,
      token: fullToken,
      message: "Bot registered successfully. Add this token to VALID_TOKENS environment variable."
    });
    
  } catch (e) {
    console.error("/api/register-bot error", e);
    return res.status(500).json({ 
      error: "Server error",
      message: process.env.NODE_ENV === 'development' ? e.message : 'Internal server error'
    });
  }
}