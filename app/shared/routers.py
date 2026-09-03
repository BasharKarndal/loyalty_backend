from fastapi import APIRouter

from app.modules.auth.presentation.router import router as auth_router
from app.modules.customer.presentation.router import router as customer_router
from app.modules.gift.presentation.router import gift_types_router, gifts_router
from app.modules.purchase.presentation.router import router as purchase_router
from app.modules.reports.presentation.router import router as reports_router
from app.modules.settings.presentation.router import router as settings_router
from app.modules.subscription.presentation.router import router as subscriptions_router
from app.modules.user.presentation.router import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(subscriptions_router)
api_router.include_router(customer_router)
api_router.include_router(purchase_router)
api_router.include_router(reports_router)
api_router.include_router(gift_types_router)
api_router.include_router(gifts_router)
api_router.include_router(settings_router)
