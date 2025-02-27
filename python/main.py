import requests
import os
from fastapi import FastAPI, Request
from redis import asyncio as aioredis

from auth import Auth
from joke import Joke
from rate_limit.limits import RateLimiter

app = FastAPI()
redis_client = aioredis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    db=int(os.getenv('REDIS_DB', '0'))
)

@app.get("/joke")
async def root(request: Request):
    response = requests.get("https://api.chucknorris.io/jokes/random").json()
    return Joke.from_dict(response)

# Add middleware - order is important
app.add_middleware(RateLimiter, redis_client=redis_client)
app.add_middleware(Auth)
