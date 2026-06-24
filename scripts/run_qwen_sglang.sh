#!/usr/bin/env bash
# run_qwen_sglang.sh
# --------------------------------------------------------------
# Launches an sglang inference server for the Qwen‑3‑VL‑8B model.
# The server will expose an OpenAI‑compatible endpoint at
# http://0.0.0.0:8000/v1 (adjust PORT if desired).
# --------------------------------------------------------------

set -e

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
# Path where the model was copied on the SOL machine (scratch space recommended)
MODEL_DIR="/scratch/${USER}/models/Qwen3-VL-8B-Instruct"
# Port for the OpenAI‑compatible API
PORT=8000
# Conda environment location (must match install_sglang.sh)
CONDA_ENV_PATH="/scratch/${USER}/sglang_env"

# -------------------------------------------------------------------
# Verify model directory exists
# -------------------------------------------------------------------
if [ ! -d "$MODEL_DIR" ]; then
  echo "❌ Model directory $MODEL_DIR does not exist. Please copy the model files there before starting the server."
  exit 1
fi

# -------------------------------------------------------------------
# Activate the conda environment
# -------------------------------------------------------------------
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_PATH"

# -------------------------------------------------------------------
# Launch sglang server
# -------------------------------------------------------------------
# sglang serve will start a FastAPI/Uvicorn server that mimics the OpenAI API.
# The flags used below are recommended for a 8‑B model on a GPU.
sglang serve \
  --model-path "$MODEL_DIR" \
  --port $PORT \
  --api-version v1 \
  --max-batch-size 8 \
  --max-tokens 2048

# The command blocks and prints logs such as:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
