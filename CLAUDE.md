# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spraycharles is a low and slow password spraying tool designed for authorized penetration testing. It implements multiple authentication modules for different services (Office365, OWA, ADFS, Okta, SMB, etc.) and is built using Python with the Typer CLI framework.

## Development Commands

### Setup and Installation
```bash
# Install from source with Poetry (recommended for development)
pip3 install poetry
poetry install

# Install from PyPI
pip3 install spraycharles

# Build Docker container
cd extras && docker build . -t spraycharles
```

### Code Quality and Testing
```bash
# Format code with Black
poetry run black spraycharles/

# Sort imports with isort
poetry run isort spraycharles/ --profile black --filter-files

# Run pre-commit hooks
poetry run pre-commit run --all-files

# Run tests with pytest
poetry run pytest
```

## Architecture

### Core Components

1. **CLI Entry Point** (`spraycharles/__main__.py`): Uses Typer to create the main CLI application, dynamically loading all command modules.

2. **Command Modules** (`spraycharles/commands/`):
   - `spray.py`: Main spraying functionality
   - `analyze.py`: Results analysis
   - `gen.py`: Password list generation
   - `parse.py`: NTLM/SMB domain extraction
   - `modules.py`: List available spray modules

3. **Core Library** (`spraycharles/lib/`):
   - `spraycharles.py`: Main Spraycharles class orchestrating spray operations
   - `analyze.py`: Statistical analysis of spray results
   - `logger.py`: Logging configuration with Rich console output
   - `utils/`: Notification handlers and result management

4. **Target Modules** (`spraycharles/targets/`):
   - Each file implements a specific authentication protocol (e.g., `Office365.py`, `Smb.py`)
   - `BaseHttpTarget.py`: Base class for HTTP-based targets
   - All modules follow a consistent interface for authentication attempts

### Key Design Patterns

- **Module System**: Target modules are dynamically loaded and must implement a standard interface
- **Single-threaded by Design**: Intentionally slow to avoid detection during penetration tests
- **File-based Configuration**: Supports YAML config files and saves last configuration
- **Live File Updates**: Username/password lists can be modified during execution

### Dependencies

- `typer` & `typer-config`: CLI framework and configuration
- `rich`: Console output formatting and progress bars
- `requests` & `requests_ntlm`: HTTP authentication
- `impacket`: SMB protocol implementation
- `numpy`: Statistical analysis
- `pymsteams`, `discord-webhook`: Notifications

## Important Notes

- Output files are stored in `~/.spraycharles/` by default
- The tool creates `last-config.yaml` in the current directory after each run
- Pre-commit hooks enforce code formatting with Black and isort
- All target modules inherit from BaseHttpTarget for consistent behavior
- Results are output in JSON format for analysis