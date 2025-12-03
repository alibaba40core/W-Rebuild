"""
W-Rebuild Restore Module
Handles restoration of tool configurations, settings, and environment variables
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class RestoreManager:
    """Manages restore operations for tools and environment variables"""
    
    def __init__(self):
        # Default backup location in OneDrive (same as backup)
        self.onedrive_path = self._get_onedrive_path()
        self.backup_root = Path(self.onedrive_path) / "Backup Folders" / "W-Rebuild"
        
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
    
    def _extract_zip_backup(self, zip_path: str) -> Optional[str]:
        """
        Extract a zip backup to temporary directory
        
        Args:
            zip_path: Path to the zip file
            
        Returns:
            Path to extracted directory or None if failed
        """
        import tempfile
        import zipfile
        
        try:
            # Create temp directory for extraction
            temp_dir = Path(tempfile.gettempdir())
            backup_name = Path(zip_path).stem
            extract_dir = temp_dir / f"{backup_name}_extracted"
            
            # Remove if exists
            if extract_dir.exists():
                import shutil
                shutil.rmtree(extract_dir, ignore_errors=True)
            
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the actual backup folder (may be nested)
            backup_folder = extract_dir / backup_name
            if backup_folder.exists():
                return str(backup_folder)
            else:
                # Sometimes the extraction creates the folder structure directly
                return str(extract_dir)
                
        except Exception as e:
            print(f"Failed to extract zip backup: {e}")
            return None
    
    def _cleanup_extracted_backup(self, extracted_path: str):
        """
        Clean up extracted backup directory
        
        Args:
            extracted_path: Path to the extracted backup directory
        """
        import shutil
        
        try:
            # Get the parent extraction directory
            extract_dir = Path(extracted_path)
            if "_extracted" in extract_dir.name:
                target_dir = extract_dir
            else:
                target_dir = extract_dir.parent
                if "_extracted" in target_dir.name:
                    pass  # Use parent
                else:
                    target_dir = extract_dir  # Use current
            
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)
                
        except Exception as e:
            print(f"Failed to cleanup extracted backup: {e}")
    
    def list_available_backups(self) -> List[Dict]:
        """
        List all available backup folders and zip files in the backup root directory
        
        Returns:
            List of backup metadata dictionaries sorted by timestamp (newest first)
        """
        backups = []
        
        if not self.backup_root.exists():
            return backups
        
        # Scan for backup zip files and folders
        for item in self.backup_root.iterdir():
            # Handle zip files
            if item.is_file() and item.suffix == '.zip' and item.stem.startswith('backup_'):
                try:
                    # Extract to temp to read manifest
                    extracted_path = self._extract_zip_backup(str(item))
                    if extracted_path:
                        manifest_path = Path(extracted_path) / "manifest.json"
                        
                        if manifest_path.exists():
                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                manifest = json.load(f)
                            
                            backup_info = {
                                "backup_name": item.stem,
                                "backup_path": str(item),
                                "is_compressed": True,
                                "extracted_path": extracted_path,
                                "timestamp": manifest.get("timestamp", "unknown"),
                                "datetime": manifest.get("datetime", ""),
                                "tools_count": len(manifest.get("tools", [])),
                                "env_vars_count": len(manifest.get("environment_variables", [])),
                                "manifest": manifest
                            }
                            
                            backups.append(backup_info)
                            
                            # Don't cleanup yet - will cleanup after user closes restore tab
                            
                except Exception as e:
                    print(f"Warning: Could not read zip backup {item.name}: {e}")
            
            # Handle uncompressed folders (legacy)
            elif item.is_dir() and item.name.startswith('backup_'):
                manifest_path = item / "manifest.json"
                
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        
                        # Extract backup metadata
                        backup_info = {
                            "backup_name": item.name,
                            "backup_path": str(item),
                            "is_compressed": False,
                            "timestamp": manifest.get("timestamp", "unknown"),
                            "datetime": manifest.get("datetime", ""),
                            "tools_count": len(manifest.get("tools", [])),
                            "env_vars_count": len(manifest.get("environment_variables", [])),
                            "manifest": manifest
                        }
                        
                        backups.append(backup_info)
                    
                    except Exception as e:
                        print(f"Warning: Could not read backup {item.name}: {e}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return backups
    
    def get_most_recent_backup(self) -> Optional[Dict]:
        """
        Get the most recent backup
        
        Returns:
            Backup metadata dictionary or None if no backups found
        """
        backups = self.list_available_backups()
        return backups[0] if backups else None
    
    def load_backup_details(self, backup_path: str, is_compressed: bool = False, extracted_path: str = None) -> Optional[Dict]:
        """
        Load detailed information from a backup's manifest
        
        Args:
            backup_path: Path to the backup folder or zip file
            is_compressed: Whether the backup is a zip file
            extracted_path: Path to extracted backup (if compressed)
            
        Returns:
            Dictionary with backup details or None if failed
        """
        # Handle compressed backups
        if is_compressed:
            if extracted_path and Path(extracted_path).exists():
                manifest_path = Path(extracted_path) / "manifest.json"
            else:
                # Need to extract first
                extracted_path = self._extract_zip_backup(backup_path)
                if not extracted_path:
                    return None
                manifest_path = Path(extracted_path) / "manifest.json"
        else:
            manifest_path = Path(backup_path) / "manifest.json"
        
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Parse tools information
            tools_list = []
            for tool in manifest.get("tools", []):
                tool_info = {
                    "name": tool.get("name", "Unknown"),
                    "version": tool.get("version", "Unknown"),
                    "original_path": tool.get("path", ""),
                    "backed_up_items": tool.get("backed_up_items", []),
                    "backed_up_count": len(tool.get("backed_up_items", []))
                }
                tools_list.append(tool_info)
            
            # Parse environment variables
            env_vars = manifest.get("environment_variables", [])
            
            return {
                "backup_name": manifest.get("backup_name", ""),
                "timestamp": manifest.get("timestamp", ""),
                "datetime": manifest.get("datetime", ""),
                "backup_location": manifest.get("backup_location", backup_path),
                "tools": tools_list,
                "environment_variables": env_vars,
                "tools_count": len(tools_list),
                "env_vars_count": len(env_vars)
            }
        
        except Exception as e:
            print(f"Error loading backup details: {e}")
            return None
    
    def get_backup_summary(self, backup_path: str) -> str:
        """
        Generate a human-readable summary of a backup
        
        Args:
            backup_path: Path to the backup folder
            
        Returns:
            Formatted summary string
        """
        details = self.load_backup_details(backup_path)
        
        if not details:
            return "Unable to load backup details"
        
        summary_parts = []
        
        summary_parts.append(f"📦 Backup: {details['backup_name']}")
        summary_parts.append(f"🕐 Created: {details['datetime']}")
        summary_parts.append(f"📁 Location: {details['backup_location']}")
        summary_parts.append("")
        
        # Tools summary
        if details['tools']:
            summary_parts.append(f"🔧 Tools ({details['tools_count']}):")
            for tool in details['tools']:
                summary_parts.append(f"  • {tool['name']} v{tool['version']}")
                summary_parts.append(f"    - {tool['backed_up_count']} item(s) backed up")
        else:
            summary_parts.append("🔧 Tools: None")
        
        summary_parts.append("")
        
        # Environment variables summary
        if details['environment_variables']:
            summary_parts.append(f"🌍 Environment Variables ({details['env_vars_count']}):")
            for env_var in details['environment_variables'][:5]:  # Show first 5
                summary_parts.append(f"  • {env_var['name']}")
            if details['env_vars_count'] > 5:
                summary_parts.append(f"  ... and {details['env_vars_count'] - 5} more")
        else:
            summary_parts.append("🌍 Environment Variables: None")
        
        return '\n'.join(summary_parts)
    
    def compare_tools_with_system(self, backup_path: str, detected_tools: List, is_compressed: bool = False, extracted_path: str = None) -> Dict:
        """
        Compare backup tools with currently detected tools
        
        Args:
            backup_path: Path to the backup folder or zip file
            detected_tools: List of DetectedTool objects from system scan (including browsers)
            is_compressed: Whether the backup is a zip file
            extracted_path: Path to extracted backup (if compressed)
            
        Returns:
            Dictionary with missing_tools and installed_tools lists
        """
        details = self.load_backup_details(backup_path, is_compressed, extracted_path)
        if not details or not details['tools']:
            return {
                'missing_tools': [],
                'installed_tools': [],
                'version_mismatch': []
            }
        
        # Create dictionary of detected tool names to tool objects (case-insensitive)
        detected_dict = {tool.name.lower(): tool for tool in detected_tools}
        
        # Debug logging
        print(f"\n=== Comparison Debug ===")
        print(f"Backup tools count: {len(details['tools'])}")
        print(f"Backup tool names: {[t['name'] for t in details['tools']]}")
        print(f"Detected tool names (lowercase): {list(detected_dict.keys())}")
        
        missing_tools = []
        installed_tools = []
        version_mismatch = []
        
        for backup_tool in details['tools']:
            tool_name = backup_tool['name']
            tool_version = backup_tool['version']
            
            # Check if tool exists in detected tools (case-insensitive)
            detected_tool = detected_dict.get(tool_name.lower())
            
            print(f"\nChecking: {tool_name}")
            print(f"  Looking for: '{tool_name.lower()}'")
            print(f"  Found: {detected_tool.name if detected_tool else 'NOT FOUND'}")
            
            if detected_tool:
                # Tool is installed, check version
                if detected_tool.version != tool_version:
                    version_mismatch.append({
                        'name': tool_name,
                        'backup_version': tool_version,
                        'installed_version': detected_tool.version,
                        'backup_data': backup_tool
                    })
                else:
                    installed_tools.append({
                        'name': tool_name,
                        'version': tool_version,
                        'backup_data': backup_tool
                    })
            else:
                # Check if tool has winget or download URL
                winget_id = self.get_winget_package_id(tool_name)
                download_url = self.get_download_url(tool_name, tool_version)
                
                missing_tools.append({
                    'name': tool_name,
                    'version': tool_version,
                    'backup_data': backup_tool,
                    'winget_id': winget_id,
                    'download_url': download_url
                })
        
        return {
            'missing_tools': missing_tools,
            'installed_tools': installed_tools,
            'version_mismatch': version_mismatch
        }
    
    def get_winget_package_id(self, tool_name: str) -> Optional[str]:
        """
        Get winget package ID for a tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Winget package ID or None if not available
        """
        # Common tool to winget ID mappings
        winget_ids = {
            'Visual Studio Code': 'Microsoft.VisualStudioCode',
            'Python': 'Python.Python.3.12',
            'Node.js': 'OpenJS.NodeJS',
            'Git': 'Git.Git',
            'Docker Desktop': 'Docker.DockerDesktop',
            'Postman': 'Postman.Postman',
            'IntelliJ IDEA': 'JetBrains.IntelliJIDEA.Community',
            'PyCharm': 'JetBrains.PyCharm.Community',
            'Android Studio': 'Google.AndroidStudio',
            'JetBrains Toolbox': 'JetBrains.Toolbox',
            'Notepad++': 'Notepad++.Notepad++',
            'DBeaver': 'dbeaver.dbeaver',
            'Azure Data Studio': 'Microsoft.AzureDataStudio',
            'Oracle SQL Developer': 'Oracle.SQLDeveloper',
            'Oracle SQL Developer (Config Only)': 'Oracle.SQLDeveloper',  # Config-only detection
            'MobaXterm': 'Mobatek.MobaXterm',
            # Browsers
            'Google Chrome': 'Google.Chrome',
            'Microsoft Edge': 'Microsoft.Edge',
            'Mozilla Firefox': 'Mozilla.Firefox',
            'Brave Browser': 'Brave.Brave',
            'Opera': 'Opera.Opera',
            'Vivaldi': 'Vivaldi.Vivaldi',
            'VLC': 'VideoLAN.VLC',
            '7-Zip': '7zip.7zip',
            'WinRAR': 'RARLab.WinRAR',
            'Microsoft Teams': 'Microsoft.Teams',
            'Slack': 'SlackTechnologies.Slack',
            'Zoom': 'Zoom.Zoom',
            'Chrome': 'Google.Chrome',
            'Firefox': 'Mozilla.Firefox',
            'Edge': 'Microsoft.Edge',
            'Windows Terminal': 'Microsoft.WindowsTerminal',
            'PowerShell': 'Microsoft.PowerShell',
            'Anaconda': 'Anaconda.Anaconda3',
            'Miniconda': 'Anaconda.Miniconda3',
            'MySQL Workbench': 'Oracle.MySQLWorkbench',
            'PuTTY': 'PuTTY.PuTTY',
            'WinSCP': 'WinSCP.WinSCP',
            'FileZilla': 'TimKosse.FileZilla.Client',
            'Eclipse': 'EclipseAdoptium.Temurin.11.JDK',
            'Maven': 'Apache.Maven',
            'Gradle': 'Gradle.Gradle'
        }
        
        return winget_ids.get(tool_name)
    
    def get_download_url(self, tool_name: str, version: str = None) -> Optional[str]:
        """
        Get direct download URL for a tool
        
        Args:
            tool_name: Name of the tool
            version: Version of the tool (optional, used for versioned URLs)
            
        Returns:
            Download URL or None if not available
        """
        # Tool to download URL mappings with version support
        if tool_name == 'Mockoon' and version:
            return f'https://github.com/mockoon/mockoon/releases/download/v{version}/mockoon.setup.{version}.exe'
        elif tool_name == 'Insomnia':
            return 'https://github.com/Kong/insomnia/releases/latest/download/Insomnia.Core.exe'
        elif tool_name == 'MobaXterm':
            # MobaXterm installer (direct download)
            return 'https://download.mobatek.net/2432023122823706/MobaXterm_Installer_v24.3.exe'
        elif tool_name == 'Oracle SQL Developer':
            # SQL Developer is portable and requires Oracle account login
            # Provide instructions for manual download with the backed-up version
            if version:
                return f'manual:https://www.oracle.com/database/sqldeveloper/technologies/download/|Download Oracle SQL Developer {version} (requires Oracle login, then extract to Program Files)'
            else:
                return 'manual:https://www.oracle.com/database/sqldeveloper/technologies/download/|Download Oracle SQL Developer (requires Oracle login, then extract to Program Files)'
        
        # Fallback to static mappings
        download_urls = {
            'Mockoon': 'https://github.com/mockoon/mockoon/releases/latest/download/mockoon.setup.exe',
            # Add more tools with direct download URLs here
        }
        
        return download_urls.get(tool_name)
    
    def install_tool_via_winget(self, tool_name: str, winget_id: str) -> Dict:
        """
        Install a tool using winget
        
        Args:
            tool_name: Name of the tool
            winget_id: Winget package ID
            
        Returns:
            Dictionary with installation result
        """
        import subprocess
        
        try:
            # First check if already installed
            check_result = subprocess.run(
                ['winget', 'list', '--id', winget_id, '--exact'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # If found in list, it's already installed
            if check_result.returncode == 0 and winget_id in check_result.stdout:
                return {
                    'success': True,
                    'message': f'{tool_name} is already installed',
                    'output': 'Already installed - skipped installation',
                    'tool': tool_name,
                    'already_installed': True
                }
            
            # Run winget install command with --disable-interactivity to minimize prompts
            result = subprocess.run(
                ['winget', 'install', '--id', winget_id, '--silent', '--accept-package-agreements', '--accept-source-agreements', '--disable-interactivity'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            # Combine stdout and stderr for full output
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                # Create desktop and Start Menu shortcuts for all installed tools
                self._create_shortcuts(tool_name, winget_id)
                
                return {
                    'success': True,
                    'message': f'{tool_name} installed successfully',
                    'output': output,
                    'tool': tool_name
                }
            else:
                # Extract meaningful error from output
                error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
                if not error_msg:
                    error_msg = f'Exit code: {result.returncode}'
                
                # Check for common error patterns
                if 'already installed' in output.lower() or 'no applicable update found' in output.lower():
                    return {
                        'success': True,
                        'message': f'{tool_name} is already installed',
                        'output': output,
                        'tool': tool_name,
                        'already_installed': True
                    }
                elif 'no package found' in output.lower() or 'no applicable' in output.lower():
                    error_msg = f'Package not found in winget repository'
                elif 'administrator' in output.lower():
                    error_msg = f'Requires administrator privileges'
                
                return {
                    'success': False,
                    'message': f'Failed to install {tool_name}: {error_msg}',
                    'output': output,
                    'tool': tool_name
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': f'Installation of {tool_name} timed out (exceeded 10 minutes)',
                'tool': tool_name
            }
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'winget not found - please install App Installer from Microsoft Store',
                'tool': tool_name
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error installing {tool_name}: {str(e)}',
                'tool': tool_name
            }
    
    def install_tool_via_url(self, tool_name: str, download_url: str) -> Dict:
        """
        Download and install a tool from a URL
        
        Args:
            tool_name: Name of the tool
            download_url: URL to download the installer or special prefix like 'choco:'
            
        Returns:
            Dictionary with installation result
        """
        import subprocess
        import urllib.request
        import os
        import tempfile
        
        # Check for special cases that need manual download
        if download_url.startswith('manual:'):
            # Parse manual download instruction
            parts = download_url.split('|', 1)
            url = parts[0].replace('manual:', '')
            message = parts[1] if len(parts) > 1 else f'Manual download required from: {url}'
            
            # Open browser to download page
            import webbrowser
            try:
                webbrowser.open(url)
                browser_opened = True
            except:
                browser_opened = False
            
            return {
                'success': False,
                'message': f'{message}' + (' (Browser opened)' if browser_opened else ''),
                'tool': tool_name,
                'manual_url': url,
                'requires_manual': True
            }
        
        # Check for Oracle URLs that require login
        if download_url.startswith('https://www.oracle.com'):
            import webbrowser
            try:
                webbrowser.open(download_url)
                browser_opened = True
            except:
                browser_opened = False
            
            return {
                'success': False,
                'message': f'{tool_name} requires Oracle account login. ' + ('Download page opened in browser.' if browser_opened else f'Visit: {download_url}'),
                'tool': tool_name,
                'manual_url': download_url,
                'requires_manual': True
            }
        
        # Check for special installation methods
        if download_url.startswith('choco:'):
            # Chocolatey installation
            package_name = download_url.split(':', 1)[1]
            return self.install_tool_via_chocolatey(tool_name, package_name)
        
        try:
            # Create temp directory for download
            temp_dir = tempfile.gettempdir()
            
            # Extract filename from URL or use tool name
            filename = download_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]  # Remove query parameters
            if not filename.endswith(('.exe', '.msi', '.zip')):
                filename = f"{tool_name.replace(' ', '_')}_installer.exe"
            
            temp_file = os.path.join(temp_dir, filename)
            
            # Download the installer
            urllib.request.urlretrieve(download_url, temp_file)
            
            # Handle ZIP files (extract and look for installer)
            if filename.endswith('.zip'):
                import zipfile
                extract_dir = os.path.join(temp_dir, f"{tool_name.replace(' ', '_')}_extracted")
                with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # For SQL Developer, it's portable - just extract
                if 'sqldeveloper' in filename.lower():
                    # SQL Developer is portable, extract to Program Files
                    install_dir = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'sqldeveloper')
                    if os.path.exists(install_dir):
                        import shutil
                        shutil.rmtree(install_dir, ignore_errors=True)
                    
                    shutil.copytree(extract_dir, install_dir, dirs_exist_ok=True)
                    
                    return {
                        'success': True,
                        'message': f'{tool_name} extracted to {install_dir}',
                        'tool': tool_name
                    }
                
                # Clean up
                os.remove(temp_file)
                return {
                    'success': False,
                    'message': f'{tool_name} downloaded as ZIP but no installer found',
                    'tool': tool_name
                }
            
            # Determine installation method based on tool and file type
            if filename.endswith('.msi'):
                # MSI installer
                result = subprocess.run(
                    ['msiexec', '/i', temp_file, '/quiet', '/norestart'],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
            else:
                # EXE installer - use tool-specific silent flags
                silent_flags = self._get_silent_install_flags(tool_name)
                result = subprocess.run(
                    [temp_file] + silent_flags,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
            
            # Clean up temp file
            try:
                os.remove(temp_file)
            except:
                pass
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'{tool_name} installed successfully from URL',
                    'tool': tool_name
                }
            else:
                return {
                    'success': True,  # Some installers return non-zero even on success
                    'message': f'{tool_name} installer executed (exit code: {result.returncode})',
                    'tool': tool_name
                }
        
        except urllib.error.URLError as e:
            return {
                'success': False,
                'message': f'Failed to download {tool_name}: {str(e)}',
                'tool': tool_name
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': f'Installation of {tool_name} timed out',
                'tool': tool_name
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error installing {tool_name}: {str(e)}',
                'tool': tool_name
            }
    
    def _get_silent_install_flags(self, tool_name: str) -> List[str]:
        """
        Get silent installation flags for specific tools
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List of command-line flags for silent installation
        """
        # Tool-specific silent installation flags
        silent_flags_map = {
            'Mockoon': ['/VERYSILENT', '/NORESTART'],
            'MobaXterm': ['/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'],
            'Insomnia': ['/S'],
            'Default': ['/S', '/SILENT', '/VERYSILENT']  # Try multiple common flags
        }
        
        return silent_flags_map.get(tool_name, silent_flags_map['Default'])
    
    def install_tool_via_chocolatey(self, tool_name: str, package_name: str) -> Dict:
        """
        Install a tool using Chocolatey package manager
        
        Args:
            tool_name: Name of the tool
            package_name: Chocolatey package name
            
        Returns:
            Dictionary with installation result
        """
        import subprocess
        
        try:
            # Check if chocolatey is installed
            choco_check = subprocess.run(
                ['choco', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if choco_check.returncode != 0:
                return {
                    'success': False,
                    'message': f'Chocolatey not installed. Install from https://chocolatey.org',
                    'tool': tool_name
                }
            
            # Install package via chocolatey
            result = subprocess.run(
                ['choco', 'install', package_name, '-y'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode == 0 or 'successfully installed' in output.lower():
                return {
                    'success': True,
                    'message': f'{tool_name} installed successfully via Chocolatey',
                    'output': output,
                    'tool': tool_name
                }
            else:
                error_msg = result.stderr.strip() if result.stderr.strip() else 'Installation failed'
                return {
                    'success': False,
                    'message': f'Failed to install {tool_name} via Chocolatey: {error_msg}',
                    'output': output,
                    'tool': tool_name
                }
        
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'Chocolatey not found. Install from https://chocolatey.org',
                'tool': tool_name
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': f'Installation of {tool_name} via Chocolatey timed out',
                'tool': tool_name
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error installing {tool_name} via Chocolatey: {str(e)}',
                'tool': tool_name
            }
    
    def _create_shortcuts(self, tool_name: str, winget_id: str) -> bool:
        """
        Create desktop and Start Menu shortcuts for all installed applications
        
        Args:
            tool_name: Name of the tool
            winget_id: Winget package ID
            
        Returns:
            True if shortcuts created successfully
        """
        try:
            import subprocess
            
            # Common installation locations to search
            search_paths = [
                # Winget portable packages
                os.path.expandvars(rf'%LOCALAPPDATA%\Microsoft\WinGet\Packages\{winget_id}_Microsoft.Winget.Source_8wekyb3d8bbwe'),
                # Standard Program Files
                os.path.expandvars(rf'%PROGRAMFILES%\{tool_name}'),
                os.path.expandvars(rf'%PROGRAMFILES(X86)%\{tool_name}'),
                # User local installations
                os.path.expandvars(rf'%LOCALAPPDATA%\Programs\{tool_name}'),
                # Common vendor folders
                os.path.expandvars(rf'%PROGRAMFILES%\{winget_id.split(".")[0]}'),
            ]
            
            # Tool-specific executable preferences (use non-console versions)
            preferred_exes = {
                'Oracle.SQLDeveloper': ['sqldeveloper64W.exe', 'sqldeveloper.exe'],
                'Microsoft.VisualStudioCode': ['Code.exe'],
                'Docker.DockerDesktop': ['Docker Desktop.exe'],
                'Postman.Postman': ['Postman.exe'],
                'Mobatek.MobaXterm': ['MobaXterm.exe'],
                'Git.Git': ['git-bash.exe', 'git-gui.exe'],
            }
            
            exe_path = None
            exe_name = None
            
            # Get preferred executable names for this tool
            preferred = preferred_exes.get(winget_id, [f'{tool_name}.exe'])
            
            # Search for the executable
            for search_path in search_paths:
                if not os.path.exists(search_path):
                    continue
                
                for root, dirs, files in os.walk(search_path):
                    # First check for preferred executables
                    for pref_exe in preferred:
                        if pref_exe in files:
                            exe_path = os.path.join(root, pref_exe)
                            exe_name = pref_exe
                            break
                    
                    if exe_path:
                        break
                    
                    # Fallback: find main .exe (not uninstall/setup/helper)
                    for file in files:
                        if file.lower().endswith('.exe'):
                            lower_file = file.lower()
                            # Skip non-main executables
                            if any(x in lower_file for x in ['uninstall', 'setup', 'install', 'update', 'helper', 'crash', 'elevation']):
                                continue
                            exe_path = os.path.join(root, file)
                            exe_name = file
                            break
                    
                    if exe_path:
                        break
                
                if exe_path:
                    break
            
            if not exe_path or not os.path.exists(exe_path):
                return False
            
            # Create shortcuts using PowerShell
            shortcut_name = tool_name.replace('(Config Only)', '').strip()
            
            # Desktop shortcut
            desktop_cmd = f'''
            $WshShell = New-Object -ComObject WScript.Shell
            $Desktop = [Environment]::GetFolderPath('Desktop')
            $ShortcutPath = Join-Path $Desktop '{shortcut_name}.lnk'
            if (Test-Path $ShortcutPath) {{ Remove-Item $ShortcutPath -Force }}
            $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
            $Shortcut.TargetPath = '{exe_path}'
            $Shortcut.WorkingDirectory = '{os.path.dirname(exe_path)}'
            $Shortcut.Description = '{shortcut_name}'
            $Shortcut.Save()
            Write-Host 'Desktop shortcut created'
            '''
            
            subprocess.run(['powershell', '-Command', desktop_cmd], capture_output=True, timeout=10)
            
            # Start Menu shortcut
            startmenu_cmd = f'''
            $WshShell = New-Object -ComObject WScript.Shell
            $StartMenu = [Environment]::GetFolderPath('StartMenu') + '\\Programs'
            $ShortcutPath = Join-Path $StartMenu '{shortcut_name}.lnk'
            if (Test-Path $ShortcutPath) {{ Remove-Item $ShortcutPath -Force }}
            $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
            $Shortcut.TargetPath = '{exe_path}'
            $Shortcut.WorkingDirectory = '{os.path.dirname(exe_path)}'
            $Shortcut.Description = '{shortcut_name}'
            $Shortcut.Save()
            Write-Host 'Start Menu shortcut created'
            '''
            
            subprocess.run(['powershell', '-Command', startmenu_cmd], capture_output=True, timeout=10)
            
            return True
            
        except Exception as e:
            # Silently fail if shortcut creation doesn't work
            pass
        
        return False
    
    def restore_tool_configs(self, backup_path: str, tool_name: str, tool_data: Dict, is_compressed: bool = False, extracted_path: str = None) -> Dict:
        """
        Restore configurations for a specific tool
        
        Args:
            backup_path: Path to the backup folder or zip file
            tool_name: Name of the tool
            tool_data: Tool data from manifest
            is_compressed: Whether the backup is a zip file
            extracted_path: Path to extracted backup (if compressed)
            
        Returns:
            Dictionary with restoration results
        """
        import shutil
        import winreg
        import subprocess
        
        # Use extracted path for compressed backups
        if is_compressed and extracted_path:
            working_backup_path = extracted_path
        else:
            working_backup_path = backup_path
        
        results = {
            'success': True,
            'restored_items': [],
            'failed_items': [],
            'skipped_items': []
        }
        
        try:
            backed_up_items = tool_data.get('backed_up_items', [])
            
            # Debug logging
            print(f"\n=== Restore Config Debug for {tool_name} ===")
            print(f"Working backup path: {working_backup_path}")
            print(f"Backed up items count: {len(backed_up_items)}")
            print(f"Tool data keys: {tool_data.keys()}")
            
            for item in backed_up_items:
                item_type = item.get('type')
                backup_location = item.get('destination')  # Where file was backed up TO
                restore_target = item.get('source')  # Where to restore it TO (original location)
                
                if not backup_location or not restore_target:
                    continue
                
                # backup_location is the full path where the file/folder was backed up
                # restore_target is where we want to restore it (original AppData location)
                
                if item_type == 'file':
                    # Restore file
                    try:
                        if os.path.exists(backup_location):
                            # Create destination directory if needed
                            dest_dir = os.path.dirname(restore_target)
                            if dest_dir and not os.path.exists(dest_dir):
                                os.makedirs(dest_dir, exist_ok=True)
                            
                            # Copy file from backup to original location
                            shutil.copy2(backup_location, restore_target)
                            results['restored_items'].append(f"File: {os.path.basename(restore_target)}")
                        else:
                            results['skipped_items'].append(f"Backup file not found: {backup_location}")
                    except Exception as e:
                        results['failed_items'].append(f"Failed to restore {os.path.basename(restore_target)}: {str(e)}")
                        results['success'] = False
                
                elif item_type == 'directory' or item_type == 'folder':
                    # Restore directory
                    try:
                        if os.path.exists(backup_location):
                            # Create parent directory if needed
                            parent_dir = os.path.dirname(restore_target)
                            if parent_dir and not os.path.exists(parent_dir):
                                os.makedirs(parent_dir, exist_ok=True)
                            
                            # Remove existing destination if it exists
                            if os.path.exists(restore_target):
                                shutil.rmtree(restore_target, ignore_errors=True)
                            
                            # Copy directory from backup to original location
                            shutil.copytree(backup_location, restore_target, dirs_exist_ok=True)
                            results['restored_items'].append(f"Directory: {os.path.basename(restore_target)}")
                        else:
                            results['skipped_items'].append(f"Backup folder not found: {backup_location}")
                    except Exception as e:
                        results['failed_items'].append(f"Failed to restore {os.path.basename(restore_target)}: {str(e)}")
                        results['success'] = False
                
                elif item_type == 'registry':
                    # Restore registry
                    try:
                        if os.path.exists(backup_location):
                            # Import registry file
                            result = subprocess.run(
                                ['reg', 'import', backup_location],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            if result.returncode == 0:
                                results['restored_items'].append(f"Registry: {os.path.basename(backup_location)}")
                            else:
                                results['failed_items'].append(f"Failed to import registry: {result.stderr}")
                                results['success'] = False
                        else:
                            results['skipped_items'].append(f"Registry file not found: {backup_location}")
                    except Exception as e:
                        results['failed_items'].append(f"Failed to restore registry: {str(e)}")
                        results['success'] = False
            
            # Special handling for extensions/plugins
            extension_results = self._restore_extensions(tool_name, working_backup_path)
            if extension_results:
                results['restored_items'].extend(extension_results['installed'])
                results['failed_items'].extend(extension_results['failed'])
                results['skipped_items'].extend(extension_results['skipped'])
            
            # Special handling for SQL Developer version migration
            if 'sql developer' in tool_name.lower():
                self._migrate_sqldeveloper_versions()
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'restored_items': [],
                'failed_items': [f"Error restoring {tool_name}: {str(e)}"],
                'skipped_items': []
            }
    
    def _restore_extensions(self, tool_name: str, backup_path: str) -> Optional[Dict]:
        """
        Restore extensions/plugins for all supported code editors
        
        Args:
            tool_name: Name of the tool
            backup_path: Path to the backup folder
            
        Returns:
            Dictionary with installation results or None
        """
        # VS Code
        if tool_name.lower() in ['visual studio code', 'vs code', 'vscode']:
            return self._restore_vscode_extensions(backup_path, 'code', 'vscode')
        
        # VS Code Insiders
        if tool_name.lower() in ['vs code insiders', 'vscode insiders']:
            return self._restore_vscode_extensions(backup_path, 'code-insiders', 'vscode-insiders')
        
        # JetBrains IDEs
        jetbrains_mapping = {
            'intellij idea': ('idea', 'intellij'),
            'pycharm': ('pycharm', 'pycharm'),
            'webstorm': ('webstorm', 'webstorm'),
            'rider': ('rider', 'rider'),
            'datagrip': ('datagrip', 'datagrip')
        }
        
        tool_lower = tool_name.lower()
        if tool_lower in jetbrains_mapping:
            ide_cmd, folder_name = jetbrains_mapping[tool_lower]
            return self._restore_jetbrains_plugins(backup_path, tool_name, folder_name)
        
        # Sublime Text
        if tool_name.lower() in ['sublime text', 'sublime']:
            return self._restore_sublime_packages(backup_path)
        
        return None
    
    def _restore_vscode_extensions(self, backup_path: str, command: str, folder_name: str) -> Dict:
        """
        Restore VS Code/Insiders extensions from backup
        
        Args:
            backup_path: Path to the backup folder
            command: Command to use (code or code-insiders)
            folder_name: Folder name in backup (vscode or vscode-insiders)
            
        Returns:
            Dictionary with installation results
        """
        results = {
            'installed': [],
            'failed': [],
            'skipped': []
        }
        
        # Look for extensions.txt in the backup
        extensions_file = os.path.join(backup_path, folder_name, 'extensions.txt')
        
        if not os.path.exists(extensions_file):
            results['skipped'].append(f"No {folder_name}/extensions.txt found in backup")
            return results
        
        try:
            # Read extensions list
            with open(extensions_file, 'r', encoding='utf-8') as f:
                extensions = [line.strip() for line in f if line.strip()]
            
            if not extensions:
                results['skipped'].append("No extensions in backup")
                return results
            
            # Check if command is available
            check = subprocess.run(
                [command, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if check.returncode != 0:
                results['skipped'].append(f"'{command}' command not available in PATH")
                return results
            
            # Install each extension
            for ext in extensions:
                try:
                    result = subprocess.run(
                        [command, '--install-extension', ext, '--force'],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        results['installed'].append(f"Extension: {ext}")
                    else:
                        results['failed'].append(f"Extension {ext}: {result.stderr.strip()}")
                        
                except subprocess.TimeoutExpired:
                    results['failed'].append(f"Extension {ext}: Installation timeout")
                except Exception as e:
                    results['failed'].append(f"Extension {ext}: {str(e)}")
            
        except Exception as e:
            results['failed'].append(f"Error reading extensions list: {str(e)}")
        
        return results
    
    def _restore_jetbrains_plugins(self, backup_path: str, tool_name: str, folder_name: str) -> Dict:
        """
        Restore JetBrains IDE plugins from backup
        
        Note: JetBrains plugins are included in the config folder backup,
        so this just validates the restore happened.
        
        Args:
            backup_path: Path to the backup folder
            tool_name: Name of the IDE
            folder_name: Folder name in backup
            
        Returns:
            Dictionary with results
        """
        results = {
            'installed': [],
            'failed': [],
            'skipped': []
        }
        
        plugins_file = os.path.join(backup_path, folder_name, 'plugins.txt')
        
        if os.path.exists(plugins_file):
            try:
                with open(plugins_file, 'r', encoding='utf-8') as f:
                    plugins = [line.strip() for line in f if line.strip()]
                
                if plugins:
                    results['installed'].append(f"Plugins restored with config ({len(plugins)} plugins)")
                else:
                    results['skipped'].append("No plugins in backup")
            except Exception as e:
                results['failed'].append(f"Error reading plugins list: {str(e)}")
        else:
            results['skipped'].append(f"No plugins.txt found")
        
        return results
    
    def _restore_sublime_packages(self, backup_path: str) -> Dict:
        """
        Restore Sublime Text packages from backup
        
        Note: Sublime packages are included in the AppData backup,
        so this just validates the restore happened.
        
        Args:
            backup_path: Path to the backup folder
            
        Returns:
            Dictionary with results
        """
        results = {
            'installed': [],
            'failed': [],
            'skipped': []
        }
        
        packages_file = os.path.join(backup_path, 'sublime', 'packages.txt')
        
        if os.path.exists(packages_file):
            try:
                with open(packages_file, 'r', encoding='utf-8') as f:
                    packages = [line.strip() for line in f if line.strip()]
                
                if packages:
                    results['installed'].append(f"Packages restored with config ({len(packages)} packages)")
                else:
                    results['skipped'].append("No packages in backup")
            except Exception as e:
                results['failed'].append(f"Error reading packages list: {str(e)}")
        else:
            results['skipped'].append("No packages.txt found")
        
        return results
    
    def _migrate_sqldeveloper_versions(self) -> bool:
        """
        Migrate SQL Developer settings from old version to new version
        
        SQL Developer creates version-specific folders (system24.3.0, system24.3.1, etc.)
        This copies ALL settings including connections, preferences, NLS settings, fonts, line numbers
        from the most recent old version to any newer versions
        
        Returns:
            True if migration successful
        """
        try:
            import shutil
            
            sqldeveloper_path = os.path.expandvars(r'%APPDATA%\SQL Developer')
            if not os.path.exists(sqldeveloper_path):
                return False
            
            # Find all system folders (system24.3.0.xxx, system24.3.1.xxx, etc.)
            system_folders = []
            for item in os.listdir(sqldeveloper_path):
                if item.startswith('system') and os.path.isdir(os.path.join(sqldeveloper_path, item)):
                    system_folders.append(item)
            
            if len(system_folders) < 2:
                return False  # Nothing to migrate
            
            # Sort by version (newest first)
            system_folders.sort(reverse=True)
            
            # Get newest and second newest
            newest = system_folders[0]
            source = system_folders[1]  # Most recent old version
            
            newest_path = os.path.join(sqldeveloper_path, newest)
            source_path = os.path.join(sqldeveloper_path, source)
            
            # Check if newest already has connections (skip if already migrated)
            connections_check = None
            for root, dirs, files in os.walk(newest_path):
                if 'connections.json' in files:
                    connections_check = os.path.join(root, 'connections.json')
                    break
            
            if connections_check and os.path.exists(connections_check):
                # Check if file has content (size > 10 bytes)
                if os.path.getsize(connections_check) > 10:
                    return True  # Already migrated
            
            # Copy ALL important folders and files from old version to new version
            # This includes: connections, preferences, NLS settings, fonts, line numbers, etc.
            
            # 1. Copy all o.sqldeveloper.* folders (contains product-preferences.xml with NLS, fonts, line numbers)
            for item in os.listdir(source_path):
                if item.startswith('o.sqldeveloper.'):
                    source_folder = os.path.join(source_path, item)
                    dest_folder = os.path.join(newest_path, item)
                    
                    if os.path.isdir(source_folder):
                        if os.path.exists(dest_folder):
                            shutil.rmtree(dest_folder, ignore_errors=True)
                        shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
            
            # 2. Copy all o.jdeveloper.* folders (contains connections.json)
            for item in os.listdir(source_path):
                if item.startswith('o.jdeveloper.'):
                    source_folder = os.path.join(source_path, item)
                    dest_folder = os.path.join(newest_path, item)
                    
                    if os.path.isdir(source_folder):
                        if os.path.exists(dest_folder):
                            shutil.rmtree(dest_folder, ignore_errors=True)
                        shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
            
            # 3. Copy all o.ide.* folders (contains IDE preferences)
            for item in os.listdir(source_path):
                if item.startswith('o.ide.'):
                    source_folder = os.path.join(source_path, item)
                    dest_folder = os.path.join(newest_path, item)
                    
                    if os.path.isdir(source_folder):
                        if os.path.exists(dest_folder):
                            shutil.rmtree(dest_folder, ignore_errors=True)
                        shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
            
            # 4. Copy system_cache folder (contains additional preferences)
            system_cache_src = os.path.join(source_path, 'system_cache')
            system_cache_dest = os.path.join(newest_path, 'system_cache')
            if os.path.exists(system_cache_src):
                if os.path.exists(system_cache_dest):
                    shutil.rmtree(system_cache_dest, ignore_errors=True)
                shutil.copytree(system_cache_src, system_cache_dest, dirs_exist_ok=True)
            
            # 5. Copy UserSnippets folder if exists
            snippets_src = os.path.join(source_path, 'UserSnippets')
            snippets_dest = os.path.join(newest_path, 'UserSnippets')
            if os.path.exists(snippets_src):
                if os.path.exists(snippets_dest):
                    shutil.rmtree(snippets_dest, ignore_errors=True)
                shutil.copytree(snippets_src, snippets_dest, dirs_exist_ok=True)
            
            return True
            
        except Exception:
            return False
    
    def restore_backup(self, backup_path: str, selected_tools: List[str], 
                       selected_env_vars: List[str]) -> Dict:
        """
        Restore selected tools and environment variables from a backup
        
        Args:
            backup_path: Path to the backup folder
            selected_tools: List of tool names to restore
            selected_env_vars: List of environment variable names to restore
            
        Returns:
            Dictionary with restoration results
            
        Note: This is a placeholder for Step 3 implementation
        """
        # TODO: Implement in next phase
        # Will handle:
        # - Tool installation (if not present)
        # - Configuration file restoration
        # - Registry key import
        # - Environment variable restoration
        # - Extension/plugin installation
        
        return {
            "success": False,
            "message": "Restore functionality will be implemented in next phase",
            "restored_tools": [],
            "restored_env_vars": [],
            "errors": []
        }
    
    def install_tool_with_winget(self, tool_name: str, winget_id: str) -> Dict:
        """
        Install a tool using winget (simplified wrapper)
        
        Args:
            tool_name: Name of the tool
            winget_id: Winget package ID
            
        Returns:
            Dictionary with installation results
        """
        return self.install_tool_via_winget(tool_name, winget_id)
    
    def restore_environment_variable(self, var_name: str, var_value: str) -> Dict:
        """
        Restore an environment variable
        
        Args:
            var_name: Name of the environment variable
            var_value: Value to set
            
        Returns:
            Dictionary with restoration results
        """
        import subprocess
        
        try:
            # Use setx command to set user environment variable permanently
            # Note: setx has a limitation of 1024 characters
            if len(var_value) > 1024:
                return {
                    'success': False,
                    'error': f'Value too long ({len(var_value)} chars). Maximum is 1024 characters for setx.'
                }
            
            # Escape quotes in the value
            escaped_value = var_value.replace('"', '\\"')
            
            # Use shell=True and shorter timeout
            # Note: setx writes success message to stdout, not stderr
            result = subprocess.run(
                f'setx {var_name} "{escaped_value}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # setx returns 0 on success and writes "SUCCESS: Specified value was saved." to stdout
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'Successfully set {var_name}'
                }
            else:
                # On error, setx writes to stderr
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                return {
                    'success': False,
                    'error': error_msg or 'Unknown error setting environment variable'
                }
        
        except subprocess.TimeoutExpired:
            # Even if it times out, the variable might have been set
            # Try to verify by reading it back
            import os
            try:
                # Check if variable was actually set
                test_result = subprocess.run(
                    f'echo %{var_name}%',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if test_result.returncode == 0 and var_value in test_result.stdout:
                    return {
                        'success': True,
                        'message': f'Successfully set {var_name} (verified after timeout)'
                    }
            except:
                pass
            
            return {
                'success': False,
                'error': 'Command timed out after 10 seconds. Variable may or may not have been set.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
