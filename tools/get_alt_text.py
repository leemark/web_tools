from dotenv import load_dotenv
import os
import chainlit as cl

# Load environment variables
load_dotenv()

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()