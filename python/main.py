import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis import Redis

from auth import Auth
from joke import Joke
from rate_limit.limits import RateLimiter

app = FastAPI()
redis_client = Redis(host='redis', port=6379, db=0)
rate_limiter = RateLimiter(redis_client)

@app.get("/joke")
async def root(request: Request):
    auth_token = request.headers.get('authorization')
    if not rate_limiter.is_allowed(auth_token, request.state.plan):
        return JSONResponse(status_code=429, content={'error': 'Rate limit exceeded'})

    response = requests.get("https://api.chucknorris.io/jokes/random").json()
    Joke.from_dict(response)
    return Joke.from_dict(response)

app.add_middleware(Auth)
