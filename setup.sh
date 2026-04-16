#!/usr/bin/env bash
# ============================================================
# AgriSolve DaaS — Homebrew Setup & Dependency Picker
# Run: chmod +x setup.sh && ./setup.sh
# ============================================================

set -euo pipefail

# ── Colours ─────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

# ── Helpers ──────────────────────────────────────────────────
header()  { echo -e "\n${BOLD}${BLUE}══════════════════════════════════════════${RESET}"; echo -e "${BOLD}${BLUE}  $1${RESET}"; echo -e "${BOLD}${BLUE}══════════════════════════════════════════${RESET}"; }
step()    { echo -e "\n${CYAN}▶ $1${RESET}"; }
ok()      { echo -e "${GREEN}  ✓ $1${RESET}"; }
warn()    { echo -e "${YELLOW}  ⚠ $1${RESET}"; }
info()    { echo -e "  ${BLUE}$1${RESET}"; }
ask()     { echo -e "\n${BOLD}${YELLOW}$1${RESET}"; }

install_if_missing() {
  local pkg=$1 tap=${2:-}
  if brew list --formula "$pkg" &>/dev/null; then
    ok "$pkg already installed"
  else
    step "Installing $pkg..."
    [[ -n "$tap" ]] && brew tap "$tap"
    brew install "$pkg"
    ok "$pkg installed"
  fi
}

install_cask_if_missing() {
  local pkg=$1
  if brew list --cask "$pkg" &>/dev/null; then
    ok "$pkg (cask) already installed"
  else
    step "Installing cask: $pkg..."
    brew install --cask "$pkg"
    ok "$pkg installed"
  fi
}

pick() {
  # pick <prompt> <default_index> option1 option2 ...
  local prompt=$1 default=$2; shift 2
  local opts=("$@") choice
  ask "$prompt"
  for i in "${!opts[@]}"; do
    local marker="  "; [[ $i -eq $default ]] && marker="${CYAN}▶${RESET}"
    echo -e "  ${marker} [${BOLD}$((i+1))${RESET}] ${opts[$i]}"
  done
  echo -e "  [${BOLD}s${RESET}] Skip this step"
  read -rp "  Choice (default $((default+1))): " choice
  choice=${choice:-$((default+1))}
  if [[ "$choice" == "s" ]]; then PICK_RESULT="SKIP"; return; fi
  PICK_RESULT="${opts[$((choice-1))]}"
}

confirm() {
  read -rp "  ${BOLD}$1 [y/N]: ${RESET}" ans
  [[ "${ans,,}" == "y" ]]
}

# ── Trap for clean exit ───────────────────────────────────────
trap 'echo -e "\n${RED}Script interrupted.${RESET}"; exit 1' INT

# ═══════════════════════════════════════════════════════════════
header "Step 0 — Homebrew Health Check"
# ═══════════════════════════════════════════════════════════════

if ! command -v brew &>/dev/null; then
  warn "Homebrew not found. Installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  ok "Homebrew found: $(brew --version | head -1)"
fi

step "Updating Homebrew..."
brew update

step "Checking for outdated packages..."
OUTDATED=$(brew outdated --formula 2>/dev/null || true)
OUTDATED_CASKS=$(brew outdated --cask 2>/dev/null || true)

if [[ -z "$OUTDATED" && -z "$OUTDATED_CASKS" ]]; then
  ok "Everything is up to date"
else
  [[ -n "$OUTDATED" ]]       && { warn "Outdated formulae:"; echo "$OUTDATED" | sed 's/^/    /'; }
  [[ -n "$OUTDATED_CASKS" ]] && { warn "Outdated casks:";    echo "$OUTDATED_CASKS" | sed 's/^/    /'; }
  if confirm "Upgrade all outdated packages now?"; then
    brew upgrade
    ok "All packages upgraded"
  else
    warn "Skipping upgrade — run 'brew upgrade' manually later"
  fi
fi

step "Running brew doctor..."
brew doctor 2>&1 | grep -E "^Warning:|^Error:" | sed 's/^/  /' || ok "No issues found"

step "Cleaning up old versions..."
brew cleanup -s
ok "Cleanup done"

echo -e "\n${BOLD}Installed formulae:${RESET}"
brew list --formula | column

# ═══════════════════════════════════════════════════════════════
header "Step 1 — Core Language Runtime"
# ═══════════════════════════════════════════════════════════════

pick "Python version manager:" 0 \
  "pyenv  (best-in-class, switch between versions)" \
  "mise   (polyglot: Python + Node + Ruby in one tool)" \
  "asdf   (original polyglot manager)" \
  "Skip   (use system Python)"

case "$PICK_RESULT" in
  pyenv*)
    install_if_missing pyenv
    if ! brew list --formula python &>/dev/null; then
      step "Installing latest stable Python via pyenv..."
      LATEST_PY=$(pyenv install --list | grep -E '^\s+3\.[0-9]+\.[0-9]+$' | tail -1 | tr -d ' ')
      pyenv install "$LATEST_PY" || warn "Python $LATEST_PY may already be installed"
      pyenv global "$LATEST_PY"
      ok "Python $LATEST_PY set as global"
    fi
    PYENV_INIT='eval "$(pyenv init -)"'
    for rc in ~/.zshrc ~/.bashrc; do
      grep -q "pyenv init" "$rc" 2>/dev/null || echo "$PYENV_INIT" >> "$rc"
    done
    ;;
  mise*)
    install_if_missing mise
    mise use --global python@latest
    ok "mise installed Python (latest)"
    ;;
  asdf*)
    install_if_missing asdf
    asdf plugin add python 2>/dev/null || true
    asdf install python latest
    asdf global python latest
    ;;
  SKIP|Skip*) warn "Skipping Python version manager" ;;
esac

pick "Python package manager:" 0 \
  "uv   (blazing fast, Rust-based, replaces pip+venv+pip-tools)" \
  "pip  (standard, comes with Python)" \
  "pipx (for global CLI tools only)"

case "$PICK_RESULT" in
  uv*)
    install_if_missing uv
    ok "uv installed — use 'uv pip install', 'uv venv', 'uv run'"
    ;;
  pip*) ok "Using system pip" ;;
  pipx*)
    install_if_missing pipx
    pipx ensurepath
    ;;
  SKIP) warn "Skipping" ;;
esac

# ═══════════════════════════════════════════════════════════════
header "Step 2 — Version Control"
# ═══════════════════════════════════════════════════════════════

install_if_missing git

pick "Git credential helper:" 0 \
  "gh   (GitHub CLI — PAT, SSH, PR management in one tool)" \
  "git-credential-manager (cross-platform, GUI prompts)" \
  "SSH  (manual key setup — most secure)"

case "$PICK_RESULT" in
  gh*)
    install_if_missing gh
    step "Authenticating with GitHub..."
    if gh auth status &>/dev/null; then
      ok "Already authenticated with GitHub"
    else
      gh auth login
    fi
    ;;
  git-credential*)
    install_cask_if_missing git-credential-manager
    ;;
  SSH*)
    if [[ ! -f ~/.ssh/id_ed25519 ]]; then
      read -rp "  Enter your GitHub email: " GH_EMAIL
      ssh-keygen -t ed25519 -C "$GH_EMAIL" -f ~/.ssh/id_ed25519 -N ""
      eval "$(ssh-agent -s)"
      ssh-add ~/.ssh/id_ed25519
      info "Your public key (add to GitHub → Settings → SSH keys):"
      cat ~/.ssh/id_ed25519.pub
    else
      ok "SSH key already exists at ~/.ssh/id_ed25519"
    fi
    ;;
  SKIP) warn "Skipping credential helper" ;;
esac

pick "Git TUI / history explorer:" 0 \
  "lazygit  (best-in-class TUI, staging/branching/log)" \
  "gitui    (Rust-based TUI, very fast)" \
  "tig      (ncurses log browser, lightweight)" \
  "Skip"

case "$PICK_RESULT" in
  lazygit*) install_if_missing lazygit ;;
  gitui*)   install_if_missing gitui ;;
  tig*)     install_if_missing tig ;;
  SKIP|Skip*) warn "Skipping Git TUI" ;;
esac

# ═══════════════════════════════════════════════════════════════
header "Step 3 — Data Ingestion + Validation"
# ═══════════════════════════════════════════════════════════════

pick "In-process SQL / data validation engine:" 0 \
  "duckdb   (best-in-class: query CSV/Parquet/JSON with SQL, zero-server)" \
  "sqlite   (lightweight, universal, good for persistent star schema)" \
  "Both     (duckdb for validation, sqlite for storage)"

case "$PICK_RESULT" in
  duckdb*)  install_if_missing duckdb ;;
  sqlite*)  install_if_missing sqlite ;;
  Both*)    install_if_missing duckdb; install_if_missing sqlite ;;
  SKIP)     warn "Skipping" ;;
esac

pick "Python data stack (installed into your project venv):" 0 \
  "pandas + openpyxl + duckdb-engine   (standard AgriSolve validation stack)" \
  "polars + connectorx                  (10x faster than pandas, Rust-based)" \
  "Both                                 (polars for speed, pandas for compatibility)"

PYTHON_STACK="$PICK_RESULT"
# Installed into venv in Step 8

pick "CSV/data quality checker:" 0 \
  "great_expectations  (industry standard, generates HTML validation reports)" \
  "pandera             (lightweight schema validation, integrates with pandas/polars)" \
  "frictionless        (OKFN standard, validates tabular data against schemas)" \
  "Skip (manual validation only)"

DATA_QUALITY="$PICK_RESULT"

# ═══════════════════════════════════════════════════════════════
header "Step 4 — Database (optional, for scale)"
# ═══════════════════════════════════════════════════════════════

pick "Production database (use when Power BI in-memory gets slow, 5+ clients):" 0 \
  "postgresql  (best-in-class open source RDBMS, Power BI connects natively)" \
  "Skip for now (DuckDB + SQLite is sufficient for first 10 clients)"

case "$PICK_RESULT" in
  postgresql*)
    install_if_missing postgresql@16
    brew services start postgresql@16
    ok "PostgreSQL 16 running as a service"
    ;;
  SKIP|Skip*) info "Skipping — revisit at 5+ clients" ;;
esac

# ═══════════════════════════════════════════════════════════════
header "Step 5 — Orchestration + Automation"
# ═══════════════════════════════════════════════════════════════

pick "Task runner / script orchestration:" 0 \
  "just     (best-in-class Makefile replacement, clean syntax)" \
  "make     (universal, already on macOS)" \
  "poethepoet (Python-native task runner, lives in pyproject.toml)"

case "$PICK_RESULT" in
  just*)        install_if_missing just ;;
  make*)        ok "make already available on macOS" ;;
  poethepoet*)  info "poethepoet installed via pip in venv setup" ;;
  SKIP)         warn "Skipping" ;;
esac

pick "Local automation / workflow tool (for refresh monitoring at 5+ clients):" 0 \
  "Skip for now — GitHub Actions handles scheduling until 5+ clients" \
  "n8n   (self-hosted on VPS later — Hetzner R100/mo)"

case "$PICK_RESULT" in
  n8n*)
    install_if_missing node
    npm install -g n8n
    ok "n8n installed — run 'n8n start' to launch"
    ;;
  SKIP|Skip*) info "Revisit when refresh monitoring becomes a time drain" ;;
esac

# ═══════════════════════════════════════════════════════════════
header "Step 6 — Code Editor + Dev Tooling"
# ═══════════════════════════════════════════════════════════════

pick "Primary code editor:" 0 \
  "VS Code              (best ecosystem for Python + Power Query + SQL + Git)" \
  "Cursor               (VS Code fork with AI pair programming built-in)" \
  "Neovim               (terminal-native, blazing fast, steep curve)" \
  "Skip (already installed)"

case "$PICK_RESULT" in
  "VS Code"*)   install_cask_if_missing visual-studio-code ;;
  Cursor*)      install_cask_if_missing cursor ;;
  Neovim*)      install_if_missing neovim ;;
  SKIP|Skip*)   ok "Skipping editor install" ;;
esac

pick "Terminal multiplexer:" 0 \
  "tmux     (industry standard, session persistence, split panes)" \
  "zellij   (modern Rust-based, better defaults out of the box)" \
  "Skip"

case "$PICK_RESULT" in
  tmux*)   install_if_missing tmux ;;
  zellij*) install_if_missing zellij ;;
  SKIP|Skip*) warn "Skipping" ;;
esac

# ═══════════════════════════════════════════════════════════════
header "Step 7 — Utilities"
# ═══════════════════════════════════════════════════════════════

step "Installing essential CLI utilities (non-negotiable)..."
UTILS=(curl wget jq yq ripgrep fd bat tree watch httpie)
for u in "${UTILS[@]}"; do install_if_missing "$u"; done

pick "JSON/data exploration in terminal:" 0 \
  "jq + jless   (jq for transforms, jless for interactive browsing)" \
  "jq only" \
  "fx           (interactive JSON viewer, Node-based)"

case "$PICK_RESULT" in
  "jq + jless"*) install_if_missing jq; install_if_missing jless ;;
  "jq only"*)    install_if_missing jq ;;
  fx*)           install_if_missing node; npm install -g fx ;;
  SKIP)          warn "Skipping" ;;
esac

pick "Secret / environment variable management:" 0 \
  "direnv   (auto-loads .env per project directory — best workflow)" \
  "dotenv   (manual load via CLI)" \
  "Skip (use .env files manually)"

case "$PICK_RESULT" in
  direnv*)
    install_if_missing direnv
    for rc in ~/.zshrc ~/.bashrc; do
      grep -q "direnv hook" "$rc" 2>/dev/null || echo 'eval "$(direnv hook bash)"' >> "$rc"
    done
    ok "direnv installed — add 'eval \"\$(direnv hook zsh)\"' to ~/.zshrc"
    ;;
  SKIP|Skip*|dotenv*) warn "Using manual .env approach" ;;
esac

# ═══════════════════════════════════════════════════════════════
header "Step 8 — Project Python Environment"
# ═══════════════════════════════════════════════════════════════

PROJ_DIR="$HOME/AgriSolve"
step "Creating project at $PROJ_DIR..."
mkdir -p "$PROJ_DIR"
cd "$PROJ_DIR"

if command -v uv &>/dev/null; then
  step "Creating virtual environment with uv..."
  uv venv .venv
  source .venv/bin/activate

  step "Installing Python dependencies (from your choices)..."

  # Core always installed
  uv pip install pandas openpyxl duckdb duckdb-engine requests python-dotenv rich typer

  case "$PYTHON_STACK" in
    polars*)   uv pip install polars connectorx pyarrow ;;
    Both*)     uv pip install polars connectorx pyarrow pandas openpyxl ;;
    *)         uv pip install pandas openpyxl ;;
  esac

  case "$DATA_QUALITY" in
    great_expectations*) uv pip install great-expectations ;;
    pandera*)            uv pip install pandera ;;
    frictionless*)       uv pip install frictionless ;;
  esac

  # Dev tooling always
  uv pip install pytest pytest-cov black ruff mypy pre-commit ipython

  ok "Python environment ready at $PROJ_DIR/.venv"

elif python3 -m venv --help &>/dev/null; then
  step "Creating virtual environment with venv..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install pandas openpyxl duckdb requests python-dotenv rich typer pytest black ruff
  ok "Python environment ready"
else
  warn "No Python found — install via pyenv then re-run"
fi

# ═══════════════════════════════════════════════════════════════
header "Step 9 — Git Repository Init"
# ═══════════════════════════════════════════════════════════════

cd "$PROJ_DIR"

if [[ ! -d .git ]]; then
  step "Initialising git repo..."
  git init
  git branch -M main

  # .gitignore
  cat > .gitignore << 'EOF'
# Python
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/

# Environment
.env
.envrc

# Data (never commit client data)
data/raw/
data/exports/
*.csv
*.xlsx
!sample_data/*.csv

# Power BI
*.pbix

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/settings.json
*.swp
EOF

  # pyproject.toml
  cat > pyproject.toml << 'EOF'
[project]
name = "AgriSolve"
version = "0.1.0"
description = "AgriSolve DaaS — Power BI dashboard product for SME brokers"
requires-python = ">=3.11"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.black]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
EOF

  # Folder structure
  mkdir -p src/{ingestion,validation,models} tests sample_data docs scripts

  # Validation scaffold
  cat > src/validation/check_commission.py << 'PYEOF'
"""
Commission export validator — runs before every Power BI refresh.
Usage: python src/validation/check_commission.py data/exports/Commission_YYYYMM.csv
"""
import sys
import duckdb
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

REQUIRED_COLS = {
    "Period", "PolicyNumber", "Provider",
    "Adviser", "CommissionType", "CommissionAmount", "StatementId"
}

def validate(filepath: str) -> bool:
    path = Path(filepath)
    if not path.exists():
        console.print(f"[red]File not found: {filepath}[/red]")
        return False

    con = duckdb.connect()
    df = con.execute(f"SELECT * FROM read_csv_auto('{path}', header=true)").df()

    table = Table(title=f"Validation — {path.name}", show_header=True)
    table.add_column("Check"); table.add_column("Result"); table.add_column("Detail")

    passed = True

    # Column check
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        table.add_row("Required columns", "[red]FAIL[/red]", f"Missing: {missing}")
        passed = False
    else:
        table.add_row("Required columns", "[green]PASS[/green]", f"{len(df.columns)} columns present")

    # Row count
    table.add_row("Row count", "[green]PASS[/green]", str(len(df)))

    # Null check on critical columns
    for col in ["PolicyNumber", "CommissionAmount", "Provider"]:
        if col in df.columns:
            null_count = df[col].isna().sum()
            status = "[green]PASS[/green]" if null_count == 0 else "[yellow]WARN[/yellow]"
            table.add_row(f"Nulls in {col}", status, f"{null_count} nulls")

    # Amount check
    if "CommissionAmount" in df.columns:
        negatives = (df["CommissionAmount"] < 0).sum()
        if negatives > 0:
            table.add_row("Negative amounts", "[yellow]WARN[/yellow]", f"{negatives} reversal lines")
        else:
            table.add_row("Negative amounts", "[green]PASS[/green]", "None")

        total = df["CommissionAmount"].sum()
        table.add_row("Total commission", "[blue]INFO[/blue]", f"R {total:,.2f}")

    # Duplicate check
    if {"PolicyNumber", "Period", "CommissionType"}.issubset(df.columns):
        dupes = df.duplicated(subset=["PolicyNumber", "Period", "CommissionType"]).sum()
        status = "[yellow]WARN[/yellow]" if dupes > 0 else "[green]PASS[/green]"
        table.add_row("Duplicate lines", status, f"{dupes} duplicates")

    console.print(table)
    return passed

if __name__ == "__main__":
    fp = sys.argv[1] if len(sys.argv) > 1 else "data/exports/Commission_YYYYMM.csv"
    success = validate(fp)
    sys.exit(0 if success else 1)
PYEOF

  # Pre-commit config
  cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
EOF

  git add .
  git commit -m "chore: initialise AgriSolve DaaS project structure"
  ok "Git repo initialised with first commit"
else
  ok "Git repo already initialised"
fi

# ═══════════════════════════════════════════════════════════════
header "Step 10 — Remote + Pre-commit Hooks"
# ═══════════════════════════════════════════════════════════════

REMOTE_URL="https://github.com/AgriSolveSA/AgriSolve.git"

if git remote get-url origin &>/dev/null 2>&1; then
  ok "Remote 'origin' already set: $(git remote get-url origin)"
else
  if confirm "Add GitHub remote ($REMOTE_URL)?"; then
    git remote add origin "$REMOTE_URL"
    ok "Remote added"
  fi
fi

if command -v pre-commit &>/dev/null || [[ -f .venv/bin/pre-commit ]]; then
  step "Installing pre-commit hooks..."
  .venv/bin/pre-commit install 2>/dev/null || pre-commit install
  ok "Pre-commit hooks installed"
fi

if confirm "Push to GitHub now (branch: main)?"; then
  git push -u origin main
  ok "Pushed to origin/main"
fi

# ═══════════════════════════════════════════════════════════════
header "Step 11 — Smoke Tests"
# ═══════════════════════════════════════════════════════════════

step "Running smoke tests..."

PASS=0; FAIL=0

smoke() {
  local label=$1 cmd=$2
  if eval "$cmd" &>/dev/null 2>&1; then
    ok "$label"
    ((PASS++))
  else
    warn "$label — FAILED (run manually: $cmd)"
    ((FAIL++))
  fi
}

smoke "git"              "git --version"
smoke "Python 3"         "python3 --version"
smoke "pip / uv"         "command -v uv || command -v pip3"
smoke "duckdb"           "duckdb --version"
smoke "jq"               "jq --version"
smoke "rg (ripgrep)"     "rg --version"
smoke "bat"              "bat --version"
smoke "GitHub CLI"       "gh --version"
smoke "pre-commit"       ".venv/bin/pre-commit --version || pre-commit --version"
smoke "Commission validator" "python3 $PROJ_DIR/src/validation/check_commission.py --help 2>/dev/null || true"

echo ""
echo -e "${BOLD}Smoke tests: ${GREEN}$PASS passed${RESET} / ${RED}$FAIL failed${RESET}"

# ═══════════════════════════════════════════════════════════════
header "✓ Setup Complete"
# ═══════════════════════════════════════════════════════════════

echo -e "
${BOLD}Project location:${RESET}  $PROJ_DIR
${BOLD}Virtual env:${RESET}       $PROJ_DIR/.venv  (activate: source .venv/bin/activate)
${BOLD}Validator:${RESET}         python3 src/validation/check_commission.py <file.csv>
${BOLD}Remote:${RESET}            $REMOTE_URL

${BOLD}${CYAN}Next commands:${RESET}
  cd $PROJ_DIR
  source .venv/bin/activate
  python3 src/validation/check_commission.py data/exports/Commission_202601_CLEAN.csv
  git status

${BOLD}${YELLOW}Reminder:${RESET} Never commit .pbix files or client CSVs to Git.
           Those stay in the client's SharePoint folder.
"
