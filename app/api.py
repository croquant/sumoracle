from ninja import NinjaAPI

api = NinjaAPI()


@api.get("")
def root(request):
    """Return a simple confirmation message."""
    return {"status": "ok"}
