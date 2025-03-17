#!/usr/bin/env python3
"""
Formatting utilities for Jenkins Dashboard
This module provides consistent formatting and color functionality across the dashboard.
"""

from colorama import Fore, Back, Style, init
from tabulate import tabulate

# Initialize colorama
init(autoreset=True)

# Color constants
class Colors:
    # Text colors
    HEADER = Fore.BLUE + Style.BRIGHT
    TITLE = Fore.CYAN + Style.BRIGHT
    SUCCESS = Fore.GREEN
    WARNING = Fore.YELLOW
    ERROR = Fore.RED
    CRITICAL = Fore.WHITE + Back.RED
    INFO = Fore.WHITE
    RESET = Style.RESET_ALL
    
    # Status specific colors
    STATUS_ONLINE = Fore.GREEN
    STATUS_OFFLINE = Fore.RED
    STATUS_TEMP_OFFLINE = Fore.YELLOW
    
    STATUS_SUCCESS = Fore.GREEN
    STATUS_UNSTABLE = Fore.YELLOW
    STATUS_FAILED = Fore.RED
    STATUS_DISABLED = Fore.BLUE
    STATUS_BUILDING = Fore.CYAN
    STATUS_NOT_BUILT = Fore.WHITE

    # Disk usage colors
    DISK_LOW = Fore.GREEN
    DISK_MEDIUM = Fore.YELLOW
    DISK_HIGH = Fore.RED
    DISK_CRITICAL = Fore.WHITE + Back.RED

# Common formatting functions
def format_header(text):
    """Format a section header with consistent styling"""
    return f"\n{Colors.HEADER}{'=' * 65}\n{' ' * ((65 - len(text)) // 2)}{text}\n{'=' * 65}{Colors.RESET}\n"

def format_subheader(text):
    """Format a sub-section header with consistent styling"""
    return f"\n{Colors.TITLE}{text}:{Colors.RESET}"

def format_status(status, colorize=True):
    """
    Format a status string with appropriate color
    
    Args:
        status: Status string
        colorize: Whether to apply color
        
    Returns:
        Formatted status string
    """
    if not colorize:
        return status
        
    status_lower = status.lower() if status else ""
    
    if status_lower in ["online", "success"]:
        return f"{Colors.STATUS_ONLINE}{status}{Colors.RESET}"
    elif status_lower in ["offline", "failed", "failure"]:
        return f"{Colors.STATUS_OFFLINE}{status}{Colors.RESET}"
    elif "temporarily" in status_lower or status_lower in ["unstable"]:
        return f"{Colors.STATUS_TEMP_OFFLINE}{status}{Colors.RESET}"
    elif status_lower in ["disabled"]:
        return f"{Colors.STATUS_DISABLED}{status}{Colors.RESET}"
    elif "progress" in status_lower or "building" in status_lower:
        return f"{Colors.STATUS_BUILDING}{status}{Colors.RESET}"
    elif "not built" in status_lower:
        return f"{Colors.STATUS_NOT_BUILT}{status}{Colors.RESET}"
    
    return status

def format_percentage(value, reverse=False):
    """
    Format a percentage with appropriate color
    Higher is better when reverse=False (default)
    Lower is better when reverse=True
    
    Args:
        value: Percentage value (can be string like "85.5%" or number)
        reverse: Whether lower values are better
        
    Returns:
        Colored percentage string
    """
    # Extract numeric value from string if needed
    if isinstance(value, str):
        try:
            numeric_value = float(value.strip('%'))
        except ValueError:
            return value
    else:
        numeric_value = float(value)
    
    # Apply coloring based on thresholds
    if reverse:  # Lower is better (e.g., disk usage)
        if numeric_value < 70:
            color = Colors.DISK_LOW
        elif numeric_value < 85:
            color = Colors.DISK_MEDIUM
        elif numeric_value < 95:
            color = Colors.DISK_HIGH
        else:
            color = Colors.DISK_CRITICAL
    else:  # Higher is better (e.g., success rate)
        if numeric_value > 90:
            color = Colors.STATUS_SUCCESS
        elif numeric_value > 75:
            color = Colors.STATUS_UNSTABLE
        else:
            color = Colors.STATUS_FAILED
            
    # Format the string with the chosen color
    if isinstance(value, str) and '%' in value:
        return f"{color}{value}{Colors.RESET}"
    else:
        return f"{color}{numeric_value:.1f}%{Colors.RESET}"

def format_size(size_bytes, precision=2):
    """
    Format a size in bytes to a human-readable string
    
    Args:
        size_bytes: Size in bytes or "Unknown"
        precision: Number of decimal places
        
    Returns:
        Formatted size string
    """
    try:
        if not isinstance(size_bytes, (int, float)) or size_bytes == "Unknown":
            return "Unknown"
            
        # Convert to appropriate unit
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{(size_bytes / 1024):.{precision}f} KB"
        elif size_bytes < 1024**3:
            return f"{(size_bytes / (1024**2)):.{precision}f} MB"
        elif size_bytes < 1024**4:
            return f"{(size_bytes / (1024**3)):.{precision}f} GB"
        else:
            return f"{(size_bytes / (1024**4)):.{precision}f} TB"
    except Exception:
        return "Unknown"

def format_duration(ms):
    """
    Format a duration in milliseconds to a human-readable string
    
    Args:
        ms: Duration in milliseconds or "Unknown"
        
    Returns:
        Formatted duration string
    """
    try:
        if not isinstance(ms, (int, float)) or ms == "Unknown":
            return "Unknown"
            
        # Convert milliseconds to seconds
        seconds = ms / 1000
        
        # Format duration
        if seconds < 60:
            return f"{seconds:.1f} sec"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} min"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hrs"
    except Exception:
        return "Unknown"

def format_timestamp(timestamp):
    """
    Format a timestamp to a human-readable date
    
    Args:
        timestamp: Milliseconds since epoch or "Unknown"
        
    Returns:
        Formatted date string
    """
    from datetime import datetime
    
    try:
        if not isinstance(timestamp, (int, float)) or timestamp == "Unknown":
            return "Unknown"
            
        # Convert milliseconds to seconds
        timestamp_sec = timestamp / 1000
        dt = datetime.fromtimestamp(timestamp_sec)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Unknown"

def color_table(data, headers, tablefmt='grid', colorize_columns=None):
    """
    Create a colored table with tabulate
    
    Args:
        data: List of rows
        headers: List of column headers
        tablefmt: Table format for tabulate
        colorize_columns: Dict mapping column indices to color functions
        
    Returns:
        Tabulated string with colored cells
    """
    # Make a copy of the data to avoid modifying the original
    colored_data = [row[:] for row in data]
    
    # Apply color functions to specified columns
    if colorize_columns:
        for row in colored_data:
            for col_idx, color_func in colorize_columns.items():
                if col_idx < len(row):
                    row[col_idx] = color_func(row[col_idx])
    
    # Color the headers
    colored_headers = [f"{Colors.HEADER}{h}{Colors.RESET}" for h in headers]
    
    return tabulate(colored_data, headers=colored_headers, tablefmt=tablefmt)

def display_table(title, data, headers, tablefmt='grid', colorize_columns=None):
    """
    Display a titled, colored table
    
    Args:
        title: Table title
        data: List of rows
        headers: List of column headers
        tablefmt: Table format for tabulate
        colorize_columns: Dict mapping column indices to color functions
    """
    print(format_subheader(title))
    print(color_table(data, headers, tablefmt, colorize_columns))
