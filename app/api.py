from ninja import NinjaAPI

from .routes import basho_router, division_router, rikishi_router, root_router

api = NinjaAPI()
api.add_router("", root_router)
api.add_router("rikishi/", rikishi_router)
api.add_router("division/", division_router)
api.add_router("basho/", basho_router)
