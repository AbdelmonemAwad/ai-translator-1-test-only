#!/bin/bash
# AI Translator (الترجمان الآلي) Installation Script
# نص تنصيب المترجم الآلي
# Support: Ubuntu Server 22.04+ with Casa OS
# Version: 2.2.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="AI Translator"
APP_DIR="/opt/ai-translator"
SERVICE_NAME="ai-translator"
SERVICE_USER="ai-translator"
DATABASE_NAME="ai_translator_db"
REQUIRED_PYTHON_VERSION="3.10"
SUPPORTED_VIDEO_FORMATS="mp4,mkv,avi,mov,wmv,flv,webm,m4v,3gp,ogv,ts,m2ts,vob,asf,rm,rmvb"

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "          AI Translator Installation Script"
    echo "          نص تنصيب المترجم الآلي"
    echo "=================================================================="
    echo "Support: Ubuntu Server 22.04+ with Casa OS"
    echo "Version: 1.0.0"
    echo "=================================================================="
    echo -e "${NC}"
}

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root. Use: sudo $0"
    fi
}

install_system_dependencies() {
    log "Installing system dependencies..."
    
    # Update package list
    apt update && apt upgrade -y
    
    # Install essential packages for AI Translator
    apt install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        postgresql \
        postgresql-contrib \
        nginx \
        ufw \
        htop \
        tree \
        unzip \
        ffmpeg \
        mediainfo \
        openssl \
        supervisor \
        sqlite3 \
        libsqlite3-dev \
        pkg-config \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        libpng-dev \
        libwebp-dev \
        libopus-dev \
        libmp3lame-dev \
        libx264-dev \
        libx265-dev \
        libvpx-dev \
        libaom-dev \
        libdav1d-dev \
        libsvtav1-dev \
        python3-dev \
        python3-tk \
        python3-setuptools \
        python3-wheel \
        python3-cffi \
        python3-brotli \
        cython3 \
        rsync \
        vim \
        nano \
        net-tools \
        dnsutils \
        iputils-ping \
        systemd \
        systemctl
    
    # Install additional Python dependencies for AI processing
    apt install -y \
        python3-numpy \
        python3-scipy \
        python3-matplotlib \
        python3-pandas \
        python3-pillow \
        python3-requests \
        python3-flask \
        python3-sqlalchemy \
        python3-psycopg2 \
        python3-cryptography \
        python3-jwt \
        python3-dateutil \
        python3-six
    
    # Install AI-specific libraries
    pip3 install --upgrade pip
    pip3 install \
        openai-whisper \
        torch \
        torchaudio \
        torchvision \
        transformers \
        accelerate \
        datasets \
        tokenizers
    
    log "System dependencies installed ✓"
}

install_whisper() {
    log "Installing OpenAI Whisper..."
    
    # Install Whisper with GPU support
    pip3 install --upgrade openai-whisper
    
    # Download default models
    log "Downloading Whisper models (this may take time)..."
    python3 -c "import whisper; whisper.load_model('medium.en')"
    python3 -c "import whisper; whisper.load_model('base.en')"
    
    log "Whisper installed with models ✓"
}

check_os() {
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot determine OS version"
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        error "This installer only supports Ubuntu Server"
    fi
    
    VERSION_NUM=$(echo "$VERSION_ID" | cut -d. -f1)
    if [[ $VERSION_NUM -lt 22 ]]; then
        error "Ubuntu 22.04 or higher is required"
    fi
    
    log "Detected Ubuntu $VERSION_ID - Compatible ✓"
}

check_nvidia_gpu() {
    log "Checking for NVIDIA GPU..."
    
    if ! command -v lspci >/dev/null 2>&1; then
        warn "lspci not found, installing pciutils..."
        apt install -y pciutils
    fi
    
    # Get all NVIDIA GPUs
    mapfile -t nvidia_gpus < <(lspci | grep -i nvidia | grep -i -E "(vga|3d)")
    local gpu_count=${#nvidia_gpus[@]}
    
    if [[ $gpu_count -eq 0 ]]; then
        error "NVIDIA GPU is required for AI processing. Please install an NVIDIA graphics card before proceeding."
    elif [[ $gpu_count -eq 1 ]]; then
        log "NVIDIA GPU detected: ${nvidia_gpus[0]} ✓"
        export NVIDIA_GPU_DETECTED=true
        export SELECTED_GPU_INDEX=0
    else
        log "Multiple NVIDIA GPUs detected ($gpu_count GPUs):"
        echo ""
        echo -e "${BLUE}GPU Performance Analysis and Service Distribution:${NC}"
        
        # Analyze GPU performance and suggest distribution
        declare -a gpu_scores
        declare -a gpu_names
        declare -a gpu_memories
        
        if command -v nvidia-smi >/dev/null 2>&1; then
            for i in "${!nvidia_gpus[@]}"; do
                local gpu_name=$(nvidia-smi -i $i --query-gpu=name --format=csv,noheader,nounits 2>/dev/null || echo "Unknown")
                local gpu_memory=$(nvidia-smi -i $i --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null || echo "0")
                
                gpu_names[$i]="$gpu_name"
                gpu_memories[$i]="$gpu_memory"
                
                # Calculate performance score based on memory and known GPU performance
                local score=0
                case "$gpu_name" in
                    *"RTX 4090"*|*"RTX 4080"*|*"RTX 3090"*|*"RTX 3080"*|*"A100"*|*"H100"*) score=100 ;;
                    *"RTX 4070"*|*"RTX 3070"*|*"RTX 2080"*|*"A40"*|*"A6000"*) score=80 ;;
                    *"RTX 4060"*|*"RTX 3060"*|*"RTX 2070"*|*"GTX 1080"*) score=60 ;;
                    *"RTX 2060"*|*"GTX 1070"*|*"GTX 1660"*) score=40 ;;
                    *) 
                        # Score based on memory if unknown model
                        if [[ $gpu_memory -gt 12000 ]]; then score=90
                        elif [[ $gpu_memory -gt 8000 ]]; then score=70
                        elif [[ $gpu_memory -gt 6000 ]]; then score=50
                        else score=30
                        fi
                    ;;
                esac
                
                # Adjust score based on memory
                if [[ $gpu_memory -gt 16000 ]]; then score=$((score + 10))
                elif [[ $gpu_memory -lt 6000 ]]; then score=$((score - 20))
                fi
                
                gpu_scores[$i]=$score
            done
            
            # Sort GPUs by performance score
            for i in "${!nvidia_gpus[@]}"; do
                local recommendation=""
                if [[ ${gpu_scores[$i]} -ge 80 ]]; then
                    recommendation="${GREEN}[Recommended for Ollama - Heavy LLM Processing]${NC}"
                elif [[ ${gpu_scores[$i]} -ge 60 ]]; then
                    recommendation="${YELLOW}[Suitable for Whisper - Audio Processing]${NC}"
                else
                    recommendation="${RED}[Limited Performance - Consider upgrade]${NC}"
                fi
                
                echo "  [$((i+1))] ${gpu_names[$i]} (${gpu_memories[$i]}MB VRAM) - Score: ${gpu_scores[$i]}/100"
                echo "      ${nvidia_gpus[$i]}"
                echo "      $recommendation"
                echo ""
            done
            
            echo -e "${BLUE}Service Distribution Recommendation:${NC}"
            # Find best GPU for Ollama (highest score)
            local best_ollama_idx=0
            local best_whisper_idx=0
            local highest_score=0
            local second_highest_score=0
            
            for i in "${!gpu_scores[@]}"; do
                if [[ ${gpu_scores[$i]} -gt $highest_score ]]; then
                    second_highest_score=$highest_score
                    best_whisper_idx=$best_ollama_idx
                    highest_score=${gpu_scores[$i]}
                    best_ollama_idx=$i
                elif [[ ${gpu_scores[$i]} -gt $second_highest_score ]]; then
                    second_highest_score=${gpu_scores[$i]}
                    best_whisper_idx=$i
                fi
            done
            
            echo "💡 Ollama (LLM): GPU $((best_ollama_idx+1)) - ${gpu_names[$best_ollama_idx]} (Highest Performance)"
            echo "🎤 Whisper (Audio): GPU $((best_whisper_idx+1)) - ${gpu_names[$best_whisper_idx]}"
            echo ""
            
            # Ask user for service distribution
            echo -e "${YELLOW}Would you like to use the recommended GPU distribution? [Y/n]:${NC} "
            read -r use_recommendation
            
            if [[ "$use_recommendation" =~ ^[Yy]$|^$ ]]; then
                export OLLAMA_GPU_INDEX=$best_ollama_idx
                export WHISPER_GPU_INDEX=$best_whisper_idx
                log "Using recommended distribution:"
                log "  Ollama: GPU $best_ollama_idx (${gpu_names[$best_ollama_idx]})"
                log "  Whisper: GPU $best_whisper_idx (${gpu_names[$best_whisper_idx]})"
            else
                # Manual selection
                echo ""
                echo -e "${YELLOW}Select GPU for Ollama (LLM Processing) [1-$gpu_count]:${NC} "
                while true; do
                    read -r ollama_choice
                    if [[ "$ollama_choice" =~ ^[0-9]+$ ]] && [[ $ollama_choice -ge 1 ]] && [[ $ollama_choice -le $gpu_count ]]; then
                        export OLLAMA_GPU_INDEX=$((ollama_choice-1))
                        break
                    else
                        warn "Invalid selection. Please enter a number between 1 and $gpu_count."
                    fi
                done
                
                echo -e "${YELLOW}Select GPU for Whisper (Audio Processing) [1-$gpu_count]:${NC} "
                while true; do
                    read -r whisper_choice
                    if [[ "$whisper_choice" =~ ^[0-9]+$ ]] && [[ $whisper_choice -ge 1 ]] && [[ $whisper_choice -le $gpu_count ]]; then
                        export WHISPER_GPU_INDEX=$((whisper_choice-1))
                        break
                    else
                        warn "Invalid selection. Please enter a number between 1 and $gpu_count."
                    fi
                done
                
                log "Manual selection:"
                log "  Ollama: GPU $OLLAMA_GPU_INDEX (${gpu_names[$OLLAMA_GPU_INDEX]})"
                log "  Whisper: GPU $WHISPER_GPU_INDEX (${gpu_names[$WHISPER_GPU_INDEX]})"
            fi
        else
            # Fallback without nvidia-smi
            for i in "${!nvidia_gpus[@]}"; do
                echo "  [$((i+1))] ${nvidia_gpus[$i]}"
            done
            
            echo ""
            echo -e "${YELLOW}Select GPU for Ollama [1-$gpu_count]:${NC} "
            read -r ollama_choice
            export OLLAMA_GPU_INDEX=$((ollama_choice-1))
            
            echo -e "${YELLOW}Select GPU for Whisper [1-$gpu_count]:${NC} "
            read -r whisper_choice
            export WHISPER_GPU_INDEX=$((whisper_choice-1))
        fi
        
        export NVIDIA_GPU_DETECTED=true
    fi
    
    # Check if nvidia-smi is available
    if command -v nvidia-smi >/dev/null 2>&1; then
        log "NVIDIA drivers already installed ✓"
        
        # Show GPU information
        if [[ -n "$SELECTED_GPU_INDEX" ]]; then
            log "Selected GPU details:"
            nvidia-smi -i $SELECTED_GPU_INDEX --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits
        fi
    else
        warn "NVIDIA GPU found but drivers may not be installed"
        log "NVIDIA drivers will be installed automatically"
        export INSTALL_NVIDIA_DRIVERS=true
    fi
}

check_casa_os() {
    if command -v casaos >/dev/null 2>&1; then
        log "Casa OS detected ✓"
        export CASA_OS_DETECTED=true
    else
        warn "Casa OS not detected. Installing in standard mode."
        export CASA_OS_DETECTED=false
    fi
}

install_system_dependencies() {
    log "Installing system dependencies..."
    
    apt update
    apt install -y \
        curl \
        wget \
        git \
        build-essential \
        ffmpeg \
        python3.11 \
        python3.11-dev \
        python3.11-venv \
        python3-pip \
        postgresql \
        postgresql-contrib \
        postgresql-server-dev-all \
        nginx \
        supervisor \
        ufw \
        htop \
        unzip \
        pciutils
    
    log "System dependencies installed ✓"
}

install_nvidia_drivers() {
    if [[ "$INSTALL_NVIDIA_DRIVERS" == "true" ]]; then
        log "Installing NVIDIA drivers..."
        
        # Add NVIDIA repository
        apt update
        apt install -y software-properties-common
        add-apt-repository -y ppa:graphics-drivers/ppa
        apt update
        
        # Install latest NVIDIA driver
        ubuntu-drivers autoinstall
        
        log "NVIDIA drivers installed ✓"
        warn "System reboot may be required for NVIDIA drivers to work properly"
        
        # Install NVIDIA Container Toolkit for Docker support (optional)
        if command -v docker >/dev/null 2>&1; then
            log "Installing NVIDIA Container Toolkit..."
            curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
            curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
                sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
                tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
            apt update
            apt install -y nvidia-container-toolkit
            log "NVIDIA Container Toolkit installed ✓"
        fi
    else
        log "NVIDIA drivers already installed ✓"
    fi
}

setup_python() {
    log "Setting up Python environment..."
    
    # Detect available Python version
    if command -v python3.11 >/dev/null 2>&1; then
        PYTHON_CMD="python3.11"
        log "Using Python 3.11"
    elif command -v python3.10 >/dev/null 2>&1; then
        PYTHON_CMD="python3.10"
        log "Using Python 3.10"
    elif command -v python3.9 >/dev/null 2>&1; then
        PYTHON_CMD="python3.9"
        log "Using Python 3.9"
    else
        PYTHON_CMD="python3"
        log "Using default Python 3"
    fi
    
    # Set as default python3
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/$PYTHON_CMD 1
    
    # Install pip
    curl -sS https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD
    
    log "Python 3.11 environment ready ✓"
}

install_ollama() {
    log "Installing Ollama..."
    
    if ! command -v ollama >/dev/null 2>&1; then
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Configure Ollama service with GPU selection
        local ollama_gpu=""
        if [[ -n "$OLLAMA_GPU_INDEX" ]]; then
            ollama_gpu="$OLLAMA_GPU_INDEX"
        elif [[ -n "$SELECTED_GPU_INDEX" ]]; then
            ollama_gpu="$SELECTED_GPU_INDEX"
        fi
        
        if [[ -n "$ollama_gpu" ]]; then
            log "Configuring Ollama to use GPU $ollama_gpu"
            
            # Create Ollama systemd override directory
            mkdir -p /etc/systemd/system/ollama.service.d
            
            # Create GPU-specific environment override
            cat > "/etc/systemd/system/ollama.service.d/gpu-override.conf" << EOF
[Service]
Environment="CUDA_VISIBLE_DEVICES=$ollama_gpu"
Environment="OLLAMA_GPU_LAYERS=999"
Environment="OLLAMA_MEMORY_POOL_SIZE=2048MB"
EOF
            
            systemctl daemon-reload
            log "Ollama GPU configuration: GPU $ollama_gpu ✓"
        fi
        
        # Start ollama service
        systemctl enable ollama
        systemctl start ollama
        
        # Wait for service to be ready
        sleep 3
        
        # Download default model
        log "Downloading Llama 3 model (this may take a while)..."
        if [[ -n "$ollama_gpu" ]]; then
            CUDA_VISIBLE_DEVICES=$ollama_gpu ollama pull llama3
        else
            ollama pull llama3
        fi
        
        log "Ollama installed and Llama 3 model downloaded ✓"
    else
        log "Ollama already installed ✓"
        
        # Update GPU configuration if needed
        if [[ -n "$OLLAMA_GPU_INDEX" ]] || [[ -n "$SELECTED_GPU_INDEX" ]]; then
            local ollama_gpu="${OLLAMA_GPU_INDEX:-$SELECTED_GPU_INDEX}"
            log "Updating Ollama GPU configuration to use GPU $ollama_gpu"
            
            mkdir -p /etc/systemd/system/ollama.service.d
            cat > "/etc/systemd/system/ollama.service.d/gpu-override.conf" << EOF
[Service]
Environment="CUDA_VISIBLE_DEVICES=$ollama_gpu"
Environment="OLLAMA_GPU_LAYERS=999"
Environment="OLLAMA_MEMORY_POOL_SIZE=2048MB"
EOF
            
            systemctl daemon-reload
            systemctl restart ollama
            log "Ollama GPU configuration updated ✓"
        fi
    fi
}

install_whisper() {
    log "Installing OpenAI Whisper..."
    
    pip3 install --upgrade pip
    pip3 install openai-whisper
    
    log "Whisper installed ✓"
}

setup_database() {
    log "Setting up PostgreSQL database..."
    
    # Start PostgreSQL
    systemctl enable postgresql
    systemctl start postgresql
    
    # Create database and user
    sudo -u postgres psql -c "CREATE DATABASE $DATABASE_NAME;"
    sudo -u postgres psql -c "CREATE USER ai_translator WITH PASSWORD 'ai_translator_2025';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO ai_translator;"
    sudo -u postgres psql -c "ALTER USER ai_translator CREATEDB;"
    
    # Configure PostgreSQL for local connections
    PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
    PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"
    
    # Backup original configs
    cp "$PG_CONFIG_DIR/postgresql.conf" "$PG_CONFIG_DIR/postgresql.conf.backup"
    cp "$PG_CONFIG_DIR/pg_hba.conf" "$PG_CONFIG_DIR/pg_hba.conf.backup"
    
    # Configure PostgreSQL
    echo "listen_addresses = 'localhost'" >> "$PG_CONFIG_DIR/postgresql.conf"
    echo "port = 5432" >> "$PG_CONFIG_DIR/postgresql.conf"
    
    # Allow local connections
    sed -i "s/#local   all             all                                     peer/local   all             all                                     md5/" "$PG_CONFIG_DIR/pg_hba.conf"
    
    # Restart PostgreSQL
    systemctl restart postgresql
    
    export DATABASE_URL="postgresql://ai_translator:ai_translator_2025@localhost:5432/$DATABASE_NAME"
    
    log "PostgreSQL database configured ✓"
}

create_user() {
    log "Creating application user..."
    
    if ! id "$SERVICE_USER" >/dev/null 2>&1; then
        useradd --system --home-dir "$APP_DIR" --shell /bin/bash "$SERVICE_USER"
        log "User $SERVICE_USER created ✓"
    else
        log "User $SERVICE_USER already exists ✓"
    fi
}

install_application() {
    log "Installing AI Translator application..."
    
    # Create application directory
    mkdir -p "$APP_DIR"
    
    # Copy application files
    cp -r . "$APP_DIR/"
    cd "$APP_DIR"
    
    # Create Python virtual environment
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install \
        flask \
        flask-sqlalchemy \
        gunicorn \
        psycopg2-binary \
        psutil \
        pynvml \
        requests \
        email-validator \
        werkzeug \
        sendgrid
    
    # Set permissions
    chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"
    chmod +x "$APP_DIR/install.sh"
    
    # Initialize database
    sudo -u "$SERVICE_USER" bash -c "cd $APP_DIR && source venv/bin/activate && python database_setup.py"
    
    log "Application installed ✓"
}

setup_systemd_service() {
    log "Setting up systemd service..."
    
    # GPU environment setup for Whisper
    local whisper_gpu_env=""
    if [[ -n "$WHISPER_GPU_INDEX" ]]; then
        whisper_gpu_env="Environment=WHISPER_GPU_DEVICE=$WHISPER_GPU_INDEX"
        log "Whisper GPU environment configured for device $WHISPER_GPU_INDEX"
    elif [[ -n "$SELECTED_GPU_INDEX" ]]; then
        whisper_gpu_env="Environment=WHISPER_GPU_DEVICE=$SELECTED_GPU_INDEX"
        log "Whisper GPU environment configured for device $SELECTED_GPU_INDEX"
    fi

    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=AI Translator Web Application
After=network.target postgresql.service ollama.service
Wants=postgresql.service ollama.service

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=DATABASE_URL=postgresql://ai_translator:ai_translator_2025@localhost:5432/$DATABASE_NAME
Environment=SESSION_SECRET=$(openssl rand -base64 32)
Environment=FLASK_ENV=production
${whisper_gpu_env}
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --keepalive 2 --reload main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    log "Systemd service configured ✓"
}

setup_nginx() {
    log "Setting up Nginx reverse proxy..."
    
    cat > "/etc/nginx/sites-available/$SERVICE_NAME" << EOF
server {
    listen 80;
    server_name localhost;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable site
    ln -sf "/etc/nginx/sites-available/$SERVICE_NAME" "/etc/nginx/sites-enabled/"
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx config
    nginx -t
    
    systemctl enable nginx
    systemctl restart nginx
    
    log "Nginx configured ✓"
}

setup_firewall() {
    log "Configuring firewall..."
    
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH
    ufw allow ssh
    
    # Allow HTTP and HTTPS
    ufw allow 80
    ufw allow 443
    
    # Allow Casa OS if detected
    if [[ "$CASA_OS_DETECTED" == "true" ]]; then
        ufw allow 80/tcp
        ufw allow 443/tcp
    fi
    
    ufw --force enable
    
    log "Firewall configured ✓"
}

casa_os_integration() {
    if [[ "$CASA_OS_DETECTED" == "true" ]]; then
        log "Setting up Casa OS integration..."
        
        # Create Casa OS app configuration
        mkdir -p /var/lib/casaos/apps
        
        cat > "/var/lib/casaos/apps/ai-translator.json" << EOF
{
    "name": "AI Translator",
    "icon": "🤖",
    "description": "Advanced AI-powered translation system for movies and TV shows",
    "url": "http://localhost:80",
    "category": "Media",
    "port": 80,
    "tags": ["ai", "translation", "media", "subtitles"],
    "author": "عبدالمنعم عوض",
    "version": "1.0.0"
}
EOF
        
        log "Casa OS integration completed ✓"
    fi
}

start_services() {
    log "Starting services..."
    
    systemctl start "$SERVICE_NAME"
    systemctl start nginx
    
    # Wait for services to start
    sleep 5
    
    # Check service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "AI Translator service started ✓"
    else
        error "Failed to start AI Translator service"
    fi
    
    if systemctl is-active --quiet nginx; then
        log "Nginx service started ✓"
    else
        error "Failed to start Nginx service"
    fi
}

create_admin_user() {
    log "Creating default admin user..."
    
    sudo -u "$SERVICE_USER" bash -c "cd $APP_DIR && source venv/bin/activate && python -c \"
from app import app
from models import db, Settings
with app.app_context():
    # Create admin credentials
    admin_user = Settings.query.filter_by(key='web_username').first()
    if not admin_user:
        admin_user = Settings(key='web_username', value='admin', section='DEFAULT')
        db.session.add(admin_user)
    
    admin_pass = Settings.query.filter_by(key='web_password').first()
    if not admin_pass:
        admin_pass = Settings(key='web_password', value='admin123', section='DEFAULT')
        db.session.add(admin_pass)
    
    # Store GPU configuration for services
    if '$OLLAMA_GPU_INDEX':
        ollama_gpu = Settings.query.filter_by(key='ollama_gpu_index').first()
        if not ollama_gpu:
            ollama_gpu = Settings(key='ollama_gpu_index', value='$OLLAMA_GPU_INDEX', section='SYSTEM', description='NVIDIA GPU index for Ollama LLM processing')
            db.session.add(ollama_gpu)
    
    if '$WHISPER_GPU_INDEX':
        whisper_gpu = Settings.query.filter_by(key='whisper_gpu_index').first()
        if not whisper_gpu:
            whisper_gpu = Settings(key='whisper_gpu_index', value='$WHISPER_GPU_INDEX', section='SYSTEM', description='NVIDIA GPU index for Whisper audio processing')
            db.session.add(whisper_gpu)
    
    # Fallback for single GPU setup
    if '$SELECTED_GPU_INDEX' and not '$OLLAMA_GPU_INDEX':
        gpu_setting = Settings.query.filter_by(key='selected_gpu_index').first()
        if not gpu_setting:
            gpu_setting = Settings(key='selected_gpu_index', value='$SELECTED_GPU_INDEX', section='SYSTEM', description='Selected NVIDIA GPU index for AI processing')
            db.session.add(gpu_setting)
    
    db.session.commit()
    print('Admin user created: admin / admin123')
\""
    
    log "Default admin user: admin / admin123 ✓"
}

print_completion() {
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "          AI Translator Installation Complete!"
    echo "          تم تنصيب المترجم الآلي بنجاح!"
    echo "=================================================================="
    echo ""
    echo "🌐 Application URL: http://$(hostname -I | awk '{print $1}')"
    echo "👤 Default Login: admin / admin123"
    echo ""
    
    # Show GPU configuration
    if [[ -n "$OLLAMA_GPU_INDEX" ]] || [[ -n "$WHISPER_GPU_INDEX" ]] || [[ -n "$SELECTED_GPU_INDEX" ]]; then
        echo "🎮 GPU Service Distribution:"
        if command -v nvidia-smi >/dev/null 2>&1; then
            if [[ -n "$OLLAMA_GPU_INDEX" ]]; then
                echo "   💡 Ollama (LLM): GPU $OLLAMA_GPU_INDEX - $(nvidia-smi -i $OLLAMA_GPU_INDEX --query-gpu=name --format=csv,noheader,nounits)"
            fi
            if [[ -n "$WHISPER_GPU_INDEX" ]]; then
                echo "   🎤 Whisper (Audio): GPU $WHISPER_GPU_INDEX - $(nvidia-smi -i $WHISPER_GPU_INDEX --query-gpu=name --format=csv,noheader,nounits)"
            fi
            if [[ -n "$SELECTED_GPU_INDEX" ]] && [[ -z "$OLLAMA_GPU_INDEX" ]]; then
                echo "   🤖 AI Processing: GPU $SELECTED_GPU_INDEX - $(nvidia-smi -i $SELECTED_GPU_INDEX --query-gpu=name --format=csv,noheader,nounits)"
            fi
        else
            if [[ -n "$OLLAMA_GPU_INDEX" ]]; then
                echo "   💡 Ollama (LLM): GPU $OLLAMA_GPU_INDEX"
            fi
            if [[ -n "$WHISPER_GPU_INDEX" ]]; then
                echo "   🎤 Whisper (Audio): GPU $WHISPER_GPU_INDEX"
            fi
            if [[ -n "$SELECTED_GPU_INDEX" ]] && [[ -z "$OLLAMA_GPU_INDEX" ]]; then
                echo "   🤖 AI Processing: GPU $SELECTED_GPU_INDEX"
            fi
        fi
        echo ""
    fi
    
    echo "📋 Service Commands:"
    echo "   sudo systemctl status $SERVICE_NAME    # Check status"
    echo "   sudo systemctl restart $SERVICE_NAME   # Restart"
    echo "   sudo systemctl logs -f $SERVICE_NAME   # View logs"
    echo ""
    echo "📁 Application Directory: $APP_DIR"
    echo "📊 Database: PostgreSQL ($DATABASE_NAME)"
    echo "🤖 AI Engine: Ollama (Llama 3)"
    echo "🎵 Audio Processing: Whisper + FFmpeg"
    echo ""
    if [[ "$CASA_OS_DETECTED" == "true" ]]; then
        echo "🏠 Casa OS: Available in Apps dashboard"
    fi
    echo "=================================================================="
    echo -e "${NC}"
}

# Main installation process
main() {
    print_header
    
    log "Starting AI Translator installation..."
    
    check_root
    check_os
    check_nvidia_gpu
    check_casa_os
    
    install_system_dependencies
    install_nvidia_drivers
    setup_python
    install_ollama
    install_whisper
    setup_database
    create_user
    install_application
    setup_systemd_service
    setup_nginx
    setup_firewall
    casa_os_integration
    start_services
    create_admin_user
    
    print_completion
}

# Run installation
main "$@"