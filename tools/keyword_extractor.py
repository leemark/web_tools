from dotenv import load_dotenv
import os
import anthropic
import requests
from bs4 import BeautifulSoup
import sys

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def extract_keywords(url):
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
            max_tokens=200,
            temperature=0,
            system=(
                "You are a skilled keyword extraction expert. Your task is to analyze the provided webpage content and identify the most "
                "relevant and important keywords and phrases that capture the main topics and themes. Focus on selecting keywords that "
                "are meaningful, specific, and relevant to the content's subject matter. Consider factors such as frequency, prominence, "
                "and contextual significance when choosing keywords. Provide the keywords as a comma-separated list."
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
                                "Please extract the most relevant and important keywords and phrases from the above webpage content. "
                                "Provide them as a comma-separated list."
                            ),
                        },
                    ],
                }
            ],
        )

        # Extract the generated keywords from the API response
        keywords = message.content[0].text
        return keywords

    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error calling Anthropic API: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python keyword_extractor.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    keywords = extract_keywords(url)
    print(keywords)