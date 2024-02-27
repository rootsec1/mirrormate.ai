from fastapi import APIRouter

# Local
from util import get_cached_usernames


router = APIRouter()
__cached_username_set__ = get_cached_usernames()


@router.get("/persona/{lichess_username}")
async def train_persona(lichess_username: str):
    """Train the model for the given lichess_username"""
    return list(__cached_username_set__)
