import { MongoClient } from "mongodb";

let client;

async function getClient() {
  if (!process.env.MONGODB_URI) {
    return null;
  }
  if (!client) {
    client = new MongoClient(process.env.MONGODB_URI);
    await client.connect();
  }
  return client;
}

export default async function handler(req, res) {
  try {
    const mongoClient = await getClient();
    if (!mongoClient) {
      return res.status(200).json({ links: [], note: "MONGODB_URI nicht gesetzt" });
    }

    const dbName = process.env.MONGODB_DB || "afdver_bot";
    const colName = process.env.MONGODB_COLLECTION || "links";
    const db = mongoClient.db(dbName);
    const col = db.collection(colName);

    // Find newest 500 links
    const cursor = col.find({}, { projection: { _id: 0 } }).sort({ updated_at: -1 }).limit(500);
    const data = await cursor.toArray();

    res.setHeader("Cache-Control", "s-maxage=60, stale-while-revalidate=300");
    return res.status(200).json({ links: data });
  } catch (e) {
    console.error("/api/links error", e);
    return res.status(500).json({ error: "Serverfehler" });
  }
}
