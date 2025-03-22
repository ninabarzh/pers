# backend/src/app/routes/search.py
from starlette.responses import JSONResponse
from starlette.requests import Request
from ..typesense_client import TypesenseClient

typesense_client = TypesenseClient()

async def search(request: Request):
    query = request.query_params.get("q", "")
    results = typesense_client.search(query)
    return JSONResponse(results)
