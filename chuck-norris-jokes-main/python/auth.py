import json
import re
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from rate_limiter import RateLimiter
from fastapi import Request
from helpers.cached_accounts_file_helper import CachedAccountsFileHelper

rate_limiter = RateLimiter()

class Auth(BaseHTTPMiddleware):
    TOKEN_PATTERN = re.compile(r'^[\d-]+$')  # Only numbers and hyphens

    def __init__(self, app, accounts_path: str, file_helper: CachedAccountsFileHelper):
        super().__init__(app)
        self.accounts = file_helper.read_json_file(accounts_path)

    def _validate_token(self, token: str) -> bool:
        """Validate token format"""
        if not token or not isinstance(token, str):
            return False
        return bool(self.TOKEN_PATTERN.match(token))

    async def dispatch(self, request, call_next):
        auth_token = request.headers.get('authorization')
        
        if not self._validate_token(auth_token):
            return JSONResponse(status_code=403, content={'error': 'Invalid token format!'})
            
        if auth_token not in self.accounts:
            return JSONResponse(status_code=403, content={'error': 'Invalid token!'})
            
        account = self.accounts[auth_token]
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