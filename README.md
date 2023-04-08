# Gina - Locally Hosted Chatbot Blender - by decentricity

Gina (previously named Lina) is a locally hosted chatbot based on the BlenderBot Distill model from Facebook / HuggingFace. The chatbot utilizes the Telegram API to communicate with users and supports both text and voice input/output. Additionally, Lina can scrape website content if a URL is provided in the user's message.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features
- Text and voice input/output
- URL scraping and content summarization
- Built using the Blender model from OpenAI
- Runs on the Telegram platform

## Requirements
- Python 3.6 or later
- Packages: `torch`, `speech_recognition`, `gtts`, `transformers`, `telegram`, `pydub`, `beautifulsoup4`, `requests`, and `re`

### ⚠️ **Warning:** The `facebook/blenderbot-400M-distill` model has the following hardware requirements:

- A GPU with at least 16 GB of VRAM (e.g., NVIDIA Tesla V100 or equivalent)
- A modern, high-performance CPU and sufficient system RAM to handle moderate model sizes

## Installation
1. Clone the repository:
```
git clone https://github.com/Decentricity/Gina-LocallyHostedChatbot-Blender.git
```
2. Install required packages using pip:
```
pip install -r requirements.txt
```
3. Set your Telegram Bot Token in the `TELEGRAM_API_TOKEN` variable within the `main.py` script.

## Usage
1. Run the `main.py` script to start the chatbot:
```
python main.py
```

2. Find your chatbot on Telegram by searching for its username.

3. Start a conversation with your chatbot by sending a message or a voice note.

4. Gina will reply with a voice message.

5. Write "#toggle" to her to toggle to text and back to voice.

6. Write a URL in your message for her to read the contents of the page.

