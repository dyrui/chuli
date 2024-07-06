import os
import re
import requests
from github import Github
from github.InputFileContent import InputFileContent

# 配置
url = "http://example.com"  # 要获取内容的URL
github_token = "your_actual_token_here"  # 你的GitHub访问令牌
gist_description = "Clash node content"  # Gist描述
gist_filename = "clash_nodes.txt"  # Gist文件名
gist_id_file = "/root/gist_id.txt"  # 用于存储Gist ID的文件路径

# 设置自定义头信息，包括 User-Agent
headers = {
    "User-Agent": "clash verge"
}

# 获取网址内容
response = requests.get(url, headers=headers)
if response.status_code == 200:
    content = response.text
else:
    raise Exception(f"Failed to retrieve content from {url}, status code {response.status_code}")

# 处理 "proxies:" 段落内容
lines = content.splitlines()
proxies_start = None
proxies_end = None
for i, line in enumerate(lines):
    if line.strip() == "proxies:":
        proxies_start = i
    elif proxies_start is not None and line.strip() and not line.startswith(" "):
        proxies_end = i
        break

if proxies_start is not None:
    if proxies_end is None:
        proxies_end = len(lines)

    proxies = lines[proxies_start + 1:proxies_end]
    seen_servers = set()
    unique_proxies = []
    for line in proxies:
        match = re.search(r'server: ([^,]+)', line)
        if match:
            server_ip = match.group(1)
            if server_ip not in seen_servers:
                seen_servers.add(server_ip)
                unique_proxies.append(line)
        else:
            unique_proxies.append(line)

    filtered_content = lines[:proxies_start + 1] + unique_proxies + lines[proxies_end:]
else:
    filtered_content = lines

filtered_content = "\n".join(filtered_content)

# 使用PyGithub
g = Github(github_token)
user = g.get_user()

# 检查是否有存储的Gist ID
if os.path.exists(gist_id_file):
    with open(gist_id_file, 'r') as file:
        gist_id = file.read().strip()
    try:
        existing_gist = g.get_gist(gist_id)
        print(f"Found existing Gist: {existing_gist.html_url}, updating it...")
        existing_gist.edit(
            description=gist_description,
            files={gist_filename: InputFileContent(filtered_content)}
        )
        print("Gist updated:", existing_gist.html_url)
    except Exception as e:
        print(f"Failed to update Gist: {e}")
        print("Creating a new Gist instead...")
        new_gist = user.create_gist(
            public=False,  # 设置为私密Gist
            files={gist_filename: InputFileContent(filtered_content)},
            description=gist_description
        )
        # 保存新的Gist ID
        with open(gist_id_file, 'w') as file:
            file.write(new_gist.id)
        print("New Gist created:", new_gist.html_url)
else:
    print("Creating a new Gist...")
    new_gist = user.create_gist(
        public=False,  # 设置为私密Gist
        files={gist_filename: InputFileContent(filtered_content)},
        description=gist_description
    )
    # 保存新的Gist ID
    with open(gist_id_file, 'w') as file:
        file.write(new_gist.id)
    print("Gist created:", new_gist.html_url)
