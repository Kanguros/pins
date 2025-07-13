#!/bin/bash
# Build script for Policy Inspector documentation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$SCRIPT_DIR"
SOURCE_DIR="$DOCS_DIR/source"
BUILD_DIR="$DOCS_DIR/build"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v poetry &> /dev/null; then
        log_error "Poetry is not installed. Please install Poetry first."
        exit 1
    fi
    
    # Check if in virtual environment or poetry env
    if ! poetry run python -c "import sphinx" &> /dev/null; then
        log_error "Sphinx not found. Please install documentation dependencies:"
        echo "  poetry install --with docs"
        exit 1
    fi
    
    log_info "Dependencies check passed."
}

clean_build() {
    log_info "Cleaning build directory..."
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"
    log_info "Clean complete."
}

build_html() {
    log_info "Building HTML documentation..."
    
    cd "$DOCS_DIR"
    if poetry run sphinx-build -b html "$SOURCE_DIR" "$BUILD_DIR/html"; then
        log_info "HTML documentation built successfully."
        echo "  📁 Output: $BUILD_DIR/html/index.html"
    else
        log_error "HTML build failed."
        exit 1
    fi
}

build_html_strict() {
    log_info "Building HTML documentation (strict mode - warnings as errors)..."
    
    cd "$DOCS_DIR"
    if poetry run sphinx-build -W -b html "$SOURCE_DIR" "$BUILD_DIR/html"; then
        log_info "HTML documentation built successfully (strict mode)."
        echo "  📁 Output: $BUILD_DIR/html/index.html"
    else
        log_error "HTML build failed in strict mode."
        exit 1
    fi
}

check_links() {
    log_info "Checking external links..."
    
    cd "$DOCS_DIR"
    if poetry run sphinx-build -b linkcheck "$SOURCE_DIR" "$BUILD_DIR/linkcheck"; then
        log_info "Link check completed successfully."
        echo "  📁 Report: $BUILD_DIR/linkcheck/output.txt"
    else
        log_warn "Link check found issues. Check the report for details."
    fi
}

serve_docs() {
    if [ ! -d "$BUILD_DIR/html" ]; then
        log_warn "HTML documentation not found. Building first..."
        build_html
    fi
    
    log_info "Starting local documentation server..."
    echo "  🌐 URL: http://localhost:8000"
    echo "  🔄 Press Ctrl+C to stop"
    
    cd "$BUILD_DIR/html"
    python3 -m http.server 8000
}

validate_docs() {
    log_info "Validating documentation structure..."
    
    # Check required files exist
    required_files=(
        "$SOURCE_DIR/index.md"
        "$SOURCE_DIR/conf.py"
        "$SOURCE_DIR/guides/installation.md"
        "$SOURCE_DIR/guides/quick-start.md"
        "$SOURCE_DIR/api/index.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    
    # Check for broken internal links
    log_info "Checking for MyST syntax errors..."
    if ! poetry run python -c "
import myst_parser
from myst_parser import parse_file
import sys
import os

errors = []
for root, dirs, files in os.walk('$SOURCE_DIR'):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Basic validation - could be extended
                if '```{' in content and not content.count('```{') == content.count('```'):
                    errors.append(f'Mismatched code blocks in {filepath}')
            except Exception as e:
                errors.append(f'Error reading {filepath}: {e}')

if errors:
    for error in errors:
        print(f'ERROR: {error}')
    sys.exit(1)
else:
    print('MyST syntax validation passed.')
"; then
        log_error "MyST syntax validation failed."
        exit 1
    fi
    
    log_info "Documentation validation completed successfully."
}

show_help() {
    cat << EOF
Policy Inspector Documentation Build Script

Usage: $0 [COMMAND]

Commands:
    html        Build HTML documentation (default)
    html-strict Build HTML documentation with warnings as errors
    clean       Clean build directory
    linkcheck   Check external links
    serve       Serve documentation locally on port 8000
    validate    Validate documentation structure and syntax
    all         Build HTML and check links
    help        Show this help message

Examples:
    $0 html           # Build HTML documentation
    $0 clean html     # Clean and build HTML documentation
    $0 serve          # Serve documentation locally
    $0 all            # Build everything and validate

EOF
}

# Main script logic
main() {
    cd "$PROJECT_ROOT"
    
    case "${1:-html}" in
        "clean")
            clean_build
            ;;
        "html")
            check_dependencies
            build_html
            ;;
        "html-strict")
            check_dependencies
            build_html_strict
            ;;
        "linkcheck")
            check_dependencies
            check_links
            ;;
        "serve")
            check_dependencies
            serve_docs
            ;;
        "validate")
            validate_docs
            ;;
        "all")
            check_dependencies
            validate_docs
            clean_build
            build_html_strict
            check_links
            log_info "🎉 All documentation tasks completed successfully!"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
