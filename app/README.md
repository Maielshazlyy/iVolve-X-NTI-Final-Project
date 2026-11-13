# Application source

The application source is linked as a Git submodule from the repository provided with the project brief:

<https://github.com/Ibrahim-Adel15/iVolveFinalProject>

The project pins source revision `adda14701d9119b142a767fe1f1d6486e4a8f25a` so the build inputs are reproducible and attribution remains clear.

## Services confirmed from the source files

| Component | Implementation | Port | Purpose |
|---|---|---:|---|
| Frontend | Node.js, Express, EJS | 3000 | Login and roadmap UI |
| Auth service | Python, Flask | 5000 | Signup/login API; stores accounts in MySQL |
| Roadmap service | Java 21, Spring Boot | 8080 | Returns roadmap data |
| Database | MySQL 8 | 3306 | Stores authentication data |

The upstream README describes the Auth and Roadmap service languages in reverse. The Docker build contexts and Compose configuration in this project follow the actual source tree and Dockerfiles.

Initialize the submodule when cloning this project:

```bash
git clone --recurse-submodules https://github.com/Maielshazlyy/iVolve-X-NTI-Final-Project.git
```
