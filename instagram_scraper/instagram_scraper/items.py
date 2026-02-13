import scrapy

class InstagramScraperItem(scrapy.Item):
    # La cuenta principal (ej: teeli__peachmuffin)
    Username = scrapy.Field()
    # El nombre de usuario del seguidor/seguido encontrado (slug)
    Username_Follower = scrapy.Field()
    # El nombre completo (Full Name)
    Full_Name = scrapy.Field()
    # La biografía
    Biography = scrapy.Field()
    # El número de seguidores que tiene ese seguidor
    Num_Followers = scrapy.Field()
    
    # Para la parte de SEGUIDOS (Following)
    Username_Following = scrapy.Field()
    Num_Following = scrapy.Field()
