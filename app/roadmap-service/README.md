# Roadmap API

This Java 21 and Spring Boot service returns the DevOps training roadmap as JSON. The frontend calls `GET /api/roadmap` using the internal Compose address `http://roadmap-service:8080`.

## Build and run locally

The project uses Maven. Docker Compose first runs Maven in the `roadmap-builder` service, which writes the packaged JAR to `target/`. The local Compose image then copies that JAR and starts it with Java. See [`docker/README.md`](../../docker/README.md) for the full workflow.

- `pom.xml` — Spring Boot dependencies and build configuration.
- `src/main/java/` — application entry point and roadmap controller.
- `Dockerfile` — multistage image intended for CI builds.
- `Dockerfile.local` — Compose runtime image for the locally built JAR.

The API does not use MySQL; the database is used by the Auth service.

The roadmap API is internal to the Compose/Kubernetes network. From the repository root with the Compose stack running, request it from the frontend container:

```powershell
docker compose --env-file docker/.env -f docker/compose.yaml exec frontend node -e "fetch('http://roadmap-service:8080/api/roadmap').then(r => r.text()).then(console.log).catch(err => { console.error(err); process.exit(1) })"
```

Expected result: JSON describing the roadmap topics. The browser-level check is to sign in and confirm the roadmap page displays its cards. See the root [`app/README.md`](../README.md) for the application request flow.
