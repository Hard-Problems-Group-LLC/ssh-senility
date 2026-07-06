#!/usr/bin/env python3
"""
ssh-senility.py
SSH Key Discovery Tool (Full Audit Version)
-------------------------------------------
Iterates through a specified directory (defaults to ~/.ssh), identifies valid 
private keys, and attempts to authenticate against a target host via SSH.

Features:
- Tests ALL valid private keys rather than bailing on the first success.
- Outputs a colorized, UTF-8 formatted summary table of all results.
- Uses native SSH with BatchMode and -T to prevent interactive prompts.
- Configurable random delays to avoid rate-limiting or fail2ban triggers.
- Fully compatible with standard Linux networking, including Tailscale.
"""

import os
import sys
import time
import random
import argparse
import subprocess
from pathlib import Path

# ANSI Color Codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def is_private_key(filepath: Path) -> bool:
    """
    Checks if a file is likely an SSH private key by reading its first line.
    """
    if filepath.is_dir() or filepath.suffix == '.pub':
        return False
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if "PRIVATE KEY-----" in first_line:
                return True
    except (UnicodeDecodeError, PermissionError, IOError):
        return False
        
    return False

def test_ssh_connection(key_path: Path, username: str, hostname: str) -> bool:
    """
    Attempts an SSH connection using the specified key.
    Returns True if authentication succeeds, False otherwise.
    """
    command = [
        "ssh",
        "-T",
        "-i", str(key_path),
        "-o", "BatchMode=yes",
        "-o", "PasswordAuthentication=no",
        "-o", "PubkeyAuthentication=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=5",
        f"{username}@{hostname}",
        "exit"
    ]
    
    try:
        result = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"{Colors.RED}[!] Critical error executing SSH process: {e}{Colors.RESET}", file=sys.stderr)
        return False

def print_summary_table(results: list):
    """
    Renders a UTF-8 box-drawn table summarizing the results with ANSI colors.
    """
    if not results:
        return
        
    # Determine the maximum width needed for the Key File column
    max_key_len = max((len(res['key']) for res in results), default=8)
    max_key_len = max(max_key_len, 10) # Set a minimum width of 10
    
    # Table dimensions
    col1_width = max_key_len + 2
    col2_width = 10
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}[*] Audit Complete. Summary of Results:{Colors.RESET}")
    
    # Top Border
    print(f"{Colors.CYAN}┌{'─' * col1_width}┬{'─' * col2_width}┐{Colors.RESET}")
    
    # Header
    print(f"{Colors.CYAN}│{Colors.RESET} {'Key File'.ljust(max_key_len)} {Colors.CYAN}│{Colors.RESET} {'Status'.ljust(8)} {Colors.CYAN}│{Colors.RESET}")
    
    # Separator
    print(f"{Colors.CYAN}├{'─' * col1_width}┼{'─' * col2_width}┤{Colors.RESET}")
    
    # Rows
    for res in results:
        key_padded = res['key'].ljust(max_key_len)
        if res['success']:
            # Pad the string itself, then apply colors to the word so table alignment doesn't break
            status = f"{Colors.GREEN}Success{Colors.RESET} "
        else:
            status = f"{Colors.RED}Failed{Colors.RESET}  "
            
        print(f"{Colors.CYAN}│{Colors.RESET} {key_padded} {Colors.CYAN}│{Colors.RESET} {status} {Colors.CYAN}│{Colors.RESET}")
        
    # Bottom Border
    print(f"{Colors.CYAN}└{'─' * col1_width}┴{'─' * col2_width}┘{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Test all SSH keys in a directory against a specific user and host."
    )
    parser.add_argument("username", help="The remote username to authenticate as.")
    parser.add_argument("hostname", help="The remote hostname or IP address.")
    parser.add_argument("--ssh-dir", dest="ssh_dir", default="~/.ssh", 
                        help="Path to the directory containing SSH keys (default: ~/.ssh)")
    parser.add_argument("--min-delay", dest="min_delay", type=float, default=1.0,
                        help="Minimum delay between attempts in seconds (default: 1.0)")
    parser.add_argument("--max-delay", dest="max_delay", type=float, default=3.0,
                        help="Maximum delay between attempts in seconds (default: 3.0)")
    
    args = parser.parse_args()
    ssh_path = Path(args.ssh_dir).expanduser().resolve()
    
    print(f"{Colors.BOLD}[*] Target       :{Colors.RESET} {args.username}@{args.hostname}")
    print(f"{Colors.BOLD}[*] Key Directory:{Colors.RESET} {ssh_path}")
    print(f"{Colors.BOLD}[*] Delay Range  :{Colors.RESET} {args.min_delay}s to {args.max_delay}s")
    print(f"{Colors.CYAN}" + "-" * 50 + f"{Colors.RESET}")
    
    if not ssh_path.exists() or not ssh_path.is_dir():
        print(f"{Colors.RED}[!] Error: The directory '{ssh_path}' does not exist.{Colors.RESET}", file=sys.stderr)
        sys.exit(1)

    keys_to_test = []
    try:
        for file in ssh_path.iterdir():
            if is_private_key(file):
                keys_to_test.append(file)
    except Exception as e:
        print(f"{Colors.RED}[!] Error reading directory '{ssh_path}': {e}{Colors.RESET}", file=sys.stderr)
        sys.exit(1)
        
    if not keys_to_test:
        print(f"{Colors.YELLOW}[-] No valid private keys found in {ssh_path}.{Colors.RESET}")
        sys.exit(0)
        
    print(f"[*] Found {len(keys_to_test)} potential private keys to test.\n")
    
    results = []
    
    # Iterate through keys and test them
    for i, key in enumerate(keys_to_test, start=1):
        print(f"[{i}/{len(keys_to_test)}] Testing key: {Colors.BOLD}{key.name}{Colors.RESET}...", end=" ", flush=True)
        
        success = test_ssh_connection(key, args.username, args.hostname)
        results.append({'key': key.name, 'success': success})
        
        if success:
            print(f"{Colors.GREEN}SUCCESS! \u2705{Colors.RESET}")
        else:
            print(f"{Colors.RED}Failed. \u274C{Colors.RESET}")
            
        # Apply the random delay, except after the last key
        if i < len(keys_to_test):
            delay = random.uniform(args.min_delay, args.max_delay)
            print(f"    {Colors.YELLOW}Sleeping for {delay:.2f} seconds...{Colors.RESET}")
            time.sleep(delay)
            
    # Output the final table
    print_summary_table(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Script interrupted by user. Exiting.{Colors.RESET}")
        sys.exit(130)
