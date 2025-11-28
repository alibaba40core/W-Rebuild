import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.detector import SystemDetector

print("Testing W-Rebuild Detection System")
print("=" * 50)

detector = SystemDetector()
print(f"Script path: {detector.detect_script}")
print(f"Script exists: {detector.detect_script.exists()}")
print()

print("Running detection...")
tools = detector.detect_all_tools(force_refresh=True)

print(f"\nFound {len(tools)} tools:")
for tool in tools:
    print(f"  - {tool.name} (v{tool.version}) - {tool.tool_type}")
    print(f"    Path: {tool.path}")
