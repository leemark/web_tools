from dotenv import load_dotenv
import os
import anthropic
import requests
from bs4 import BeautifulSoup
import sys

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def analyze_sentiment(url):
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
            max_tokens=100,
            temperature=0,
            system=(
                "You are a sentiment analysis expert. Your task is to determine the overall sentiment of the provided webpage content. "
                "Analyze the tone, language, and emotional expression in the content to classify the sentiment as positive, negative, or "
                "neutral. Consider factors such as word choice, context, and the overall emotional impact of the content. Provide your "
                "sentiment analysis as a single word: 'Positive', 'Negative', or 'Neutral'."
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
                                "Please analyze the sentiment of the above webpage content and provide your assessment as a single word: "
                                "'Positive', 'Negative', or 'Neutral'."
                            ),
                        },
                    ],
                }
            ],
        )

        # Extract the generated sentiment analysis from the API response
        sentiment = message.content[0].text.strip()
        return sentiment

    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error calling Anthropic API: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sentiment_analyzer.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    sentiment = analyze_sentiment(url)
    print(sentiment)