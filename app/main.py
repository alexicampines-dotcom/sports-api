"""
Punto de entrada principal de la aplicación FastAPI.
API de Resultados Deportivos (Top 5 Deportes: Fútbol, MLB, UFC, NBA, NFL).
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION, ALLOWED_ORIGINS
from app.models.schemas import HealthResponse
from app.services.espn_service import espn_service
from app.routers import soccer, mlb, ufc, nba, nfl, summary

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sports_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando API Deportiva Global...")
    logger.info("📡 Cobertura: Fútbol (Top 5 Ligas), MLB, UFC, NBA y NFL.")
    yield
    logger.info("🛑 Deteniendo API Deportiva...")
    await espn_service.close()


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Configuración de CORS para permitir peticiones desde cualquier frontend (React, Vue, Next.js, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers bajo el prefijo /api/v1
API_PREFIX = "/api/v1"
app.include_router(summary.router, prefix=API_PREFIX)
app.include_router(soccer.router, prefix=API_PREFIX)
app.include_router(mlb.router, prefix=API_PREFIX)
app.include_router(ufc.router, prefix=API_PREFIX)
app.include_router(nba.router, prefix=API_PREFIX)
app.include_router(nfl.router, prefix=API_PREFIX)

# Directorio de archivos estáticos para la interfaz de visualización
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health", response_model=HealthResponse, tags=["🩺 Diagnóstico"])
async def health_check():
    """Verifica que el servicio esté activo y saludable."""
    return HealthResponse(
        status="ok",
        version=API_VERSION,
        message="API Deportiva operativa y lista para recibir consultas",
    )


@app.get("/", tags=["🏠 Inicio y Dashboard"])
async def root_dashboard(request: Request):
    """
    Ruta raíz:
    - Si se consulta desde un navegador web, entrega el Dashboard interactivo HTML.
    - Si se consulta como JSON (Accept: application/json), entrega los metadatos de la API.
    """
    accept = request.headers.get("accept", "")
    index_file = os.path.join(STATIC_DIR, "index.html")

    if "text/html" in accept and os.path.exists(index_file):
        return FileResponse(index_file)

    return {
        "title": API_TITLE,
        "version": API_VERSION,
        "description": "API REST para resultados de los 5 deportes más vistos del mundo",
        "documentation": "/docs",
        "interactive_dashboard": "/dashboard",
        "endpoints": {
            "resumen_general": f"{API_PREFIX}/summary",
            "futbol_top5": f"{API_PREFIX}/soccer",
            "mlb_beisbol": f"{API_PREFIX}/mlb",
            "ufc_mma": f"{API_PREFIX}/ufc",
            "nba_baloncesto": f"{API_PREFIX}/nba",
            "nfl_futbol_americano": f"{API_PREFIX}/nfl",
        },
    }


@app.get("/dashboard", response_class=HTMLResponse, tags=["🏠 Inicio y Dashboard"])
async def view_dashboard():
    """Visualizador web interactivo para explorar los datos en vivo."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>Dashboard no encontrado</h1>", status_code=404)

