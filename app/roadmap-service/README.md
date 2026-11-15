# Roadmap API

This Java 21 and Spring Boot service returns the DevOps training roadmap as JSON. The frontend calls `GET /api/roadmap` using the internal Compose address `http://roadmap-service:8080`.

## Build and run locally

The project uses Maven. Docker Compose first runs Maven in the `roadmap-builder` service, which writes the packaged JAR to `target/`. The local Compose image then copies that JAR and starts it with Java. See [`docker/README.md`](../../docker/README.md) for the full workflow.

- `pom.xml` — Spring Boot dependencies and build configuration.
- `src/main/java/` — application entry point and roadmap controller.
- `Dockerfile` — multistage image intended for CI builds.
- `Dockerfile.local` — Compose runtime image for the locally built JAR.

The API does not use MySQL; the database is used by the Auth service.
