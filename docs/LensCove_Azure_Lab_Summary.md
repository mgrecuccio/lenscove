# LensCove – Azure Lab Deployment Summary

This document summarizes the steps taken to deploy the LensCove application on Azure using Azure Container Instances (ACI), Azure Container Registry (ACR), and Azure Files, including all Azure CLI commands used and the issues encountered along the way.

The goal of this lab is to deploy a production-like containerized setup while remaining cost-conscious and fully reversible.

---

## 1. Azure CLI Login

```bash
az login
```

### Issue
On macOS, Safari failed to complete the OAuth redirect back to `localhost`, resulting in a broken page.

### Fix
Use device code authentication:

```bash
az login --use-device-code
```

---

## 2. MFA / Tenant Issue

### Error
```
AADSTS50076: MFA required
No subscriptions found
```

### Fix
Log in explicitly to the correct tenant:

```bash
az logout
az account clear
az login --use-device-code --tenant <TENANT_ID>
az account list -o table
```

---

## 3. Resource Group

```bash
az group create --name lenscove-lab --location northeurope
```

---

## 4. Register Required Resource Providers

```bash
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.ContainerInstance
az provider register --namespace Microsoft.Storage
```

Check status:

```bash
az provider show --namespace Microsoft.ContainerInstance --query "registrationState" -o tsv
```

---

## 5. Azure Container Registry (ACR)

```bash
az acr create --resource-group lenscove-lab --name lenscovelabacr --sku Basic --location northeurope

az acr update --name lenscovelabacr --admin-enabled true
az acr login --name lenscovelabacr
```

---

## 6. Build and Push lenscove-web (Linux amd64)

### Issue
Image was built as `linux/arm64`, unsupported by ACI.

### Fix
Rebuild using Buildx:

```bash
docker buildx create --use || true
docker buildx inspect --bootstrap

docker buildx build --platform linux/amd64   -t lenscovelabacr.azurecr.io/lenscove-web:0.1.2   --push .
```

---

## 7. Docker Hub Pull Failures

### Issue
ACI failed to pull `postgres` and `caddy` from Docker Hub.

### Fix
Import images into ACR:

```bash
az acr import --name lenscovelabacr --source docker.io/library/postgres:16 --image postgres:16
az acr import --name lenscovelabacr --source docker.io/library/caddy:alpine --image caddy:alpine
```

---

## 8. Azure Storage & File Shares

```bash
az storage account create   --name lenscovelabstorage   --resource-group lenscove-lab   --location northeurope   --sku Standard_LRS   --kind StorageV2
```

Create file shares:

```bash
az storage share create --name media --account-name lenscovelabstorage --account-key <KEY>
az storage share create --name staticfiles --account-name lenscovelabstorage --account-key <KEY>
az storage share create --name pgdata --account-name lenscovelabstorage --account-key <KEY>
az storage share create --name caddydata --account-name lenscovelabstorage --account-key <KEY>
```

---

## 9. ACI Deployment

```bash
az container create -g lenscove-lab --file lenscove-aci.yml
```

### Networking Note
Containers in the same ACI group share `localhost`.

---

## 10. PostgreSQL and Azure Files: Why the Original Approach Failed

(see canvas document for full explanation)

---

## 11. Azure Database for PostgreSQL (Managed)

### 11.1 Create the cheapest PostgreSQL Flexible Server

```bash
az postgres flexible-server create \
  --resource-group lenscove-lab \
  --name lenscove-pg-lab \
  --location northeurope \
  --tier Burstable \
  --sku-name Standard_B1ms \
  --storage-size 32 \
  --version 16 \
  --backup-retention 7 \
  --public-access 0.0.0.0 \
  --admin-user lenscove \
  --admin-password <STRONG_PASSWORD>
```

---

### 11.2 Create the application database

```bash
az postgres flexible-server db create \
  --resource-group lenscove-lab \
  --server-name lenscove-pg-lab \
  --database-name lenscove_dev
```

---

### 11.3 Get PostgreSQL hostname

```bash
az postgres flexible-server show \
  --resource-group lenscove-lab \
  --name lenscove-pg-lab \
  --query "fullyQualifiedDomainName" \
  -o tsv
```

---

### 11.4 Ensure Django uses SSL

Django setting:

```python
"OPTIONS": {
    "sslmode": "require",
}
```

ACI env var:

```yaml
- name: POSTGRES_SSLMODE
  value: require
```

---

### 11.5 Stop / Start PostgreSQL

```bash
az postgres flexible-server stop   --resource-group lenscove-lab   --name lenscove-pg-lab
```

```bash
az postgres flexible-server start   --resource-group lenscove-lab   --name lenscove-pg-lab
```

---

### 11.5 Delete PostgreSQL and verify it's gone

```bash
az postgres flexible-server delete \
  --resource-group lenscove-lab \
  --name lenscove-pg-lab \
  --yes
```

```bash
az postgres flexible-server list \
  --resource-group lenscove-lab \
  -o table
```

---

## 12. ACI – Useful Commands

### Get public hostname

```bash
az container show   -g lenscove-lab   -n lenscove-lab-aci   --query ipAddress.fqdn   -o tsv
```

### Logs

```bash
az container logs -g lenscove-lab -n lenscove-lab-aci --container-name web
az container logs -g lenscove-lab -n lenscove-lab-aci --container-name caddy
```

### Delete ACI (stop billing)

```bash
az container delete -g lenscove-lab -n lenscove-lab-aci
```

---

## 13. Run the LensCove container locally against Azure PostgreSQL (pre-push validation)

Before pushing a new Docker image to ACR and redeploying Azure Container Instances, it is strongly recommended to validate the container locally while connecting to the Azure-managed PostgreSQL database.
This ensures:
database connectivity works
SSL is correctly enforced
migrations succeed
no runtime configuration errors exist

### 13.1 Allow local IP access to Azure PostgreSQL

Azure Database for PostgreSQL uses firewall rules. Temporarily allow your current public IP:

```bash
az postgres flexible-server firewall-rule create \
  --resource-group lenscove-lab \
  --name lenscove-pg-lab \
  --rule-name allow-local-dev \
  --start-ip-address <YOUR_PUBLIC_IP> \
  --end-ip-address <YOUR_PUBLIC_IP>
```

Your public IP can be obtained via:

```bash
curl ifconfig.me
```

### 13.2 Export environment variables locally

Configure the same environment variables used in production:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
export SECRET_KEY="<SECRET_KEY>"
export ALLOWED_HOSTS="localhost,127.0.0.1"

export POSTGRES_DB="lenscove_dev"
export POSTGRES_USER="lenscove"
export POSTGRES_PASSWORD="ciao"
export POSTGRES_HOST="lenscove-pg-lab.postgres.database.azure.com"
export POSTGRES_PORT="5432"
export POSTGRES_SSLMODE="require"
```

### 13.3 Run the container locally

Run the LensCove container image locally, connecting to Azure PostgreSQL:

```bash
docker run --rm -it \
  -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE \
  -e SECRET_KEY \
  -e ALLOWED_HOSTS \
  -e POSTGRES_DB \
  -e POSTGRES_USER \
  -e POSTGRES_PASSWORD \
  -e POSTGRES_HOST \
  -e POSTGRES_PORT \
  -e POSTGRES_SSLMODE \
  lenscovelabacr.azurecr.io/lenscove-web:0.1.2
```

You can also specify the env file to be used:

```bash
docker run --rm -it \
  -p 8000:8000 \
  --env-file .env.azure \
  lenscovelabacr.azurecr.io/lenscove-web:0.1.2
```

If you need to get extra-info about the DB connection:

```bash
docker run --rm -it \
  --platform linux/amd64 \
  -p 8000:8000 \
  --env-file .env.azure \
  lenscovelabacr.azurecr.io/lenscove-web:0.1.2 \
  sh -c "python -c 'import os, psycopg; psycopg.connect(host=os.environ[\"POSTGRES_HOST\"], user=os.environ[\"POSTGRES_USER\"], password=os.environ[\"POSTGRES_PASSWORD\"], dbname=os.environ[\"POSTGRES_DB\"], sslmode=os.environ.get(\"POSTGRES_SSLMODE\",\"require\")).close(); print(\"DB OK\")' && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 120 --log-level debug"
```

### 13.4 Validate application behavior

Verify the following:
- Application starts without errors
- Django successfully connects to Azure PostgreSQL
- Migrations run correctly
- Gunicorn starts and listens on port 8000
- Application is reachable at: http://localhost:8000
- Optional hardening check:

```bash
docker exec -it <container_id> python manage.py check --deploy
```

If the application works locally with Azure PostgreSQL, it is safe to:
build a new image tag
push it to ACR
redeploy Azure Container Instances

### 13.5 Clean up firewall rule (recommended)

Once validation is complete, remove the temporary firewall rule:

```bash
az postgres flexible-server firewall-rule delete \
  --resource-group lenscove-lab \
  --name lenscove-pg-lab \
  --rule-name allow-local-dev
```

## Summary

This lab covered:
- Azure CLI authentication pitfalls
- Resource provider registration
- Container image architecture compatibility
- Docker Hub reliability issues
- ACR-first image strategy
- Azure Files persistence limits
- Migration to Azure Database for PostgreSQL
- SSL enforcement
- Cost control via stop/start
