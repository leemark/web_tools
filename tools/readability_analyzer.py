from dotenv import load_dotenv
import os
import anthropic
import requests
from bs4 import BeautifulSoup
import sys

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def analyze_readability(url):
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
            max_tokens=400,
            temperature=0,
            system=(
                "You are a readability analysis expert. Your task is to assess the readability of the provided webpage content using "
                "metrics like the Flesch-Kincaid readability score and provide suggestions for improvement. Analyze factors such as "
                "sentence length, word complexity, and paragraph structure to determine the content's readability level. Offer specific "
                "recommendations on how to enhance the readability and make the content more accessible to a wider audience. Provide your "
                "analysis and suggestions in a clear and organized manner."
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
                                "Please analyze the readability of the above webpage content using metrics like the Flesch-Kincaid readability "
                                "score and provide suggestions for improvement."
                            ),
                        },
                    ],
                }
            ],
        )

        # Extract the generated readability analysis from the API response
        readability_analysis = message.content[0].text
        return readability_analysis

    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error calling Anthropic API: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python readability_analyzer.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    readability_analysis = analyze_readability(url)
    print(readability_analysis)