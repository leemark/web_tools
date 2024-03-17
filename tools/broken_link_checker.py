import requests
from bs4 import BeautifulSoup
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_link(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        status_code = response.status_code
        if status_code == 403:
            return url, "Forbidden (403)"
        elif status_code == 999:
            return url, "Unknown Error (999)"
        elif status_code >= 400:
            return url, status_code
        elif status_code in [301, 302]:
            # Follow the redirect and check the final destination
            redirect_url = response.headers.get("Location")
            if redirect_url:
                redirect_response = requests.head(redirect_url, allow_redirects=True, timeout=5)
                redirect_status_code = redirect_response.status_code
                if redirect_status_code >= 400:
                    return url, f"Redirects to: {redirect_url} (Status Code: {redirect_status_code})"
        return None
    except requests.exceptions.RequestException:
        return url, None

def check_webpage_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = [link.get("href") for link in soup.find_all("a")]

        broken_links = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_link, link) for link in links if link and link.startswith("http")]
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    broken_links.append(result)

        if broken_links:
            print("Broken Links Report:")
            for link, status_code in broken_links:
                print(f"URL: {link}")
                if isinstance(status_code, str):
                    print(status_code)
                else:
                    print(f"Status Code: {status_code}")
                print()
        else:
            print("No broken links found.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python broken_link_checker.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    check_webpage_links(url)