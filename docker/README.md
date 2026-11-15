# Local Containers

This directory defines the local development stack for the IVOLVE application. Docker Compose starts the frontend, authentication API, roadmap API, and MySQL database on one private Docker network.

## Services

| Service | Purpose | Local access |
|---|---|---|
| `frontend` | Web UI, signup, login, and roadmap page | http://localhost:3000 |
| `auth-service` | Flask API for account registration and login | Internal port 5000 |
| `roadmap-service` | Spring Boot API serving roadmap content | Internal port 8080 |
| `mysql` | Persistent database for application accounts | Internal port 3306 |

The frontend is the only service published to the host. Backend traffic uses Compose service names. MySQL data is stored in the `mysql-data` named volume and survives container recreation.

## Start the stack

Run these commands from the repository root in PowerShell:

```powershell
Copy-Item docker/.env.example docker/.env
# Edit docker/.env and set local-only passwords and a session secret.
docker compose --env-file docker/.env -f docker/compose.yaml --profile build run --rm roadmap-builder
docker compose --env-file docker/.env -f docker/compose.yaml up --build --detach
docker compose --env-file docker/.env -f docker/compose.yaml ps
```

The Maven builder writes the Spring Boot JAR into `app/roadmap-service/target`; Compose then packages it with `Dockerfile.local`. The normal multistage `Dockerfile` is retained for CI builds.

View logs or stop the stack:

```powershell
docker compose --env-file docker/.env -f docker/compose.yaml logs --follow
docker compose --env-file docker/.env -f docker/compose.yaml down
```

`down` preserves the database volume. Add `--volumes` only when intentionally deleting local database data. Never commit `docker/.env`.

## Files

- `compose.yaml` — service definitions, environment wiring, health checks, and the Maven builder profile.
- `.env.example` — safe template for local configuration; copy it to `.env` before running.

See the [application overview](../app/README.md) and the root [project guide](../README.md).
