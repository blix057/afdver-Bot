import { MongoClient } from "mongodb";

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
    if (req.method !== "GET") {
      return res.status(405).json({ error: "Method not allowed" });
    }

    const dbName = process.env.MONGODB_DB || "afdver_bot";
    const colName = process.env.MONGODB_COLLECTION || "links";

    const mongo = await getClient();
    const db = mongo.db(dbName);
    const col = db.collection(colName);

    // Get current date boundaries
    const today = new Date();
    const startOfToday = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    
    // Aggregate statistics
    const [stats] = await col.aggregate([
      {
        $group: {
          _id: null,
          totalLinks: { $sum: 1 },
          avgSeverity: { $avg: "$severity_score" },
          todayLinks: {
            $sum: {
              $cond: [
                { $gte: ["$created_at", startOfToday] },
                1,
                0
              ]
            }
          },
          uniqueBots: { $addToSet: "$bot_id" },
          uniqueSeenByBots: { $addToSet: "$seen_by_bots" }
        }
      }
    ]).toArray();

    if (!stats) {
      return res.status(200).json({
        totalLinks: 0,
        activeBots: 0,
        avgSeverity: 0,
        todayLinks: 0
      });
    }

    // Count unique bots from both fields
    const allBots = new Set();
    if (stats.uniqueBots) {
      stats.uniqueBots.forEach(botId => {
        if (botId) allBots.add(botId);
      });
    }
    if (stats.uniqueSeenByBots) {
      stats.uniqueSeenByBots.forEach(botArray => {
        if (Array.isArray(botArray)) {
          botArray.forEach(botId => {
            if (botId) allBots.add(botId);
          });
        }
      });
    }

    return res.status(200).json({
      totalLinks: stats.totalLinks || 0,
      activeBots: allBots.size || 0,
      avgSeverity: stats.avgSeverity || 0,
      todayLinks: stats.todayLinks || 0
    });

  } catch (e) {
    console.error("/api/stats error", e);
    return res.status(500).json({ 
      error: "Server error",
      message: process.env.NODE_ENV === 'development' ? e.message : 'Internal server error'
    });
  }
}