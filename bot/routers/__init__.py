from aiogram import Router

from . import weather_router

router = Router()
router.include_router(weather_router.router)

__all__ = ["router"]
