import requests
import time
import hashlib
import random
import ctypes
from bs4 import BeautifulSoup
from urllib.parse import quote

PROTOCOL_VERSION = 216
GAME_VERSION = "5.23"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"

def login_via_growtopia(url, username, password):
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to access {url}, status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    token_input = soup.find('input', {'name': '_token'})
    if not token_input:
        print("_token not found in the page.")
        return

    response = session.post(
        "https://login.growtopiagame.com/player/growid/login/validate",
        data={
            "growId": username,
            "password": password,
            "_token": token_input['value']
        }
    )
    if response.status_code != 200:
        print(f"Login failed, status code: {response.status_code}")
        return
    data = response.json()
    if data.get("status") == "success":
        print("Login successful!")
        return data.get("token")


def fetch_login_urls(login_data):
    url = "https://login.growtopiagame.com/player/login/dashboard?valKey=40db4045f2d8c572efe8c4a060605726"
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print("Fetching login urls...")
    try:
        response = requests.post(url, headers=headers, data=quote(login_data.strip()))
        status = response.status_code
        
        if status != 200:
            print(f"Failed to fetch login urls, status: {status}")
            time.sleep(1)
            return fetch_login_urls(login_data)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        apple_link = soup.find('a', onclick="optionChose('Apple');")
        apple_href = apple_link['href'] if apple_link else None
        google_link = soup.find('a', onclick="optionChose('Google');")
        google_href = google_link['href'] if google_link else None
        growtopia_link = soup.find('a', onclick="optionChose('Grow');")
        growtopia_href = growtopia_link['href'] if growtopia_link else None

        return {
            "apple": apple_href,
            "google": google_href,
            "growtopia": growtopia_href
        }
        
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        time.sleep(1)
        return fetch_login_urls(login_data)

def fetch_server_data(alternate=False):
    domain = "growtopia2" if alternate else "growtopia1"
    url = f"https://www.{domain}.com/growtopia/server_data.php"

    print(f"Fetching server data from {domain}.com")

    headers = {
        "User-Agent": "UbiServices_SDK_2022.Release.9_PC64_ansi_static",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = f"platform=0&protocol={PROTOCOL_VERSION}&version={GAME_VERSION}"
    try:
        response = requests.post(url, headers=headers, data=data)
        status = response.status_code
        
        if status != 200:
            print(f"Failed to fetch server data from {domain}.com, status: {status}")
            time.sleep(1)
            return fetch_server_data(not alternate)
        
        data_text = response.text
        print(f"Server data fetched successfully from {domain}.com")
        return parse_server_data(data_text)
        
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        time.sleep(1)
        return fetch_server_data(not alternate)
    
def parse_server_data(data):
    lines = data.split('\n')
    result = {}
    
    for line in lines:
        idx = line.find('|')
        if idx > -1:
            key = line[:idx].strip()
            value = line[idx + 1:].strip()
            result[key] = value
    
    return result

def generate_klv(protocol: str, rid: str) -> str:
    salts = [
        "e9fc40ec08f9ea6393f59c65e37f750aacddf68490c4f92d0d2523a5bc02ea63",
        "c85df9056ee603b849a93e1ebab5dd5f66e1fb8b2f4a8caef8d13b9f9e013fa4",
        "3ca373dffbf463bb337e0fd768a2f395b8e417475438916506c721551f32038d",
        "73eff5914c61a20a71ada81a6fc7780700fb1c0285659b4899bc172a24c14fc1",
    ]
    
    part1 = hash_sha256(hash_md5(hash_sha256(protocol)))
    part2 = salts[0]
    part3 = hash_sha256(hash_sha256(GAME_VERSION))
    part4 = salts[1]
    part5 = hash_sha256(hash_md5(hash_sha256(rid)))
    part6 = salts[2]
    part7 = hash_sha256(hash_sha256(protocol) + salts[3])
    
    combined = f"{part1}{part2}{part3}{part4}{part5}{part6}{part7}"
    return hash_sha256(combined)

def random_hex(length: int, uppercase: bool = False) -> str:
    hex_chars = '0123456789abcdef'
    hex_string = ''.join(random.choice(hex_chars) for _ in range(length))
    return hex_string.upper() if uppercase else hex_string

def random_mac() -> str:
    mac_parts = [random_hex(2) for _ in range(6)]
    return ':'.join(mac_parts)

def hash_sha256(data: str) -> str:
    data = str(data)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def hash_md5(data: str) -> str:
    data = str(data)
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def read_u32(pointer):
    return ctypes.cast(pointer, ctypes.POINTER(ctypes.c_uint32)).contents.value

def hash_string(data: str) -> int:
    if not data:
        return 0
    
    acc = ctypes.c_uint32(0x55555555)
    for char in data:
        acc.value = (acc.value >> 27) + (acc.value << 5) + ord(char)
    return acc.value
