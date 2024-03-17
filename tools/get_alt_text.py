from dotenv import load_dotenv
import os
import anthropic
import base64
import httpx
import sys

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def generate_alt_text(image_url):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        # Download the image (following redirects)
        response = httpx.get(image_url, follow_redirects=True)
        response.raise_for_status()
        image_data = base64.b64encode(response.content).decode("utf-8")
        image_media_type = response.headers["Content-Type"]

        # Send the image to the Anthropic API
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            temperature=0,
            system="Given an image, your task is to generate alternative text (alt text) that accurately and concisely describes the main content and context of the image for users who may not be able to see it. Focus on identifying and conveying the essential elements such as the setting, key subjects, actions, emotions, colors, and any text or symbols present. KEEP IT BRIEF. Your description should enable someone who cannot see the image to form a clear mental picture of its most important aspects. Remember to maintain neutrality, avoiding assumptions or interpretations that are not directly supported by the image's content. Don't assume gender and use gender neutral language whenever possible. Use clear, straightforward language and structure your description logically, starting with the most significant element and then mentioning secondary details if they are relevant and contribute to understanding the image's overall meaning or context. Prioritize accessibility and inclusiveness in your description, ensuring it is useful for a wide range of audiences.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Please provide alt text that describes this image for accessibility purposes."
                        }
                    ],
                }
            ],
        )

        # Extract the generated alt text from the API response
        alt_text = message.content[0].text
        return alt_text

    except httpx.HTTPError as e:
        print(f"Error downloading image: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error calling Anthropic API: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_alt_text.py <image_url>", file=sys.stderr)
        sys.exit(1)

    image_url = sys.argv[1]
    alt_text = generate_alt_text(image_url)
    print(alt_text)