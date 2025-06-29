#!/bin/bash
# AI Translator Installation Test Script
# سكريبت اختبار تنصيب المترجم الآلي

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[TEST-INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[TEST-WARN]${NC} $1"
}

error() {
    echo -e "${RED}[TEST-ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[TEST-SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "          AI Translator Installation Test"
    echo "          اختبار تنصيب المترجم الآلي"
    echo "=================================================================="
    echo -e "${NC}"
}

test_install_script_syntax() {
    log "Testing install.sh syntax..."
    
    if bash -n install.sh; then
        success "✓ install.sh syntax is valid"
    else
        error "✗ install.sh has syntax errors"
        return 1
    fi
}

test_install_script_functions() {
    log "Testing install.sh functions..."
    
    # Extract function names from install.sh without sourcing
    local functions_found
    functions_found=$(grep -E "^[a-zA-Z_][a-zA-Z0-9_]*\(\)" install.sh | cut -d'(' -f1)
    
    # Required functions
    local required_functions=(
        "print_header"
        "log"
        "warn" 
        "error"
        "check_root"
        "install_system_dependencies"
        "install_whisper"
        "install_ollama"
        "setup_database"
        "create_user"
        "install_application"
        "setup_systemd_service"
        "setup_nginx"
        "setup_firewall"
        "start_services"
        "create_admin_user"
        "print_completion"
    )
    
    log "Found functions in install.sh:"
    echo "$functions_found" | while read -r func; do
        [[ -n "$func" ]] && log "  - $func"
    done
    
    # Check if required functions exist in file
    for func in "${required_functions[@]}"; do
        if grep -q "^${func}()" install.sh; then
            success "✓ Function $func exists"
        else
            error "✗ Function $func missing"
        fi
    done
}

test_system_requirements() {
    log "Testing system requirements..."
    
    # Check operating system
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        log "Operating System: $PRETTY_NAME"
        
        case "$ID" in
            ubuntu)
                if [[ "$VERSION_ID" == "22.04" ]] || [[ "$VERSION_ID" == "24.04" ]]; then
                    success "✓ Ubuntu version supported"
                else
                    warn "⚠ Ubuntu version may not be fully supported"
                fi
                ;;
            debian)
                success "✓ Debian detected"
                ;;
            *)
                warn "⚠ Operating system may not be fully supported"
                ;;
        esac
    else
        warn "⚠ Cannot detect operating system"
    fi
    
    # Check available tools
    local tools=("curl" "wget" "git" "python3")
    for tool in "${tools[@]}"; do
        if command -v "$tool" >/dev/null 2>&1; then
            success "✓ $tool is available"
        else
            warn "⚠ $tool is not installed"
        fi
    done
}

test_gpu_detection() {
    log "Testing GPU detection..."
    
    if command -v nvidia-smi >/dev/null 2>&1; then
        success "✓ NVIDIA drivers detected"
        nvidia-smi -L | while read -r line; do
            log "Found: $line"
        done
    else
        warn "⚠ NVIDIA drivers not found"
        log "Install will attempt to install NVIDIA drivers"
    fi
}

test_port_availability() {
    log "Testing port availability..."
    
    local ports=(5000 80 443 5432 11434)
    for port in "${ports[@]}"; do
        if ! netstat -ln 2>/dev/null | grep -q ":$port "; then
            success "✓ Port $port is available"
        else
            warn "⚠ Port $port is in use"
            netstat -ln | grep ":$port " | head -1
        fi
    done
}

test_disk_space() {
    log "Testing disk space..."
    
    local available_space
    available_space=$(df / | awk 'NR==2 {print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    
    log "Available disk space: ${available_gb}GB"
    
    if [[ $available_gb -ge 100 ]]; then
        success "✓ Sufficient disk space (${available_gb}GB)"
    else
        warn "⚠ Low disk space (${available_gb}GB). Recommended: 100GB+"
    fi
}

test_memory() {
    log "Testing memory..."
    
    local total_mem
    total_mem=$(free -g | awk 'NR==2{print $2}')
    
    log "Total memory: ${total_mem}GB"
    
    if [[ $total_mem -ge 16 ]]; then
        success "✓ Sufficient memory (${total_mem}GB)"
    elif [[ $total_mem -ge 8 ]]; then
        warn "⚠ Limited memory (${total_mem}GB). Recommended: 16GB+"
    else
        error "✗ Insufficient memory (${total_mem}GB). Minimum: 8GB"
    fi
}

test_network_connectivity() {
    log "Testing network connectivity..."
    
    local urls=(
        "https://github.com"
        "https://ollama.ai"
        "https://pypi.org"
        "https://nvidia.com"
    )
    
    for url in "${urls[@]}"; do
        if curl -s --connect-timeout 5 "$url" >/dev/null; then
            success "✓ Can reach $url"
        else
            warn "⚠ Cannot reach $url"
        fi
    done
}

test_python_environment() {
    log "Testing Python environment..."
    
    if command -v python3.11 >/dev/null 2>&1; then
        local py_version
        py_version=$(python3.11 --version)
        success "✓ $py_version available"
    else
        warn "⚠ Python 3.11 not found, install will attempt to install it"
    fi
    
    if command -v pip3 >/dev/null 2>&1; then
        success "✓ pip3 is available"
    else
        warn "⚠ pip3 not found"
    fi
}

test_casa_os() {
    log "Testing Casa OS integration..."
    
    if [[ -d "/var/lib/casaos" ]] || [[ -f "/usr/bin/casaos" ]]; then
        success "✓ Casa OS detected"
        export CASA_OS_DETECTED=true
    else
        log "Casa OS not detected - will run in standard mode"
    fi
}

test_security_features() {
    log "Testing security features..."
    
    # Test path validation
    if grep -q "validate_file_path\|validate_browse_path" *.py 2>/dev/null; then
        success "✓ Path validation security found"
    else
        warn "⚠ Path validation security not implemented"
    fi
    
    # Test security configuration
    if [[ -f "security_config.py" ]]; then
        success "✓ Security configuration module found"
        
        # Test forbidden paths
        if grep -q "FORBIDDEN_PATHS" security_config.py; then
            success "✓ System path protection configured"
        else
            warn "⚠ System path protection missing"
        fi
        
        # Test file size limits
        if grep -q "MAX_FILE_SIZE" security_config.py; then
            success "✓ File size limits configured"
        else
            warn "⚠ File size limits missing"
        fi
        
        # Test security logging
        if grep -q "security_logger\|log_security_event" security_config.py; then
            success "✓ Security event logging configured"
        else
            warn "⚠ Security logging missing"
        fi
    else
        warn "⚠ Security configuration module not found"
    fi
}

test_server_configuration() {
    log "Testing server configuration options..."
    
    # Test port configuration in database setup
    if grep -q "server_port" database_setup.py 2>/dev/null; then
        success "✓ Port configuration option available"
    else
        warn "⚠ Port configuration option missing"
    fi
    
    # Test host binding configuration
    if grep -q "server_host" database_setup.py 2>/dev/null; then
        success "✓ Host binding configuration available"
    else
        warn "⚠ Host binding configuration missing"
    fi
    
    # Test for systemd service configuration
    if grep -q "systemd" install.sh; then
        success "✓ Systemd service configuration found"
    else
        warn "⚠ Systemd service configuration missing"
    fi
}

generate_test_report() {
    log "Generating test report..."
    
    cat > "install_test_report.txt" << EOF
AI Translator Installation Test Report
Generated: $(date)
System: $(uname -a)

Tests Performed:
- Script syntax validation
- Function availability check  
- System requirements verification
- GPU detection test
- Port availability check
- Disk space verification
- Memory check
- Network connectivity test
- Python environment test
- Casa OS detection

Recommendations:
1. Ensure all warnings are addressed before installation
2. Install NVIDIA drivers if not present
3. Free up disk space if needed
4. Consider upgrading memory if below 16GB
5. Verify network connectivity for downloads

Next Steps:
1. Review this report
2. Address any warnings
3. Run: sudo ./install.sh
4. Monitor installation logs
5. Verify installation with provided commands

EOF

    success "✓ Test report saved to install_test_report.txt"
}

run_full_test() {
    print_header
    
    log "Starting comprehensive installation test..."
    
    test_install_script_syntax
    test_install_script_functions
    test_system_requirements
    test_gpu_detection
    test_port_availability
    test_disk_space
    test_memory
    test_network_connectivity
    test_python_environment
    test_casa_os
    test_security_features
    test_server_configuration
    
    generate_test_report
    
    echo ""
    echo -e "${GREEN}=================================================================="
    echo "          Installation Test Complete"
    echo "          اكتمل اختبار التنصيب"
    echo "=================================================================="
    echo ""
    echo "📋 Review the test report: install_test_report.txt"
    echo "🚀 If all tests pass, run: sudo ./install.sh"
    echo "📚 Read installation guide: install_guide.md"
    echo "=================================================================="
    echo -e "${NC}"
}

# Run tests
run_full_test