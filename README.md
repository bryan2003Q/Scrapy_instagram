# Instagram Scraper Stealth - Proyecto de Extracción de Seguidores

Este proyecto es una herramienta avanzada de web scraping diseñada para extraer información de seguidores y seguidos de cuentas de Instagram de manera eficiente y con bajo riesgo de detección. Combina la potencia de **Scrapy**, la versatilidad de **Selenium** para el manejo de sesiones y el alto rendimiento de **Playwright** para el análisis paralelo.

## 🚀 Características

- **Acceso Híbrido**: Utiliza Selenium para el inicio de sesión humano y la extracción inicial de la lista.
- **Análisis Paralelo**: Implementa Playwright para analizar múltiples perfiles simultáneamente, logrando una velocidad 10x superior.
- **Evasión de Bloqueos**: Simulación de comportamiento humano (delays aleatorios, scroll inteligente, emulación de dispositivos).
- **Gestión de Sesiones**: Exportación e importación de cookies para evitar logins repetitivos.
- **Exportación de Datos**: Genera resultados en formato CSV con métricas detalladas (Nombre, Seguidores, Primer Dígito para análisis estadístico).

## 🛠️ Estructura del Proyecto

```text
PRACTICA_EVALUACION/
├── .gitignore               # Archivos ignorados por Git (.env, caché, etc.)
├── requirements.txt         # Dependencias del proyecto
├── ig_scraper.py            # Script principal (Versión Híbrida Optimizada)
├── README.md                # Documentación del proyecto
└── instagram_scraper/       # Proyecto Scrapy
    ├── .env                 # Variables de entorno (Credenciales)
    ├── scrapy.cfg           # Configuración de Scrapy
    └── instagram_scraper/   # Código fuente del spider
        ├── spiders/
        │   ├── instagram.py     # Lógica central del spider
        │   └── scraper_utils.py # Funciones auxiliares y scroll
        ├── settings.py      # Ajustes de Scrapy y Playwright
        ├── items.py         # Definición de estructuras de datos
        └── pipelines.py     # Procesamiento de datos extraídos
```

## 📦 Instalación y Configuración

Siga estos pasos para preparar su entorno de desarrollo en Windows:

### 1. Clonar el repositorio y preparar entorno
```powershell
# Instalar las librerías de Python
pip install -r requirements.txt
```

### 2. Instalar los motores del navegador (Crítico)
Playwright requiere descargar binarios específicos de navegadores para funcionar:
```powershell
playwright install chromium
```

### 3. Configurar variables de entorno
Cree un archivo `.env` dentro de la carpeta `instagram_scraper/` con el siguiente contenido:
```env
IG_USERNAME=tu_usuario
IG_PASSWORD=tu_contraseña
TARGET_ACCOUNT=cuenta_objetivo
PAGE_TYPE=followers  # o 'following'
FOLLOWER_COUNT=50
MAX_WORKERS=5
```

## 🖥️ Uso

Para ejecutar el scraper híbrido optimizado:
```powershell
python ig_scraper.py
```

Para usar la versión de Scrapy pura:
```powershell
cd instagram_scraper
scrapy crawl instagram
```

## ⚠️ Notas Importantes
- **Privacidad**: Use esta herramienta de manera ética y responsable.
- **Limitaciones**: Las cuentas de Instagram pueden ser bloqueadas si se realizan demasiadas peticiones en poco tiempo. Se recomienda no exceder el límite de 10 trabajadores (`MAX_WORKERS`).
- **Navegador**: Playwright se ejecuta en modo `headless=False` por defecto para mayor invisibilidad ante Instagram.

---
*Desarrollado para la cátedra de Desarrollo de Sistemas de Información.*
