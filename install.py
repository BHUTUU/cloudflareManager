import requests, subprocess
from bs4 import BeautifulSoup

url = "https://github.com/cloudflare/cloudflared/releases/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Fetch the HTML content
try:
    completed_process = subprocess.run(
        ['curl', '-sL', url],
        check=True,
        capture_output=True,
        text=True
    )

    # Access the output
    html_content = completed_process.stdout
    print(html_content)
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")

# Parse HTML using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the element with class "d-inline mr-3" and get its text
version_element = soup.find(class_="d-inline mr-3")
version_text = version_element.get_text() if version_element else None

# Extract the version number using a regular expression
import re
version_number = re.search(r'>[0-9.]*<', version_text).group() if version_text else None

print(version_number)
