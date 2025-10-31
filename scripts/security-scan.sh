#!/bin/bash
# Script de scan de sécurité Trivy local
# Usage: ./scripts/security-scan.sh [filesystem|docker-main|docker-frontend|docker-citizen-api|all]

set -e

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vérifier si Trivy est installé
if ! command -v trivy &> /dev/null; then
    echo -e "${RED}❌ Trivy n'est pas installé${NC}"
    echo -e "${YELLOW}Installation:${NC}"
    echo "  Ubuntu/Debian: sudo apt-get install wget apt-transport-https gnupg lsb-release && \\"
    echo "    wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add - && \\"
    echo "    echo \"deb https://aquasecurity.github.io/trivy-repo/deb \$(lsb_release -sc) main\" | sudo tee -a /etc/apt/sources.list.d/trivy.list && \\"
    echo "    sudo apt-get update && sudo apt-get install trivy"
    echo ""
    echo "  macOS: brew install aquasecurity/trivy/trivy"
    echo ""
    echo "  Ou télécharger depuis: https://github.com/aquasecurity/trivy/releases"
    exit 1
fi

echo -e "${BLUE}🔒 Climate AI Collective - Security Scan${NC}"
echo ""

SCAN_TYPE="${1:-all}"
EXIT_CODE=0

# Fonction pour scanner le filesystem
scan_filesystem() {
    echo -e "${BLUE}📁 Scanning filesystem and dependencies...${NC}"
    echo ""

    if trivy fs --severity CRITICAL,HIGH --exit-code 1 .; then
        echo -e "${GREEN}✅ Filesystem scan: PASSED${NC}"
    else
        echo -e "${RED}❌ Filesystem scan: FAILED (CRITICAL/HIGH vulnerabilities found)${NC}"
        EXIT_CODE=1
    fi
    echo ""
}

# Fonction pour scanner l'image Docker principale
scan_docker_main() {
    echo -e "${BLUE}🐳 Building and scanning main Docker image...${NC}"
    echo ""

    if docker build -t climate-ai/main:test -f docker/Dockerfile . > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker image built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build Docker image${NC}"
        return 1
    fi

    if trivy image --severity CRITICAL,HIGH --exit-code 1 climate-ai/main:test; then
        echo -e "${GREEN}✅ Main Docker image scan: PASSED${NC}"
    else
        echo -e "${RED}❌ Main Docker image scan: FAILED${NC}"
        EXIT_CODE=1
    fi
    echo ""
}

# Fonction pour scanner l'image Docker frontend
scan_docker_frontend() {
    echo -e "${BLUE}🐳 Building and scanning frontend Docker image...${NC}"
    echo ""

    if docker build -t climate-ai/frontend:test -f frontend/Dockerfile frontend/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend Docker image built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build frontend Docker image${NC}"
        return 1
    fi

    if trivy image --severity CRITICAL,HIGH --exit-code 1 climate-ai/frontend:test; then
        echo -e "${GREEN}✅ Frontend Docker image scan: PASSED${NC}"
    else
        echo -e "${RED}❌ Frontend Docker image scan: FAILED${NC}"
        EXIT_CODE=1
    fi
    echo ""
}

# Fonction pour scanner l'image Docker citizen-api
scan_docker_citizen_api() {
    echo -e "${BLUE}🐳 Building and scanning citizen-api Docker image...${NC}"
    echo ""

    if [ -f "services/citizen-api/Dockerfile" ]; then
        if docker build -t climate-ai/citizen-api:test -f services/citizen-api/Dockerfile services/citizen-api/ > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Citizen API Docker image built successfully${NC}"
        else
            echo -e "${RED}❌ Failed to build citizen-api Docker image${NC}"
            return 1
        fi

        if trivy image --severity CRITICAL,HIGH --exit-code 1 climate-ai/citizen-api:test; then
            echo -e "${GREEN}✅ Citizen API Docker image scan: PASSED${NC}"
        else
            echo -e "${RED}❌ Citizen API Docker image scan: FAILED${NC}"
            EXIT_CODE=1
        fi
    else
        echo -e "${YELLOW}⚠️  Citizen API Dockerfile not found, skipping${NC}"
    fi
    echo ""
}

# Exécuter les scans selon le type demandé
case "$SCAN_TYPE" in
    filesystem)
        scan_filesystem
        ;;
    docker-main)
        scan_docker_main
        ;;
    docker-frontend)
        scan_docker_frontend
        ;;
    docker-citizen-api)
        scan_docker_citizen_api
        ;;
    all)
        scan_filesystem
        scan_docker_main
        scan_docker_frontend
        scan_docker_citizen_api
        ;;
    *)
        echo -e "${RED}❌ Invalid scan type: $SCAN_TYPE${NC}"
        echo "Usage: $0 [filesystem|docker-main|docker-frontend|docker-citizen-api|all]"
        exit 1
        ;;
esac

# Résumé final
echo ""
echo -e "${BLUE}================================================${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All security scans passed!${NC}"
    echo -e "${GREEN}No CRITICAL or HIGH vulnerabilities found.${NC}"
else
    echo -e "${RED}❌ Security scans failed!${NC}"
    echo -e "${RED}CRITICAL or HIGH vulnerabilities were found.${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review the vulnerabilities listed above"
    echo "  2. Update dependencies in requirements.txt"
    echo "  3. Update base images in Dockerfiles if needed"
    echo "  4. Run the scan again to verify fixes"
fi
echo -e "${BLUE}================================================${NC}"
echo ""

exit $EXIT_CODE
