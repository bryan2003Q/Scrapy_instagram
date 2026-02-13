import scrapy
import os
from scrapy_playwright.page import PageMethod
from . import scraper_utils
from ..items import InstagramScraperItem

class InstagramSpider(scrapy.Spider):
    name = "instagram_seguidores"
    custom_settings = {
        'FEEDS': {
            'resultados.csv': {
                'format': 'csv',
                'encoding': 'utf-8',
                'fields': ['Username', 'Username_Follower', 'Full_Name', 'Biography', 'Num_Followers'],
                'overwrite': True,
            }
        }
    }
    allowed_domains = ["instagram.com"]
    login_url = "https://www.instagram.com/accounts/login/"

    async def start(self):
        yield scrapy.Request(
            url=self.login_url,
            callback=self.parse_login,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "domcontentloaded"),
                ],
            },
        )

    async def parse_login(self, response):
        page = response.meta["playwright_page"]
        username = os.getenv("IG_USERNAME")
        password = os.getenv("IG_PASSWORD")
        target = os.getenv("TARGET_ACCOUNT")
        page_type = os.getenv("PAGE_TYPE", "followers")
        max_followers = int(os.getenv("FOLLOWER_COUNT"))

        self.logger.info(f"🚀 Iniciando login para: {username}")

        try:
            # 1. Espera de 2 segundos solicitada
            await page.wait_for_timeout(2000)

            # 2. Localizar y escribir usuario (Basado en name='email' visto antes)
            user_input = await page.wait_for_selector("input[name='email'], input[name='username']", timeout=12000)
            
            # Escribir directamente sin limpiar
            await user_input.type(username, delay=50) # Delay más corto para mayor velocidad
            
            # 3. Localizar y escribir password ( name='pass')
            # Buscamos específicamente el que dice 'pass' o el tipo 'password'
            pass_input = await page.wait_for_selector("input[name='pass'], input[type='password']", timeout=12000)
            await pass_input.type(password, delay=50)

            # 4. Clic en el botón Log in (Filtrando por texto para no darle al ojo de la contraseña)
            self.logger.info("🔘 Localizando el botón 'Log in' real...")
            
            await page.wait_for_timeout(1500) # Pausa para que el botón se habilite (aria-disabled="false")

            try:
                # Buscamos el div/button que contenga específicamente "Log in" o "Iniciar sesión"
                login_btn_selector = "div[role='button']:has-text('Log in'), div[role='button']:has-text('Iniciar sesión'), button:has-text('Log in')"
                login_btn = await page.wait_for_selector(login_btn_selector, timeout=5000)
                
                await login_btn.click()
                self.logger.info("🖱️ Clic enviado al botón de login.")
            except:
                self.logger.info("⌨️ No pudimos clicar el botón, intentando con ENTER...")
                await page.keyboard.press("Enter")

            # 5. Verificación de acceso y navegación al perfil
            try:
                # Esperamos a ver el icono de Inicio o la barra de búsqueda
                await page.wait_for_selector("svg[aria-label*='Home'], svg[aria-label*='Inicio'], input[placeholder*='Search']", timeout=15000)
                self.logger.info("✅ ¡LOGIN EXITOSO!")
                
               
                await page.goto(f"https://www.instagram.com/{target}/", wait_until="domcontentloaded")
                self.logger.info(f"📍 Perfil alcanzado: {target}")
                
                # Captura para corroborar que estamos en el perfil correcto
                await page.screenshot(path="perfil_objetivo.png")

                # ==========================================
                # SCRAPEO DINÁMICO (Followers o Following)
                # ==========================================
                success = await scraper_utils.abrir_cuadro_lista(page, target, page_type)
                if success:
                    lista_nombres = await scraper_utils.extraer_nombres_con_scroll(page, max_followers)
                    self.logger.info(f"💾 Procesando {len(lista_nombres)} registros...")
                    
                    for nombre in lista_nombres:
                        yield scrapy.Request(
                            url=f"https://www.instagram.com/{nombre}/",
                            callback=self.parse_follower_profile,
                            meta={
                                "playwright": True,
                                "playwright_include_page": True,
                                "target": target,
                                "follower_name": nombre,
                                "playwright_page_methods": [
                                    # Establecer timeout de navegación específico para esta página
                                    PageMethod("set_default_navigation_timeout", 60000),
                                ],
                            },
                            dont_filter=True,
                            errback=self.handle_error, # Añadimos manejo de errores
                        )

            except Exception as e:
                self.logger.error(f"⚠️ Error en navegación/scrapeo: {str(e)}")
                # Solo tomamos captura si la página sigue abierta
                if not page.is_closed():
                    await page.screenshot(path="error_navegacion.png")

        except Exception as e:
            self.logger.error(f"💥 Error: {str(e)}")
            if not page.is_closed():
                await page.screenshot(path="error_login.png")
        finally:
            if not page.is_closed():
                await page.close()

    async def handle_error(self, failure):
        """Maneja errores de descarga (timeouts, fallos de red)"""
        self.logger.error(f"❌ Error descargando perfil: {failure.request.url}")

    async def parse_follower_profile(self, response):
        """
        Callback para procesar el perfil de cada seguidor y obtener su conteo de seguidores.
        """
        page = response.meta["playwright_page"]
        target = response.meta["target"]
        follower_name = response.meta["follower_name"]
        
        try:
            self.logger.info(f"👤 Analizando perfil de: {follower_name}")
            
            # Usamos la utilidad para extraer todos los datos del perfil
            datos = await scraper_utils.extraer_datos_completos_perfil(page)
            
            item = InstagramScraperItem()
            item['Username'] = target
            item['Username_Follower'] = follower_name
            item['Full_Name'] = datos['full_name']
            item['Biography'] = datos['biography']
            item['Num_Followers'] = datos['num_followers']
            
            yield item
            
        except Exception as e:
            self.logger.error(f"❌ Error analizando perfil de {follower_name}: {str(e)}")
        finally:
            # Importante: cerrar la página de Playwright si se usó playwright_include_page
            await page.close()
