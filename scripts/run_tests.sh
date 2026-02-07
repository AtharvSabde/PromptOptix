#!/bin/bash

# PromptOptimizer Pro - Test Runner Script
# Runs all tests with coverage reporting

set -e

echo "🧪 PromptOptimizer Pro - Test Runner"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo "ℹ $1"
}

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_error "Virtual environment not activated!"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Navigate to backend directory
cd backend

# Run tests with coverage
echo "Running tests with coverage..."
echo ""

if pytest tests/ \
    --cov=. \
    --cov-report=html \
    --cov-report=term-missing \
    --verbose \
    --color=yes \
    --tb=short; then
    
    print_success "All tests passed!"
    echo ""
    
    # Show coverage summary
    echo "======================================"
    echo "Coverage Report"
    echo "======================================"
    coverage report
    
    echo ""
    print_info "HTML coverage report generated: backend/htmlcov/index.html"
    print_info "Open it in your browser to see detailed coverage"
    
else
    print_error "Tests failed!"
    exit 1
fi

echo ""
echo "======================================"
print_success "Test run complete! 🎉"
echo "======================================"