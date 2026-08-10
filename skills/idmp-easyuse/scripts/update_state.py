import json
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Update steps array in state.json")
    parser.add_argument("--state", required=True, help="Path to state.json")
    parser.add_argument("--add-step", required=True, help="The step string to append")
    
    args = parser.parse_args()
    
    state_file = args.state
    step_to_add = getattr(args, 'add_step')
    
    if not os.path.exists(state_file):
        print(f"Error: {state_file} does not exist.")
        sys.exit(1)
        
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if "steps" not in data:
            data["steps"] = []
            
        if step_to_add not in data["steps"]:
            data["steps"].append(step_to_add)
            
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully added '{step_to_add}' to steps in {state_file}")
    except Exception as e:
        print(f"Error updating state file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
