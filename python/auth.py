import json
import os
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

from rate_limit.plans import Plan

ACCOUNTS_FILE = os.getenv('ACCOUNTS_FILE', '../accounts.json')

class Auth(BaseHTTPMiddleware):
    accounts = {}
    
    def __init__(self, app):
        super().__init__(app)
        self.refresh_accounts()
    
    def refresh_accounts(self):
        with open(ACCOUNTS_FILE) as f:
            Auth.accounts = json.load(f)
    
    async def dispatch(self, request, call_next):
        auth_token = request.headers.get('authorization')

        if auth_token not in Auth.accounts:
            return JSONResponse(status_code=403, content={'error': 'Invalid request!'})
        else:
            plan_name = Auth.accounts[auth_token].get('plan', None)
            request.state.plan = Plan.get_plan(plan_name)
            return await call_next(request)
