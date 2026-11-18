def call(Map config = [:]) {
    ['serviceName', 'context', 'image'].each { key ->
        if (!config[key]) {
            error("buildAndScanImage requires '${key}'")
        }
    }

    sh "docker build --pull -t '${config.image}' '${config.context}'"
    // Report findings without blocking the initial integration; a severity gate
    // can be enabled after the baseline image findings are reviewed.
    sh "trivy image --no-progress --exit-code 0 '${config.image}'"
}
