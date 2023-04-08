# Gina - Locally Hosted Chatbot with the Blender 400M pretrained model
## - by decentricity

Gina (previously named Lina) is a locally hosted chatbot based on the BlenderBot Distill model from Facebook / HuggingFace. The chatbot utilizes the Telegram API to communicate with users and supports both text and voice output. Additionally, Gina can scrape website content if a URL is provided in the user's message.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features
- Text and voice input/output
- URL scraping and content understanding (this model is too small to provide proper understanding but she would be able to talk in context)
- Built using the Blenderbot model from Facebook
- Fully self-hosted after that model is downloaded
- Runs on the Telegram platform

## Requirements
- Python 3.6 or later
- Packages: `torch`, ~~`speech_recognition`,~~ `gtts`, `transformers`, `telegram`, `pydub`, `beautifulsoup4`, `requests`, and `re`

## Installation
1. Clone the repository:
```
git clone https://github.com/Decentricity/Gina-LocallyHostedChatbot-Blender.git
cd Gina-LocallyHostedChatbot-Blender
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

3. Start a conversation with your chatbot by sending a message ~~or a voice note.~~ (Voice recog doesn't work yet, trying to fix. don't send Gina voicenotes yet)

4. Gina will reply with a voice message.

5. Write "#toggle" to her to toggle to text and back to voice.

6. Write a URL in your message for her to read the contents of the page.

