import os
import sys
import subprocess
import getpass
import argparse

def run_command(cmd, cwd=None):
    """Executes a shell command and streams the output."""
    print(f"\n> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: Command failed with exit code {result.returncode}")
        sys.exit(1)

def setup_environment():
    parser = argparse.ArgumentParser(description="Cross-platform OSWorld Environment Setup")
    parser.add_argument("--sol-path", type=str, help="Override default SOL path", default=None)
    args = parser.parse_args()

    python_version = "3.10"
    osworld_repo = "https://github.com/xlang-ai/OSWorld.git"
    
    # 1. Detect OS and set paths
    is_windows = sys.platform.startswith("win")
    
    if is_windows:
        print("Detected Local Windows Environment.")
        env_path = os.path.abspath("./.osworld_env")
        
        # Hide from git locally
        gitignore_path = ".gitignore"
        env_dir_name = ".osworld_env"
        if not os.path.exists(gitignore_path) or env_dir_name not in open(gitignore_path).read():
            with open(gitignore_path, "a") as f:
                f.write(f"\n{env_dir_name}\n")
            print(f"Added {env_dir_name} to .gitignore")
            
    else:
        print("Detected Linux/SOL Environment.")
        user = getpass.getuser()
        # Default to scratch on SOL unless overridden
        env_path = args.sol_path if args.sol_path else f"/scratch/{user}/osworld_env"

    print(f"\nTarget Environment Path: {env_path}")

    # 2. Check if environment already exists
    if os.path.exists(env_path):
        print(f"Warning: Directory {env_path} already exists.")
        proceed = input("Do you want to proceed with dependency installation anyway? (y/n): ")
        if proceed.lower() != 'y':
            sys.exit(0)
    else:
        # Create Conda Environment
        # Use mamba if on Linux for speed, otherwise standard conda
        conda_cmd = "mamba" if not is_windows and subprocess.call("command -v mamba", shell=True, stdout=subprocess.DEVNULL) == 0 else "conda"
        run_command(f"{conda_cmd} create --prefix {env_path} python={python_version} -y")

    # 3. Handle OSWorld Repository
    submodule_path = os.path.join("benchmarks", "OSWorld")
    standalone_path = "OSWorld"
    
    if os.path.exists(submodule_path):
        print("\nFound OSWorld submodule.")
        target_dir = submodule_path
        if not os.path.exists(os.path.join(submodule_path, "requirements.txt")):
            print("Submodule appears empty. Initializing git submodules...")
            run_command("git submodule update --init --recursive")
    else:
        if not os.path.exists(standalone_path):
            print("\nCloning OSWorld repository...")
            run_command(f"git clone {osworld_repo}")
        else:
            print("\nOSWorld directory already exists.")
        target_dir = standalone_path

    # 4. Install Dependencies
    # We must call pip directly from the newly created environment
    pip_executable = os.path.join(env_path, "Scripts", "pip") if is_windows else os.path.join(env_path, "bin", "pip")
    
    print("\nInstalling Python dependencies...")
    run_command(f"{pip_executable} install -r requirements.txt", cwd=target_dir)

    if not is_windows:
        print("\nInstalling SOL inference dependencies (vLLM)...")
        run_command(f"{pip_executable} install vllm")

    # 5. Output Next Steps
    print("\n" + "="*50)
    print("INITIALIZATION COMPLETE!")
    print("="*50)
    print("To activate this environment, run the following command in your terminal:\n")
    print(f"conda activate {env_path}")
    print("\n" + "="*50)

if __name__ == "__main__":
    setup_environment()