# LensCove — DNS + HTTPS on Azure ACI

This document captures the working configuration to expose LensCove running on **Azure Container Instances (ACI)** behind **Caddy** with **Let’s Encrypt** certificates, and a **Cloudflare**-managed domain.

Target:
- `https://lens-cove.com`
- `https://www.lens-cove.com`

---

## 1) Architecture

```
Internet
  ├─ HTTP 80  ───────────────▶ Caddy (ACI)
  └─ HTTPS 443 ──────────────▶ Caddy (ACI)
                                ├─ serves /media/* from Azure File Share
                                └─ reverse_proxy to Gunicorn/Django on localhost:8000
```

- **TLS termination**: Caddy (Let’s Encrypt)
- **Cert storage**: Azure File Share mounted at `/data` in Caddy container
- **App**: Django/Gunicorn binds `0.0.0.0:8000` in the `web` container
- **DNS**: Cloudflare CNAME records (initially DNS-only)

---

## 2) Cloudflare DNS configuration

In Cloudflare → **DNS**:

### Required records

| Type  | Name | Target | Proxy | TTL |
|------|------|--------|-------|-----|
| CNAME | `@`   | `<ACI FQDN>` | **DNS only** (grey cloud) | Auto |
| CNAME | `www` | `lens-cove.com` | **DNS only** (grey cloud) | Auto |


### Remove conflicts
Ensure there are **no extra** `A`/`AAAA`/duplicate records for `@` that point elsewhere.

---

## 3) Azure resources required

Ensure to have:
- Resource group
- ACI container group
- Azure Files shares:
  - `caddydata` (for certificates / ACME storage)
  - `media` (user/admin uploads)
  - `staticfiles` (Django collected static)

---

## 4) Caddyfile

This is the Caddyfile that should be used in the **caddy** container:

```caddyfile
{
  email admin@lens-cove.com
  storage file_system /data
}

lens-cove.com, www.lens-cove.com {
  encode gzip

  # Serve uploaded media directly (Azure File share mounted at /srv/media)
  handle_path /media/* {
    root * /srv/media
    file_server
  }

  # Everything else goes to Django/Gunicorn
  reverse_proxy localhost:8000
}
```

What this does:
- Automatically obtains and renews Let’s Encrypt certs for both hostnames.
- Persists ACME data/certs under `/data` (Azure File Share).
- Serves `/media/*` directly from the `media` share.
- Proxies all other paths to Django.

---

## 5) Django production settings

### A) `ALLOWED_HOSTS`
Must include both hostnames and the ACI FQDN for troubleshooting:

```
ALLOWED_HOSTS=lens-cove.com,www.lens-cove.com,<ACI_FQDN>
```

### B) `CSRF_TRUSTED_ORIGINS`
```
CSRF_TRUSTED_ORIGINS=https://lens-cove.com,https://www.lens-cove.com
```

### C) Security flags
```
SECURE_SSL_REDIRECT=1
CSRF_COOKIE_SECURE=1
SESSION_COOKIE_SECURE=1
```

### D) Proxy header (required behind Caddy)
In settings file, add:
```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```


---

## 7) ACI container group YAML (reference)

Below is a reference pattern matching your current approach (secrets removed).

Key points:
- **Expose 80 and 443** on the container group.
- **Caddy container exposes 80 and 443**.
- **Mount caddydata to /data** and **media to /srv/media** in Caddy container.
- Web container runs migrations + collectstatic + gunicorn.
- Use the domain-based Caddyfile (not `:80` only).



## 9) Final checklist

- [x] Cloudflare DNS: `@` and `www` set, no conflicting records
- [x] ACI exposes ports 80 + 443
- [x] Caddy container exposes ports 80 + 443
- [x] Caddy mounts `/data` (caddydata) and `/srv/media` (media)
- [x] Caddyfile uses `lens-cove.com, www.lens-cove.com` (not `:80`)
- [x] Django: `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` correct
- [x] Django: secure flags enabled for production
- [x] Django: DEBUG not forced true
- [x] Branding URLs use the public domain over HTTPS
