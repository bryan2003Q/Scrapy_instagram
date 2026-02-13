# Scrapy settings for instagram_scraper project

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

BOT_NAME = "instagram_scraper"

SPIDER_MODULES = ["instagram_scraper.spiders"]
NEWSPIDER_MODULE = "instagram_scraper.spiders"

# ==============================================================================
# CONFIGURACIÓN DE PLAYWRIGHT Y SCRAPY
# ==============================================================================

# Habilitar los manejadores de descarga de Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Configuración de Playwright
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,  # False para ver el navegador (imprescindible para ocultar que somos bot)
    "timeout": 60 * 1000,
}

# Simular un contexto de usuario real (Sesión persistente)
# Esto guarda tus cookies en la carpeta 'user_data' para no loguearte cada vez
PLAYWRIGHT_CONTEXT_ARGS = {
    "viewport": {"width": 1280, "height": 720},
    "locale": "es-ES",
    "timezone_id": "America/Guayaquil", # Ajusta a tu zona horaria
}

# Habilitar persistencia (Opcional: puedes comentar esto si prefieres login limpio cada vez)
# PLAYWRIGHT_PERSISTENT_CONTEXT_PATH = "playwright_session"

# User-Agent para parecer un navegador real
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Ignorar las reglas de robots.txt (Instagram bloquea scrapers por defecto)
ROBOTSTXT_OBEY = False

# ==============================================================================
# CONFIGURACIÓN DE CONCURRENCIA Y TIMINGS
# ==============================================================================

# Número máximo de peticiones concurrentes (ajustado por MAX_WORKERS en .env o por defecto)
CONCURRENT_REQUESTS = int(os.getenv("MAX_WORKERS", 5))

# Retardo entre peticiones para no saturar y parecer humano
DOWNLOAD_DELAY = 2  # Segundos de espera entre peticiones

# Reintentos automáticos para fallos de red o timeouts
RETRY_ENABLED = True
RETRY_TIMES = 2

DOWNLOAD_TIMEOUT = 60

# Cookies habilitadas para mantener la sesión
COOKIES_ENABLED = True

# ==============================================================================
# OTRAS CONFIGURACIONES
# ==============================================================================

# Desactivar la consola Telnet
TELNETCONSOLE_ENABLED = False

# Configure logging
LOG_LEVEL = "INFO"

# Codificación de salida
FEED_EXPORT_ENCODING = "utf-8"




