# LensCove – Azure Deployment (Lab Documentation)

> **Scope**: This document describes a **lab / learning deployment** of LensCove on Azure.  
> It is intended for transparency, reproducibility, and future reference.
>
> ⚠️ **Security disclaimer**  
> - All secrets, passwords, and keys are **redacted**.  

---

## Architecture Overview

This deployment uses:

- **Azure Container Registry (ACR)** – private container image storage
- **Azure Container Instances (ACI)** – container runtime
- **Azure Files** – persistent volumes (media, static, db, Caddy data)
- **Azure Database for PostgreSQL – Flexible Server** – managed database

Images are built for **linux/amd64** only, as ACI does not support `arm64` images.

---

## 1. Azure CLI Authentication

```bash
az login
```

### Issue (macOS)
Safari failed to complete the OAuth redirect back to `localhost`.

### Fix
Use device-code authentication:

```bash
az login --use-device-code
```

---

## 2. Tenant & MFA Resolution

### Error
```
AADSTS50076: MFA required
No subscriptions found
```

### Fix
Explicitly authenticate against the correct tenant:

```bash
az logout
az account clear
az login --use-device-code --tenant <TENANT_ID>
az account list -o table
```

> ℹ️ Tenant IDs are **not secrets**, but should still not be published verbatim.

---

## 3. Resource Group

```bash
az group create \
  --name lenscove-lab \
  --location northeurope
```

---

## 4. Required Resource Providers

```bash
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.ContainerInstance
az provider register --namespace Microsoft.Storage
```

Verify registration:

```bash
az provider show \
  --namespace Microsoft.ContainerInstance \
  --query "registrationState" \
  -o tsv
```

---

## 5. Azure Container Registry (ACR)

```bash
az acr create \
  --resource-group lenscove-lab \
  --name lenscovelabacr \
  --sku Basic \
  --location northeurope
```

```bash
az acr update \
  --name lenscovelabacr \
  --admin-enabled true
```

Login:

```bash
az acr login --name lenscovelabacr
```

> ⚠️ **Security note**  
> Prefer a Service Principar with `AcrPull` / `AcrPush` roles instead. 

---

## 6. Build & Push Application Image (linux/amd64)

### Problem
Local builds on Apple Silicon produced `linux/arm64` images, unsupported by ACI.

### Solution
Use Docker Buildx to force `linux/amd64`:

```bash
docker buildx create --use || true
docker buildx inspect --bootstrap

Docker buildx build \
  --platform linux/amd64 \
  -t lenscovelabacr.azurecr.io/lenscove-web:<TAG> \
  --push .
```

---

## 7. Docker Hub Pull Reliability

### Issue
ACI intermittently failed to pull images directly from Docker Hub.

### Fix
Import base images into ACR:

```bash
az acr import \
  --name lenscovelabacr \
  --source docker.io/library/postgres:16 \
  --image postgres:16

az acr import \
  --name lenscovelabacr \
  --source docker.io/library/caddy:alpine \
  --image caddy:alpine
```

This ensures ACI pulls **only from ACR**.

---

## 8. Azure Storage (Azure Files)

```bash
az storage account create \
  --name lenscovelabstorage \
  --resource-group lenscove-lab \
  --location northeurope \
  --sku Standard_LRS \
  --kind StorageV2
```

Create file shares:

```bash
az storage share create --name media        --account-name lenscovelabstorage --account-key <REDACTED>
az storage share create --name staticfiles  --account-name lenscovelabstorage --account-key <REDACTED>
az storage share create --name pgdata       --account-name lenscovelabstorage --account-key <REDACTED>
az storage share create --name caddydata    --account-name lenscovelabstorage --account-key <REDACTED>
```

---

## 9. Azure Container Instances (ACI)

```bash
az container create \
  --resource-group lenscove-lab \
  --file lenscove-aci.yml
```

### Networking Note
All containers in the same ACI group share **localhost networking**.

---

## 10. Azure Database for PostgreSQL (Flexible Server)

### Create (lab configuration)

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
  --admin-password <REDACTED>
```

> ⚠️ **Security note**  
> `0.0.0.0` **only for testing**.

---

### Create application database

```bash
az postgres flexible-server db create \
  --resource-group lenscove-lab \
  --server-name lenscove-pg-lab \
  --database-name lenscove_dev
```

### Retrieve hostname

```bash
az postgres flexible-server show \
  --resource-group lenscove-lab \
  --name lenscove-pg-lab \
  --query "fullyQualifiedDomainName" \
  -o tsv
```

---

## 11. SSL Enforcement (Required)

Django database options:

```python
"OPTIONS": {
    "sslmode": "require",
}
```

ACI environment variable:

```yaml
- name: POSTGRES_SSLMODE
  value: require
```

---

## 12. Useful ACI Commands

Get public FQDN:

```bash
az container show \
  -g lenscove-lab \
  -n lenscove-lab-aci \
  --query ipAddress.fqdn \
  -o tsv
```

Logs:

```bash
az container logs -g lenscove-lab -n lenscove-lab-aci --container-name web
az container logs -g lenscove-lab -n lenscove-lab-aci --container-name caddy
```

Delete ACI (stop billing):

```bash
az container delete -g lenscove-lab -n lenscove-lab-aci
```

---

## 13. Pre-Push Local Validation Against Azure PostgreSQL

### Allow local IP (temporary)

```bash
az postgres flexible-server firewall-rule create \
  --resource-group lenscove-lab \
  --name lenscove-pg-lab \
  --rule-name allow-local-dev \
  --start-ip-address <YOUR_PUBLIC_IP> \
  --end-ip-address <YOUR_PUBLIC_IP>
```

Get IP:

```bash
curl ifconfig.me
```

---

### Local container run

```bash
docker run --rm -it \
  -p 8000:8000 \
  --env-file .env.azure \
  lenscovelabacr.azurecr.io/lenscove-web:<TAG>
```

Optional DB connectivity check:

```bash
docker run --rm -it \
  --platform linux/amd64 \
  -p 8000:8000 \
  --env-file .env.azure \
  lenscovelabacr.azurecr.io/lenscove-web:<TAG> \
  sh -c "python -c 'print(\"DB OK\")' && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000"
```

---

### Cleanup firewall rule

```bash
az postgres flexible-server firewall-rule delete \
  --resource-group lenscove-lab \
  --name lenscove-pg-lab \
  --rule-name allow-local-dev
```

---

## Summary

This lab deployment demonstrated:

- Azure CLI authentication edge cases
- ARM vs AMD64 container compatibility
- ACR-first image strategy
- Docker Hub reliability mitigation
- Persistent storage with Azure Files
- Migration to managed PostgreSQL
- SSL enforcement
- Cost control via stop/start

