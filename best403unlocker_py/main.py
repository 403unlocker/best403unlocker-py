import configparser
import platform
import subprocess
from typing import List

import dns.resolver
import requests
from tqdm import tqdm
import shutil
import ipaddress
import os


def test_url_with_custom_dns(url, dns_server, results):
    def resolve_dns_with_custom_server(hostname, dns_server):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server, dns_server]
        if "://" in hostname:
            hostname = hostname.split("://")[1]
        if "/" in hostname:
            hostname = hostname.split("/")[0]
        try:
            answer = resolver.resolve(hostname)
            return answer[0].address
        except Exception as e:
            return None

    tqdm.write(f"Testing with DNS server: {dns_server}")
    ip_address = resolve_dns_with_custom_server(url, dns_server)
    if ip_address:
        try:
            headers = {
                "Host": url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            proxies = {"http": None, "https": None, "ftp": None}
            response = requests.get(
                f"http://{ip_address}", timeout=2, proxies=proxies, headers=headers
            )
            tqdm.write(f"Status Code: {response.status_code}")
            if response.status_code >= 200 and response.status_code < 300:
                results[dns_server] = response.elapsed.total_seconds()
                tqdm.write(
                    f"*****\n\n\t\t OK {round(response.elapsed.total_seconds(),2)}\n\n*****"
                )
            # print(f"Response: {response.text}")
        except requests.RequestException as e:
            pass
            # tqdm.write(f"HTTP request error: {e}")
    else:
        tqdm.write("Failed to resolve DNS.")


def read_config():
    config_path = os.path.expanduser("~/.unlock403/best403unlocker.conf")
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(config_path):
        response = requests.get(
            "https://raw.githubusercontent.com/MSNP1381/best403unlocker-py/refs/heads/main/best403unlocker.conf"
        )
        with open(config_path, "w") as configfile:
            configfile.write(response.text)
    config = configparser.ConfigParser()
    config.read(config_path)
    dns_servers = config.get("dns", "dns").replace('"', "").split()
    return dns_servers


def write_dns_config(dns_servers):
    config_path = os.path.expanduser("~/.unlock403/best403unlocker.conf")
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    config = configparser.ConfigParser()
    config["dns"] = {"dns": " ".join(dns_servers)}
    with open(config_path, "w") as configfile:
        config.write(configfile)


def sort_dict(results: dict):
    values = sorted(results.items(), key=lambda item: item[1])
    return [i[0] for i in values]


def set_dns(dns_servers: List[str]):
    os_type = platform.system().lower()

    def validate_dns_servers(dns_servers):
        valid_dns_servers = []
        for i in dns_servers:
            try:
                ipaddress.ip_address(i)
                valid_dns_servers.append(i)
            except ValueError:
                tqdm.write(f"Invalid DNS server IP: {i}")
                exit()
        return valid_dns_servers

    dns_servers = validate_dns_servers(dns_servers)
    if os_type == "windows":
        set_dns_windows(dns_servers)
    elif os_type == "darwin":
        set_dns_mac(dns_servers)
    elif os_type == "linux":
        set_dns_linux(dns_servers)
    else:
        print(f"Unsupported OS: {os_type}")


def set_dns_windows(dns_servers):
    # ***The requested operation requires elevation (Run as administrator).***
    # interface = "Ethernet"  # Change this to your network interface name if different
    # command = f'netsh interface ip set dns name="{interface}" static {dns_servers[0]}'
    # subprocess.run(command, shell=True)
    # for dns in dns_servers[1:]:
    #     command = f'netsh interface ip add dns name="{interface}" {dns} index=2'
    #     subprocess.run(command, shell=True)
    # Beautiful print with "*" padding and Windows logo in ASCII
    columns, _ = shutil.get_terminal_size()
    padding = "*" * columns

    windows_logo = """\
             _.-;;-._
      '-..-'|   ||   |
      '-..-'|_.-;;-._|
      '-..-'|   ||   |
jgs   '-..-'|_.-''-._|"""
    print(padding)
    print(windows_logo)
    print("Windows detected")
    print("windows doesn't support changing DNS servers, change it manually")
    print()
    if len(dns_servers) >= 1:
        print(padding)
        print(dns_servers[0])
    if len(dns_servers) > 1:
        print(dns_servers[1])
        print()

        print(padding)
    print()


def set_dns_mac(dns_servers):
    network_service = "Wi-Fi"  # Change this to your network service name if different
    dns_string = ",".join(dns_servers)
    command = f"networksetup -setdnsservers {network_service} {dns_string}"
    subprocess.run(command, shell=True)


def set_dns_linux(dns_servers):
    resolv_conf = "/etc/resolv.conf"
    with open(resolv_conf, "w") as file:
        for dns in dns_servers:
            file.write(f"nameserver {dns}\n")


def scan_dns_servers(url, dns_servers):
    results = {i: 1000 for i in dns_servers}
    for dns_server in tqdm(dns_servers, desc="Testing DNS servers"):
        test_url_with_custom_dns(url, dns_server, results)
    return results


def main():
    url = "developers.google.com"
    dns_servers = read_config()
    results = scan_dns_servers(url, dns_servers)
    sorted_dns_servers = sort_dict(results)
    write_dns_config(sorted_dns_servers)
    set_dns(sorted_dns_servers)


if __name__ == "__main__":
    main()
