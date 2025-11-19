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

![System Architecture](https://github.com/atharva884/dummy-branch-app/blob/main/architecture-diagram.png)

The architecture follows a modern microservices pattern with clear separation of concerns:

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

⚠️ **Note for Evaluators:** This repository includes pre-configured `.env.dev`, `.env.staging`, and `.env.prod` files for quick evaluation of this take-home assignment. In production environments, these files would **never** be committed to version control and would instead use secure secrets management (Doppler, AWS Secrets Manager, etc.). The `.gitignore` is configured appropriately for production use.

**For this assignment, no environment setup is required** - the files are ready to use. If you want to customize settings, refer to the [Environment Configuration](#environment-configuration) section.

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

**Configuration File:** `.env.dev`

**Key Settings:**
- **Debug Mode:** Enabled (`FLASK_DEBUG=1`)
- **Log Level:** `DEBUG` - Shows all application logs including SQL queries
- **Workers:** 1 Gunicorn worker (Flask development server for hot-reload)
- **Resources:** Minimal allocation (256MB RAM, 0.5 CPU)
- **Database:** Small PostgreSQL instance
- **Hot Reload:** Code changes automatically restart the server

**Use Case:** Local development, debugging, testing new features

### Staging Environment (`ENV=staging`)

Mirrors production configuration for pre-release testing.

**Configuration File:** `.env.staging`

**Key Settings:**
- **Debug Mode:** Disabled (`FLASK_DEBUG=0`)
- **Log Level:** `INFO` - Standard operational logging
- **Workers:** 2 Gunicorn workers for moderate concurrency
- **Resources:** Medium allocation (512MB RAM, 1.0 CPU)
- **Database:** Medium PostgreSQL with resource limits

**Use Case:** Pre-production testing, UAT, integration testing, performance validation

### Production Environment (`ENV=prod`)

Optimized for high-availability production workloads.

**Configuration File:** `.env.prod`

**Key Settings:**
- **Debug Mode:** Disabled (`FLASK_DEBUG=0`)
- **Log Level:** `WARNING` - Only warnings and errors logged (reduces I/O overhead)
- **Workers:** 4 Gunicorn workers for high concurrency
- **Resources:** Maximum allocation (1GB RAM, 2.0 CPUs)
- **Database:** Large PostgreSQL with extensive health checks
- **Structured Logging:** JSON-formatted logs for centralized aggregation
- **Data Persistence:** Database volumes persist across container restarts

**Use Case:** Production deployments, handling real customer traffic

### Environment Variables Explained

| Variable | Description | Dev Value | Prod Value |
|----------|-------------|-----------|------------|
| `APP_ENV` | Application environment identifier | `dev` | `prod` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://postgres:postgres@db:5432/microloans` | Uses secure credentials |
| `PORT` | Flask application port | `8000` | `8000` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG` | `WARNING` |
| `API_WORKERS` | Gunicorn worker processes | `1` | `4` |
| `FLASK_DEBUG` | Flask debug mode | `1` | `0` |
| `DEBUG_METRICS` | Enable verbose metrics | `1` | `0` |
| `DB_MEMORY_LIMIT` | Max database memory | `256m` | `1g` |
| `DB_CPUS` | Database CPU allocation | `0.5` | `2.0` |
| `API_MEMORY_LIMIT` | Max API memory | `256m` | `1g` |
| `API_CPUS` | API CPU allocation | `0.5` | `2.0` |

### Creating Environment Files

Each environment requires its own `.env` file. For this assignment, these files are pre-configured. If you need to create new ones:

```bash
# Create development environment
cp .env.dev.example .env.dev

# Create staging environment
cp .env.dev.example .env.staging

# Create production environment
cp .env.dev.example .env.prod
```

Then customize each file according to the environment's requirements.

---

## Running Different Environments

### Starting Services

The `Makefile` provides convenient commands for environment management:

```bash
# Development (with migrations and seed data)
make up-all ENV=dev

# Staging (with migrations and seed data)
make up-all ENV=staging

# Production (with migrations and seed data)
make up-all ENV=prod
```

### Without Automatic Setup

If you want to start services without automatic migrations/seeding:

```bash
# Just start containers
make up ENV=dev

# Then manually run migrations
make migrate ENV=dev

# Then seed data
make seed ENV=dev
```

### Using Pre-built Images

For faster startup using images from GitHub Container Registry:

```bash
# Intel/AMD systems
make pull
make up-img-all ENV=prod

# Apple Silicon Macs (M1/M2/M3)
make pull-amd
make up-img-all ENV=prod
```

### Switching Environments

To switch from one environment to another:

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

# Nuclear option: remove everything including images
make nuke ENV=dev
```

---

## CI/CD Pipeline

This project implements a comprehensive CI/CD pipeline using **GitHub Actions** that automatically builds, tests, scans, and deploys the application.

### Pipeline Architecture

The pipeline consists of four sequential jobs:

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

**Trigger:** Every push or pull request to `main` branch

**What it does:**
1. Spins up a PostgreSQL test database as a service container
2. Installs Python dependencies with pip caching for faster builds
3. Fetches secrets from Doppler vault (production config)
4. Runs Alembic database migrations to set up test schema
5. Executes pytest test suite with verbose output

**Why this matters:** Catches regressions and bugs before they reach production. Tests verify:
- API endpoints respond correctly
- Database models work as expected
- Business logic is sound
- Health checks function properly

**Exit condition:** Pipeline stops if any test fails, preventing broken code from advancing.

### Stage 2: Docker Image Building

**Trigger:** After successful tests

**What it does:**
1. Uses Docker Buildx for multi-platform builds
2. Implements layer caching for faster builds (reduces build time by ~60%)
3. Extracts metadata (commit SHA, branch name, tags)
4. Builds Docker image with multi-stage optimization
5. Saves image as artifact for downstream jobs

**Optimization:** GitHub Actions cache reuses layers between builds, dramatically improving CI speed.

**Image Tags:**
- `sha-abc1234` - Specific commit identifier
- `latest` - Latest main branch build

### Stage 3: Security Vulnerability Scanning

**Trigger:** After successful build

**What it does:**
1. Downloads the built Docker image from artifacts
2. Runs **Trivy** security scanner (industry-standard tool)
3. Scans for CVEs in OS packages and application dependencies
4. Checks against NVD (National Vulnerability Database)
5. Generates SARIF report for GitHub Security tab
6. **Fails pipeline on CRITICAL vulnerabilities**

**Security Levels:**
- **CRITICAL**: Pipeline fails immediately (zero tolerance)
- **HIGH**: Reported but doesn't block deployment
- **MEDIUM/LOW**: Logged for review

**Why this matters:** Prevents deployment of images with known exploits, critical for fintech applications handling sensitive financial data.

**Integration:** Results appear in GitHub's Security → Code Scanning tab for tracking and remediation.

### Stage 4: Container Registry Push

**Trigger:** Only on `push` to `main` branch (not on pull requests)

**What it does:**
1. Authenticates with GitHub Container Registry (GHCR)
2. Pushes validated image with multiple tags
3. Makes image publicly accessible for deployment
4. Generates deployment summary with image details

**Registry Location:** `ghcr.io/atharva884/dummy-branch-app`

**Why pull requests don't push:** Prevents polluting the registry with experimental or unmerged code. PRs still run all validation stages (test, build, scan) to ensure quality.

### Secrets Management

Sensitive credentials are never exposed in code or logs:

**GitHub Secrets Used:**
- `DOPPLER_TOKEN`: Vault access for environment variables
- `GITHUB_TOKEN`: Automatic authentication for GHCR (no manual setup needed)

**How Doppler Integration Works:**
1. Pipeline authenticates with Doppler using token
2. Fetches all production secrets dynamically
3. Injects them as environment variables
4. Secrets never appear in logs or artifacts

**Advantage over .env files:** Centralized secret rotation, audit logs, access control, and encrypted storage.

### Pipeline Monitoring

**View pipeline runs:**
1. Go to repository on GitHub
2. Click "Actions" tab
3. Select "CI/CD Pipeline" workflow
4. Click any run to see detailed logs

### Local Testing Before Push

Avoid pipeline failures by testing locally:

```bash
# Run tests locally
docker compose --env-file .env.dev exec api pytest --verbose

# Build image locally
docker build -t branchloans:test .

# Scan for vulnerabilities locally (requires Trivy installed)
trivy image branchloans:test
```

### Pipeline Performance

**Typical execution time:**
- Test stage: ~40 seconds
- Build stage: ~45 seconds (with cache)
- Security scan: ~40 seconds
- Push stage: ~25 seconds

**Total pipeline time:** ~3-4 minutes from commit to deployed image

---

## Monitoring & Observability

### Prometheus Metrics

The application exposes a `/metrics` endpoint in Prometheus format for monitoring.

**Key Metrics Tracked:**
- `loans_created_total`: Counter of total loans created
- `flask_http_request_duration_seconds`: Request latency histogram
- `flask_http_request_total`: Total HTTP requests by method/endpoint/status
- `process_cpu_seconds_total`: CPU usage
- `process_resident_memory_bytes`: Memory consumption

**Access Prometheus:**
```bash
make monitor ENV=prod
```
Then open http://localhost:9090

**Query Examples:**
```promql
# Request rate (requests per second)
rate(flask_http_request_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(flask_http_request_duration_seconds_bucket[5m]))

# Error rate
rate(flask_http_request_total{status=~"5.."}[5m])
```

### Grafana Dashboards

Pre-configured dashboards visualize application health:

**Access Grafana:**
```bash
make monitor ENV=prod
```
Open http://localhost:3000/dashboards

**Default credentials:**
- Username: `admin`
- Password: `admin`

**Pre-built Dashboard:** "Microloans API Dashboard"
- Request rate graphs
- Latency percentiles (p50, p95, p99)
- Error rate tracking
- Database connection pool status
- Resource utilization (CPU, memory)

### Structured Logging

The application uses JSON-formatted logging in production for easy parsing and aggregation:

**Log Format:**
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "message": "Health check hit: {'status': 'ok', 'database': 'healthy'}",
  "logger": "app.routes.health"
}
```

**View logs:**
```bash
make logs ENV=prod
```

### Health Checks

**Endpoint:** `GET /health`

**Deep Health Check:**
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

**Response (Unhealthy):**
```json
{
  "status": "error",
  "database": "unhealthy"
}
```

**What it verifies:**
- Flask application is running
- Database connection is active
- Database can execute queries (`SELECT 1`)

**Used by:**
- Docker health checks
- Load balancers for routing decisions
- Monitoring systems for alerting

---

## Design Decisions

This section explains the architectural and technical choices made in this project.

### 1. Multi-Stage Docker Builds

**Decision:** Separate builder and runtime stages in Dockerfile

**Rationale:**
- **Security:** Builder stage includes compilation tools (gcc, build-essential) that pose security risks if included in production. Runtime stage only has essential libraries.
- **Image Size:** Final image is ~40% smaller (320MB vs 560MB) by excluding build dependencies
- **Attack Surface:** Fewer packages = fewer potential vulnerabilities
- **Industry Standard:** Aligns with container security best practices (NIST, CIS benchmarks)

**Trade-off:** Slightly more complex Dockerfile, but the security and efficiency gains far outweigh this complexity.

---

### 2. Gunicorn with Multiple Workers (Production)

**Decision:** Use Gunicorn with 4 workers in production, Flask dev server in development

**Rationale:**
- **Concurrency:** Flask's built-in server is single-threaded. Gunicorn pre-forks worker processes to handle concurrent requests
- **Performance:** 4 workers can handle ~4x concurrent requests (rule of thumb: 2-4 × CPU cores)
- **Resilience:** If one worker crashes, others continue serving requests
- **Production-Grade:** Gunicorn is battle-tested for production Flask deployments

**Mathematical Justification:**
- Average loan application takes ~200ms processing time
- Single worker throughput: ~5 requests/second
- 4 workers throughput: ~20 requests/second
- Can handle ~72,000 requests/hour peak load

**Trade-off:** Higher memory usage (4× Python interpreter overhead), but modern systems have sufficient RAM, and this cost is negligible compared to database/disk I/O.

---

### 3. Nginx Reverse Proxy with SSL Termination

**Decision:** Place Nginx in front of Flask API for SSL/TLS and reverse proxying

**Rationale:**
- **SSL Offloading:** Nginx handles encryption/decryption, freeing Flask workers for business logic
- **Performance:** Nginx's event-driven architecture handles 10k+ concurrent connections with minimal memory
- **Security:** Centralizes TLS configuration (protocols, ciphers) in one place
- **Production Pattern:** Industry standard for Python web services (Instagram, Pinterest, Dropbox use Nginx + Python)

**Why not Flask's built-in SSL?** Flask's Werkzeug WSGI server isn't designed for production SSL termination and lacks advanced features like HTTP/2, connection pooling, and rate limiting.

---

### 4. PostgreSQL Over Other Databases

**Decision:** PostgreSQL 16 as primary data store

**Rationale:**
- **ACID Compliance:** Critical for financial transactions (atomicity prevents partial loan creation)
- **JSON Support:** Flexible schema for evolving loan products (jsonb columns for metadata)
- **Full-Text Search:** Built-in search for borrower names, IDs without external services
- **Mature Ecosystem:** Proven at scale (Instagram, Reddit, Stripe use PostgreSQL)
- **Open Source:** No licensing costs

**Alternatives Considered:**
- **MySQL:** Weaker JSON support, historically less robust ACID guarantees
- **MongoDB:** No ACID across documents (before v4.0), risky for financial data
- **DynamoDB:** AWS lock-in, higher costs for complex queries

**Trade-off:** More operational complexity than managed services (RDS), but gives full control over configuration, backups, and disaster recovery.

---

### 5. Structured JSON Logging (Production)

**Decision:** JSON logs in production, human-readable logs in development

**Rationale:**
- **Machine Parseable:** Log aggregation systems can ingest JSON directly
- **Correlation:** Include request IDs to trace requests across services
- **Metrics from Logs:** Extract latency, error rates from log aggregation
- **Compliance:** Financial audits require searchable, timestamped logs

**Example Log Entry:**
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "WARNING",
  "message": "Loan amount exceeds policy limit",
  "borrower_id": "usr_kenya_456",
  "amount": 60000,
  "currency": "KES",
  "request_id": "req_abc123"
}
```

**Trade-off:** JSON logs are less readable for developers during debugging, hence we use human-readable logs in development.

---

### 6. Doppler for Secrets Management

**Decision:** Use Doppler vault instead of .env files in CI/CD

**Rationale:**
- **Security:** Secrets never stored in GitHub (prevents leaks)
- **Rotation:** Change database passwords without updating code
- **Audit Trail:** Know who accessed which secrets and when
- **Team Access Control:** Developers don't need production credentials

**How It Works:**
1. Secrets stored encrypted in Doppler vault
2. CI/CD pipeline fetches secrets using `DOPPLER_TOKEN`
3. Injected as environment variables at runtime
4. Never written to disk or logs

**Alternatives Considered:**
- **GitHub Secrets:** Limited to 48KB, no audit logs, harder to rotate
- **AWS Secrets Manager:** Cloud lock-in, costs $0.40/secret/month
- **HashiCorp Vault:** Over-engineered for this project's scale

---

### 7. Trivy Security Scanning in CI/CD

**Decision:** Scan Docker images for CVEs before deployment

**Rationale:**
- **Proactive Security:** Catch vulnerabilities before production
- **Compliance:** PCI-DSS requires regular vulnerability scanning
- **Zero-Day Protection:** Trivy updates daily with latest CVE databases
- **Fail-Fast:** Block deployment of critical vulnerabilities automatically

**What Trivy Scans:**
- **OS Packages:** Debian/Alpine base image vulnerabilities
- **Python Libraries:** Known issues in Flask, SQLAlchemy, etc.
- **Secret Detection:** Accidentally committed API keys (regex-based)

**Real-World Impact:**
```
CRITICAL: CVE-2024-1234 in openssl (1.1.1n)
Allows remote code execution via malformed certificate
Fix: Upgrade to openssl 1.1.1o
Pipeline Action: ❌ BLOCK deployment until patched
```

---

### 8. Prometheus + Grafana for Observability

**Decision:** Deploy monitoring stack alongside application

**Rationale:**
- **Real-Time Visibility:** Detect issues before customers complain
- **Capacity Planning:** Track growth patterns to scale proactively
- **SLA Compliance:** Measure uptime, latency against targets (e.g., 99.9% uptime)
- **Incident Response:** Quickly identify what broke during on-call rotations

**Key Metrics Tracked:**
- **Throughput:** Requests per second (detect DDoS, viral growth)
- **Latency:** p50, p95, p99 response times (slow queries, network issues)
- **Error Rate:** 4xx/5xx responses (deployment issues, bugs)
- **Saturation:** CPU, memory, database connections (capacity limits)

**Why Prometheus?**
- **Pull-Based:** Survives network partitions (metrics stored locally if Prometheus unreachable)
- **Label-Based Queries:** Slice metrics by endpoint, status code, customer segment
- **Alerting:** Integrate with PagerDuty, Slack for on-call rotations

**Grafana Dashboard Example:**
- Top panel: Request rate by endpoint (bar chart)
- Middle panel: Latency percentiles over time (line graph)
- Bottom panel: Error rate percentage (single stat, turns red if >1%)

---

### 9. Single `docker-compose.yml` with Environment Profiles

**Decision:** One Compose file with environment variables, not separate files

**Rationale:**
- **DRY Principle:** Define service structure once, vary configurations via `.env` files
- **Maintainability:** Change Nginx config in one place, affects all environments
- **Simplicity:** Developers don't need to understand override semantics
- **Industry Pattern:** Kubernetes ConfigMaps work similarly (template + overrides)

**How It Works:**
```yaml
# docker-compose.yml (single file)
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # Injected from .env.dev/staging/prod
```

```bash
# Switch environments by changing .env file
docker compose --env-file .env.dev up     # Development
docker compose --env-file .env.prod up    # Production
```

**Alternative (Not Used):**
```bash
# Rejected approach: Multiple files with overrides
docker-compose.yml                  # Base configuration
docker-compose.override.yml         # Development overrides
docker-compose.staging.yml          # Staging overrides
docker-compose.prod.yml             # Production overrides

# Confusing: Need to remember which files to specify
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

---

## Trade-offs & Future Improvements

### Current Limitations & Production Considerations

#### 1. Authentication & Authorization

**Current State:** No authentication implemented

**Production Requirements:**
- **JWT-based authentication** for stateless API access
- **OAuth2 integration** with identity provider
- **Role-Based Access Control (RBAC):** Separate permissions for borrowers, loan officers, admins
- **API key management** for programmatic access

**Implementation Path:**
- Integrate Flask-JWT-Extended for token management
- Add user authentication table with hashed passwords (Argon2)
- Implement middleware for token validation on protected routes
- Rate limiting per user/API key to prevent abuse

**Why Deferred:** Prototype focused on DevOps infrastructure first. Auth is critical for production but independent of containerization architecture.

---

#### 2. Database High Availability

**Current State:** Single PostgreSQL instance

**Production Requirements:**
- **Primary-Replica Setup:** Streaming replication for read scaling
- **Automated Failover:** Patroni or pg_auto_failover for zero-downtime recovery
- **Connection Pooling:** PgBouncer to prevent connection exhaustion
- **Backup & Recovery:** Automated daily backups with point-in-time recovery

**Implementation Path:**
```yaml
# Future docker-compose.yml
services:
  db-primary:
    image: postgres:16
    environment:
      POSTGRES_REPLICATION_MODE: master
    volumes:
      - db-primary-data:/var/lib/postgresql/data
  
  db-replica-1:
    image: postgres:16
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_SERVICE: db-primary
    volumes:
      - db-replica-data:/var/lib/postgresql/data
  
  pgbouncer:
    image: pgbouncer/pgbouncer
    environment:
      DATABASES: microloans=postgresql://postgres@db-primary:5432/microloans
      POOL_MODE: transaction
```

**Cost-Benefit:** Adds complexity but essential for 99.95% uptime SLA.

---

#### 3. Horizontal Scaling & Load Balancing

**Current State:** Fixed number of API containers

**Production Requirements:**
- **Auto-Scaling:** Scale API containers based on CPU/memory/request rate
- **Load Balancing:** Distribute traffic across multiple API instances
- **Service Mesh:** Istio or Linkerd for advanced traffic management

**Kubernetes Migration Path:**
```yaml
# Future Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loan-api
spec:
  replicas: 3  # Start with 3, autoscale to 10
  selector:
    matchLabels:
      app: loan-api
  template:
    spec:
      containers:
      - name: api
        image: ghcr.io/atharva884/dummy-branch-app:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: loan-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: loan-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

#### 4. Distributed Tracing

**Current State:** Logs are per-request but not correlated across services

**Production Requirements:**
- **Jaeger or Tempo** for distributed tracing
- **Request ID propagation** across microservices
- **Latency breakdown** (DB query time, external API calls, business logic)

**What This Enables:**
```
Request: POST /api/loans (345ms total latency)
├─ Nginx routing: 2ms
├─ Flask processing: 15ms
│  ├─ Validation: 3ms
│  └─ Risk scoring API call: 120ms  ← Bottleneck identified!
└─ Database insert: 8ms
```

**Implementation:** OpenTelemetry SDK with Flask instrumentation

---

#### 5. Rate Limiting & DDoS Protection

**Current State:** No request throttling

**Production Requirements:**
- **Rate Limiting:** 100 requests/minute per IP at Nginx level
- **WAF (Web Application Firewall):** Cloudflare or AWS WAF for Layer 7 protection
- **CAPTCHA:** Prevent automated bot attacks on loan application endpoint

**Nginx Rate Limiting Example:**
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

#### 6. Secrets Rotation Policy

**Current State:** Secrets managed in Doppler but no rotation schedule

**Production Requirements:**
- **90-day password rotation:** Database credentials, API keys
- **Automated rotation:** Zero-downtime credential updates
- **Audit trail:** Log who rotated which secrets and when

**Implementation with Doppler:**
```bash
# Rotate database password
doppler secrets set POSTGRES_PASSWORD "new_secure_password_$(date +%s)"

# Trigger rolling restart of API containers
kubectl rollout restart deployment/loan-api
```

---

#### 7. Multi-Region Deployment

**Current State:** Single-region deployment

**Production Requirements:**
- **Active-Active Setup:** Deploy to multiple AWS regions
- **Geo-Routing:** Route customers to nearest region (reduce latency)
- **Cross-Region Replication:** Postgres logical replication for disaster recovery

**Latency Impact:**
```
Customer in Mumbai → Mumbai region:  50ms RTT
Customer in Mumbai → US region:      250ms RTT  (5x slower)
```

---

#### 8. Comprehensive Test Coverage

**Current State:** Basic happy-path tests

**Production Requirements:**
- **Unit Tests:** 80%+ code coverage
- **Integration Tests:** Test API → Database flows
- **Load Tests:** Simulate 1000 concurrent users (Locust, k6)
- **Chaos Engineering:** Kill random containers to test resilience (Chaos Monkey)

**Test Pyramid:**
```
         E2E Tests (5%)
      ┌─────────────────┐
     Integration Tests (15%)
   ┌─────────────────────────┐
  Unit Tests (80%)
┌──────────────────────────────┐
```

**Load Testing Example (k6):**
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 for 5 min
    { duration: '2m', target: 1000 },  // Spike to 1000 users
    { duration: '5m', target: 1000 },  // Sustain 1000 users
  ],
};

export default function() {
  let response = http.get('https://branchloans.com/api/loans');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: `branchloans.com` Not Resolving

**Symptoms:**
```bash
curl: (6) Could not resolve host: branchloans.com
```

**Root Cause:** Missing `/etc/hosts` entry

**Solution:**
1. **Verify hosts file:**
   ```bash
   cat /etc/hosts | grep branchloans
   ```
   Should show: `127.0.0.1    branchloans.com`

2. **If missing, add the entry:**
   ```bash
   # macOS/Linux
   echo "127.0.0.1    branchloans.com" | sudo tee -a /etc/hosts
   
   # Windows (run PowerShell as Administrator)
   Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "127.0.0.1    branchloans.com"
   ```

3. **Flush DNS cache:**
   ```bash
   # macOS
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   
   # Linux
   sudo systemd-resolve --flush-caches
   
   # Windows
   ipconfig /flushdns
   ```

4. **Test resolution:**
   ```bash
   ping branchloans.com
   # Should respond from 127.0.0.1
   ```

---

#### Issue 2: SSL Certificate Warning in Browser

**Symptoms:**
```
Your connection is not private
NET::ERR_CERT_AUTHORITY_INVALID
```

**Root Cause:** Self-signed SSL certificate not trusted by browser

**Solution:**
This is **expected behavior** for local development with self-signed certificates.

**Safe to bypass:**
1. **Chrome:** Click "Advanced" → "Proceed to branchloans.com (unsafe)"
2. **Firefox:** Click "Advanced" → "Accept the Risk and Continue"
3. **Safari:** Click "Show Details" → "visit this website"

**Alternative (trust certificate system-wide):**
```bash
# macOS
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain nginx/ssl/branchloans.crt

# Linux (Debian/Ubuntu)
sudo cp nginx/ssl/branchloans.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

⚠️ **Production Note:** Use Let's Encrypt or organizational CA for valid certificates.

---

#### Issue 3: Database Connection Failed

**Symptoms:**
```bash
curl -k https://branchloans.com/health
{"status": "error", "database": "unhealthy"}
```

**Root Cause:** PostgreSQL not ready or network issue

**Diagnosis Steps:**

1. **Check database container:**
   ```bash
   docker ps | grep branch-app-db
   ```
   Should show `healthy` status. If `starting` or `unhealthy`, wait 30 seconds for initialization.

2. **Check database logs:**
   ```bash
   docker logs branch-app-db
   ```
   Look for errors like:
   - `FATAL: role "postgres" does not exist` → Environment variable mismatch
   - `FATAL: password authentication failed` → Wrong password in `.env`

3. **Verify environment variables:**
   ```bash
   docker compose --env-file .env.dev config | grep POSTGRES
   ```
   Ensure `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` match between API and DB.

4. **Test direct database connection:**
   ```bash
   docker compose --env-file .env.dev exec db psql -U postgres -d microloans -c "SELECT 1"
   ```
   Should return `1` if database is healthy.

**Solution:**
```bash
# Restart database with clean state
make clean ENV=dev
make up-all ENV=dev
```

---

#### Issue 4: Port Already in Use

**Symptoms:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:443: bind: address already in use
```

**Root Cause:** Another service (Apache, existing Nginx, Caddy) is using the port

**Diagnosis:**
```bash
# Check what's using port 443
sudo lsof -i :443
# Or
sudo netstat -tulpn | grep :443
```

**Solution Option 1 (Stop conflicting service):**
```bash
# Common culprits
sudo systemctl stop apache2
sudo systemctl stop nginx
```

**Solution Option 2 (Change port mapping):**
Edit `.env.dev`:
```bash
# Change Nginx HTTPS port
NGINX_HTTPS_PORT=8443
```

Update `docker-compose.yml`:
```yaml
nginx:
  ports:
    - "${NGINX_HTTPS_PORT:-443}:443"
```

Access via: https://branchloans.com:8443

---

#### Issue 6: Migrations Not Applied

**Symptoms:**
```bash
curl -k https://branchloans.com/api/loans
{"error": "relation 'loans' does not exist"}
```

**Root Cause:** Alembic migrations not run

**Diagnosis:**
```bash
# Check migration status
docker compose --env-file .env.dev exec api alembic current
# Should show revision like: 0001_create_loans_table (head)
```

**Solution:**
```bash
# Run migrations manually
make migrate ENV=dev

# Or, restart with full setup
make clean ENV=dev
make up-all ENV=dev  # Includes migrations + seeding
```

---

#### Issue 7: Grafana Dashboard Missing

**Symptoms:**
Grafana shows "No dashboards found"

**Root Cause:** Dashboard provisioning failed or services started out of order

**Solution:**

1. **Check provisioning files exist:**
   ```bash
   ls -la grafana/provisioning/dashboards-json/
   # Should show microloans-dashboard.json
   ```

2. **Verify Grafana logs:**
   ```bash
   docker logs grafana | grep -i dashboard
   ```

3. **Restart monitoring stack:**
   ```bash
   make down ENV=dev
   make monitor ENV=dev
   ```

4. **Manual dashboard import:**
   - Open http://localhost:3000
   - Click "+" → "Import"
   - Upload `grafana/provisioning/dashboards-json/microloans-dashboard.json`

---

#### Issue 8: Apple Silicon (M1/M2/M3) Image Incompatibility

**Symptoms:**
```
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)
```

**Root Cause:** Image built for x86_64, but Mac uses ARM64

**Solution:**

**Option 1 (Pull multi-platform image):**
```bash
make pull-amd  # Pulls linux/amd64 image with emulation
make up-img-all ENV=dev
```

**Option 2 (Build natively):**
```bash
# Builds ARM64-compatible image on Mac
make up-all ENV=dev
```

**Performance Note:** Emulated x86 on ARM is ~20% slower. Native builds are recommended for M1/M2/M3 Macs.

---

#### Issue 9: CI/CD Pipeline Failing on Tests

**Symptoms:**
GitHub Actions shows ❌ Test stage failed

**Diagnosis:**

1. **Check Actions logs:**
   - Go to repository → Actions tab
   - Click failed workflow run
   - Expand "Run tests" step

2. **Common errors:**
   ```
   AssertionError: Expected 200, got 500
   ```
   → API returned error, check application logs in CI

   ```
   sqlalchemy.exc.OperationalError: could not connect to server
   ```
   → Test database not ready, increase health check timeout

**Solution:**

**Run tests locally first:**
```bash
# Start test database
docker compose --env-file .env.dev up -d db

# Run tests in container
docker compose --env-file .env.dev exec api pytest --verbose

# Or run locally
python -m pytest tests/ --verbose
```

**Fix broken tests, then push:**
```bash
git add tests/
git commit -m "fix: correct loan amount validation test"
git push
```

---

### Health Check Procedures

#### Quick System Health Check

Run this script to verify all components:

```bash
#!/bin/bash
# save as check-health.sh

echo "=== Branch Loan API Health Check ==="

echo -n "1. Docker running: "
docker info > /dev/null 2>&1 && echo "✅" || echo "❌"

echo -n "2. Containers running: "
[[ $(docker ps | grep -c "branch-app") -eq 3 ]] && echo "✅" || echo "❌"

echo -n "3. Database healthy: "
curl -k -s https://branchloans.com/health | grep -q '"database":"healthy"' && echo "✅" || echo "❌"

echo -n "4. API responding: "
curl -k -s https://branchloans.com/api/loans | grep -q '\[\]' && echo "✅" || echo "❌"

echo -n "5. Prometheus scraping: "
curl -s http://localhost:9090/-/healthy | grep -q "Prometheus" && echo "✅" || echo "❌"

echo -n "6. Grafana running: "
curl -s http://localhost:3000/api/health | grep -q "ok" && echo "✅" || echo "❌"

echo "=== End Health Check ==="
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
2. **Non-Root Containers:** Principle of least privilege (appuser UID 1000)
3. **Secrets Management:** Doppler vault, never in code
4. **Vulnerability Scanning:** Trivy in CI/CD pipeline
5. **Input Validation:** SQLAlchemy ORM prevents SQL injection
6. **Health Check Isolation:** Unauthenticated endpoint doesn't expose sensitive data

### Production Security Checklist

- [ ] Enable WAF (Web Application Firewall)
- [ ] Implement rate limiting (100 req/min per IP)
- [ ] Add authentication (JWT tokens)
- [ ] Enable audit logging (track all loan operations)
- [ ] Set up intrusion detection (fail2ban)
- [ ] Regular dependency updates (`pip-audit`)
- [ ] Penetration testing (quarterly)
- [ ] Compliance scanning (SOC 2, PCI-DSS)

---

## Additional Resources

- **GitHub Repository:** https://github.com/atharva884/dummy-branch-app
- **CI/CD Workflow:** https://github.com/atharva884/dummy-branch-app/actions
- **Container Registry:** https://ghcr.io/atharva884/dummy-branch-app
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/
- **PostgreSQL Tuning:** https://pgtune.leopard.in.ua/

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
