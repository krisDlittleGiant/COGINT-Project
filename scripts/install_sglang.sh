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
# Finished
# -------------------------------------------------------------------
echo "✅ Conda environment with sglang installed at $CONDA_ENV_PATH"
