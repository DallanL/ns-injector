import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(docs_url=None, redoc_url=None) # Disable swagger, unnecessary attack surface
templates = Jinja2Templates(directory="templates")

CONFIG_FILE = os.getenv("CONFIG_FILE", "/app/config/endpoints.json")

# In-memory cache for the config to avoid disk reads on every request
_config_cache = {}
_last_mtime = 0

def get_config() -> dict:
    global _config_cache, _last_mtime
    try:
        current_mtime = os.path.getmtime(CONFIG_FILE)
        if current_mtime > _last_mtime:
            with open(CONFIG_FILE, 'r') as f:
                _config_cache = json.load(f)
            _last_mtime = current_mtime
            logger.info("Configuration reloaded from disk.")
    except FileNotFoundError:
        logger.error(f"Config file {CONFIG_FILE} not found.")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {CONFIG_FILE}. Using last known good config.")
    
    return _config_cache

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/{role}")
async def serve_injector(request: Request, role: str):
    config = get_config()
    logging.info(f"Role endpoint triggered: {role}")
    
    # Resolve the requested role or fallback to 'default'
    scripts = config.get(role)
    if not scripts:
        scripts = config.get("default")
        
    if not scripts:
        raise HTTPException(status_code=404, detail="Endpoint not configured and no default found.")

    # Render template
    response = templates.TemplateResponse(
        "injector.js",
        {"request": request, "scripts": scripts},
        media_type="application/javascript"
    )
    
    # Crucial: Prevent the browser from caching the loader itself.
    # We want dynamic changes to reflect immediately on the next page load.
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
