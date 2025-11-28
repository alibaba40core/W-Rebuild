"""
Test script for backup functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.backup import BackupManager

def test_backup_manager():
    """Test the BackupManager class"""
    
    print("=== W-Rebuild Backup Test ===\n")
    
    # Initialize backup manager
    manager = BackupManager()
    print(f"✓ Backup Manager initialized")
    print(f"  OneDrive Path: {manager.onedrive_path}")
    print(f"  Backup Root: {manager.backup_root}\n")
    
    # Test tool configuration loading
    print(f"✓ Loaded {len(manager.tool_configs)} tool configurations:")
    for tool_name in manager.tool_configs.keys():
        print(f"  • {tool_name}")
    print()
    
    # Create a test backup with sample data
    print("Creating test backup...")
    
    sample_tools = [
        {
            'name': 'Visual Studio Code',
            'version': '1.85.0',
            'path': 'C:\\Program Files\\Microsoft VS Code\\Code.exe'
        }
    ]
    
    sample_env_vars = [
        {
            'name': 'PATH',
            'value': 'C:\\Windows\\System32'
        },
        {
            'name': 'JAVA_HOME',
            'value': 'C:\\Program Files\\Java\\jdk-17'
        }
    ]
    
    try:
        results = manager.create_backup(
            selected_tools=sample_tools,
            selected_env_vars=sample_env_vars,
            backup_name="test_backup"
        )
        
        if results['success']:
            print("\n✓ Backup created successfully!")
            print(f"\n{manager.get_backup_summary(results)}")
        else:
            print("\n✗ Backup failed")
            print(results)
    
    except Exception as e:
        print(f"\n✗ Error during backup: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # List all backups
    print("\n" + "="*50)
    print("Available Backups:")
    backups = manager.list_backups()
    
    if backups:
        for backup in backups:
            print(f"\n• {backup['name']}")
            print(f"  Timestamp: {backup['timestamp']}")
            print(f"  Tools: {len(backup['manifest'].get('tools', []))}")
            print(f"  Env Vars: {len(backup['manifest'].get('environment_variables', []))}")
    else:
        print("  No backups found")

if __name__ == "__main__":
    test_backup_manager()
