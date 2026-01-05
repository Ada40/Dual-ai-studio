# Installation Guide - Dual AI Studio

## Table of Contents
- [System Requirements](#system-requirements)
- [Python Requirements](#python-requirements)
- [Installation Steps](#installation-steps)
- [Optional Components](#optional-components)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Verifying Installation](#verifying-installation)
- [First Run Instructions](#first-run-instructions)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

Dual AI Studio is compatible with the following operating systems:

### Windows
- **OS Version**: Windows 10 or later (64-bit)
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: 2GB free space (more for AI models and creative tools)
- **Processor**: Multi-core processor recommended

### macOS
- **OS Version**: macOS 10.15 (Catalina) or later
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: 2GB free space (more for AI models and creative tools)
- **Processor**: Intel or Apple Silicon (M1/M2/M3)

### Linux
- **Distributions**: Ubuntu 20.04+, Debian 10+, Fedora 33+, or equivalent
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: 2GB free space (more for AI models and creative tools)
- **Processor**: Multi-core processor recommended

---

## Python Requirements

Dual AI Studio requires **Python 3.8 or higher**.

### Check Your Python Version

```bash
python --version
# or
python3 --version
```

### Installing Python

If you need to install or upgrade Python:

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and **check "Add Python to PATH"**
3. Verify installation: `python --version`

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3 --version
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Fedora
sudo dnf install python3.11 python3-pip

# Verify installation
python3 --version
```

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Ada40/Dual-ai-studio.git
cd Dual-ai-studio
```

### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment isolates dependencies and prevents conflicts:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

If you encounter SSL errors or slow downloads, try:

```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### 4. Verify Core Installation

```bash
python -c "import flask, openai, anthropic; print('Core dependencies installed successfully!')"
```

---

## Optional Components

### Ollama Installation (Local AI Models)

Ollama allows you to run AI models locally without API costs.

#### Windows
1. Download Ollama from [ollama.ai](https://ollama.ai)
2. Run the installer
3. Open Command Prompt and verify: `ollama --version`
4. Pull a model: `ollama pull llama2`

#### macOS
```bash
# Download and install from ollama.ai, or use Homebrew
brew install ollama

# Verify installation
ollama --version

# Pull a model
ollama pull llama2
```

#### Linux
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version

# Pull a model
ollama pull llama2
```

#### Starting Ollama Service
```bash
# The service usually starts automatically
# To manually start:
ollama serve

# To test:
ollama run llama2
```

### Creative Tools Installation

Install these tools separately based on your needs:

#### Blender (3D Modeling & Animation)
- **Website**: [blender.org](https://www.blender.org/download/)
- **Version**: 3.0 or later recommended
- **Installation**: Download and follow platform-specific installer

#### Godot Engine (Game Development)
- **Website**: [godotengine.org](https://godotengine.org/download)
- **Version**: 4.0 or later recommended
- **Installation**: Download and extract (portable) or use installer

#### GIMP (Image Editing)
```bash
# Windows: Download from gimp.org
# macOS
brew install --cask gimp

# Linux
sudo apt install gimp  # Ubuntu/Debian
sudo dnf install gimp  # Fedora
```

#### Audacity (Audio Editing)
```bash
# Windows: Download from audacityteam.org
# macOS
brew install --cask audacity

# Linux
sudo apt install audacity  # Ubuntu/Debian
sudo dnf install audacity  # Fedora
```

#### FFmpeg (Video Processing)
```bash
# Windows: Download from ffmpeg.org or use chocolatey
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora
```

---

## Database Setup

Dual AI Studio uses SQLite for data storage, which is automatically configured.

### Automatic Database Creation

The database file is **automatically created** on first run:
- Location: `./database/dual_ai_studio.db`
- No manual setup required
- Tables are created automatically by the application

### Manual Database Initialization (if needed)

If you need to reset or manually initialize the database:

```bash
python -c "from app import init_db; init_db()"
```

### Database Location

The SQLite database is stored locally:
- **Default path**: `./database/dual_ai_studio.db`
- **Configuration**: Can be changed in `config.py` or environment variables

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred editor
nano .env  # or vim, code, etc.
```

### 2. Required Configuration

Edit `.env` with your API keys and preferences:

```ini
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# OpenAI API (Optional - for GPT models)
OPENAI_API_KEY=sk-your-openai-api-key

# Anthropic API (Optional - for Claude models)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Ollama Configuration (Optional - for local models)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Database Configuration
DATABASE_PATH=./database/dual_ai_studio.db

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

### 3. API Keys

To use cloud AI services, obtain API keys:

- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com)

**Note**: API keys are optional if using Ollama for local models.

### 4. File Permissions (Linux/macOS)

Ensure proper permissions:

```bash
chmod +x run.sh  # If using a run script
chmod 755 database/  # Database directory
```

---

## Verifying Installation

### 1. Check Python Dependencies

```bash
pip list | grep -E "(flask|openai|anthropic|requests)"
```

Expected output should include:
- flask
- openai
- anthropic
- requests
- (and other dependencies)

### 2. Run System Check

```bash
python -c "
import sys
print(f'Python Version: {sys.version}')

try:
    import flask
    print(f'Flask: {flask.__version__}')
except ImportError:
    print('Flask: NOT INSTALLED')

try:
    import openai
    print(f'OpenAI: {openai.__version__}')
except ImportError:
    print('OpenAI: NOT INSTALLED')

try:
    import anthropic
    print(f'Anthropic: Installed')
except ImportError:
    print('Anthropic: NOT INSTALLED')

print('\\nSystem check complete!')
"
```

### 3. Test Ollama Connection (if installed)

```bash
curl http://localhost:11434/api/version
```

---

## First Run Instructions

### 1. Start the Application

```bash
# Make sure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Run the application
python app.py

# Or if using a run script
./run.sh  # Linux/macOS
run.bat   # Windows
```

### 2. Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

### 3. Initial Setup

1. **Choose AI Backend**: Select between OpenAI, Anthropic, or Ollama
2. **Configure Settings**: Set your preferences in the settings panel
3. **Test Connection**: Send a test message to verify AI connectivity
4. **Explore Features**: Try different creative tools and AI capabilities

### 4. Stopping the Application

Press `Ctrl+C` in the terminal to stop the server.

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: `pip install` fails with permission error

**Solution**:
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### Issue: Python version too old

**Solution**:
```bash
# Check version
python --version

# Install Python 3.8+ from python.org
# Or use pyenv for version management
pyenv install 3.11.0
pyenv local 3.11.0
```

#### Issue: Module not found errors

**Solution**:
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Issue: Ollama connection refused

**Solution**:
```bash
# Check if Ollama is running
ollama serve

# Verify in another terminal
ollama list

# Check the correct port (default 11434)
curl http://localhost:11434/api/version
```

#### Issue: Database locked error

**Solution**:
```bash
# Close all instances of the application
# Delete lock file if exists
rm database/*.db-lock

# Restart application
python app.py
```

#### Issue: Port 5000 already in use

**Solution**:
```bash
# Change port in .env file
PORT=5001

# Or specify when running
flask run --port 5001
```

#### Issue: API key not recognized

**Solution**:
1. Check `.env` file exists in project root
2. Verify no extra spaces around API keys
3. Restart the application after changing `.env`
4. Check environment variables loaded:
   ```bash
   python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

#### Issue: Slow performance

**Solution**:
- Increase system RAM allocation
- Use local models with Ollama instead of API calls
- Close unnecessary applications
- Check internet connection for API-based models

#### Issue: SSL Certificate errors

**Solution**:
```bash
# Update certificates
pip install --upgrade certifi

# Or bypass SSL (not recommended for production)
export PYTHONHTTPSVERIFY=0  # Linux/macOS
set PYTHONHTTPSVERIFY=0     # Windows
```

### Getting Help

If you encounter issues not covered here:

1. **Check Documentation**: Review README.md and project wiki
2. **Search Issues**: Look for similar problems in GitHub Issues
3. **Create Issue**: Open a new issue with:
   - Your OS and Python version
   - Error messages and logs
   - Steps to reproduce
4. **Community Support**: Join discussions in the repository

---

## Additional Resources

- **GitHub Repository**: [Ada40/Dual-ai-studio](https://github.com/Ada40/Dual-ai-studio)
- **Project Wiki**: Check repository wiki for advanced topics
- **API Documentation**: 
  - [OpenAI API Docs](https://platform.openai.com/docs)
  - [Anthropic API Docs](https://docs.anthropic.com)
  - [Ollama Documentation](https://github.com/jmorganca/ollama)

---

## License and Copyright

Copyright © 2026 RFS (Ada40)

This project is licensed under the terms specified in the LICENSE file.

For questions, issues, or contributions, please visit the [GitHub repository](https://github.com/Ada40/Dual-ai-studio).

---

**Installation Complete!** 🎉

You're now ready to explore the creative possibilities of Dual AI Studio. Happy creating!
