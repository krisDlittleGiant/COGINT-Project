import os
import subprocess
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run Gemma 12B via vLLM on SOL")
    parser.add_argument("--model", type=str, default="google/gemma-12b-it", help="Path to model or HuggingFace repo name")
    parser.add_argument("--port", type=int, default=8000, help="Port to expose the OpenAI-compatible server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface to bind to")
    parser.add_argument("--tp", type=int, default=1, help="Tensor parallel size (number of GPUs to use)")
    args = parser.parse_args()

    # Redirect HuggingFace cache to avoid filling up the small home directory quota on SOL
    if "HF_HOME" not in os.environ:
        user = os.environ.get("USER", "default_user")
        os.environ["HF_HOME"] = f"/scratch/{user}/hf_cache"



    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", args.model,
        "--host", args.host,
        "--port", str(args.port),
        "--dtype", "auto",
        "--tensor-parallel-size", str(args.tp),
        "--trust-remote-code",
        "--limit-mm-per-prompt", "image=4",
        "--gpu-memory-utilization", "0.90", # You have the whole 80GB GPU now!
        "--max-model-len", "32768"          # Lots of context room for OSWorld screenshots
    ]
    
    if "mistral" in args.model.lower() or "pixtral" in args.model.lower():
        cmd.extend(["--tokenizer-mode", "mistral"])
    
    print(f"Starting vLLM server with command: {' '.join(cmd)}")
    try:
        # Strip out LD_LIBRARY_PATH so the supercomputer's outdated system NCCL
        # doesn't override the correct pip-installed version and crash PyTorch!
        env = os.environ.copy()
        env.pop("LD_LIBRARY_PATH", None)
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Server exited with error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Shutting down server.")

if __name__ == "__main__":
    main()
