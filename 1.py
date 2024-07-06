import os
import requests
from github import Github
from github.InputFileContent import InputFileContent

# 配置
url = "XXXXXX"  # 要获取内容的URL
github_token = "XXXXXX"  # 你的GitHub访问令牌
gist_description = "123 "  # Gist描述
gist_filename = "XXXXX"  # Gist文件名
gist_id_file = "/home/gist_id.txt"  # 用于存储Gist ID的文件路径
local_backup_file = "/home/backup_file.txt"  # 本地备份文件路径

# 设置自定义头信息
headers = {
    "User-Agent": "clash verge"
}

# 获取网址内容
response = requests.get(url, headers=headers)
if response.status_code == 200:
    content = response.text
else:
    raise Exception(f"Failed to retrieve content from {url}, status code {response.status_code}")

# 去除重复的server节点
unique_servers = set()
filtered_lines = []
for line in content.splitlines():
    if "server:" in line:
        server = line.strip().split("server:")[1].strip()
        if server not in unique_servers:
            unique_servers.add(server)
            filtered_lines.append(line)
    else:
        filtered_lines.append(line)

filtered_content = "\n".join(filtered_lines)

# 将内容保存到本地备份文件
with open(local_backup_file, 'w') as backup_file:
    backup_file.write(filtered_content)

# 使用PyGithub
print("GitHub Token:", github_token)  # 调试输出，确保令牌正确传递
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
            public=False,
            files={gist_filename: InputFileContent(filtered_content)},
            description=gist_description
        )
        with open(gist_id_file, 'w') as file:
            file.write(new_gist.id)
        print("New Gist created:", new_gist.html_url)
else:
    print("Creating a new Gist...")
    new_gist = user.create_gist(
        public=False,
        files={gist_filename: InputFileContent(filtered_content)},
        description=gist_description
    )
    with open(gist_id_file, 'w') as file:
        file.write(new_gist.id)
    print("Gist created:", new_gist.html_url)
