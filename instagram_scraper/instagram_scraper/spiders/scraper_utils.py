import asyncio
import logging
import random
import os

logger = logging.getLogger(__name__)

async def abrir_cuadro_lista(page, target_account, page_type):
    """
    Localiza el botón de seguidores o seguidos y abre el diálogo.
    page_type puede ser 'followers' o 'following'
    """
    logger.info(f"🔍 Intentando abrir la lista de {page_type} de: {target_account}")
    try:
        # Selector dinámico basado en page_type
        selector = f'a[href="/{target_account}/{page_type}/"]'
        
        await page.wait_for_selector(selector, timeout=10000)
        await page.click(selector)
        await page.wait_for_selector('div[role="dialog"]', timeout=10000)
        logger.info(f"✅ Cuadro de {page_type} abierto.")
        return True
    except Exception as e:
        logger.error(f"❌ Error al abrir {page_type}: {str(e)}")
        return False


async def abrir_cuadro_lista(page, target_account, page_type):
    """
    Localiza el botón de seguidores o seguidos y abre el diálogo.
    """
    logger.info(f"🔍 Intentando abrir la lista de {page_type} de: {target_account}")
    try:
        selector = f'a[href="/{target_account}/{page_type}/"]'
        await page.wait_for_selector(selector, timeout=10000)
        await page.click(selector)
        await page.wait_for_selector('div[role="dialog"]', timeout=10000)
        logger.info(f"✅ Cuadro de {page_type} abierto.")
        return True
    except Exception as e:
        logger.error(f"❌ Error al abrir {page_type}: {str(e)}")
        return False

async def scroll_modal_smart(page):
    """
    Versión Playwright del 'scroll_modal_smart' de Selenium.
    Busca automáticamente el div dentro del diálogo que tiene el scroll habilitado.
    """
    try:
        scroll_script = """
        () => {
            const dialog = document.querySelector('div[role="dialog"]');
            if (!dialog) return false;
            
            // Buscar todos los divs y encontrar el que realmente scrollea
            const divs = dialog.querySelectorAll('div');
            for (let div of divs) {
                // Si el contenido es al menos un 20% más alto que el área visible
                if (div.scrollHeight > div.clientHeight * 1.2) {
                    div.scrollTop = div.scrollHeight;
                    return true;
                }
            }
            return false;
        }
        """
        result = await page.evaluate(scroll_script)
        if result:
            # Pausa aleatoria para carga de datos
            await page.wait_for_timeout(random.randint(1500, 2500))
            return True
        return False
    except Exception:
        return False

async def extraer_nombres_con_scroll(page, max_count):
    """
    Extrae usernames de forma robusta realizando scroll inteligente.
    Basado en extract_followers_list_selenium.
    """
    encontrados = set()
    consecutive_no_progress = 0
    max_no_progress = 10
    scroll_attempts = 0
    max_scroll_attempts = 200
    
    logger.info(f"🚀 Iniciando extracción con scroll inteligente (Objetivo: {max_count})")
    
    try:
        while len(encontrados) < max_count and consecutive_no_progress < max_no_progress and scroll_attempts < max_scroll_attempts:
            conteo_inicial = len(encontrados)
            
            # --- PARTE A: EXTRAER NOMBRES ACTUALES ---
            nuevos_nombres = await page.evaluate('''() => {
                const dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) return [];
                const links = Array.from(dialog.querySelectorAll('a[href*="/"]'));
                return links.map(link => {
                    const href = link.getAttribute('href');
                    if (href && href.includes('/')) {
                        const parts = href.split('/').filter(p => p.length > 0);
                        const username = parts[0];
                        const ignore = ["explore", "reels", "direct", "accounts", "p"];
                        if (username && !ignore.includes(username)) {
                            return username;
                        }
                    }
                    return null;
                }).filter(name => name !== null);
            }''')
            
            for nombre in nuevos_nombres:
                if len(encontrados) < max_count:
                    encontrados.add(nombre)
            
            # Gestión de progreso
            total_ahora = len(encontrados)
            if total_ahora > conteo_inicial:
                consecutive_no_progress = 0
                logger.info(f"  ✓ Progreso: {total_ahora}/{max_count} (+{total_ahora - conteo_inicial} nuevos)")
            else:
                consecutive_no_progress += 1
                if consecutive_no_progress % 2 == 0:
                    logger.warning(f"  ⏳ Sin nuevos usuarios ({consecutive_no_progress}/{max_no_progress})")
            
            if len(encontrados) >= max_count:
                break
                
            # --- PARTE B: REALIZAR SCROLL INTELIGENTE ---
            scroll_attempts += 1
            scroll_success = await scroll_modal_smart(page)
            
            if not scroll_success and consecutive_no_progress > 3:
                # Intento de respaldo forzado
                await page.evaluate('''() => {
                    const dialog = document.querySelector('div[role="dialog"]');
                    if (dialog) dialog.scrollTop = dialog.scrollHeight;
                }''')

        logger.info(f"✅ Extracción completada. Total: {len(encontrados)} en {scroll_attempts} scrolls.")
        return list(encontrados)

    except Exception as e:
        logger.error(f"❌ Error durante el scroll/extracción: {str(e)}")
        return list(encontrados)

def limpiar_conteo(texto):
    """
    Convierte textos como '4.2K' o '1.5M' en números enteros.
    También quita comas y puntos.
    """
    if not texto or texto == "N/A":
        return texto
        
    texto = texto.lower().replace(",", "").replace(" ", "")
    
    try:
        if 'k' in texto:
            return int(float(texto.replace('k', '')) * 1000)
        if 'm' in texto:
            return int(float(texto.replace('m', '')) * 1000000)
        # Si tiene un punto decimal pero no sufijo (ej. 4.500 en algunas regiones)
        if '.' in texto:
            return int(float(texto))
        return int(texto)
    except:
        return texto # Si falla la conversión, devolvemos el texto original

async def extraer_conteo_seguidores(page):
    """
    Extrae el número de seguidores de un perfil de Instagram.
    Utiliza el selector span[title] dentro del enlace de followers.
    """
    try:
        logger.info("📊 Intentando extraer conteo de seguidores...")
        # Esperar un poco a que cargue el contenido dinámico
        await page.wait_for_timeout(1500)
        
        # Intentamos localizar el enlace que lleva a /followers/
        selectors = [
            'a[href*="/followers/"] span[title]',
            'a[href*="/followers/"] span',
            'span[title]',
        ]
        
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    # 1. Intentar sacar el número exacto del 'title'
                    dato = await element.get_attribute("title")
                    
                    # 2. Si no hay title, sacar el texto visible (ej. '4.2K')
                    if not dato:
                        dato = await element.inner_text()
                    
                    if dato:
                        resultado = limpiar_conteo(dato)
                        logger.info(f"✅ Conteo procesado: {resultado}")
                        return resultado
            except:
                continue
                
        logger.warning("⚠️ No se pudo encontrar el conteo de seguidores.")
        return "N/A"
    except Exception as e:
        logger.error(f"❌ Error al extraer conteo: {str(e)}")
        return "Error"
