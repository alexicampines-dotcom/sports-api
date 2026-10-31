# 🏆 API Deportiva Global con FastAPI

API RESTful moderna, asíncrona y de alto rendimiento construida con **Python** y **FastAPI**, diseñada específicamente para alimentar portales y aplicaciones web deportivas.

Proporciona marcadores en vivo, resultados finales, programaciones y estadísticas de los **5 deportes más vistos del planeta**:
1. ⚽ **Fútbol**: Las **Top 5 ligas del mundo** (Premier League, LaLiga, Serie A, Bundesliga, Ligue 1).
2. ⚾ **Béisbol (MLB)**: Major League Baseball (carreras, hits, errores, innings).
3. 🥊 **Artes Marciales Mixtas (UFC / MMA)**: Carteleras completas, peleadores, métodos de victoria y títulos en juego.
4. 🏀 **Baloncesto (NBA)**: Puntos por cuarto, prórrogas y marcadores en vivo.
5. 🏈 **Fútbol Americano (NFL)**: Resultados de la semana, cuartos y estado del partido.

---

## 🌟 Características Principales

- **Velocidad Extrema (<5ms en caché)**: Motor de caché en memoria asíncrono con TTL configurable para evitar saturar las fuentes de datos y garantizar respuestas instantáneas.
- **Top 5 Ligas de Fútbol Consolidadas**: Permite consultar ligas individuales o todas a la vez en una única llamada.
- **Endpoint Resumen Unificado (`/api/v1/summary`)**: Ejecuta peticiones concurrentes con `asyncio.gather` para recopilar lo más destacado de los 5 deportes en una sola respuesta JSON optimizada para la portada de tu web.
- **Normalización de Datos con Pydantic v2**: Respuestas estandarizadas con modelos estrictos (equipos, logos, estadios, transmisiones, atletas, estados).
- **CORS Configurado**: Listo para consumir desde cualquier frontend (React, Vue, Next.js, Angular, Svelte o apps móviles Flutter / React Native).
- **Documentación Interactiva Swagger / OpenAPI**: Incluye Swagger UI (`/docs`) y ReDoc (`/redoc`).
- **Dashboard Web Moderno Integrado**: Incluye una interfaz web en modo oscuro accesible en `/dashboard` para previsualizar los resultados en tiempo real sin salir del navegador.

---

## 📁 Estructura del Proyecto

```text
sports_api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # Aplicación FastAPI, CORS, middlewares y rutas
│   ├── config.py                # Configuración, endpoints de ESPN, TTL de caché
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Modelos Pydantic v2 de validación y respuesta
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache.py             # Caché asíncrono en memoria con TTL
│   │   ├── parsers.py           # Normalización de eventos (Fútbol, MLB, UFC, NBA, NFL)
│   │   └── espn_service.py      # Cliente HTTP asíncrono hacia los servicios deportivos
│   └── routers/
│       ├── __init__.py
│       ├── summary.py           # GET /api/v1/summary (Resumen de los 5 deportes)
│       ├── soccer.py            # GET /api/v1/soccer (Top 5 ligas europeas)
│       ├── mlb.py               # GET /api/v1/mlb (Grandes Ligas)
│       ├── ufc.py               # GET /api/v1/ufc (Combates y eventos UFC)
│       ├── nba.py               # GET /api/v1/nba (Baloncesto NBA)
│       └── nfl.py               # GET /api/v1/nfl (Fútbol Americano NFL)
│
├── static/
│   └── index.html               # Dashboard web interactivo con Tailwind CSS
│
├── tests/
│   ├── __init__.py
│   └── test_api.py              # Suite de pruebas unitarias y de integración
│
├── requirements.txt             # Dependencias del proyecto
├── run.py                       # Script para iniciar el servidor uvicorn
├── .gitignore
└── README.md                    # Documentación técnica completa
```

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar o navegar a la carpeta del proyecto
```bash
cd "C:\Users\alexi\.gemini\antigravity\scratch\sports_api"
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la API
Puedes iniciar el servidor directamente con el script provisto:
```bash
python run.py
```
O directamente con `uvicorn`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Una vez en marcha:
- **Dashboard Web**: [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
- **Documentación Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Healthcheck**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 Referencia de Endpoints

### 1. Resumen General (Los 5 Deportes)
Ideal para pintar el Home de tu portal deportivo:
- `GET /api/v1/summary`
  - Parámetros opcionales: `date=YYYYMMDD`, `force_refresh=true|false`
  - Retorna: Contadores globales y listas de partidos de Fútbol, MLB, UFC, NBA y NFL.

---

### 2. ⚽ Fútbol (Top 5 Ligas del Mundo)
- `GET /api/v1/soccer/leagues`: Lista los metadatos de las 5 ligas soportadas.
- `GET /api/v1/soccer`: Obtiene partidos de las ligas con filtro.
  - Parámetro `league`:
    - `all` (por defecto: devuelve las 5 ligas consolidadas)
    - `premier_league` (Inglaterra 🇬🇧)
    - `laliga` (España 🇪🇸)
    - `serie_a` (Italia 🇮🇹)
    - `bundesliga` (Alemania 🇩🇪)
    - `ligue_1` (Francia 🇫🇷)
  - Parámetro `date`: Fecha en formato `YYYYMMDD` (ej: `20261030`).
- Endpoints directos por conveniencia:
  - `GET /api/v1/soccer/premier-league`
  - `GET /api/v1/soccer/laliga`
  - `GET /api/v1/soccer/serie-a`
  - `GET /api/v1/soccer/bundesliga`
  - `GET /api/v1/soccer/ligue-1`

---

### 3. ⚾ Béisbol (MLB)
- `GET /api/v1/mlb`:
  - Resultados, carreras, hits, errores e innings.
  - Parámetros: `date=YYYYMMDD`, `force_refresh=true|false`.

---

### 4. 🥊 Artes Marciales Mixtas (UFC)
- `GET /api/v1/ufc`:
  - Evento principal (UFC Numerado o Fight Night).
  - Cartelera estelar y preliminar.
  - Peleadores, apodos, fotos, récords (`16-0-0`), métodos de victoria (KO, Sumisión, Decisión) y asalto.
  - Indicador de pelea de título (`is_title_fight: true`).

---

### 5. 🏀 Baloncesto (NBA)
- `GET /api/v1/nba`:
  - Marcadores de la jornada de hoy o fecha indicada.
  - Puntuación por cuartos (`linescores`), tiempo de juego en vivo y prórrogas.

---

### 6. 🏈 Fútbol Americano (NFL)
- `GET /api/v1/nfl`:
  - Partidos de la semana en curso.
  - Marcadores, cuartos y estado de juego.

---

## 💻 Ejemplos de Consumo Frontend

### Consumo con JavaScript / TypeScript (Fetch API / React / Next.js)
```javascript
// Obtener el resumen de los 5 deportes para la portada
async function loadSportsHome() {
  const response = await fetch('http://localhost:8000/api/v1/summary');
  const data = await response.json();
  
  console.log(`Fútbol: ${data.counts.soccer} partidos`);
  console.log(`NBA: ${data.counts.nba} partidos`);
  console.log(`MLB: ${data.counts.mlb} partidos`);
  console.log(`UFC: ${data.counts.ufc} eventos`);
  console.log(`NFL: ${data.counts.nfl} partidos`);
}

// Obtener solo partidos de LaLiga española
async function loadLaLiga() {
  const response = await fetch('http://localhost:8000/api/v1/soccer/laliga');
  const data = await response.json();
  data.events.forEach(match => {
    console.log(`${match.away_team.name} ${match.away_team.score} - ${match.home_team.score} ${match.home_team.name} (${match.status.detail})`);
  });
}
```

### Consumo con cURL
```bash
# Consultar resumen general
curl -X GET "http://localhost:8000/api/v1/summary" -H "accept: application/json"

# Consultar Premier League
curl -X GET "http://localhost:8000/api/v1/soccer/premier-league" -H "accept: application/json"

# Consultar UFC
curl -X GET "http://localhost:8000/api/v1/ufc" -H "accept: application/json"
```

---

## 🧪 Ejecución de Pruebas Automatizadas

Para validar que todos los modelos y endpoints funcionen correctamente:
```bash
set PYTHONPATH=.
python tests/test_api.py
```
Resultado:
```text
[OK] Health check test passed
[OK] Soccer leagues endpoint test passed
==================================================
SUCCESS: TODOS LOS TESTS UNITARIOS PASARON CORRECTAMENTE!
==================================================
```

