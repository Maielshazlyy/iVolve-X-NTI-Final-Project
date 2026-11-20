# Jenkins Shared Library

This library keeps the three service pipelines consistent. Add the library to Jenkins under **Manage Jenkins → System → Global Pipeline Libraries**:

- Name: `ivolve-shared`
- Default version: `main`
- Retrieval method: Git
- Project repository URL: the GitHub clone URL for this repository
- Library path: `jenkins/shared-library`

The service-specific Jenkinsfiles call `serviceCiPipeline`, which validates its configuration and runs the common build, scan, ECR publish, Kubernetes manifest update, and cleanup stages. The implementation is in `vars/`; its README documents each callable step.

Keep the library trusted only for this reviewed project repository. Credentials are loaded by credential ID at runtime and must not be embedded in library source.
