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
    print("=" * 60)
    print("⚽ ⚾ 🥊 🏀 🏈 INICIANDO API DEPORTIVA (TOP 5 DEPORTES)")
    print("Documentación Swagger UI: http://127.0.0.1:8000/docs")
    print("Dashboard Web Deportivo:  http://127.0.0.1:8000/dashboard")
    print("Resumen de API:           http://127.0.0.1:8000/api/v1/summary")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

