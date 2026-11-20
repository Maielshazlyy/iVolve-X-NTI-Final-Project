# Frontend

The frontend is a Node.js and Express web application. It renders the signup/login screens and the training roadmap, keeps the authenticated session, and calls the Auth and Roadmap APIs over the container network.

## Request flow

1. The browser opens the frontend at port `3000`.
2. Signup and login requests are sent to the Flask Auth service.
3. After successful login, Express stores the user in a session.
4. The roadmap page requests `GET /api/roadmap` from the Spring Boot service and renders the returned topics.

## Configuration

| Variable | Purpose |
|---|---|
| `AUTH_SERVICE_URL` | Auth API base URL; Compose sets `http://auth-service:5000` |
| `ROADMAP_SERVICE_URL` | Roadmap API base URL; Compose sets `http://roadmap-service:8080` |
| `SESSION_SECRET` | Signs the session cookie; set a private value in `docker/.env` |

## Run

Use the full local stack from the repository root as documented in [`docker/README.md`](../../docker/README.md). The frontend container is built from the `Dockerfile` in this directory.

From the repository root, after creating `docker/.env` and building the Maven JAR:

```powershell
docker compose --env-file docker/.env -f docker/compose.yaml up --build --detach
docker compose --env-file docker/.env -f docker/compose.yaml ps
Invoke-WebRequest http://localhost:3000/ -UseBasicParsing | Select-Object StatusCode
```

Expected result: the frontend is `Up` and the HTTP request returns status `200`. Open `http://localhost:3000`, sign up with a local demo account, log in, and check that the roadmap renders. Frontend logs are available with `docker compose --env-file docker/.env -f docker/compose.yaml logs --tail 50 frontend`.
