"""
Cloudflare Worker - API Proxy для RoadMate.

Этот worker проксирует запросы к backend API, обслуживает статику с Cloudflare Pages,
и добавляет необходимые заголовки для CORS.
"""
from typing import Tuple

API_BASE_URL = "https://api.roadmate.digital"
FRONTEND_ORIGINS = [
    "https://roadmate.digital",
    "https://www.roadmate.digital",
]

async def on_fetch(request: Request, env: dict, ctx: ExecutionContext) -> Response:
    """Обработка входящих запросов."""
    url = request.url
    
    if url.path.startswith("/api/"):
        return await proxy_to_api(request, env, ctx)
    
    if url.path.startswith("/ws/"):
        return await proxy_to_websocket(request, env, ctx)
    
    return await handle_frontend(request, env, ctx)

async def proxy_to_api(request: Request, env: dict, ctx: ExecutionContext) -> Response:
    """Проксирование API запросов."""
    api_url = f"{API_BASE_URL}{url.path}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("cf-connecting-ip", None)
    headers.pop("cf-ray", None)
    headers.pop("cf-request-id", None)
    
    try:
        response = await ctx.fetch(api_url, {
            "method": request.method,
            "headers": headers,
            "body": await request.text() if request.body else None,
        })
        
        return Response(
            response.body(),
            status=response.status,
            headers=response.headers,
        )
    except Exception as e:
        return Response(
            f"API Error: {str(e)}",
            status=502,
            headers={"Content-Type": "text/plain"},
        )

async def proxy_to_websocket(request: Request, env: dict, ctx: ExecutionContext) -> Response:
    """WebSocket требует специальной обработки."""
    return Response(
        "WebSocket not supported in Worker. Use direct backend connection.",
        status=426,
        headers={"Content-Type": "text/plain"},
    )

async def handle_frontend(request: Request, env: dict, ctx: ExecutionContext) -> Response:
    """Обслуживание статики или SPA."""
    return ctx.wait_until(fetch("https://roadmate.pages.dev" + url.path))

def add_cors_headers(request: Request) -> dict:
    """Добавление CORS заголовков."""
    origin = request.headers.get("origin", "")
    headers = {
        "Access-Control-Allow-Origin": origin if origin in FRONTEND_ORIGINS else FRONTEND_ORIGINS[0],
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Credentials": "true",
    }
    return headers