#!/usr/bin/env python3
"""
Extract commands and command links from all_data.json and add a 'used' field.

This script reads the all_data.json file, extracts all unique commands mentioned
in the levels, filters out non-command words, and creates a new JSON file with
each command having a 'used' field set to False.
"""

import json
import re

# Path to the input and output files
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "levels_data"
INPUT_FILE = DATA_DIR / 'all_data.json'
OUTPUT_FILE = DATA_DIR / 'commands_data.json'

# List of known Linux commands to filter by
KNOWN_COMMANDS = [
    'ssh', 'ls', 'cd', 'cat', 'file', 'du', 'find', 'grep', 'man', 'sort', 'uniq',
    'strings', 'base64', 'tr', 'tar', 'gzip', 'bzip2', 'xxd', 'mkdir', 'cp', 'mv',
    'telnet', 'nc', 'ncat', 'openssl', 's_client', 'nmap', 'netstat', 'ss', 'socat',
    'diff', 'bash', 'screen', 'tmux', 'bg', 'fg', 'jobs', 'chmod', 'cron', 'crontab',
    'vi', 'id', 'pwd', 'sh', 'more', 'less', 'head', 'tail', 'touch', 'echo', 'printf',
    'sed', 'awk', 'cut', 'paste', 'join', 'comm', 'wc', 'git', 'wget', 'curl', 'ping',
    'traceroute', 'ifconfig', 'ip', 'netcat', 'ps', 'top', 'kill', 'pkill', 'killall',
    'sudo', 'su', 'chown', 'chgrp', 'chmod', 'umask', 'df', 'mount', 'umount', 'ln',
    'stat', 'whatis', 'whereis', 'which', 'locate', 'updatedb', 'date', 'cal', 'expr',
    'test', 'true', 'false', 'sleep', 'wait', 'history', 'clear', 'logout', 'exit',
    'shutdown', 'reboot', 'poweroff', 'passwd', 'who', 'w', 'last', 'finger', 'uname',
    'hostname', 'hostnamectl', 'uptime', 'free', 'vmstat', 'iostat', 'mpstat', 'sar',
    'lsof', 'fuser', 'pgrep', 'pstree', 'nice', 'renice', 'time', 'timeout', 'watch',
    'xargs', 'env', 'printenv', 'set', 'export', 'alias', 'unalias', 'source', 'eval',
    'exec', 'shopt', 'ulimit', 'umask', 'getopts', 'read', 'declare', 'typeset', 'local',
    'readonly', 'unset', 'shift', 'trap', 'wait', 'builtin', 'command', 'enable', 'help',
    'let', 'bc', 'dc', 'factor', 'seq', 'yes', 'nl', 'fold', 'fmt', 'pr', 'od', 'hexdump',
    'split', 'csplit', 'expand', 'unexpand', 'tee', 'script', 'wall', 'write', 'mesg',
    'talk', 'ipcalc', 'host', 'dig', 'nslookup', 'whois', 'iptables', 'firewall-cmd',
    'systemctl', 'service', 'journalctl', 'dmesg', 'rsync', 'scp', 'sftp', 'ftp', 'tftp',
    'mail', 'mailx', 'mutt', 'zip', 'unzip', 'ar', 'cpio', 'rpm', 'dpkg', 'apt', 'yum',
    'dnf', 'pacman', 'zypper', 'make', 'gcc', 'g++', 'ld', 'ar', 'nm', 'objdump', 'strip',
    'gdb', 'strace', 'ltrace', 'ldd', 'nm', 'size', 'file', 'readelf', 'c++filt', 'addr2line',
    'gprof', 'gcov', 'valgrind', 'perf', 'as', 'lex', 'yacc', 'bison', 'flex', 'ctags',
    'cscope', 'indent', 'splint', 'lint', 'cppcheck', 'doxygen', 'javac', 'java', 'javadoc',
    'jar', 'python', 'perl', 'ruby', 'php', 'node', 'npm', 'pip', 'gem', 'composer', 'cargo',
    'go', 'rustc', 'cargo', 'dotnet', 'mono', 'mcs', 'sqlite3', 'mysql', 'psql', 'redis-cli',
    'mongo', 'mongod', 'mongos', 'mongoexport', 'mongoimport', 'mongodump', 'mongorestore',
    'pg_dump', 'pg_restore', 'mysqldump', 'mysqlimport', 'vacuum', 'analyze', 'explain',
    'select', 'insert', 'update', 'delete', 'create', 'alter', 'drop', 'truncate', 'grant',
    'revoke', 'commit', 'rollback', 'savepoint', 'begin', 'end', 'vacuum', 'analyze',
    'explain', 'select', 'insert', 'update', 'delete', 'create', 'alter', 'drop', 'truncate',
    'grant', 'revoke', 'commit', 'rollback', 'savepoint', 'begin', 'end'
]

def extract_commands():
    """
    Extract all unique commands from all_data.json and create a new JSON file
    with each command having a 'used' field set to False.
    """
    # Read the input file
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Dictionary to store all unique commands and their links
    commands_dict = {}

    # Process each level
    for level in data['levels_info']:
        # Extract commands from the 'commands' field
        if level['commands']:
            # Split by commas, spaces, and newlines
            cmd_list = re.split(r'[,\s\n]+', level['commands'])
            for cmd in cmd_list:
                cmd = cmd.strip()
                # Only include if it's a known command
                if cmd and cmd.lower() in [c.lower() for c in KNOWN_COMMANDS] and cmd not in commands_dict:
                    commands_dict[cmd] = {
                        'name': cmd,
                        'url': '',
                        'used': False
                    }

        # Extract commands from the 'commands_links' field
        for cmd_link in level['commands_links']:
            cmd_name = cmd_link['text'].strip()
            # Only include if it's a known command
            if cmd_name and cmd_name.lower() in [c.lower() for c in KNOWN_COMMANDS]:
                if cmd_name not in commands_dict:
                    commands_dict[cmd_name] = {
                        'name': cmd_name,
                        'url': cmd_link['url'],
                        'used': False
                    }
                elif cmd_name in commands_dict and not commands_dict[cmd_name]['url']:
                    # Update URL if it wasn't set before
                    commands_dict[cmd_name]['url'] = cmd_link['url']

    # Convert dictionary to list
    commands_list = list(commands_dict.values())

    # Sort by command name
    commands_list.sort(key=lambda x: x['name'])

    # Write to output file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(commands_list, f, indent=2)

    print(f"Extracted {len(commands_list)} unique commands to {OUTPUT_FILE}")
    return commands_list

if __name__ == "__main__":
    extract_commands()
