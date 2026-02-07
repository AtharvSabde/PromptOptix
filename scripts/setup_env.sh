#!/bin/bash

# PromptOptimizer Pro - Environment Setup Script
# This script automates the setup process for development

set -e  # Exit on error

echo "🎯 PromptOptimizer Pro - Setup Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo "ℹ $1"
}

# Check Python version
echo "Step 1: Checking Python version..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        print_success "Python $PYTHON_VERSION detected"
    else
        print_error "Python 3.11+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi
echo ""

# Check if virtual environment exists
echo "Step 2: Setting up virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        print_info "Deleted existing virtual environment"
    else
        print_info "Using existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment ready"
fi
echo ""

# Activate virtual environment
echo "Step 3: Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"
echo ""

# Upgrade pip
echo "Step 4: Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded to latest version"
echo ""

# Install dependencies
echo "Step 5: Installing dependencies..."
print_info "This may take a few minutes..."
cd backend
if pip install -r requirements.txt > /dev/null 2>&1; then
    print_success "All dependencies installed"
else
    print_error "Failed to install dependencies"
    print_info "Try running: pip install -r backend/requirements.txt"
    exit 1
fi
cd ..
echo ""

# Setup environment file
echo "Step 6: Configuring environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Created .env file from template"
    print_warning "IMPORTANT: You must edit .env and add your API keys!"
    echo ""
    print_info "Required API keys:"
    echo "  1. ANTHROPIC_API_KEY - Get from: https://console.anthropic.com/settings/keys"
    echo "  2. GROQ_API_KEY (optional) - Get from: https://console.groq.com/keys"
    echo ""
    read -p "Do you want to open .env for editing now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if command -v nano &>/dev/null; then
            nano .env
        elif command -v vim &>/dev/null; then
            vim .env
        elif command -v vi &>/dev/null; then
            vi .env
        else
            print_warning "No text editor found. Please manually edit .env file"
        fi
    fi
else
    print_warning ".env file already exists (not overwriting)"
    print_info "If you need to reset it, delete .env and run this script again"
fi
echo ""

# Create necessary directories
echo "Step 7: Creating project directories..."
mkdir -p data/test_prompts
mkdir -p data/benchmark_results
mkdir -p backend/logs
mkdir -p backend/cache
print_success "Project directories created"
echo ""

# Validate configuration
echo "Step 8: Validating configuration..."
cd backend
if python3 -c "from config import Config; errors = Config.validate(); exit(0 if not errors else 1)" 2>/dev/null; then
    print_success "Configuration is valid"
else
    print_warning "Configuration validation failed - you may need to add API keys"
fi
cd ..
echo ""

# Summary
echo "======================================"
echo "🎉 Setup Complete!"
echo "======================================"
echo ""
print_info "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Make sure you've added your API keys to .env file"
echo ""
echo "  3. Start the development server:"
echo "     cd backend && python app.py"
echo ""
echo "  4. The API will be available at: http://localhost:5000"
echo ""
echo "  5. Run tests:"
echo "     pytest backend/tests/"
echo ""
print_info "Documentation:"
echo "  - README.md - Project overview"
echo "  - docs/API.md - API documentation"
echo "  - docs/SURVEY_ALIGNMENT.md - Research mapping"
echo ""
print_success "Happy coding! 🚀"