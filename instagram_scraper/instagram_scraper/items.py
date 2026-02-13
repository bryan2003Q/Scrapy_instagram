import scrapy

class InstagramScraperItem(scrapy.Item):
    # La cuenta principal (ej: teeli__peachmuffin)
    Username = scrapy.Field()
    # El nombre del seguidor/seguido encontrado
    Username_Follower = scrapy.Field()
    # El número de seguidores que tiene ese seguidor (lo usaremos en el siguiente paso)
    Num_Followers = scrapy.Field()
