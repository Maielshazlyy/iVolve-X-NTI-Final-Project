def call(Map config = [:]) {
    ['serviceName', 'manifestPath', 'image'].each { key ->
        if (!config[key]) {
            error("updateKubernetesManifest requires '${key}'")
        }
    }

    def serviceName = config.serviceName.toString()
    def manifestPath = config.manifestPath.toString()
    def image = config.image.toString()
    def imageTag = image.substring(image.lastIndexOf(':') + 1)

    withEnv([
        "SERVICE_NAME=${serviceName}",
        "MANIFEST_PATH=${manifestPath}",
        "IMAGE_URI=${image}",
        "IMAGE_TAG=${imageTag}"
    ]) {
        withCredentials([usernamePassword(
            credentialsId: 'github-manifest-push',
            usernameVariable: 'GITHUB_USERNAME',
            passwordVariable: 'GITHUB_TOKEN'
        )]) {
            sh '''#!/bin/sh
set -eu

test -f "$MANIFEST_PATH"
sed -i -E "s|(image:[[:space:]]*).*|\\1${IMAGE_URI}|" "$MANIFEST_PATH"
grep -F "image: ${IMAGE_URI}" "$MANIFEST_PATH" >/dev/null
git diff --check

git config user.name "iVolve Jenkins"
git config user.email "jenkins[bot]@users.noreply.github.com"
git add -- "$MANIFEST_PATH"
if git diff --cached --quiet; then
  echo "Manifest already references ${IMAGE_URI}; no commit needed."
  exit 0
fi

git commit -m "Deploy ${SERVICE_NAME} image ${IMAGE_TAG}"
askpass="$(mktemp)"
trap 'rm -f "$askpass"' EXIT
cat > "$askpass" <<'ASKPASS'
#!/bin/sh
case "$1" in
  *Username*) printf '%s\n' "$GITHUB_USERNAME" ;;
  *) printf '%s\n' "$GITHUB_TOKEN" ;;
esac
ASKPASS
chmod 700 "$askpass"
GIT_ASKPASS="$askpass" GIT_TERMINAL_PROMPT=0 git push origin HEAD:main
'''
        }
    }
}
