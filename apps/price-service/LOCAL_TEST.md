# Nimbus Signals – price-service (Local Testing)

This service fetches live BTC/ETH prices from CoinGecko, stores a rolling
window of recent samples in memory, and exposes Prometheus metrics and
health/readiness endpoints.

---

## 1. Run locally with Python (venv)

### Prerequisites

- Python 3.12 installed
- Dependencies installed via:

  ```powershell
  # From repo root
  python -m venv venv
  .\venv\Scripts\Activate.ps1  # PowerShell

  cd apps\price-service
  pip install -r requirements.txt
  ```

### Start the service

```powershell
cd apps\price-service
uvicorn main:app --app-dir src --reload --port 8080
```

You should see logs similar to:

```text
INFO ... Effective config: SYMBOLS=['BTC', 'ETH'], FETCH_INTERVAL_SECONDS=15, WINDOW_SIZE=50
INFO ... Startup complete: background price fetch task started.
INFO ... Starting price fetch loop for symbols=['BTC', 'ETH'], interval=15s, window=50
```

---

## 2. Run via Docker

### Build the image

From `apps\price-service`:

```powershell
docker build -t price-service:local .
```

### Run the container

```powershell
docker run --rm -p 8080:8080 price-service:local
```

You should see logs similar to the local `uvicorn` run, including the
`Effective config:` line and periodic `Fetched prices successfully...` messages.

You can also override basic config via environment variables, for example:

```powershell
docker run --rm -p 8080:8080 `
  -e SYMBOLS="BTC,ETH" `
  -e FETCH_INTERVAL_SECONDS="15" `
  -e WINDOW_SIZE="50" `
  price-service:local
```

---

## 3. Example `curl` checks

All examples assume the service is listening on `http://localhost:8080`.

### 3.1 Liveness – `/healthz`

```powershell
curl http://localhost:8080/healthz
```

Expected:

```json
{"status":"ok"}
```

### 3.2 Readiness – `/readyz`

Immediately after startup:

```powershell
curl -i http://localhost:8080/readyz
```

Expected:

- Status: `503 Service Unavailable`
- Body similar to:

```json
{"status":"not_ready","reason":"no price data fetched yet"}
```

After a few seconds (once prices have been fetched):

```powershell
curl -i http://localhost:8080/readyz
```

Expected:

- Status: `200 OK`
- Body:

```json
{"status":"ready"}
```

### 3.3 Prices – `/prices`

All symbols, default window:

```powershell
curl http://localhost:8080/prices
```

Single symbol, custom window:

```powershell
curl "http://localhost:8080/prices?symbol=BTC&window=5"
```

Example (shape only; values will differ):

```json
{
  "symbols": ["BTC"],
  "window": 5,
  "data": {
    "BTC": [
      {"timestamp": 1731737177.123, "price": 64231.12},
      ...
    ]
  }
}
```

### 3.4 Prometheus metrics – `/metrics`

```powershell
curl http://localhost:8080/metrics
```

Look for:

- `price_current{symbol="BTC"}`
- `price_update_ts{symbol="ETH"}`
- `price_fetch_latency_seconds_bucket{...}`
- `price_fetch_errors_total`

The response is standard Prometheus text format and is what Prometheus
will scrape in Kubernetes.
