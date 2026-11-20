# Authentication API

This service is a Flask API that creates user accounts and authenticates login requests. It persists account records in MySQL and is called by the Express frontend over the private Compose network.

## Runtime configuration

The service reads database settings from environment variables supplied by Docker Compose:

| Variable | Purpose |
|---|---|
| `DB_HOST` | MySQL Compose service name (`mysql`) |
| `DB_PORT` | MySQL port (`3306`) |
| `DB_NAME` | Application database |
| `DB_USER` | Application database account |
| `DB_PASSWORD` | Application database password |

The Compose health check calls `/health`; the frontend waits for the service to become healthy. Configure secrets in the ignored `docker/.env` file, never in this README or source control.

## Run

Start the complete application using [`docker/README.md`](../../docker/README.md). The service image is defined by the local `Dockerfile`; Python dependencies are listed in `requirements.txt`.

The Auth API is intentionally not published on a host port. Check its health from inside the Compose network:

```powershell
docker compose --env-file docker/.env -f docker/compose.yaml ps
docker compose --env-file docker/.env -f docker/compose.yaml exec auth-service python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:5000/health'); print(r.status, r.read().decode())"
```

Expected result: the container health is `healthy` and the request returns HTTP `200` with service/database health data. The UI's signup/login flow is the end-to-end functional check. View service logs with `docker compose --env-file docker/.env -f docker/compose.yaml logs --tail 50 auth-service`.
