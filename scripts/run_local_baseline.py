import os
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run Local OSWorld Baseline")
    parser.add_argument("--max-steps", type=int, default=30, help="Maximum step count for the baseline")
    parser.add_argument("--model", type=str, default="gemma-12b", help="Model identifier to use")
    parser.add_argument("--observation-type", type=str, default="screenshot_a11y_tree", choices=["screenshot", "a11y_tree", "screenshot_a11y_tree", "som"], help="Observation type for the environment")
    parser.add_argument("--provider-name", type=str, default="docker", choices=["docker", "vmware", "virtualbox"], help="Virtual machine provider")
    parser.add_argument("--path-to-vm", type=str, default=None, help="Path to the virtual machine (.vmx file for vmware, .qcow2 for docker)")
    parser.add_argument("--example-id", type=str, default=None, help="Specific task ID to run")
    args = parser.parse_args()

    max_steps = args.max_steps
    model = args.model
    obs_type = args.observation_type
    provider = args.provider_name
    path_to_vm = args.path_to_vm
    example_id = args.example_id
    
    run_script = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "OSWorld", "run.py")
    osworld_dir = os.path.dirname(run_script)
    
    cmd = [
        "python", run_script,
        "--max_steps", str(max_steps),
        "--model", model,
        "--provider_name", provider,
        "--observation_type", obs_type
    ]
    
    if path_to_vm:
        cmd.extend(["--path_to_vm", path_to_vm])
        
    if example_id:
        cmd.extend(["--example_id", example_id])

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
