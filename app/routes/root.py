from ninja import Router

router = Router()


@router.get("")
def root(request):
    """Return a simple confirmation message."""
    return {"status": "ok"}
