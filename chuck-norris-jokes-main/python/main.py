import requests
from fastapi import FastAPI
from auth import Auth
from joke import Joke
from helpers.cached_accounts_file_helper import CachedAccountsFileHelper

app = FastAPI()
# Create single instance
file_helper = CachedAccountsFileHelper(refresh_interval=300)  # 5 minutes

@app.get("/joke")
async def root():
    response = requests.get("https://api.chucknorris.io/jokes/random").json()
    return Joke.from_dict(response)

# Add middleware with dependencies
app.add_middleware(
    Auth,
    accounts_path="./accounts.json",
    file_helper=file_helper
)