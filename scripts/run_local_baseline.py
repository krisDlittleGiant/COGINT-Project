import os
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run Local OSWorld Baseline")
    parser.add_argument("--max-steps", type=int, default=30, help="Maximum step count for the baseline")
    parser.add_argument("--model", type=str, default="gemma-12b", help="Model identifier to use")
    args = parser.parse_args()

    max_steps = args.max_steps
    model = args.model

    # Target the OSWorld run.py directly
    osworld_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "benchmarks", "OSWorld"))
    run_script = os.path.join(osworld_dir, "run.py")

    cmd = [
        "python", run_script,
        "--max_steps", str(max_steps),
        "--model", model,
        "--provider_name", "docker"
    ]

    print(f"Running OSWorld Baseline with max_steps={max_steps} and model={model}...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, cwd=osworld_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Baseline run failed with error: {e}")
    except KeyboardInterrupt:
        print("Baseline run interrupted.")

if __name__ == "__main__":
    main()
