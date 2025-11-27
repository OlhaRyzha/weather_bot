from aiogram import Router
from .city import router as city_router
from .location import router as location_router
from .shortcuts import router as shortcuts_router
from .start import router as start_router

router = Router()

router.include_router(start_router)
router.include_router(city_router)
router.include_router(location_router)
router.include_router(shortcuts_router)

__all__ = ["router"]
