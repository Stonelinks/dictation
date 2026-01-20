#!/usr/bin/env bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Running Whisper Dictation Test Suite ===${NC}"
echo ""

# Parse command line arguments
COVERAGE=false
VERBOSE=false
MARKERS=""
PYTEST_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --unit|-u)
            MARKERS="-m unit"
            shift
            ;;
        --integration|-i)
            MARKERS="-m integration"
            shift
            ;;
        --linux|-l)
            MARKERS="-m linux"
            shift
            ;;
        --macos|-m)
            MARKERS="-m macos"
            shift
            ;;
        *)
            PYTEST_ARGS="$PYTEST_ARGS $1"
            shift
            ;;
    esac
done

# Run formatting check before tests
echo -e "${BLUE}Checking code formatting...${NC}"
if ./format.sh --check; then
    echo ""
else
    echo -e "${YELLOW}Tip: Run './format.sh' to auto-fix formatting issues${NC}"
    echo ""
    exit 1
fi

# Build pytest command
CMD="uv run pytest"

if [ "$VERBOSE" = true ]; then
    CMD="$CMD -v"
else
    CMD="$CMD -q"
fi

if [ "$COVERAGE" = true ]; then
    CMD="$CMD --cov=whisper_dictation --cov-report=term-missing --cov-report=html"
fi

if [ -n "$MARKERS" ]; then
    CMD="$CMD $MARKERS"
fi

if [ -n "$PYTEST_ARGS" ]; then
    CMD="$CMD $PYTEST_ARGS"
fi

# Run tests
echo -e "${BLUE}Running:${NC} $CMD"
echo ""

if eval $CMD; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"

    if [ "$COVERAGE" = true ]; then
        echo -e "${BLUE}Coverage report saved to htmlcov/index.html${NC}"
    fi

    exit 0
else
    echo ""
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi
