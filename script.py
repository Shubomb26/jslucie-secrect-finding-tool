import sys
import os
import requests
import subprocess
import urllib3
from urllib.parse import urlparse

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SEPARATOR = "----------------------\n"

def download_js(url, download_dir):
    try:
        # 🔥 SSL verification disabled here
        response = requests.get(url, timeout=3600, verify=False)
        response.raise_for_status()

        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)

        if not filename.endswith(".js"):
            filename += ".js"

        file_path = os.path.join(download_dir, filename)

        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path, filename

    except Exception as e:
        print(f"[!] Download failed: {url} -> {e}")
        return None, None


def run_jsluice(mode, file_path):
    try:
        result = subprocess.run(
            ["jsluice", mode, file_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"[!] jsluice error:\n{result.stderr.strip()}"

        output = result.stdout.strip()

        if not output:
            return "No results found."

        return output

    except Exception as e:
        return f"[!] Execution error: {e}"


def main():
    if len(sys.argv) != 3:
        print("Usage: python js_automation.py <input_urls.txt> <output.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    download_dir = "downloaded_js"
    os.makedirs(download_dir, exist_ok=True)

    with open(input_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    with open(output_file, "w", encoding="utf-8") as out:

        for url in urls:
            print(f"[+] Processing: {url}")

            file_path, filename = download_js(url, download_dir)
            if not file_path:
                continue

            urls_output = run_jsluice("urls", file_path)
            secrets_output = run_jsluice("secrets", file_path)

            out.write(SEPARATOR)
            out.write(f"JS URL: {url}\n")
            out.write(f"File Name: {filename}\n")
            out.write(SEPARATOR)

            out.write("\n[URLs]\n")
            out.write(urls_output + "\n")

            out.write("\n[Secrets]\n")
            out.write(secrets_output + "\n\n")

    print(f"\n[✔] Completed. Output saved to: {output_file}")


if __name__ == "__main__":
    main()
