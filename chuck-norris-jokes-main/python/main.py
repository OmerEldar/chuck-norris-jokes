import requests
from fastapi import FastAPI
from auth import Auth
from joke import Joke
from redis_connection import RedisConnection
from rate_limiter import RateLimiter

# Create Redis connection at startup
redis_connection = RedisConnection()
rate_limiter = RateLimiter(redis_connection)

app = FastAPI()

@app.get("/joke")
async def root():
    response = requests.get("https://api.chucknorris.io/jokes/random").json()
    return Joke.from_dict(response)

app.add_middleware(Auth)
