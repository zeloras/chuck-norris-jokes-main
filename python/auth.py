import json
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

from rate_limit.plans import Plan

ACCOUNTS_FILE = '../accounts.json'

class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        auth_token = request.headers.get('authorization')

        with open(ACCOUNTS_FILE) as f:
            accounts = json.load(f)

        if auth_token not in accounts:
            return JSONResponse(status_code=403, content={'error': 'Invalid request!'})
        else:
            plan_name = accounts[auth_token].get('plan', None)
            request.state.plan = Plan.get_plan(plan_name)
            return await call_next(request)
