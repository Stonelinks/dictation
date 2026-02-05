#!/usr/bin/env bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
CHECK_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--check]"
            exit 1
            ;;
    esac
done

# Target directories
TARGETS="dictation tests"

# Track if any issues were found
ISSUES_FOUND=false

if [ "$CHECK_MODE" = true ]; then
    echo -e "${BLUE}=== Checking Code Formatting (read-only) ===${NC}"
    echo ""

    # Check formatting
    echo -e "${BLUE}Checking code formatting...${NC}"
    if uv run ruff format --check $TARGETS; then
        echo -e "${GREEN}✓ All files are properly formatted${NC}"
    else
        echo -e "${RED}✗ Formatting issues found${NC}"
        ISSUES_FOUND=true
    fi
    echo ""

    # Check linting
    echo -e "${BLUE}Checking code linting...${NC}"
    if uv run ruff check $TARGETS; then
        echo -e "${GREEN}✓ No linting issues found${NC}"
    else
        echo -e "${RED}✗ Linting issues found${NC}"
        ISSUES_FOUND=true
    fi
    echo ""

    if [ "$ISSUES_FOUND" = true ]; then
        echo -e "${YELLOW}Tip: Run './format.sh' to auto-fix formatting issues${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ All checks passed!${NC}"
        exit 0
    fi
else
    echo -e "${BLUE}=== Auto-fixing Code Formatting and Linting ===${NC}"
    echo ""

    # Auto-fix formatting
    echo -e "${BLUE}Running code formatter...${NC}"
    if uv run ruff format $TARGETS; then
        echo -e "${GREEN}✓ Code formatting complete${NC}"
    else
        echo -e "${RED}✗ Formatting failed${NC}"
        ISSUES_FOUND=true
    fi
    echo ""

    # Auto-fix linting issues
    echo -e "${BLUE}Running code linter with auto-fix...${NC}"
    if uv run ruff check --fix $TARGETS; then
        echo -e "${GREEN}✓ Code linting complete${NC}"
    else
        echo -e "${RED}✗ Some linting issues could not be auto-fixed${NC}"
        ISSUES_FOUND=true
    fi
    echo ""

    # Run check to see if any unfixable issues remain
    echo -e "${BLUE}Verifying all issues were fixed...${NC}"
    if uv run ruff check $TARGETS 2>&1 | grep -q "Found"; then
        echo -e "${YELLOW}⚠ Some issues require manual fixes${NC}"
        echo ""
        uv run ruff check $TARGETS
        ISSUES_FOUND=true
    else
        echo -e "${GREEN}✓ All issues fixed successfully!${NC}"
    fi
    echo ""

    if [ "$ISSUES_FOUND" = true ]; then
        echo -e "${YELLOW}Please review and fix remaining issues manually${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ Code is clean and ready!${NC}"
        exit 0
    fi
fi
