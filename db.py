import os
import logging
import re
from datetime import datetime
from typing import Dict, Optional

from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()

URL_REGEX = re.compile(r"https?://\S+", re.IGNORECASE)

class LinkStore:
    """
    MongoDB-backed store for tweet/source links with de-duplication.
    Each link is stored once with metadata; subsequent inserts are no-ops.
    """

    def __init__(self, mongo_uri: Optional[str] = None, db_name: str = "afdver_bot", collection: str = "links"):
        self.logger = logging.getLogger(__name__)
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI")
        if not self.mongo_uri:
            raise ValueError("Missing MongoDB connection string. Set MONGODB_URI in .env")

        self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
        try:
            # Trigger server selection to validate connection
            self.client.admin.command("ping")
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise

        self.db = self.client[db_name]
        self.col = self.db[collection]

        # Ensure unique index on url
        try:
            self.col.create_index("url", unique=True)
        except Exception as e:
            self.logger.warning(f"Could not create unique index on url: {e}")

    def extract_urls(self, text: str) -> list:
        if not text:
            return []
        return [u.rstrip('.,);]"\'') for u in URL_REGEX.findall(text)]

    def upsert_link(self, url: str, metadata: Dict) -> bool:
        """
        Insert link if not present. Returns True if inserted, False if already existed.
        """
        try:
            now = datetime.utcnow()
            result = self.col.update_one(
                {"url": url},
                {"$setOnInsert": {"url": url, "created_at": now},
                 "$set": {**metadata, "updated_at": now}},
                upsert=True,
            )
            # If upserted_id exists, it was newly inserted
            inserted = result.upserted_id is not None
            if inserted:
                self.logger.info(f"Inserted new link: {url}")
            else:
                self.logger.debug(f"Link already exists or updated: {url}")
            return inserted
        except errors.DuplicateKeyError:
            return False
        except Exception as e:
            self.logger.error(f"Failed to upsert link {url}: {e}")
            return False

    def store_from_tweet_analysis(self, tweet_analysis: Dict) -> int:
        """
        Extract all URLs from the tweet text and store them with metadata.
        Returns the number of new links inserted.
        """
        text = tweet_analysis.get("text", "")
        urls = self.extract_urls(text)
        count = 0
        for url in set(urls):
            metadata = {
                "tweet_id": tweet_analysis.get("tweet_id"),
                "author_id": tweet_analysis.get("author_id"),
                "created_at": tweet_analysis.get("created_at"),
                "severity_score": tweet_analysis.get("severity_score"),
                "categories": tweet_analysis.get("categories", []),
                "matched_keywords": tweet_analysis.get("matched_keywords", []),
                "source_account": tweet_analysis.get("source_account"),
                "collection_method": tweet_analysis.get("collection_method"),
            }
            if self.upsert_link(url, metadata):
                count += 1
        return count
