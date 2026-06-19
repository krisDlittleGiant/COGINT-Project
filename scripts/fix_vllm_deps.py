import subprocess
import sys

def run_command(cmd):
    print(f"\n> Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Error: Command failed with exit code {result.returncode}")
        sys.exit(1)

def main():
    print("Resolving vLLM and Pixtral dependency conflicts...")
    
    # Use the python executable currently running to invoke pip
    pip_cmd = f"{sys.executable} -m pip"
    
    # Pixtral requires recent versions of transformers, vLLM, and mistral_common to properly parse the images.
    packages = [
        "vllm>=0.6.4",
        "transformers>=4.45.0",
        "mistral_common>=1.4.4",
        "accelerate",
        "xformers"
    ]
    
    run_command(f"{pip_cmd} install --upgrade {' '.join(packages)}")
    
    print("\n" + "="*50)
    print("Dependencies upgraded successfully!")
    print("You can now re-run the sol_run_gemma.py script.")
    print("="*50)

if __name__ == "__main__":
    main()
