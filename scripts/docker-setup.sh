#!/bin/bash

# Docker Setup Script for Catalyst Center Templates
# This script helps you set up and run the application in Docker

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p data logs output
    mkdir -p templates/{network,security,automation,monitoring,community}
    print_success "Directories created"
}

# Build and run the application
run_application() {
    local mode=${1:-production}
    
    if [ "$mode" = "development" ]; then
        print_status "Starting application in development mode..."
        docker-compose -f docker-compose.dev.yml up --build
    else
        print_status "Starting application in production mode..."
        docker-compose up --build -d
    fi
}

# Stop the application
stop_application() {
    print_status "Stopping application..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    print_success "Application stopped"
}

# Show logs
show_logs() {
    local mode=${1:-production}
    
    if [ "$mode" = "development" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f catalyst-templates
    fi
}

# Clean up Docker resources
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v
    docker-compose -f docker-compose.dev.yml down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Show help
show_help() {
    echo "Catalyst Center Templates Docker Setup"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup           Set up the application (create directories, build images)"
    echo "  start           Start the application in production mode"
    echo "  start-dev       Start the application in development mode"
    echo "  stop            Stop the application"
    echo "  logs            Show application logs"
    echo "  logs-dev        Show development logs"
    echo "  cleanup         Clean up Docker resources"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup        # Initial setup"
    echo "  $0 start        # Start in production"
    echo "  $0 start-dev    # Start in development"
    echo "  $0 logs         # View logs"
    echo "  $0 cleanup      # Clean up everything"
}

# Main script logic
case "${1:-help}" in
    setup)
        check_docker
        create_directories
        print_success "Setup completed! You can now run '$0 start' or '$0 start-dev'"
        ;;
    start)
        check_docker
        run_application production
        ;;
    start-dev)
        check_docker
        run_application development
        ;;
    stop)
        stop_application
        ;;
    logs)
        show_logs production
        ;;
    logs-dev)
        show_logs development
        ;;
    cleanup)
        cleanup
        ;;
    help|*)
        show_help
        ;;
esac
