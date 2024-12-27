import json
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from rate_limiter import RateLimiter

file = open('../accounts.json')
accounts = json.load(file)
rate_limiter = RateLimiter()

class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        auth_token = request.headers.get('authorization')
        
        if auth_token not in accounts:
            return JSONResponse(status_code=403, content={'error': 'Invalid token!'})
            
        account = accounts[auth_token]
        # Check rate limits
        if not rate_limiter.is_allowed(
            auth_token,
            account['rate_limit'],
            account.get('daily_limit')
        ):
            return JSONResponse(
                status_code=429,
                content={'error': 'Rate limit exceeded!'}
            )
            
        request.account = account
        return await call_next(request)