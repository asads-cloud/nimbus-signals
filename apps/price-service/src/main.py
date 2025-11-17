import asyncio
import logging
import time
import os
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

#----------------- Configuress  -------------------------

DEFAULT_SYMBOLS: List[str] = ["BTC", "ETH"]
DEFAULT_FETCH_INTERVAL_SECONDS: int = 15
DEFAULT_WINDOW_SIZE: int = 50

SYMBOLS: List[str] = DEFAULT_SYMBOLS
FETCH_INTERVAL_SECONDS: int = DEFAULT_FETCH_INTERVAL_SECONDS
WINDOW_SIZE: int = DEFAULT_WINDOW_SIZE

# CoinGecko mapping for our symbols
COINGECKO_IDS: Dict[str, str] = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
}

#------------------- Logging setup stuff for now ------------------------------------------

logger = logging.getLogger("nimbus-signals.price-service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

#------------------- Config from environment variables ------------------------------------------

def load_symbols_from_env() -> List[str]:
    raw = os.getenv("SYMBOLS")
    if not raw:
        return DEFAULT_SYMBOLS

    requested = [s.strip().upper() for s in raw.split(",") if s.strip()]
    symbols: List[str] = []

    for sym in requested:
        if sym in COINGECKO_IDS:
            symbols.append(sym)
        else:
            logger.warning(
                "Ignoring unsupported symbol from SYMBOLS env var: %s (supported: %s)",
                sym,
                ", ".join(COINGECKO_IDS.keys()),
            )

    if not symbols:
        logger.warning(
            "No valid symbols from SYMBOLS env var (%s). Falling back to defaults: %s",
            raw,
            DEFAULT_SYMBOLS,
        )
        return DEFAULT_SYMBOLS

    return symbols

def load_int_from_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default

    try:
        value = int(raw)
        if value <= 0:
            raise ValueError("must be positive")
        return value
    except ValueError:
        logger.warning(
            "Invalid value for %s=%r. Using default %s.",
            name,
            raw,
            default,
        )
        return default

SYMBOLS: List[str] = load_symbols_from_env()
FETCH_INTERVAL_SECONDS: int = load_int_from_env(
    "FETCH_INTERVAL_SECONDS",
    DEFAULT_FETCH_INTERVAL_SECONDS,
)
WINDOW_SIZE: int = load_int_from_env(
    "WINDOW_SIZE",
    DEFAULT_WINDOW_SIZE,
)

logger.info(
    "Effective config: SYMBOLS=%s, FETCH_INTERVAL_SECONDS=%s, WINDOW_SIZE=%s",
    SYMBOLS,
    FETCH_INTERVAL_SECONDS,
    WINDOW_SIZE,
)

#--------------- In-memory price storage ---------------------------------------------------------------------------------

@dataclass
class PricePoint:
    timestamp: float  # Unix epoch seconds
    price: float      # Price in USD!!!!!!!!!!!

# symbol -> deque of PricePoint
price_history: Dict[str, Deque[PricePoint]] = {
    symbol: deque(maxlen=WINDOW_SIZE) for symbol in SYMBOLS
}

latest_fetch_success: bool = False

#--------- CUSTOM METRICS FORM PROMETHEUS -------------------------

# Current price per symbol
PRICE_CURRENT = Gauge(
    "price_current",
    "Current price in USD",
    labelnames=["symbol"],
)

# Last update timestamp per symbol.
PRICE_UPDATE_TS = Gauge(
    "price_update_ts",
    "Unix timestamp of last successful price update",
    labelnames=["symbol"],
)

# Latency of fetch operation
PRICE_FETCH_LATENCY_SECONDS = Histogram(
    "price_fetch_latency_seconds",
    "Time spent fetching prices from CoinGecko in seconds",
)

# Total number of fetch errors
PRICE_FETCH_ERRORS_TOTAL = Counter(
    "price_fetch_errors_total",
    "Total number of errors when fetching prices from CoinGecko",
)

#----------------- Price fetching logic -------------------------------------------------

async def fetch_prices_once(client: httpx.AsyncClient) -> None:
    """
    Fetch current prices for all configured SYMBOLS from CoinGecko and
    update the in-memory price_history + Prometheus metrics.
    """
    global latest_fetch_success

    ids_param = ",".join(COINGECKO_IDS[symbol] for symbol in SYMBOLS)
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ids_param,
        "vs_currencies": "usd",
    }

    start = time.time()
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        now = time.time()

        for symbol in SYMBOLS:
            coingecko_id = COINGECKO_IDS[symbol]
            try:
                price = float(data[coingecko_id]["usd"])
            except (KeyError, TypeError, ValueError) as e:
                logger.warning("Missing/invalid price for %s: %s", symbol, e)
                continue

            # Update in-memory history
            price_history[symbol].append(PricePoint(timestamp=now, price=price))

            # Update Prometheus gauges
            PRICE_CURRENT.labels(symbol=symbol).set(price)
            PRICE_UPDATE_TS.labels(symbol=symbol).set(now)

        latest_fetch_success = True
        duration = now - start
        PRICE_FETCH_LATENCY_SECONDS.observe(duration)

        logger.info(
            "Fetched prices successfully for %s in %.3fs",
            SYMBOLS,
            duration,
        )
    except httpx.HTTPError as e:
        latest_fetch_success = False
        PRICE_FETCH_ERRORS_TOTAL.inc()
        logger.error("Error fetching prices from CoinGecko: %s", e)


async def price_fetch_loop() -> None:
    """
    Background loop that continuously fetches prices every FETCH_INTERVAL_SECONDS.
    """
    logger.info(
        "Starting price fetch loop for symbols=%s, interval=%ss, window=%s",
        SYMBOLS,
        FETCH_INTERVAL_SECONDS,
        WINDOW_SIZE,
    )

    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            await fetch_prices_once(client)
            await asyncio.sleep(FETCH_INTERVAL_SECONDS)

def has_any_prices() -> bool:
    return any(len(history) > 0 for history in price_history.values())

#-------------------------- FastAPI app and  lifecycle --------------------------------------

app = FastAPI(title="Nimbus Signals - Price Service")

@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(price_fetch_loop())
    logger.info("Startup complete: background price fetch task started.")

#---------------- heealth & readiness endpoints -------------------------------------

@app.get("/healthz")
async def healthz() -> dict:
    """
    Basic liveness probe: if this endpoint responds, the app is running.
    """
    return {"status": "ok"}

@app.get("/readyz")
async def readyz() -> JSONResponse:
    """
    Readiness probe: only OK once at least one price has been fetched.
    """
    if not has_any_prices():
        # 503 so Kubernetes (later) knows we're not ready yet
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": "no price data fetched yet",
            },
        )

    return JSONResponse(content={"status": "ready"})

#------------------------- Prices endpointss ---------------------------------------------------

@app.get("/prices")
async def get_prices(
    symbol: Optional[str] = Query(
        default=None,
        description="Symbol to query (e.g., BTC, ETH). If omitted, returns all symbols.",
    ),
    window: Optional[int] = Query(
        default=None,
        ge=1,
        description="Max number of recent samples to return (capped by WINDOW_SIZE).",
    ),
) -> dict:
    """
    Return recent price samples from in-memory history.

    Example:
    GET /prices?symbol=BTC&window=10
    """
    if window is None:
        effective_window = WINDOW_SIZE
    else:
        effective_window = min(window, WINDOW_SIZE)

    symbols_to_return: List[str]
    if symbol is None:
        symbols_to_return = SYMBOLS
    else:
        symbol = symbol.upper()
        if symbol not in SYMBOLS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported symbol '{symbol}'. Supported: {', '.join(SYMBOLS)}",
            )
        symbols_to_return = [symbol]

    result: Dict[str, List[dict]] = {}

    for sym in symbols_to_return:
        history = list(price_history.get(sym, []))[-effective_window:]
        result[sym] = [
            {
                "timestamp": point.timestamp,
                "price": point.price,
            }
            for point in history
        ]

    return {
        "symbols": symbols_to_return,
        "window": effective_window,
        "data": result,
    }

#-------------- Prometheus metrics endpoint --------------------

@app.get("/metrics")
async def metrics() -> Response:
    """
    Expose Prometheus metrics in the standard text-based format.
    This will include the default process & Python metrics.
    Custom business metrics can be added too (hopefully ill have time)
    """
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
