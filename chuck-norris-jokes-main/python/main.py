import requests
from fastapi import FastAPI
from auth import Auth
from joke import Joke

app = FastAPI()

@app.get("/joke")
async def root():
    response = requests.get("https://api.chucknorris.io/jokes/random").json()
    return Joke.from_dict(response)

app.add_middleware(Auth)
