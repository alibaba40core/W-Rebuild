import subprocess
import json
from pathlib import Path

script_path = Path(__file__).parent / "scripts" / "detect.ps1"
print(f"Script path: {script_path}")
print(f"Exists: {script_path.exists()}\n")

print("Running PowerShell script...")
result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-NoLogo", "-NonInteractive", "-File", str(script_path)],
    capture_output=True,
    text=True,
    timeout=30
)

print(f"Return code: {result.returncode}")
print(f"\nSTDOUT length: {len(result.stdout)}")
print(f"STDERR length: {len(result.stderr)}")

if result.stderr:
    print(f"\nSTDERR:\n{result.stderr}")

if result.stdout:
    print(f"\nSTDOUT (raw):\n{result.stdout}")
    print("\n" + "="*60)
    
    # Try to parse as JSON
    try:
        data = json.loads(result.stdout.strip())
        print(f"\nParsed JSON successfully!")
        print(f"Type: {type(data)}")
        print(f"Content: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError as e:
        print(f"\nFailed to parse JSON: {e}")
        print(f"Attempting to parse line by line...")
        for i, line in enumerate(result.stdout.split('\n'), 1):
            print(f"Line {i}: {repr(line)}")
else:
    print("\nNo output from script!")
