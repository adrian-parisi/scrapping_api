# Docker Development Environment

This document describes how to use the Docker Compose setup for local development of the ZenRows API.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

### Starting the Development Environment

```bash
# Start all services
./scripts/dev.sh start

# Or use docker-compose directly
docker-compose up -d
```

### Accessing the Services

- **API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **PostgreSQL**: localhost:5432
  - Database: `zenrows_api`
  - Username: `zenrows_user`
  - Password: `zenrows_password`

## Development Script

The `scripts/dev.sh` script provides convenient commands for managing the development environment:

```bash
# Start the development environment
./scripts/dev.sh start

# Stop the development environment
./scripts/dev.sh stop

# Restart the development environment
./scripts/dev.sh restart

# View logs from all services
./scripts/dev.sh logs

# View logs from API service only
./scripts/dev.sh logs-api

# View logs from PostgreSQL service only
./scripts/dev.sh logs-db

# Open a shell in the API container
./scripts/dev.sh shell

# Open a PostgreSQL shell
./scripts/dev.sh db-shell

# Show status of all services
./scripts/dev.sh status

# Clean up everything (removes all containers and volumes)
./scripts/dev.sh clean

# Show help
./scripts/dev.sh help
```

## Services

### PostgreSQL Database

- **Image**: postgres:15-alpine
- **Port**: 5432
- **Database**: zenrows_api
- **Username**: zenrows_user
- **Password**: zenrows_password
- **Health Check**: Built-in PostgreSQL health check
- **Volume**: Persistent data storage

### API Application

- **Image**: Built from local Dockerfile
- **Port**: 8080
- **Environment Variables**:
  - `DATABASE_URL`: Automatically configured to connect to PostgreSQL
  - `API_KEY_PEPPER`: Set to `dev-pepper-key-change-in-production`
- **Dependencies**: Waits for PostgreSQL to be healthy before starting
- **Restart Policy**: `unless-stopped`

### Database Initialization

- **Service**: db-init
- **Purpose**: Runs database migrations and seeds initial data
- **Dependencies**: Waits for PostgreSQL to be healthy
- **Tasks**:
  1. Runs Alembic migrations (`alembic upgrade head`)
  2. Seeds the database with templates (`python scripts/seed_templates.py`)

## Environment Variables

### Development Environment

The following environment variables are automatically set in the Docker Compose environment:

```yaml
DATABASE_URL: postgresql://zenrows_user:zenrows_password@postgres:5432/zenrows_api
API_KEY_PEPPER: dev-pepper-key-change-in-production
```

### Production Environment

For production deployment, you should override these variables:

```bash
docker-compose up -d -e DATABASE_URL="your-production-db-url" -e API_KEY_PEPPER="your-secure-pepper"
```

## Database Management

### Running Migrations

Migrations are automatically run during the `db-init` service. To run them manually:

```bash
# Open a shell in the API container
./scripts/dev.sh shell

# Run migrations
poetry run alembic upgrade head
```

### Seeding Data

Templates are automatically seeded during the `db-init` service. To seed manually:

```bash
# Open a shell in the API container
./scripts/dev.sh shell

# Seed templates
poetry run python scripts/seed_templates.py
```

### Database Shell

Access the PostgreSQL database directly:

```bash
# Using the development script
./scripts/dev.sh db-shell

# Or using docker-compose directly
docker-compose exec postgres psql -U zenrows_user -d zenrows_api
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8080 or 5432
   lsof -i :8080
   lsof -i :5432
   
   # Stop the conflicting service or change ports in docker-compose.yml
   ```

2. **Database Connection Issues**
   ```bash
   # Check if PostgreSQL is healthy
   docker-compose ps
   
   # Check PostgreSQL logs
   ./scripts/dev.sh logs-db
   ```

3. **API Not Starting**
   ```bash
   # Check API logs
   ./scripts/dev.sh logs-api
   
   # Check if all environment variables are set
   docker-compose exec api env | grep -E "(DATABASE_URL|API_KEY_PEPPER)"
   ```

4. **Clean Start**
   ```bash
   # Stop and remove everything
   ./scripts/dev.sh clean
   
   # Start fresh
   ./scripts/dev.sh start
   ```

### Logs

View logs from different services:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f db-init
```

## Development Workflow

1. **Start the environment**: `./scripts/dev.sh start`
2. **Make code changes** in your local files
3. **Rebuild the API** if needed: `docker-compose up -d --build api`
4. **View logs**: `./scripts/dev.sh logs-api`
5. **Test the API**: Visit http://localhost:8080/docs
6. **Stop when done**: `./scripts/dev.sh stop`

## Production Considerations

This Docker Compose setup is designed for **local development only**. For production:

1. Use environment-specific configuration
2. Set secure passwords and API keys
3. Use proper secrets management
4. Configure proper networking and security
5. Use production-grade PostgreSQL configuration
6. Set up proper monitoring and logging
