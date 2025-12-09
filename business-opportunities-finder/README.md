# Business Opportunities Finder

Sistema automatizado que descubre y analiza diariamente las 10 mejores oportunidades de negocio para crear aplicaciones SaaS, herramientas de automatización, y micro-servicios con IA.

## 🚀 Features

- **Análisis diario automatizado** de múltiples fuentes (Reddit, HackerNews, ProductHunt, etc.)
- **Scoring inteligente** usando Gemini 3 para análisis semántico
- **Dashboard interactivo** para explorar oportunidades
- **Histórico completo** con analytics y tendencias
- **Sistema de gestión** para marcar oportunidades como seleccionadas/descartadas

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.11+ con FastAPI
- **Base de datos:** PostgreSQL 15
- **IA:** Google Gemini 3 API
- **Scheduler:** APScheduler
- **Frontend:** HTML + Vanilla JavaScript + CSS
- **Deployment:** Docker + Docker Compose

## 📋 Requisitos

- Python 3.11 o superior
- Docker y Docker Compose
- API Keys:
  - Google Gemini API
  - Reddit API (OAuth2)
  - ProductHunt API (opcional)
  - Twitter API (opcional)

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd business-opportunities-finder
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus API keys
```

### 3. Levantar con Docker

```bash
docker-compose up -d
```

### 4. Aplicar migraciones

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Acceder al dashboard

Abrir en navegador: `http://localhost:8000`

## 📁 Estructura del Proyecto

```
business-opportunities-finder/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuración
│   │   ├── models/              # Modelos SQLAlchemy
│   │   ├── services/            # Lógica de negocio
│   │   │   ├── scrapers/        # Web scrapers
│   │   │   ├── gemini_analyzer.py
│   │   │   ├── scorer.py
│   │   │   └── report_generator.py
│   │   ├── database/            # DB config
│   │   ├── scheduler/           # Tareas programadas
│   │   └── api/                 # API routes
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🎯 Uso

### Ejecución Manual del Análisis Diario

```bash
docker-compose exec backend python -m app.scheduler.daily_job
```

### API Endpoints

- `GET /api/opportunities` - Listar oportunidades con filtros
- `GET /api/opportunities/{id}` - Detalle de oportunidad
- `PATCH /api/opportunities/{id}` - Actualizar estado/notas
- `GET /api/reports/{date}` - Informe de un día específico
- `GET /api/analytics` - Estadísticas agregadas

### Documentación API

Acceder a: `http://localhost:8000/docs`

## 📊 Modelo de Scoring

Cada oportunidad se puntúa de 0 a 10 usando 6 criterios:

- **Dolor y Urgencia** (30%) - Nivel de frustración y necesidad inmediata
- **Frecuencia** (20%) - Cuántas veces se menciona el problema
- **Disposición a Pagar** (20%) - Capacidad económica del sector
- **Baja Competencia** (15%) - Nivel de saturación del mercado (invertido)
- **Facilidad Técnica** (10%) - Viabilidad de implementación
- **Sinergia con IA** (5%) - Potencial de automatización con IA

**Fórmula:**
```
Score = 0.3×Dolor + 0.2×Frecuencia + 0.2×Pago + 0.15×BajaComp + 0.1×Facilidad + 0.05×IA
```

## 🔐 Privacidad y Compliance

- No se almacenan datos personales identificables (PII)
- Uso de APIs oficiales cuando están disponibles
- Respeto a `robots.txt` y rate limits
- Almacenamiento solo de contenido público agregado

## 📝 Licencia

MIT License - Ver archivo LICENSE para detalles

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir cambios importantes.

## 📧 Contacto

Para preguntas o soporte, abre un issue en GitHub.
