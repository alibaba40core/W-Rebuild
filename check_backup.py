import json
import os

manifest_path = r'C:\Users\mohamman\OneDrive - AMDOCS\Backup Folders\W-Rebuild\backup_20251211_173313\manifest.json'
manifest = json.load(open(manifest_path))

sql_dev = [t for t in manifest.get('tools', []) if 'Oracle SQL' in t.get('name', '')]

if sql_dev:
    tool = sql_dev[0]
    print(f"Name: {tool.get('name')}")
    print(f"Backed up items: {len(tool.get('backed_up_items', []))}")
    
    if tool.get('backed_up_items'):
        print(f"\nFirst 5 backed up items:")
        for i, item in enumerate(tool['backed_up_items'][:5]):
            print(f"  {i+1}. {item}")
    else:
        print("No backed up items found!")
        
    # Check what's actually in the backup folder
    backup_folder = r'C:\Users\mohamman\OneDrive - AMDOCS\Backup Folders\W-Rebuild\backup_20251211_173313\sqldeveloper'
    if os.path.exists(backup_folder):
        items = os.listdir(backup_folder)
        print(f"\nActual files in backup folder: {len(items)}")
        for item in items[:10]:
            print(f"  - {item}")
else:
    print("SQL Developer not found in manifest")
