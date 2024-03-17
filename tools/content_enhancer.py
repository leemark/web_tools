from dotenv import load_dotenv
import os
import anthropic
import requests
from bs4 import BeautifulSoup
import sys

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def analyze_content(url):
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
            max_tokens=1500,
            temperature=0.5,
            system=(
                "You are an expert SEO consultant and content strategist. Your task is to analyze the provided webpage content "
                "and provide actionable advice to improve SEO and enhance the content. Focus on identifying key areas for optimization, "
                "such as keyword placement, content structure, readability, and engagement. Suggest specific techniques and strategies "
                "to increase visibility, attract organic traffic, and improve user experience. Provide your recommendations in a clear, "
                "concise, and actionable manner."
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
                                "Please analyze the above webpage content and provide actionable SEO advice and content enhancement tips "
                                "to increase visibility and engagement."
                            ),
                        },
                    ],
                }
            ],
        )

        # Extract the generated advice from the API response
        advice = message.content[0].text
        return advice

    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error calling Anthropic API: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python content_enhancer.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    advice = analyze_content(url)
    print(advice)