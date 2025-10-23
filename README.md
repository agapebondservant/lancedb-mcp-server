## LanceDB MCP server

This is a basic, serverless MCP server that uses LanceDB to store and retrieve data.

(Forked from: <a href="https://github.com/lancedb/lancedb-mcp-server/"  target="_blank">Original LanceDB MCP Repo</a>)

It provides 1 tool:
* Retrieve docs

## Installation

### Build Docker image
```
source .env
podman login -u ${DOCKER_USERNAME}${DOCKER_USERNAME_SUFFIX} -p ${DOCKER_PASSWORD} ${DOCKER_HOST}
podman build -t ${DOCKER_HOST}/${DOCKER_USERNAME}/lancedb-mcp-server:latest .
podman push ${DOCKER_HOST}/${DOCKER_USERNAME}/lancedb-mcp-server:latest
```

Deploy to Openshift
```
oc new-project mcpserver
oc create secret generic mcp-server-secret --from-env-file .env
oc get secret mcp-server-secret -oyaml > k8s/mcp-server-secret.yaml
oc create secret docker-registry quay-creds --docker-server=quay.io --docker-username=${DOCKER_USERNAME}${DOCKER_USERNAME_SUFFIX} --docker-password=${DOCKER_PASSWORD} --docker-email=${DOCKER_EMAIL}
oc apply -f k8s/deployment.yaml
```
