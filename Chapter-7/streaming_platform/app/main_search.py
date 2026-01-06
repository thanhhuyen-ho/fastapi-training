import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from app.db_connection import es_client, redis_client
from app.es_queries import top_ten_artists_query

from elasticsearch import BadRequestError

router = APIRouter(prefix="/search", tags=["search"])

logger = logging.getLogger("uvicorn")

def get_elasticsearch_client():
    return es_client

def get_redis_client():
    return redis_client

@router.get("/top/ten/artists/{country}")
async def top_ten_artists_by_country(
    country: str, 
    es_client=Depends(get_elasticsearch_client),
    redis_client=Depends(get_redis_client),
):
    cache_key = f"top_ten_artists_{country}"
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        logger.info(
            f"Returning cached data for {country}"
        )
        return json.loads(cached_data)

    try:
        response = await es_client.search(
            **top_ten_artists_query(country)
        )
    except BadRequestError as e:
        logger.error(e)
        raise HTTPException(
            status_code=400, 
            detail="Invalid country"
        )
    artists = [
        {
            "artist": record.get("key"),
            "views": record.get("views",{}).get("value"),
        }
        for record in response["aggregations"]["top_ten_artists"]["buckets"]
    ]
    
    await redis_client.set(
        cache_key, 
        json.dumps(artists), 
        ex=3600
    )
        
    return artists