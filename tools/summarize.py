from dotenv import load_dotenv
import os
import anthropic
import requests
from bs4 import BeautifulSoup
import sys

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def summarize_content(url):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        content = " ".join([p.get_text() for p in soup.find_all("p")])

        # Send the content to the Anthropic API
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0,
            system=(
                "You are a skilled content summarizer. Your task is to read the provided article or document and generate a concise "
                "summary that captures the most important points and key takeaways. Focus on condensing the content while preserving "
                "the essential information and context. Aim to create a summary that allows readers to quickly grasp the main ideas "
                "without having to read the entire piece. Structure your summary in a logical and easily digestible format."
            ),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": content,
                        },
                        {
                            "type": "text",
                            "text": (
                                "Please provide a concise summary of the above article, highlighting the key points and main takeaways."
                            ),
                        },
                    ],
                }
            ],
        )

        # Extract the generated summary from the API response
        summary = message.content[0].text
        return summary

    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error calling Anthropic API: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python summarize.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    summary = summarize_content(url)
    print(summary)