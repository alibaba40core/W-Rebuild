"""
W-Rebuild Backup Module
Handles backup of tool configurations, settings, and environment variables
"""

import os
import json
import shutil
import zipfile
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import subprocess


class BackupManager:
    """Manages backup operations for tools and environment variables"""
    
    def __init__(self):
        # Default backup location in OneDrive
        self.onedrive_path = self._get_onedrive_path()
        self.backup_root = Path(self.onedrive_path) / "Backup Folders" / "W-Rebuild"
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # Tool configuration mapping - defines what to backup for each tool
        self.tool_configs = self._load_tool_configs()
    
    def _get_onedrive_path(self) -> str:
        """Get OneDrive folder path"""
        # Try OneDrive - AMDOCS first
        onedrive_amdocs = os.path.expandvars(r"%USERPROFILE%\OneDrive - AMDOCS")
        if os.path.exists(onedrive_amdocs):
            return onedrive_amdocs
        
        # Fall back to regular OneDrive
        onedrive = os.path.expandvars(r"%USERPROFILE%\OneDrive")
        if os.path.exists(onedrive):
            return onedrive
        
        # Fall back to Documents if OneDrive not available
        return os.path.expandvars(r"%USERPROFILE%\Documents")
    
    def _load_tool_configs(self) -> Dict[str, Dict]:
        """Load configuration mapping for each tool"""
        return {
            # Code Editors & IDEs
            "Visual Studio Code": {
                "name": "vscode",
                "paths": [
                    {
                        "source": r"%APPDATA%\Code\User",
                        "type": "folder",
                        "description": "Complete User Configuration (settings, keybindings, snippets)"
                    },
                    {
                        "source": r"%USERPROFILE%\.vscode",
                        "type": "folder",
                        "description": "Extensions folder and global settings"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\Classes\*\shell\VSCode",
                        "type": "registry",
                        "description": "Context Menu Integration"
                    }
                ]
            },
            "VS Code Insiders": {
                "name": "vscode-insiders",
                "paths": [
                    {
                        "source": r"%APPDATA%\Code - Insiders\User",
                        "type": "folder",
                        "description": "User Configuration"
                    }
                ]
            },
            
            # JetBrains IDEs
            "IntelliJ IDEA": {
                "name": "intellij",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.IntelliJIdea*",
                        "type": "folder",
                        "description": "Complete Configuration"
                    },
                    {
                        "source": r"%APPDATA%\JetBrains\IntelliJIdea*",
                        "type": "folder",
                        "description": "AppData Configuration"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\JetBrains\IntelliJ IDEA",
                        "type": "registry",
                        "description": "Registry Settings"
                    }
                ]
            },
            "PyCharm": {
                "name": "pycharm",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.PyCharm*",
                        "type": "folder",
                        "description": "Complete Configuration"
                    },
                    {
                        "source": r"%APPDATA%\JetBrains\PyCharm*",
                        "type": "folder",
                        "description": "AppData Configuration"
                    }
                ]
            },
            "WebStorm": {
                "name": "webstorm",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.WebStorm*",
                        "type": "folder",
                        "description": "Complete Configuration"
                    },
                    {
                        "source": r"%APPDATA%\JetBrains\WebStorm*",
                        "type": "folder",
                        "description": "AppData Configuration"
                    }
                ]
            },
            "Rider": {
                "name": "rider",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.Rider*",
                        "type": "folder",
                        "description": "Complete Configuration"
                    },
                    {
                        "source": r"%APPDATA%\JetBrains\Rider*",
                        "type": "folder",
                        "description": "AppData Configuration"
                    }
                ]
            },
            "DataGrip": {
                "name": "datagrip",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.DataGrip*",
                        "type": "folder",
                        "description": "Complete Configuration"
                    },
                    {
                        "source": r"%APPDATA%\JetBrains\DataGrip*",
                        "type": "folder",
                        "description": "AppData Configuration"
                    }
                ]
            },
            
            # Text Editors
            "Notepad++": {
                "name": "notepadpp",
                "paths": [
                    {
                        "source": r"%APPDATA%\Notepad++",
                        "type": "folder",
                        "description": "Complete Configuration"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\Notepad++",
                        "type": "registry",
                        "description": "Registry Settings"
                    }
                ]
            },
            "Sublime Text": {
                "name": "sublime",
                "paths": [
                    {
                        "source": r"%APPDATA%\Sublime Text",
                        "type": "folder",
                        "description": "Packages and Settings"
                    }
                ]
            },
            
            # Terminal Tools
            "MobaXterm": {
                "name": "mobaxterm",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\Documents\MobaXterm",
                        "type": "folder",
                        "description": "Sessions and Configuration"
                    },
                    {
                        "source": r"%APPDATA%\MobaXterm",
                        "type": "folder",
                        "description": "AppData Configuration"
                    },
                    {
                        "source": r"%USERPROFILE%\MobaXterm.ini",
                        "type": "file",
                        "description": "Main Configuration File"
                    }
                ]
            },
            "PuTTY": {
                "name": "putty",
                "paths": [
                    {
                        "source": r"HKEY_CURRENT_USER\Software\SimonTatham\PuTTY",
                        "type": "registry",
                        "description": "PuTTY Registry Settings"
                    }
                ]
            },
            "Windows Terminal": {
                "name": "terminal",
                "paths": [
                    {
                        "source": r"%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_*\LocalState\settings.json",
                        "type": "file",
                        "description": "Settings"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Console",
                        "type": "registry",
                        "description": "Console Settings"
                    }
                ]
            },
            "Cmder": {
                "name": "cmder",
                "paths": [
                    {
                        "source": r"%APPDATA%\cmder",
                        "type": "folder",
                        "description": "Configuration"
                    }
                ]
            },
            
            # Version Control
            "Git": {
                "name": "git",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.gitconfig",
                        "type": "file",
                        "description": "Git Config"
                    },
                    {
                        "source": r"%USERPROFILE%\.gitignore_global",
                        "type": "file",
                        "description": "Global Gitignore"
                    },
                    {
                        "source": r"%USERPROFILE%\.git-credentials",
                        "type": "file",
                        "description": "Git Credentials"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\Microsoft\Git",
                        "type": "registry",
                        "description": "Git Registry Settings"
                    }
                ]
            },
            
            # Database Tools
            "Oracle SQL Developer": {
                "name": "sqldeveloper",
                "paths": [
                    {
                        "source": r"%APPDATA%\SQL Developer",
                        "type": "folder",
                        "description": "Configuration and Connections"
                    }
                ]
            },
            "DBeaver": {
                "name": "dbeaver",
                "paths": [
                    {
                        "source": r"%APPDATA%\DBeaverData",
                        "type": "folder",
                        "description": "Workspace and Connections"
                    }
                ]
            },
            "MySQL Workbench": {
                "name": "mysql-workbench",
                "paths": [
                    {
                        "source": r"%APPDATA%\MySQL\Workbench",
                        "type": "folder",
                        "description": "Connections and Models"
                    }
                ]
            },
            "MongoDB Compass": {
                "name": "mongodb-compass",
                "paths": [
                    {
                        "source": r"%APPDATA%\MongoDB Compass",
                        "type": "folder",
                        "description": "Connections and Favorites"
                    }
                ]
            },
            
            # API Tools
            "Postman": {
                "name": "postman",
                "paths": [
                    {
                        "source": r"%APPDATA%\Postman",
                        "type": "folder",
                        "description": "Collections and Settings"
                    }
                ]
            },
            "Insomnia": {
                "name": "insomnia",
                "paths": [
                    {
                        "source": r"%APPDATA%\Insomnia",
                        "type": "folder",
                        "description": "Workspaces and Requests"
                    }
                ]
            },
            "Mockoon": {
                "name": "mockoon",
                "paths": [
                    {
                        "source": r"%APPDATA%\mockoon",
                        "type": "folder",
                        "description": "Mock APIs"
                    }
                ]
            },
            
            # Build Tools & Languages
            "Maven": {
                "name": "maven",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.m2\settings.xml",
                        "type": "file",
                        "description": "Maven Settings"
                    },
                    {
                        "source": r"%USERPROFILE%\.m2\repository",
                        "type": "folder",
                        "description": "Local Repository (optional, can be large)"
                    }
                ]
            },
            "Gradle": {
                "name": "gradle",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.gradle\gradle.properties",
                        "type": "file",
                        "description": "Gradle Properties"
                    }
                ]
            },
            "Python": {
                "name": "python",
                "paths": [
                    {
                        "source": r"%APPDATA%\pip\pip.ini",
                        "type": "file",
                        "description": "Pip Configuration"
                    }
                ]
            },
            "Node.js": {
                "name": "nodejs",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.npmrc",
                        "type": "file",
                        "description": "NPM Configuration"
                    }
                ]
            },
            
            # Docker & Containers
            "Docker": {
                "name": "docker",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.docker\config.json",
                        "type": "file",
                        "description": "Docker Configuration"
                    }
                ]
            },
            
            # Communication Tools
            "Slack": {
                "name": "slack",
                "paths": [
                    {
                        "source": r"%APPDATA%\Slack",
                        "type": "folder",
                        "description": "Workspace Configuration"
                    }
                ]
            },
            "Microsoft Teams": {
                "name": "teams",
                "paths": [
                    {
                        "source": r"%APPDATA%\Microsoft\Teams",
                        "type": "folder",
                        "description": "Teams Settings"
                    }
                ]
            },
            
            # SSH & Security
            "SSH": {
                "name": "ssh",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\.ssh\config",
                        "type": "file",
                        "description": "SSH Configuration"
                    },
                    {
                        "source": r"%USERPROFILE%\.ssh\known_hosts",
                        "type": "file",
                        "description": "Known Hosts"
                    },
                    {
                        "source": r"%USERPROFILE%\.ssh\*.pub",
                        "type": "file",
                        "description": "Public Keys"
                    }
                ]
            },
            
            # Shell Profiles
            "PowerShell": {
                "name": "powershell",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\Documents\PowerShell",
                        "type": "folder",
                        "description": "PowerShell Profile and Modules"
                    }
                ]
            },
            "Windows PowerShell": {
                "name": "windows-powershell",
                "paths": [
                    {
                        "source": r"%USERPROFILE%\Documents\WindowsPowerShell",
                        "type": "folder",
                        "description": "Windows PowerShell Profile"
                    }
                ]
            },
            
            # Browsers
            "Google Chrome": {
                "name": "chrome",
                "paths": [
                    {
                        "source": r"%LOCALAPPDATA%\Google\Chrome\User Data\Default",
                        "type": "folder",
                        "description": "Default Profile (Bookmarks, History, Extensions, Settings)"
                    },
                    {
                        "source": r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State",
                        "type": "file",
                        "description": "Chrome Local State"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\Google\Chrome",
                        "type": "registry",
                        "description": "Chrome Registry Settings"
                    }
                ]
            },
            "Microsoft Edge": {
                "name": "edge",
                "paths": [
                    {
                        "source": r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default",
                        "type": "folder",
                        "description": "Default Profile (Bookmarks, History, Extensions, Settings)"
                    },
                    {
                        "source": r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Local State",
                        "type": "file",
                        "description": "Edge Local State"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\Microsoft\Edge",
                        "type": "registry",
                        "description": "Edge Registry Settings"
                    }
                ]
            },
            "Mozilla Firefox": {
                "name": "firefox",
                "paths": [
                    {
                        "source": r"%APPDATA%\Mozilla\Firefox\Profiles",
                        "type": "folder",
                        "description": "All Firefox Profiles (Bookmarks, Extensions, Settings)"
                    },
                    {
                        "source": r"%APPDATA%\Mozilla\Firefox\profiles.ini",
                        "type": "file",
                        "description": "Firefox Profiles Configuration"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\Mozilla\Firefox",
                        "type": "registry",
                        "description": "Firefox Registry Settings"
                    }
                ]
            },
            "Brave Browser": {
                "name": "brave",
                "paths": [
                    {
                        "source": r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default",
                        "type": "folder",
                        "description": "Default Profile (Bookmarks, History, Extensions, Settings)"
                    },
                    {
                        "source": r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Local State",
                        "type": "file",
                        "description": "Brave Local State"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\BraveSoftware\Brave-Browser",
                        "type": "registry",
                        "description": "Brave Registry Settings"
                    }
                ]
            },
            "Opera": {
                "name": "opera",
                "paths": [
                    {
                        "source": r"%APPDATA%\Opera Software\Opera Stable",
                        "type": "folder",
                        "description": "Opera Profile (Bookmarks, Extensions, Settings)"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\Opera Software",
                        "type": "registry",
                        "description": "Opera Registry Settings"
                    }
                ]
            },
            "Vivaldi": {
                "name": "vivaldi",
                "paths": [
                    {
                        "source": r"%LOCALAPPDATA%\Vivaldi\User Data\Default",
                        "type": "folder",
                        "description": "Default Profile (Bookmarks, History, Extensions, Settings)"
                    },
                    {
                        "source": r"%LOCALAPPDATA%\Vivaldi\User Data\Local State",
                        "type": "file",
                        "description": "Vivaldi Local State"
                    },
                    {
                        "source": r"HKEY_CURRENT_USER\Software\Vivaldi",
                        "type": "registry",
                        "description": "Vivaldi Registry Settings"
                    }
                ]
            }
        }
    
    def create_backup(self, selected_tools: List[Dict], selected_env_vars: List[Dict], 
                     backup_name: Optional[str] = None) -> Dict:
        """
        Create a backup of selected tools and environment variables
        Creates backup in temp directory, zips it to OneDrive, then deletes temp folder
        
        Args:
            selected_tools: List of dicts with 'name', 'version', 'path'
            selected_env_vars: List of dicts with 'name', 'value'
            backup_name: Optional custom backup name
        
        Returns:
            Dict with backup results and manifest path
        """
        import tempfile
        
        # Create timestamped backup folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not backup_name:
            backup_name = f"backup_{timestamp}"
        
        # Create backup in temp directory first
        temp_dir = Path(tempfile.gettempdir())
        backup_dir = temp_dir / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize manifest
        manifest = {
            "backup_name": backup_name,
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "tools": [],
            "environment_variables": selected_env_vars,
            "backup_location": str(backup_dir)
        }
        
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }
        
        # Backup each selected tool
        for tool in selected_tools:
            tool_name = tool['name']
            tool_version = tool['version']
            
            # Get backup configuration for this tool
            tool_config = self._get_tool_config(tool_name)
            
            if not tool_config:
                results["skipped"].append({
                    "tool": tool_name,
                    "reason": "No backup configuration defined"
                })
                continue
            
            # Create tool-specific folder
            tool_folder = backup_dir / tool_config['name']
            tool_folder.mkdir(exist_ok=True)
            
            tool_manifest = {
                "name": tool_name,
                "version": tool_version,
                "path": tool['path'],
                "backed_up_items": []
            }
            
            # Backup each configured path
            for path_config in tool_config['paths']:
                try:
                    source_path = os.path.expandvars(path_config['source'])
                    
                    if path_config['type'] == 'extensions':
                        # Special handling for extensions
                        backed_up = self._backup_extensions(tool_name, source_path, tool_folder, path_config)
                    else:
                        backed_up = self._backup_path(source_path, tool_folder, path_config)
                    
                    if backed_up:
                        tool_manifest["backed_up_items"].append(backed_up)
                
                except Exception as e:
                    print(f"Error backing up {path_config['source']}: {str(e)}")
                    results["failed"].append({
                        "tool": tool_name,
                        "path": path_config['source'],
                        "error": str(e)
                    })
            
            # Always add tool to manifest if it was in the selected list, even if backup had issues
            if tool_manifest["backed_up_items"]:
                results["success"].append(tool_name)
            else:
                # Tool was selected but no items were backed up
                results["skipped"].append({
                    "tool": tool_name,
                    "reason": "No items could be backed up (paths may not exist)"
                })
            
            # Add to manifest regardless to preserve tool information
            manifest["tools"].append(tool_manifest)
        
        # Save environment variables to JSON
        if selected_env_vars:
            env_file = backup_dir / "environment_variables.json"
            with open(env_file, 'w', encoding='utf-8') as f:
                json.dump(selected_env_vars, f, indent=2)
        
        # Save manifest
        manifest_path = backup_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        # Move backup from temp to final location (skip ZIP for now for speed)
        final_backup_dir = self.backup_root / backup_name
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # Remove existing backup if present
        if final_backup_dir.exists():
            shutil.rmtree(final_backup_dir, ignore_errors=True)
        
        # Move from temp to final location
        shutil.move(str(backup_dir), str(final_backup_dir))
        
        return {
            "success": True,
            "backup_dir": str(final_backup_dir),
            "manifest_path": str(final_backup_dir / "manifest.json"),
            "results": results,
            "timestamp": timestamp,
            "is_compressed": False
        }
    
    def _get_tool_config(self, tool_name: str) -> Optional[Dict]:
        """Get backup configuration for a tool by name"""
        # Check exact match first
        if tool_name in self.tool_configs:
            return self.tool_configs[tool_name]
        
        # Check for partial matches (e.g., "VS Code" matches "Visual Studio Code")
        for key, config in self.tool_configs.items():
            if tool_name.lower() in key.lower() or key.lower() in tool_name.lower():
                return config
        
        return None
    
    def _safe_copy_tree(self, src: Path, dst: Path) -> tuple[int, int, list]:
        """
        Safely copy a directory tree, skipping locked files instead of failing.
        Also skips large cache/temp folders that aren't needed for backup.
        
        Returns:
            tuple: (files_copied, files_skipped, skipped_files_list)
        """
        files_copied = 0
        files_skipped = 0
        skipped_files = []
        
        # Folders to skip (cache, temp files, large unnecessary data)
        skip_folders = {
            'Cache', 'Code Cache', 'GPUCache', 'Service Worker',
            'DawnCache', 'ShaderCache', 'blob_storage', 'Session Storage',
            'IndexedDB', 'File System', 'WebStorage', 'Local Storage',
            'BrowserMetrics', 'optimization_guide_hints',
            'optimization_guide_model_and_features_store',
            'Storage', 'VideoDecodeStats', 'BudgetDatabase'
        }
        
        # Create destination directory
        dst.mkdir(parents=True, exist_ok=True)
        
        for item in src.rglob('*'):
            try:
                # Skip cache and temporary folders
                if any(skip_folder in item.parts for skip_folder in skip_folders):
                    continue
                
                # Calculate relative path
                rel_path = item.relative_to(src)
                dest_item = dst / rel_path
                
                if item.is_dir():
                    # Create directory
                    dest_item.mkdir(parents=True, exist_ok=True)
                elif item.is_file():
                    # Copy file
                    dest_item.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(item), str(dest_item))
                    files_copied += 1
            except (PermissionError, OSError) as e:
                # File is locked or inaccessible - skip it
                files_skipped += 1
                skipped_files.append(str(item.relative_to(src)))
            except Exception as e:
                # Other errors - skip and log
                files_skipped += 1
                skipped_files.append(str(item.relative_to(src)))
        
        return files_copied, files_skipped, skipped_files
    
    def _backup_path(self, source_path: str, dest_folder: Path, path_config: Dict) -> Optional[Dict]:
        """Backup a file, folder, or registry key"""
        # Handle registry keys
        if path_config.get('type') == 'registry':
            return self._backup_registry_key(source_path, dest_folder, path_config)
        
        source = Path(source_path)
        
        # Handle wildcards in path
        if '*' in source_path:
            parent = Path(source_path.rsplit('*', 1)[0].rstrip('\\'))
            if parent.exists():
                matches = list(parent.parent.glob(parent.name + '*'))
                if matches:
                    source = matches[0]  # Use first match
                else:
                    return None
            else:
                return None
        
        if not source.exists():
            return None
        
        dest_name = source.name
        dest_path = dest_folder / dest_name
        
        try:
            if source.is_file():
                # Try to copy file, skip if locked
                try:
                    shutil.copy2(source, dest_path)
                except (PermissionError, OSError) as e:
                    # File is locked, skip it
                    print(f"Warning: Skipping locked file {source.name}")
                    return None
            elif source.is_dir():
                # Use safe copy for directories to handle locked files
                if dest_path.exists():
                    shutil.rmtree(dest_path, ignore_errors=True)
                
                files_copied, files_skipped, skipped_files = self._safe_copy_tree(source, dest_path)
                
                # Log skipped files for browser data
                if files_skipped > 0:
                    print(f"Info: Backed up {files_copied} files, skipped {files_skipped} locked files from {source.name}")
                
                # Consider backup successful if at least some files were copied
                if files_copied == 0 and files_skipped > 0:
                    print(f"Warning: All files in {source.name} were locked or inaccessible")
                    return None
            
            return {
                "description": path_config['description'],
                "source": str(source),
                "destination": str(dest_path),
                "type": path_config['type'],
                "size_bytes": self._get_size(dest_path)
            }
        
        except Exception as e:
            # Log but don't fail the entire backup
            print(f"Warning: Could not backup {source}: {str(e)}")
            return None
    
    def _backup_registry_key(self, registry_path: str, dest_folder: Path, path_config: Dict) -> Optional[Dict]:
        """Backup a Windows registry key to .reg file"""
        try:
            # Extract registry key path
            reg_key = registry_path.strip()
            
            # Create sanitized filename from registry path
            filename = reg_key.replace('HKEY_CURRENT_USER\\', 'HKCU_')
            filename = filename.replace('HKEY_LOCAL_MACHINE\\', 'HKLM_')
            filename = filename.replace('\\', '_') + '.reg'
            
            dest_file = dest_folder / filename
            
            # Use reg.exe to export the key
            result = subprocess.run(
                ['reg', 'export', reg_key, str(dest_file), '/y'],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0 and dest_file.exists():
                return {
                    "description": path_config['description'],
                    "source": registry_path,
                    "destination": str(dest_file),
                    "type": "registry",
                    "size_bytes": dest_file.stat().st_size
                }
            else:
                # Registry key might not exist, return None instead of failing
                return None
        
        except Exception as e:
            # Don't fail backup if registry key doesn't exist or can't be exported
            print(f"Warning: Could not backup registry key {registry_path}: {e}")
            return None
    
    def _backup_extensions(self, tool_name: str, extensions_path: str, dest_folder: Path, 
                          path_config: Dict) -> Optional[Dict]:
        """Backup extensions list (VS Code, etc.)"""
        if "code" in tool_name.lower() or "vscode" in tool_name.lower():
            return self._backup_vscode_extensions(dest_folder)
        
        return None
    
    def _backup_vscode_extensions(self, dest_folder: Path, command: str = 'code') -> Optional[Dict]:
        """Backup VS Code/Insiders extensions list"""
        try:
            # Get list of installed extensions
            result = subprocess.run(
                [command, '--list-extensions'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                extensions = result.stdout.strip().split('\n')
                extensions = [ext for ext in extensions if ext.strip()]  # Filter empty lines
                
                if extensions:
                    extensions_file = dest_folder / "extensions.txt"
                    
                    with open(extensions_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(extensions))
                    
                    return {
                        "description": "Extensions List",
                        "source": f"{command} CLI",
                        "destination": str(extensions_file),
                        "type": "extensions",
                        "count": len(extensions)
                    }
        
        except Exception:
            pass
        
        return None
    
    def _backup_jetbrains_plugins(self, dest_folder: Path, tool_name: str, ide_name: str) -> Optional[Dict]:
        """Backup JetBrains IDE plugins list"""
        try:
            # Look for plugins folder in user profile and AppData
            plugin_paths = [
                Path(os.path.expandvars(r"%USERPROFILE%")) / f".{tool_name.replace(' ', '')}*" / "config" / "plugins",
                Path(os.path.expandvars(r"%APPDATA%")) / "JetBrains" / f"{tool_name.replace(' ', '')}*" / "plugins"
            ]
            
            plugins_list = []
            for pattern_path in plugin_paths:
                # Handle wildcards in path
                parent = pattern_path.parent
                if '*' in str(pattern_path):
                    import glob
                    matches = glob.glob(str(pattern_path))
                    for match in matches:
                        plugin_dir = Path(match)
                        if plugin_dir.exists():
                            # List plugin folders
                            plugins = [p.name for p in plugin_dir.iterdir() if p.is_dir()]
                            plugins_list.extend(plugins)
            
            if plugins_list:
                plugins_file = dest_folder / "plugins.txt"
                with open(plugins_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(sorted(set(plugins_list))))
                
                return {
                    "description": "Plugins List",
                    "source": "Plugin directories",
                    "destination": str(plugins_file),
                    "type": "plugins",
                    "count": len(set(plugins_list))
                }
        
        except Exception:
            pass
        
        return None
    
    def _backup_sublime_packages(self, dest_folder: Path) -> Optional[Dict]:
        """Backup Sublime Text packages list"""
        try:
            # Sublime Text stores packages in AppData
            packages_path = Path(os.path.expandvars(r"%APPDATA%\Sublime Text\Installed Packages"))
            
            if packages_path.exists():
                # List .sublime-package files
                packages = [p.stem for p in packages_path.glob("*.sublime-package")]
                
                if packages:
                    packages_file = dest_folder / "packages.txt"
                    with open(packages_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(sorted(packages)))
                    
                    return {
                        "description": "Packages List",
                        "source": str(packages_path),
                        "destination": str(packages_file),
                        "type": "packages",
                        "count": len(packages)
                    }
        
        except Exception:
            pass
        
        return None
    
    def _get_size(self, path: Path) -> int:
        """Get size of file or folder in bytes"""
        if path.is_file():
            return path.stat().st_size
        
        total = 0
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        
        return total
    
    def _create_zip_archive(self, backup_dir: Path) -> Optional[str]:
        """
        Create a zip archive of the backup directory
        
        Args:
            backup_dir: Path to the backup directory to compress
            
        Returns:
            Path to the created zip file, or None if failed
        """
        try:
            zip_path = f"{backup_dir}.zip"
            
            # Minimum timestamp for ZIP format (1980-01-01)
            min_zip_time = time.mktime((1980, 1, 1, 0, 0, 0, 0, 0, 0))
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                # Walk through all files in the backup directory
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Create relative path for the archive
                        arcname = os.path.relpath(file_path, backup_dir.parent)
                        
                        # Get file stats and check timestamp
                        file_stat = os.stat(file_path)
                        
                        # If file timestamp is before 1980, use current time
                        if file_stat.st_mtime < min_zip_time:
                            # Create ZipInfo manually with valid timestamp
                            zi = zipfile.ZipInfo(filename=arcname)
                            zi.date_time = time.localtime(time.time())[:6]
                            zi.compress_type = zipfile.ZIP_DEFLATED
                            zi.external_attr = file_stat.st_mode << 16
                            
                            with open(file_path, 'rb') as f:
                                zipf.writestr(zi, f.read())
                        else:
                            # Normal write for files with valid timestamps
                            zipf.write(file_path, arcname)
            
            return zip_path
        
        except Exception as e:
            print(f"Failed to create zip archive: {e}")
            return None
    
    def list_backups(self) -> List[Dict]:
        """List all available backups (both folders and zip files)"""
        backups = []
        
        if not self.backup_root.exists():
            return backups
        
        # Check for both directories and zip files
        for item in self.backup_root.iterdir():
            # Check zip files
            if item.is_file() and item.suffix == '.zip':
                try:
                    backups.append({
                        "name": item.stem,
                        "path": str(item),
                        "is_compressed": True,
                        "size": item.stat().st_size,
                        "timestamp": item.stem.split('_', 1)[-1] if '_' in item.stem else "unknown"
                    })
                except Exception:
                    pass
            
            # Check directories (legacy uncompressed backups)
            elif item.is_dir():
                manifest_path = item / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        
                        backups.append({
                            "name": item.name,
                            "path": str(item),
                            "manifest": manifest,
                            "is_compressed": False,
                            "timestamp": manifest.get("timestamp", "unknown")
                        })
                    except Exception:
                        pass
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def get_backup_summary(self, backup_results: Dict) -> str:
        """Generate a human-readable summary of backup results"""
        results = backup_results['results']
        
        summary_parts = []
        
        if results['success']:
            summary_parts.append(f"✓ Successfully backed up {len(results['success'])} tool(s):")
            for tool in results['success']:
                summary_parts.append(f"  • {tool}")
        
        if results['failed']:
            summary_parts.append(f"\n✗ Failed to backup {len(results['failed'])} item(s):")
            for item in results['failed']:
                summary_parts.append(f"  • {item['tool']}: {item['error']}")
        
        if results['skipped']:
            summary_parts.append(f"\n⊘ Skipped {len(results['skipped'])} tool(s):")
            for item in results['skipped']:
                summary_parts.append(f"  • {item['tool']}: {item['reason']}")
        
        summary_parts.append(f"\n📁 Backup location: {backup_results['backup_dir']}")
        
        return '\n'.join(summary_parts)
