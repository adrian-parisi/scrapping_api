#!/bin/bash

# ZenRows API Development Script
# This script helps manage the Docker Compose development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "ZenRows API Development Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the development environment"
    echo "  stop      Stop the development environment"
    echo "  restart   Restart the development environment"
    echo "  logs      Show logs from all services"
    echo "  logs-api  Show logs from API service only"
    echo "  logs-db   Show logs from PostgreSQL service only"
    echo "  shell     Open a shell in the API container"
    echo "  db-shell  Open a PostgreSQL shell"
    echo "  clean     Stop and remove all containers and volumes"
    echo "  status    Show status of all services"
    echo "  help      Show this help message"
    echo ""
}

# Function to start the development environment
start_dev() {
    print_status "Starting ZenRows API development environment..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Start services
    docker-compose up -d postgres
    print_status "Waiting for PostgreSQL to be ready..."
    sleep 10
    
    # Run database initialization
    print_status "Initializing database..."
    docker-compose up db-init
    
    # Start API service
    print_status "Starting API service..."
    docker-compose up -d api
    
    print_success "Development environment started!"
    print_status "API available at: http://localhost:8080"
    print_status "API docs available at: http://localhost:8080/docs"
    print_status "PostgreSQL available at: localhost:5432"
}

# Function to stop the development environment
stop_dev() {
    print_status "Stopping development environment..."
    docker-compose down
    print_success "Development environment stopped!"
}

# Function to restart the development environment
restart_dev() {
    print_status "Restarting development environment..."
    stop_dev
    start_dev
}

# Function to show logs
show_logs() {
    docker-compose logs -f
}

# Function to show API logs
show_api_logs() {
    docker-compose logs -f api
}

# Function to show database logs
show_db_logs() {
    docker-compose logs -f postgres
}

# Function to open shell in API container
open_shell() {
    print_status "Opening shell in API container..."
    docker-compose exec api /bin/bash
}

# Function to open database shell
open_db_shell() {
    print_status "Opening PostgreSQL shell..."
    docker-compose exec postgres psql -U zenrows_user -d zenrows_api
}

# Function to clean up everything
clean_dev() {
    print_warning "This will remove all containers, volumes, and data. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up development environment..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_success "Development environment cleaned!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show status
show_status() {
    print_status "Development environment status:"
    docker-compose ps
}

# Main script logic
case "${1:-help}" in
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    restart)
        restart_dev
        ;;
    logs)
        show_logs
        ;;
    logs-api)
        show_api_logs
        ;;
    logs-db)
        show_db_logs
        ;;
    shell)
        open_shell
        ;;
    db-shell)
        open_db_shell
        ;;
    clean)
        clean_dev
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
