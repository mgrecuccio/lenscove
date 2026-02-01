# Changelog

All notable changes to this project will be documented in this file.

---

## [0.1.4] — 2026-02-01
### 🔧 Release Automation via GitHub Actions

### Added
- Automated release and deployment pipeline
  - Releases are created automatically from Git tags
  - Linux/amd64 Docker images are built via CI and published to Azure Container Registry
- Azure Deployment documentation
  - `docs/azure-aci-lab.md` describing the LensCove deployment process
  - `docs/azure-dns-configuration.md` for the Cloudflare and Azure DNS/HTTPS configuration
- `docs/contributing.md` to explain how to contribute


---

## [0.1.2] — 2026-01-24
### 🔧 Third Public MVP Release

#### Added
- `.dockerignore` to exclude local and runtime-only files from Docker images

#### Changed
- Refactored Docker setup for production readiness
  - Dockerfile now uses a multi-stage build to reduce image size
  - `docker-compose.prod.yml` uses named volumes only (no bind mounts)
  - `makemigrations` removed from production startup sequence

---

## [0.1.1] — 2026-01-07
### 🔧 Second Public MVP Release

#### Added
- Production-ready Docker Compose configuration for deployment
- Dedicated production Django settings file (`prod.py`)
- Support for real SMTP configuration for production email delivery

#### Changed
- Refactored order confirmation email system
  - SMTP settings now configurable via environment variables
  - Improved and cleaner HTML email template for customer communications

---

## [0.1.0] — 2025-11-16
### 🎉 First Public MVP Release

#### Added
- Curated image collections browsing
- Product detail page with dimension and frame customization
- Session-based shopping cart
- Checkout flow with Order + OrderItem models
- Online payment processing using Mollie
- Payment webhooks for order status updates
- Shipping label creation via Shippo
- Shipment tracking with Shippo webhook integration
- PDF invoice generation using ReportLab
- Email notifications (customer + admin)
- Full Django Admin interface
- Dockerized backend (Django + PostgreSQL)
- `.env`-based configuration
- CI-friendly in-memory SQLite tests
- Comprehensive README with setup instructions

---

## [Unreleased]
### Planned
- User accounts and order history
- Wishlist / favorites
- Promo codes
- Search functionality
- Multi-language support

### AI-Powered Features (Planned)

#### Automatic Image Metadata Extraction
- Suggested title generation
- Tags and keywords extraction
- Color palette detection
- Object and theme recognition
- Orientation and composition analysis

#### AI-Based Product Descriptions
- Poetic or modern product descriptions
- Short marketing preview texts
- SEO-optimized keywords
- Admin-side regeneration support

#### Smart Size and Frame Recommendations
- Popular size recommendations
- Frame suggestions based on image colors
- Matching frame sets for gallery walls

#### Similar Image Suggestions
- Visual similarity search using embeddings
- "You may also like" recommendations to increase discovery

#### AI Customer Assistant
- Help with size and frame selection
- Shipping and delivery questions
- Order status lookup
- Art curation via conversational search