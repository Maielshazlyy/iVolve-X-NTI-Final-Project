def call(Map config = [:]) {
    ['serviceName', 'sourceImage', 'repository'].each { key ->
        if (!config[key]) {
            error("pushImageToEcr requires '${key}'")
        }
    }

    sh """#!/bin/sh
set -eu
account_id=\$(aws sts get-caller-identity --query Account --output text)
registry=\${account_id}.dkr.ecr.\${AWS_REGION}.amazonaws.com
build_tag=\${registry}/${config.repository}:\${IMAGE_TAG}
latest_tag=\${registry}/${config.repository}:latest
aws ecr get-login-password --region "\${AWS_REGION}" | docker login --username AWS --password-stdin "\${registry}"
docker tag '${config.sourceImage}' "\${build_tag}"
docker push "\${build_tag}"
docker tag '${config.sourceImage}' "\${latest_tag}"
docker push "\${latest_tag}"
"""
}
