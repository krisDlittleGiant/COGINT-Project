#!/usr/bin/env bash
# install_sglang_conda.sh
# -------------------------------------------------------------------
# This script creates a **conda** environment in the scratch directory
# (/scratch/${USER}/sglang_env) and installs sglang + the ML stack.
# It assumes that the `conda` command is available on the SOL machine.
# -------------------------------------------------------------------

set -e

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
# Location of the conda environment (scratch space, not on main storage)
CONDA_ENV_PATH="/scratch/${USER}/sglang_env"

# Python version to use (adjust if you need a different minor version)
PYTHON_VER="3.11"

# -------------------------------------------------------------------
# Create the conda environment (if it does not already exist)
# -------------------------------------------------------------------
if [ ! -d "$CONDA_ENV_PATH" ]; then
  echo "Creating conda environment at $CONDA_ENV_PATH"
  conda create -y -p "$CONDA_ENV_PATH" python=$PYTHON_VER
else
  echo "Conda environment already exists at $CONDA_ENV_PATH"
fi

# -------------------------------------------------------------------
# Activate the environment
# -------------------------------------------------------------------
# `conda` needs to be initialized; this works for most installations.
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_PATH"

# -------------------------------------------------------------------
# Upgrade pip and install packages
# -------------------------------------------------------------------
pip install --upgrade pip setuptools wheel

# sglang (>=0.2) + bitsandbytes for 4‑bit NF4 quantization
pip install "sglang>=0.2" bitsandbytes==0.41.3

# Core ML stack (torch, transformers, accelerate). Adjust the torch version
# according to the CUDA driver on SOL if needed.
pip install torch==2.2.0 transformers==4.41.0 accelerate==0.31.0

# -------------------------------------------------------------------
# Model download configuration
# -------------------------------------------------------------------
MODEL_ROOT="/scratch/${USER}/models"
MODEL_NAME="Qwen3-VL-8B-Instruct"
MODEL_DIR="${MODEL_ROOT}/${MODEL_NAME}"
MODEL_REPO="https://huggingface.co/Qwen/${MODEL_NAME}"

if [ -d "$MODEL_DIR" ]; then
  echo "✅ Model already present at $MODEL_DIR"
else
  echo "📥 Downloading Qwen‑3‑VL‑8B model to $MODEL_DIR …"
  mkdir -p "$MODEL_ROOT"
  # Try git lfs first
  if command -v git >/dev/null 2>&1 && git lfs version >/dev/null 2>&1; then
    git lfs clone "$MODEL_REPO" "$MODEL_DIR" || {
      echo "❌ git lfs clone failed – falling back to huggingface_hub"
      rm -rf "$MODEL_DIR"
    }
  fi

  # Fallback using huggingface_hub
  if [ ! -d "$MODEL_DIR" ]; then
    echo "🛠️ Using huggingface_hub to download…"
    pip install --upgrade huggingface_hub
    python - <<'PY'
import os
from huggingface_hub import snapshot_download
model_dir = os.getenv('MODEL_DIR')
repo_id = os.getenv('MODEL_REPO').replace('https://huggingface.co/', '')
snapshot_download(repo_id=repo_id, local_dir=model_dir, resume_download=True)
PY
  fi

  if [ -d "$MODEL_DIR" ]; then
    echo "✅ Model download completed: $MODEL_DIR"
  else
    echo "❌ Failed to download the model."
    exit 1
  fi
fi

# -------------------------------------------------------------------
# Finished
# -------------------------------------------------------------------
echo "✅ Conda environment with sglang installed at $CONDA_ENV_PATH and model ready at $MODEL_DIR"
