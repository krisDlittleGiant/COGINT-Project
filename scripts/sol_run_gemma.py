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

    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", args.model,
        "--host", args.host,
        "--port", str(args.port),
        "--dtype", "auto",
        "--tensor-parallel-size", str(args.tp),
        "--trust-remote-code",
        "--limit-mm-per-prompt", "image=4"
    ]
    
    print(f"Starting vLLM server with command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Server exited with error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Shutting down server.")

if __name__ == "__main__":
    main()
