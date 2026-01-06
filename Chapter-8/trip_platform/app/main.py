from fastapi import FastAPI, Depends, BackgroundTasks
from app.dependencies import time_range, select_category, check_coupon_validity
from app.middleware import ClientInfoMiddleware
from app.profiler import ProfileEndpointsMiddleWare
from app.internationalization import router
from app.rate_limiter import limiter
from app.background_tasks import store_query_to_external_db, logger
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from typing import Annotated

app = FastAPI()

app.include_router(router)

app.add_middleware(ClientInfoMiddleware)
app.add_middleware(ProfileEndpointsMiddleWare)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.add_middleware(SlowAPIMiddleware)

@app.get("/v1/trips")
async def get_tours(
    time_range: Annotated[time_range, Depends()] ,
):
    start, end = time_range
    message = f"Request trips from {start}"
    if end:
        return f"{message} to {end}"
    return message

@app.get("/v2/trips/{category}")
def get_trips_by_category(
    background_tasks: BackgroundTasks,
    category: Annotated[select_category, Depends()],
    discount_applicable: Annotated[
        bool, Depends(check_coupon_validity)
    ],
):
    category = category.replace("-", " ").title()
    message = f"You requested {category} trips."
    
    if discount_applicable:
        message += (
            "\n. The coupon code is valid! "
            "You will get a discount"
        )
    background_tasks.add_task(
        store_query_to_external_db, message
    )
    
    logger.info(
        "Query sent to background task "
        "end of request"
    )
    return message
