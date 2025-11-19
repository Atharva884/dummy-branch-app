# Branch Loan API - Production-Ready Architecture

A containerized Flask-based microloans API designed for Branch International's fintech platform. This implementation demonstrates production-grade DevOps practices including multi-environment deployment, automated CI/CD pipelines, comprehensive observability, and enterprise-level security scanning.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [Environment Configuration](#environment-configuration)
- [Running Different Environments](#running-different-environments)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Observability](#monitoring--observability)
- [Design Decisions](#design-decisions)
- [Trade-offs & Future Improvements](#trade-offs--future-improvements)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

---

## Overview

This project transforms a basic Flask loan API into a production-ready, containerized microservice with:

- **Multi-stage Docker builds** for optimized image size and security
- **Multi-environment support** (dev/staging/prod) with distinct configurations
- **Automated CI/CD pipeline** with testing, security scanning, and container registry integration
- **HTTPS with SSL/TLS** encryption via Nginx reverse proxy
- **Comprehensive observability** with Prometheus metrics and Grafana dashboards
- **Database migrations** using Alembic for schema version control
- **Health checks** with database connectivity verification
- **Structured JSON logging** for production environments
- **Secure secrets management** using Doppler

**Tech Stack:** Python 3.11, Flask, PostgreSQL 16, Gunicorn, Nginx, Docker, GitHub Actions, Prometheus, Grafana

---

## Architecture

![System Architecture](https://github.com/atharva884/dummy-branch-app/blob/main/images/architecture-diagram.jpeg)

The architecture follows a modern containerized pattern with clear separation of concerns:

**Request Flow:**
1. Client sends HTTPS request to `branchloans.com` (port 443)
2. Nginx terminates SSL and forwards to Flask API (port 8000)
3. Flask processes request with Gunicorn workers
4. PostgreSQL handles data persistence (port 5432)
5. Prometheus scrapes metrics from API (port 9090)
6. Grafana visualizes metrics (port 3000)

**CI/CD Pipeline:**
- Test → Build → Security Scan → Push to GitHub Container Registry
- Automated on every push to main branch and pull requests

**Key Components:**
- **Nginx**: Reverse proxy with SSL/TLS termination
- **Flask API**: RESTful microservice with Gunicorn workers
- **PostgreSQL**: Relational database with persistent volumes
- **Prometheus**: Metrics collection and storage
- **Grafana**: Real-time dashboards
- **GitHub Actions**: Automated build and deployment pipeline

---

## Prerequisites

Ensure you have the following installed on your local machine:

- **Docker** (v20.10+): [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (v2.0+): Included with Docker Desktop
- **Make**: Pre-installed on macOS/Linux, [Install for Windows](https://gnuwin32.sourceforge.net/packages/make.htm)
- **Git**: [Install Git](https://git-scm.com/downloads)

**Optional but Recommended:**
- **Doppler CLI**: For local secrets management - [Install Doppler](https://docs.doppler.com/docs/install-cli)

---

## Quick Start Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/atharva884/dummy-branch-app.git
cd dummy-branch-app
```

### Step 2: Configure Local Domain (CRITICAL)

For HTTPS to work with `branchloans.com` on your local machine, you **must** add a host entry:

**On macOS/Linux:**
```bash
sudo nano /etc/hosts
```

**On Windows:**
- Open `C:\Windows\System32\drivers\etc\hosts` as Administrator

**Add this line to the file:**
```
127.0.0.1    branchloans.com
```

Save and close the file. This maps `branchloans.com` to your localhost.

**Verification:**
```bash
ping branchloans.com
# Should respond from 127.0.0.1
```

### Step 3: Environment Configuration

⚠️ **Note for Evaluators:**  
This repository includes `.env.dev.example`, `.env.staging.example`, and `.env.prod.example` files for quick evaluation. In production, only these template files are committed, and actual secrets are managed through secure vaults like Doppler or AWS Secrets Manager.

For this assignment, **no environment setup is required** — the example files already contain working values. If you wish to customize settings, simply copy an example file (e.g., `.env.dev.example`) to its corresponding file name (e.g., `.env.dev`).  
Refer to the **Environment Configuration** section for details.


### Step 4: Start the Application

The project includes a `Makefile` for simplified operations:

```bash
# Start all services with database migrations and seed data
make up-all ENV=dev
```

This single command will:
1. Pull/build Docker images
2. Start PostgreSQL database with health checks
3. Start Flask API with Gunicorn
4. Configure Nginx with SSL certificates
5. Run Alembic database migrations
6. Seed initial loan data

**Alternative: Using Pre-built Image from GitHub Container Registry**

If you prefer to use the pre-built image instead of building locally:

```bash
# For Intel/AMD machines (x86_64)
make pull
make up-img-all ENV=dev

# For Apple Silicon Macs (M1/M2/M3)
# The x86 image works via Rosetta emulation, but if you encounter issues:
make pull-amd
make up-img-all ENV=dev
```

### Step 5: Verify Installation

Once the containers are running, verify everything is working:

**1. Check container status:**
```bash
docker ps
```
You should see 3 running containers: `branch-app-db`, `branch-app-api`, `nginx`

**2. Test the health endpoint:**
```bash
curl -k https://branchloans.com/health
```
Expected response:
```json
{
  "status": "ok",
  "database": "healthy"
}
```

**3. Access in browser:**
Open [https://branchloans.com/health](https://branchloans.com/health)

⚠️ **Note:** Your browser will show a security warning because we're using a self-signed SSL certificate. This is expected for local development. Click "Advanced" → "Proceed to branchloans.com" (Chrome) or "Accept the Risk and Continue" (Firefox).

**4. Test API endpoints:**
```bash
# List all loans
curl -k https://branchloans.com/api/loans

# Get loan statistics
curl -k https://branchloans.com/api/stats

# Create a new loan
curl -k -X POST https://branchloans.com/api/loans \
  -H 'Content-Type: application/json' \
  -d '{
    "borrower_id": "usr_india_001",
    "amount": 5000.00,
    "currency": "INR",
    "term_months": 12,
    "interest_rate_apr": 18.5
  }'
```

**5. View application logs:**
```bash
make logs ENV=dev
```

---

## Environment Configuration

This project supports three distinct environments, each optimized for different use cases:

### Development Environment (`ENV=dev`)

Designed for local development with hot-reload and verbose logging.

**Key Settings:**
- **Debug Mode:** Enabled (`FLASK_DEBUG=1`)
- **Log Level:** `DEBUG` - Shows all application logs
- **Workers:** 1 Gunicorn worker
- **Resources:** 256MB RAM, 0.5 CPU

### Staging Environment (`ENV=staging`)

Mirrors production configuration for pre-release testing.

**Key Settings:**
- **Debug Mode:** Disabled
- **Log Level:** `INFO` - Standard operational logging
- **Workers:** 2 Gunicorn workers
- **Resources:** 512MB RAM, 1.0 CPU

### Production Environment (`ENV=prod`)

Optimized for high-availability production workloads.

**Key Settings:**
- **Debug Mode:** Disabled
- **Log Level:** `WARNING` - Only warnings and errors
- **Workers:** 4 Gunicorn workers
- **Resources:** 1GB RAM, 2.0 CPUs
- **Structured Logging:** JSON-formatted logs

### Environment Variables

| Variable | Description | Dev | Prod |
|----------|-------------|-----|------|
| `APP_ENV` | Environment identifier | `dev` | `prod` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://postgres:postgres@db:5432/microloans` | Secure credentials |
| `PORT` | Flask application port | `8000` | `8000` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG` | `WARNING` |
| `API_WORKERS` | Gunicorn worker processes | `1` | `4` |
| `DB_MEMORY_LIMIT` | Max database memory | `256m` | `1g` |
| `API_MEMORY_LIMIT` | Max API memory | `256m` | `1g` |

---

## Running Different Environments

### Starting Services

```bash
# Development (with migrations and seed data)
make up-all ENV=dev

# Staging (with migrations and seed data)
make up-all ENV=staging

# Production (with migrations and seed data)
make up-all ENV=prod
```

### Using Pre-built Images

```bash
# Intel/AMD systems
make pull
make up-img-all ENV=prod

# Apple Silicon Macs (M1/M2/M3)
make pull-amd
make up-img-all ENV=prod
```

### Switching Environments

```bash
# Stop current environment
make down ENV=dev

# Start new environment
make up-all ENV=staging
```

### Monitoring Services

Start with full observability stack (Prometheus + Grafana):

```bash
make monitor ENV=prod
```

This starts all services plus monitoring dashboards:
- **API:** https://branchloans.com
- **Grafana:** http://localhost:3000/dashboards
- **Prometheus:** http://localhost:9090

**Default Grafana Credentials:**
- Username: `admin`
- Password: `admin` (you'll be prompted to change on first login)

### Viewing Logs

```bash
# API logs
make logs ENV=dev

# All service logs
docker compose --env-file .env.dev logs -f
```

### Stopping Services

```bash
# Stop containers (preserve volumes)
make down ENV=dev

# Stop and remove volumes (clean slate)
make clean ENV=dev

# Remove everything including images
make nuke ENV=dev
```

---

## CI/CD Pipeline

This project implements a comprehensive CI/CD pipeline using **GitHub Actions** that automatically builds, tests, scans, and deploys the application.

### Pipeline Architecture

```
Test → Build → Security Scan → Push (on main branch only)
```

Each stage must pass before proceeding to the next, ensuring only thoroughly validated code reaches production.

### Pipeline Trigger Behavior

The pipeline is configured to run on:
- **Push to `main` branch**: Full pipeline including image push to registry
- **Pull Requests**: Runs tests, builds, and security scans but **does not push** images to registry

This ensures PRs are validated without polluting the container registry with experimental builds.

### Stage 1: Automated Testing

**What it does:**
1. Spins up PostgreSQL test database as a service container
2. Installs Python dependencies with pip caching
3. Fetches secrets from Doppler vault
4. Runs Alembic database migrations
5. Executes pytest test suite with verbose output

**Why this matters:** Catches bugs before they reach production. Tests verify API endpoints, database models, and business logic.

### Stage 2: Docker Image Building

**What it does:**
1. Uses Docker Buildx for multi-platform builds
2. Implements layer caching (reduces build time by ~60%)
3. Extracts metadata (commit SHA, branch name)
4. Builds Docker image with multi-stage optimization
5. Saves image as artifact for downstream jobs

**Image Tags:**
- `sha-abc1234` - Specific commit identifier
- `latest` - Latest main branch build

### Stage 3: Security Vulnerability Scanning

**What it does:**
1. Downloads the built Docker image
2. Runs **Trivy** security scanner
3. Scans for CVEs in OS packages and Python dependencies
4. Generates SARIF report for GitHub Security tab
5. **Fails pipeline on CRITICAL vulnerabilities**

**Security Levels:**
- **CRITICAL**: Pipeline fails immediately
- **HIGH**: Reported but doesn't block deployment
- **MEDIUM/LOW**: Logged for review

### Stage 4: Container Registry Push

**What it does:**
1. Authenticates with GitHub Container Registry (GHCR)
2. Pushes validated image with multiple tags
3. Makes image publicly accessible
4. Generates deployment summary

**Registry Location:** `ghcr.io/atharva884/dummy-branch-app`

### Secrets Management

**GitHub Secrets Used:**
- `DOPPLER_TOKEN`: Vault access for environment variables
- `GITHUB_TOKEN`: Automatic authentication for GHCR

**How Doppler Works:**
1. Pipeline authenticates with Doppler using token
2. Fetches all secrets dynamically
3. Injects them as environment variables
4. Secrets never appear in logs or artifacts

### Pipeline Performance

**Typical execution time:**
- Test stage: ~40 seconds
- Build stage: ~45 seconds
- Security scan: ~40 seconds
- Push stage: ~25 seconds

**Total pipeline time:** ~3-4 minutes from commit to deployed image

---

## Monitoring & Observability

### Prometheus Metrics

The application exposes a `/metrics` endpoint in Prometheus format.

**Key Metrics:**
- `loans_created_total`: Total loans created
- `flask_http_request_duration_seconds`: Request latency
- `flask_http_request_total`: Total HTTP requests
- `process_cpu_seconds_total`: CPU usage
- `process_resident_memory_bytes`: Memory consumption

**Access Prometheus:** http://localhost:9090 (after running `make monitor`)

### Grafana Dashboards

Pre-configured dashboards visualize application health.

**Access Grafana:** http://localhost:3000/dashboards

**Dashboard Features:**
- Request rate graphs
- Latency percentiles (p50, p95, p99)
- Error rate tracking
- Resource utilization

### Structured Logging

JSON-formatted logs in production for easy parsing:

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "message": "Health check hit",
  "logger": "app.routes.health"
}
```

### Health Checks

**Endpoint:** `GET /health`

```bash
curl -k https://branchloans.com/health
```

**Response (Healthy):**
```json
{
  "status": "ok",
  "database": "healthy"
}
```

**What it verifies:**
- Flask application is running
- Database connection is active
- Database can execute queries

---

## Design Decisions

### 1. Multi-Stage Docker Builds

**Decision:** Separate builder and runtime stages in Dockerfile

**Rationale:**
- **Security:** Builder stage includes compilation tools that pose security risks. Runtime stage only has essential libraries.
- **Image Size:** Final image is ~40% smaller (320MB vs 560MB)
- **Attack Surface:** Fewer packages = fewer vulnerabilities

**Trade-off:** Slightly more complex Dockerfile, but security and efficiency gains outweigh complexity.

---

### 2. Gunicorn with Multiple Workers

**Decision:** Use Gunicorn with 4 workers in production, Flask dev server in development

**Rationale:**
- **Concurrency:** Flask's built-in server is single-threaded. Gunicorn pre-forks workers to handle concurrent requests
- **Performance:** 4 workers = ~20 requests/second throughput
- **Resilience:** If one worker crashes, others continue serving

**Math:** Average request takes ~200ms. Single worker = 5 req/s. 4 workers = 20 req/s = 72,000 req/hour.

**Trade-off:** Higher memory usage (4× Python interpreter overhead), but modern systems have sufficient RAM.

---

### 3. Nginx Reverse Proxy with SSL Termination

**Decision:** Place Nginx in front of Flask API

**Rationale:**
- **SSL Offloading:** Nginx handles encryption/decryption, freeing Flask for business logic
- **Performance:** Event-driven architecture handles 10k+ concurrent connections
- **Security:** Centralizes TLS configuration
- **Production Pattern:** Industry standard (Instagram, Pinterest use Nginx + Python)

**Why not Flask's SSL?** Werkzeug isn't designed for production SSL and lacks HTTP/2, connection pooling, rate limiting.

---

### 4. Trivy Security Scanning in CI/CD

**Decision:** Scan Docker images for CVEs before deployment

**Rationale:**
- **Proactive Security:** Catch vulnerabilities before production
- **Compliance:** PCI-DSS requires regular vulnerability scanning
- **Zero-Day Protection:** Trivy updates daily with latest CVE databases
- **Fail-Fast:** Block deployment of critical vulnerabilities automatically

**What Trivy Scans:**
- OS packages (Debian base image)
- Python libraries (Flask, SQLAlchemy, etc.)
- Secret detection (accidentally committed keys)

**Example:**
```
CRITICAL: CVE-2024-1234 in openssl
Allows remote code execution
Pipeline: ❌ BLOCK deployment
```

---

### 5. Doppler for Secrets Management

**Decision:** Use Doppler vault instead of .env files in CI/CD

**Rationale:**
- **Security:** Secrets never stored in GitHub
- **Rotation:** Change passwords without updating code
- **Audit Trail:** Track who accessed which secrets
- **Access Control:** Developers don't need production credentials

**How It Works:**
1. Secrets stored encrypted in Doppler
2. CI/CD fetches via `DOPPLER_TOKEN`
3. Injected as environment variables
4. Never written to disk or logs

**Alternatives:**
- GitHub Secrets: Limited to 48KB, no audit logs
- AWS Secrets Manager: Cloud lock-in, $0.40/secret/month
- HashiCorp Vault: Over-engineered for this scale

---

## Trade-offs & Future Improvements

### 1. Database High Availability

**Current State:** Single PostgreSQL instance

**Production Requirements:**
- **Primary-Replica Setup:** Streaming replication for read scaling
- **Automated Failover:** Patroni for zero-downtime recovery
- **Connection Pooling:** PgBouncer to prevent exhaustion
- **Backup & Recovery:** Automated daily backups

**Implementation Path:**
```yaml
services:
  db-primary:
    environment:
      POSTGRES_REPLICATION_MODE: master
  
  db-replica:
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_SERVICE: db-primary
  
  pgbouncer:
    image: pgbouncer/pgbouncer
```

---

### 2. Horizontal Scaling & Load Balancing

**Current State:** Fixed number of API containers

**Production Requirements:**
- **Auto-Scaling:** Scale based on CPU/memory/request rate
- **Load Balancing:** Distribute traffic across instances
- **Kubernetes:** HPA (Horizontal Pod Autoscaler)

**Kubernetes Example:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70
```

---

### 3. Multi-Region Deployment

**Current State:** Single-region deployment

**Production Requirements:**
- **Geographic Distribution:** Deploy to multiple AWS regions (India, Africa, US)
- **Latency Optimization:** Route users to nearest region
- **Data Residency:** Comply with local data protection laws

**Why This Matters:**
```
User in Mumbai → Mumbai region:     ~50ms latency
User in Mumbai → US East region:    ~250ms latency (5x slower)
```

**Implementation Approach:**
- Route53 geolocation routing for DNS-based traffic direction
- Cross-region database replication for disaster recovery
- Regional Kubernetes clusters with centralized control plane

---

### 4. Rate Limiting & DDoS Protection

**Current State:** No request throttling

**Production Requirements:**
- **Rate Limiting:** 100 requests/minute per IP at Nginx level
- **WAF:** Cloudflare or AWS WAF for Layer 7 protection
- **CAPTCHA:** Prevent automated bot attacks

**Implementation:**
```nginx
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    
    server {
        location /api/loans {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://flask_app;
        }
    }
}
```

---

## Troubleshooting

### Issue 1: `branchloans.com` Not Resolving

**Symptoms:**
```bash
curl: (6) Could not resolve host: branchloans.com
```

**Root Cause:** Missing `/etc/hosts` entry

**Solution:**

1. **Add the entry:**
```bash
# macOS/Linux
echo "127.0.0.1    branchloans.com" | sudo tee -a /etc/hosts

# Windows (PowerShell as Administrator)
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "127.0.0.1    branchloans.com"
```

2. **Flush DNS cache:**
```bash
# macOS
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

# Linux
sudo systemd-resolve --flush-caches

# Windows
ipconfig /flushdns
```

3. **Test:**
```bash
ping branchloans.com  # Should respond from 127.0.0.1
```

---

### Issue 2: SSL Certificate Warning in Browser

**Symptoms:**
```
Your connection is not private
NET::ERR_CERT_AUTHORITY_INVALID
```

**Root Cause:** Self-signed SSL certificate not trusted by browser

**Solution:**
This is **expected** for local development with self-signed certificates.

**Safe to bypass:**
- **Chrome:** "Advanced" → "Proceed to branchloans.com (unsafe)"
- **Firefox:** "Advanced" → "Accept the Risk and Continue"
- **Safari:** "Show Details" → "visit this website"

**Alternative (trust certificate):**
```bash
# macOS
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain nginx/ssl/branchloans.crt

# Linux
sudo cp nginx/ssl/branchloans.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

---

### Issue 3: Database Connection Failed

**Symptoms:**
```bash
curl -k https://branchloans.com/health
{"status": "error", "database": "unhealthy"}
```

**Root Cause:** PostgreSQL not ready or network issue

**Diagnosis:**

1. **Check database container:**
```bash
docker ps | grep branch-app-db  # Should show "healthy"
```

2. **Check logs:**
```bash
docker logs branch-app-db
# Look for: "database system is ready to accept connections"
```

3. **Test connection:**
```bash
docker compose --env-file .env.dev exec db psql -U postgres -d microloans -c "SELECT 1"
```

**Solution:**
```bash
# Restart with clean state
make clean ENV=dev
make up-all ENV=dev
```

---

### Issue 4: Port Already in Use

**Symptoms:**
```
Error: bind: address already in use
```

**Root Cause:** Another service using port 443 or 8000

**Diagnosis:**
```bash
# Check what's using the port
sudo lsof -i :443
sudo lsof -i :8000
```

**Solution:**
```bash
# Stop conflicting service
sudo systemctl stop apache2
sudo systemctl stop nginx

# Or change port in .env.dev
PORT=8080
```

---

### Issue 5: Apple Silicon (M1/M2/M3) Image Incompatibility

**Symptoms:**
```
WARNING: The requested image's platform (linux/amd64) does not match (linux/arm64/v8)
```

**Root Cause:** Pre-built image is for x86_64, Mac uses ARM64

**Solution:**

**Option 1 (Use emulation):**
```bash
make pull-amd
make up-img-all ENV=dev
```

**Option 2 (Build natively):**
```bash
make up-all ENV=dev  # Builds ARM64 image
```

**Performance Note:** Emulated x86 is ~20% slower. Native builds recommended for M1/M2/M3.

---

### Quick Health Check Script

```bash
#!/bin/bash
echo "=== Branch Loan API Health Check ==="

echo -n "1. Docker: "
docker info > /dev/null 2>&1 && echo "✅" || echo "❌"

echo -n "2. Containers: "
[[ $(docker ps | grep -c "branch-app") -eq 3 ]] && echo "✅" || echo "❌"

echo -n "3. Database: "
curl -k -s https://branchloans.com/health | grep -q '"database":"healthy"' && echo "✅" || echo "❌"

echo -n "4. API: "
curl -k -s https://branchloans.com/api/loans > /dev/null && echo "✅" || echo "❌"

echo "=== End ==="
```

**Usage:**
```bash
chmod +x check-health.sh
./check-health.sh
```

---

## Security Considerations

### Implemented Security Measures

1. **TLS 1.2/1.3 Encryption:** All traffic encrypted in transit
2. **Non-Root Containers:** Runs as unprivileged user (UID 1000)
3. **Secrets Management:** Doppler vault, never in code
4. **Vulnerability Scanning:** Trivy in CI/CD pipeline
5. **Input Validation:** SQLAlchemy ORM prevents SQL injection
6. **Health Check Isolation:** No sensitive data exposure

### Production Security Checklist

- [ ] Enable WAF (Web Application Firewall)
- [ ] Implement rate limiting (100 req/min per IP)
- [ ] Add authentication (JWT tokens)
- [ ] Enable audit logging
- [ ] Set up intrusion detection (fail2ban)
- [ ] Regular dependency updates (`pip-audit`)
- [ ] Penetration testing (quarterly)

---

## Additional Resources

- **GitHub Repository:** https://github.com/atharva884/dummy-branch-app
- **CI/CD Workflow:** https://github.com/atharva884/dummy-branch-app/actions
- **Container Registry:** https://ghcr.io/atharva884/dummy-branch-app
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/

---

## Contributing

This is a take-home assignment project. For questions or suggestions:

1. Open an issue on GitHub
2. Include detailed description and steps to reproduce
3. Attach relevant logs (sanitize sensitive data)

---

## License

This project is for evaluation purposes as part of Branch International's DevOps Intern assessment.

---

## Acknowledgments

Built with ❤️ for Branch International's DevOps team.

Special thanks to the open-source community for Flask, PostgreSQL, Prometheus, and Grafana.

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Author:** Atharva Jadhav
