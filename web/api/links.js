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

    // Parse query parameters
    const {
      page = '1',
      limit = '50',
      search = '',
      severity = '',
      dateFrom = '',
      dateTo = ''
    } = req.query;

    const pageNum = Math.max(1, parseInt(page, 10) || 1);
    const limitNum = Math.min(100, Math.max(1, parseInt(limit, 10) || 50)); // Max 100 items per page
    const skip = (pageNum - 1) * limitNum;

    // Build query filter
    const filter = {};
    
    // URL search
    if (search.trim()) {
      filter.url = { $regex: search.trim(), $options: 'i' };
    }
    
    // Severity filter
    if (severity) {
      switch (severity) {
        case 'high':
          filter.severity_score = { $gte: 7 };
          break;
        case 'medium':
          filter.severity_score = { $gte: 4, $lt: 7 };
          break;
        case 'low':
          filter.severity_score = { $lt: 4 };
          break;
      }
    }
    
    // Date range filter
    if (dateFrom || dateTo) {
      filter.created_at = {};
      if (dateFrom) {
        filter.created_at.$gte = new Date(dateFrom + 'T00:00:00.000Z');
      }
      if (dateTo) {
        filter.created_at.$lte = new Date(dateTo + 'T23:59:59.999Z');
      }
    }

    // Get total count for pagination
    const totalCount = await col.countDocuments(filter);
    const totalPages = Math.ceil(totalCount / limitNum);
    
    // Simple check - if no pagination requested, use legacy format
    const isLegacyRequest = !req.query.page && !req.query.limit && totalCount <= 500;
    
    if (isLegacyRequest) {
      // Legacy behavior for existing simple requests
      const cursor = col.find(filter, { projection: { _id: 0 } })
        .sort({ updated_at: -1, created_at: -1 })
        .limit(500);
      const data = await cursor.toArray();
      
      res.setHeader("Cache-Control", "s-maxage=60, stale-while-revalidate=300");
      return res.status(200).json({ links: data });
    }

    // Enhanced paginated response
    const cursor = col.find(filter, { projection: { _id: 0 } })
      .sort({ updated_at: -1, created_at: -1 })
      .skip(skip)
      .limit(limitNum);
    
    const data = await cursor.toArray();

    res.setHeader("Cache-Control", "s-maxage=30, stale-while-revalidate=180");
    return res.status(200).json({
      success: true,
      links: data,
      pagination: {
        currentPage: pageNum,
        totalPages,
        totalItems: totalCount,
        itemsPerPage: limitNum,
        hasNext: pageNum < totalPages,
        hasPrev: pageNum > 1
      },
      filters: {
        search: search.trim(),
        severity,
        dateFrom,
        dateTo
      }
    });
    
  } catch (e) {
    console.error("/api/links error", e);
    return res.status(500).json({ 
      error: "Server error",
      message: process.env.NODE_ENV === 'development' ? e.message : 'Internal server error'
    });
  }
}
