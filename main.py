import os
import torch
import speech_recognition as sr
from gtts import gTTS
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
#New stuff for URL scraping:
from bs4 import BeautifulSoup
import requests
import re


def recognize_speech_from_voice_note(update: Update):
    file_id = update.message.voice.file_id
    file = context.bot.get_file(file_id)
    file.download('voice_note.ogg')

    # Convert OGG to WAV using pydub
    audio = AudioSegment.from_ogg('voice_note.ogg')
    audio.export('voice_note.wav', format='wav')

    recognizer = sr.Recognizer()

    with sr.AudioFile('voice_note.wav') as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Speech Recognition service; {e}")


def voice_message(update: Update, context: CallbackContext):
    recognized_text = recognize_speech_from_voice_note(update)
    if recognized_text:
        text_message(update, context, recognized_text)


def synthesize_text(text):
    tts = gTTS(text, lang="en")
    tts.save("response.mp3")

    # Convert MP3 to OGG using pydub
    audio = AudioSegment.from_mp3("response.mp3")
    audio.export("response.ogg", format="ogg")  # Export as OGG
    
# New function to scrapey scrape, taken from the Myriad scraper
def fetch_website_text(url):
    try:
        response = requests.get(url)
        
        if response.status_code >= 200 and response.status_code < 300:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = ' '.join(soup.stripped_strings)
            truncated_text = text_content[:700]
            warning = "\nWarning: Only the first 700 characters of the web page content are displayed."
            return truncated_text + warning
        else:
            return f"Error fetching website content: Received a {response.status_code} status code."
    except Exception as e:
        return f"Error fetching website content: {e}"
        
        
def is_bot_mentioned(text, bot_username):
    return bot_username.lower() in text.lower() or "gina" in text.lower()


# Initialize the Blenderbot model and tokenizer
tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-400M-distill")

# Set your Telegram Bot Token
TELEGRAM_API_TOKEN = "----"

def generate_text(prompt, model, tokenizer):
    input_ids = tokenizer.encode(prompt, return_tensors="pt", truncation=True)

    model.config.pad_token_id = model.config.eos_token_id
    attention_mask = torch.ones(input_ids.shape, dtype=torch.long)

    output = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=1024,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.8,
        num_beams=2,
        no_repeat_ngram_size=2,
        early_stopping=True,
    )

    output_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return output_text

def synthesize_text(text):
    tts = gTTS(text, lang="en")
    tts.save("response.mp3")

    # Convert MP3 to OGG using pydub
    audio = AudioSegment.from_mp3("response.mp3")
    audio.export("response.ogg", format="ogg")  # Export as OGG

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I am Gina, your chatbot. You can send me a message and I will respond to you.")

def text_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    bot_username = context.bot.username

    # Check if the bot is mentioned or if the message is a reply to Lina's message
    if (update.message.chat.type == 'private') or is_bot_mentioned(user_input, bot_username) or (update.message.reply_to_message and update.message.reply_to_message.from_user.username == bot_username):
        if update.message.text:
            user_input = user_input.replace("Gina", "").replace(bot_username, "").strip()  # Remove "Gina" and bot_username from the user input
                # Extract the URL from the user input using regex
            url_match = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', user_input)
            if url_match:
                url = url_match.group()
                fetched_content_info = fetch_website_text(url)
                if fetched_content_info:
                    user_input += f"\nWebsite: {fetched_content_info}\n"

            prompt = f"Message: {user_input}\n"
            
        elif update.message.voice:
            # Download voice message
            voice_file = context.bot.getFile(update.message.voice.file_id)
            voice_file.download("received_voice_note.ogg")

            # Transcribe voice message
            user_input = recognize_speech("received_voice_note.ogg")
            prompt = f"Message: {user_input}\n"

        generated_text = generate_text(prompt, model, tokenizer)
        synthesize_text(generated_text)

        with open("response.ogg", "rb") as audio:
            update.message.reply_voice(
                audio,
                reply_to_message_id=update.message.reply_to_message.message_id if update.message.reply_to_message else None
            )


def error(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")


    
def text_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    bot_username = context.bot.username

    # Check if the bot is mentioned or if the message is a reply to Lina's message
    if is_bot_mentioned(user_input, bot_username) or (update.message.reply_to_message and update.message.reply_to_message.from_user.username == bot_username):
        user_input = user_input.replace("Lina", "").replace(bot_username, "").strip()  # Remove "Lina" and bot_username from the user input
        prompt = f"Message: {user_input}\n"

        generated_text = generate_text(prompt, model, tokenizer)
        synthesize_text(generated_text)

        with open("response.ogg", "rb") as audio:
            update.message.reply_voice(
                audio,
                reply_to_message_id=update.message.reply_to_message.message_id if update.message.reply_to_message else None
            )
            
            
def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, text_message))
    dp.add_handler(MessageHandler(Filters.voice, voice_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
