import logging
from flask import current_app, jsonify
import json
import requests
import os
import time
from datetime import datetime
from openai import OpenAI
import pathlib
import textwrap
from groq import Groq
import re
from dotenv import load_dotenv

import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Load environment variables
load_dotenv()

# Get API key from .env file
api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)


def get_response():
    # Encode the image into base64 because that is what LLMs use
    base64_image = encode_image("image.jpg")

    # Pass the image along with the prompt
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image."},
                {"type": "image_url", 
                 "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }
    ]

    response = client.chat.completions.create(
        model = "llama-3.2-90b-vision-preview",
        messages = messages
    )

    return response.choices[0].message.content.strip()


print(get_response())