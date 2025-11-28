"""
W-Rebuild Detector Module
Detects installed development tools and software on Windows system
"""

import json
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Optional


class DetectedTool:
    """Represents a detected software tool"""
    
    def __init__(self, name: str, version: str, path: str, tool_type: str):
        self.name = name
        self.version = version
        self.path = path
        self.tool_type = tool_type
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'path': self.path,
            'type': self.tool_type
        }
    
    def __repr__(self):
        return f"DetectedTool(name='{self.name}', version='{self.version}', type='{self.tool_type}')"


class SystemDetector:
    """Main detector class for scanning installed software"""
    
    def __init__(self, use_modular: bool = True):
        self.project_root = Path(__file__).parent.parent.parent
        self.use_modular = use_modular
        
        # Use modular detection script by default
        if use_modular:
            self.detect_script = self.project_root / "scripts" / "detect_modular.ps1"
        else:
            self.detect_script = self.project_root / "scripts" / "detect.ps1"
        
        self._cached_tools: Optional[List[DetectedTool]] = None
    
    def detect_all_tools(self, force_refresh: bool = False) -> List[DetectedTool]:
        """
        Detect all installed tools on the system
        
        Args:
            force_refresh: If True, bypass cache and run fresh detection
            
        Returns:
            List of DetectedTool objects
        """
        if not force_refresh and self._cached_tools is not None:
            return self._cached_tools
        
        try:
            # Execute PowerShell detection script
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-NoLogo", "-NonInteractive", 
                 "-File", str(self.detect_script)],
                capture_output=True,
                text=True,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Parse JSON output
            output = result.stdout.strip()
            
            # Check for errors
            if result.returncode != 0 or not output:
                error_msg = result.stderr.strip() if result.stderr else "No output from detection script"
                raise Exception(f"Detection failed (code {result.returncode}): {error_msg}")
            
            tools_data = json.loads(output)
            
            # Handle single tool or empty array
            if not tools_data:
                return []
            if isinstance(tools_data, dict):
                tools_data = [tools_data]
            
            # Convert to DetectedTool objects
            detected_tools = []
            for tool_data in tools_data:
                tool = DetectedTool(
                    name=tool_data.get('Name', 'Unknown'),
                    version=tool_data.get('Version', 'Unknown'),
                    path=tool_data.get('Path', ''),
                    tool_type=tool_data.get('Type', 'Unknown')
                )
                detected_tools.append(tool)
            
            # Cache the results
            self._cached_tools = detected_tools
            return detected_tools
            
        except subprocess.TimeoutExpired:
            raise Exception("Detection script timed out after 60 seconds")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse detection output: {e}\nOutput was: {output[:200]}")
        except Exception as e:
            # Re-raise with context
            if "Detection failed" in str(e):
                raise
            raise Exception(f"Error during detection: {e}")
    
    def get_tools_by_type(self, tool_type: str) -> List[DetectedTool]:
        """
        Get all tools of a specific type
        
        Args:
            tool_type: Type of tool (e.g., 'IDE', 'Runtime', 'Tool', 'Editor')
            
        Returns:
            List of DetectedTool objects matching the type
        """
        all_tools = self.detect_all_tools()
        return [tool for tool in all_tools if tool.tool_type.lower() == tool_type.lower()]
    
    def get_tool_by_name(self, name: str) -> Optional[DetectedTool]:
        """
        Get a specific tool by name
        
        Args:
            name: Name of the tool
            
        Returns:
            DetectedTool object or None if not found
        """
        all_tools = self.detect_all_tools()
        for tool in all_tools:
            if tool.name.lower() == name.lower():
                return tool
        return None
    
    def get_tools_summary(self) -> Dict:
        """
        Get a summary of all detected tools
        
        Returns:
            Dictionary with counts by type and total count
        """
        all_tools = self.detect_all_tools()
        
        summary = {
            'total': len(all_tools),
            'by_type': {}
        }
        
        for tool in all_tools:
            tool_type = tool.tool_type
            if tool_type not in summary['by_type']:
                summary['by_type'][tool_type] = 0
            summary['by_type'][tool_type] += 1
        
        return summary
    
    def clear_cache(self):
        """Clear cached detection results"""
        self._cached_tools = None


# Convenience function for quick detection
def detect_installed_tools() -> List[DetectedTool]:
    """
    Quick function to detect all installed tools
    
    Returns:
        List of DetectedTool objects
    """
    detector = SystemDetector()
    return detector.detect_all_tools()
