import scrapy
import os
from scrapy_playwright.page import PageMethod
from . import scraper_utils
from ..items import InstagramScraperItem

class InstagramSeguidosSpider(scrapy.Spider):
    # Le ponemos un nombre diferente para ejecutarlo por separado
    name = "instagram_seguidos"

    custom_settings = {
            'FEEDS': {
                'seguidos.csv': {
                    'format': 'csv',
                    'encoding': 'utf-8',
                    'fields': ['Username', 'Username_Following', 'Full_Name', 'Biography', 'Num_Following'],
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
        
        # AQUÍ CAMBIAMOS: Forzamos a que sea 'following' (Seguidos)
        page_type = "following" 
        max_to_scrape = int(os.getenv("FOLLOWER_COUNT"))

        self.logger.info(f"🚀 Iniciando login para Seguidos de: {target}")

        try:
            await page.wait_for_timeout(2000)

            user_input = await page.wait_for_selector("input[name='email'], input[name='username']", timeout=12000)
            await user_input.type(username, delay=50)
            
            pass_input = await page.wait_for_selector("input[name='pass'], input[type='password']", timeout=12000)
            await pass_input.type(password, delay=50)

            try:
                login_btn_selector = "div[role='button']:has-text('Log in'), div[role='button']:has-text('Iniciar sesión'), button:has-text('Log in')"
                login_btn = await page.wait_for_selector(login_btn_selector, timeout=5000)
                await login_btn.click()
            except:
                await page.keyboard.press("Enter")

            try:
                await page.wait_for_selector("svg[aria-label*='Home'], svg[aria-label*='Inicio'], input[placeholder*='Search']", timeout=15000)
                self.logger.info("✅ ¡LOGIN EXITOSO!")
                
                # Ir al perfil del objetivo
                await page.goto(f"https://www.instagram.com/{target}/", wait_until="domcontentloaded")
                
                # Abrimos el cuadro de 'Following' (Seguidos)
                success = await scraper_utils.abrir_cuadro_lista(page, target, page_type)
                
                if success:
                    # Extraemos los nombres de la lista de Seguidos con scroll
                    lista_nombres = await scraper_utils.extraer_nombres_con_scroll(page, max_to_scrape)
                    self.logger.info(f"💾 Procesando {len(lista_nombres)} Seguidos...")
                    
                    for nombre in lista_nombres:
                        yield scrapy.Request(
                            url=f"https://www.instagram.com/{nombre}/",
                            callback=self.parse_profile_follower_count,
                            meta={
                                "playwright": True,
                                "playwright_include_page": True,
                                "target": target,
                                "follower_name": nombre,
                            },
                            dont_filter=True,
                        )

            except Exception as e:
                self.logger.error(f"⚠️ Error: {str(e)}")
        finally:
            if not page.is_closed():
                await page.close()

    async def parse_profile_follower_count(self, response):
        """Callback para obtener la cantidad de seguidores de la persona que yo sigo"""
        page = response.meta["playwright_page"]
        target = response.meta["target"]
        followed_user = response.meta["follower_name"]
        
        try:
            # Usamos la utilidad para extraer todos los datos del perfil
            datos = await scraper_utils.extraer_datos_completos_perfil(page)
            
            item = InstagramScraperItem()
            item['Username'] = target
            item['Username_Following'] = followed_user
            item['Full_Name'] = datos['full_name']
            item['Biography'] = datos['biography']
            item['Num_Following'] = datos['num_followers'] # En este spider se llama Num_Following en el item
            
            yield item
            
        except Exception as e:
            self.logger.error(f"❌ Error en perfil de {followed_user}: {str(e)}")
        finally:
            await page.close()