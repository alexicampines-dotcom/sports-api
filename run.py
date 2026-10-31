"""
Script ejecutor de la API con Uvicorn.
Uso:
    python run.py
"""
import sys
import uvicorn

# Configurar encoding UTF-8 en terminales Windows para evitar UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if __name__ == "__main__":
    from app.config import HOST, PORT, RELOAD

    print("=" * 60)
    print("INICIANDO API DEPORTIVA (TOP 5 DEPORTES)")
    print(f"Documentacion Swagger UI: http://127.0.0.1:{PORT}/docs")
    print(f"Dashboard Web Deportivo:  http://127.0.0.1:{PORT}/dashboard")
    print(f"Resumen de API:           http://127.0.0.1:{PORT}/api/v1/summary")
    print("=" * 60)
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=RELOAD)
