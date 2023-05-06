import os
import torch
from gtts import gTTS
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
#New stuff for URL scraping:
from bs4 import BeautifulSoup
import requests
import re

central_dogma="Hey, let's talk.\nOkay. How are you?\nI am good.\nWonderful.\nI am an AI\n"
conversation_history=central_dogma

def strip_trailing_sentence(output_text):
    match = re.match(r"(.*[\.\?!])(.*)", output_text)
    if match:
        main_text = match.group(1)
        remaining_text = match.group(2)
        # Check if the remaining text contains any sentence-ending punctuation
        if not re.search(r"[\.\?!]", remaining_text):
            output_text = main_text
    if output_text=="":
        output_text="."
    output_text=output_text.replace("..",".")
    return output_text
    
def construct_blenderbot_prompt(conversation_history, new_prompt):
    conversation_history = conversation_history.strip()
    # Construct the new prompt
    #formatted_prompt = (f'Earlier, I said, "{last_user_content}" '
     #                   f'and you answered, "{last_bot_content}" '
      #                  f'and I am saying: {new_prompt}')
    last_lines=("\n".join(conversation_history.splitlines()[-3:]))
    all_lines=("\n".join(conversation_history.splitlines()[-3:]))
    lines = all_lines.splitlines()
    if not conversation_history=="":
        all_lines = "</s><s>".join(lines)

    new_prompt=new_prompt+"."
    new_prompt=new_prompt.replace("..",".")
    new_prompt=new_prompt.replace("?.","?")
    new_prompt=new_prompt.replace("!.","!")
    
#    formatted_prompt = (f"({last_lines})\n User: {new_prompt}\nDina:")
    formatted_prompt = (f"<s>{all_lines}</s><s>{new_prompt}</s>") 
    formatted_prompt = formatted_prompt.replace("\n","")

    return formatted_prompt
    
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
            warning = "\nThis is a website: "
            return warning+truncated_text
        else:
            return f"Error fetching website content: Received a {response.status_code} status code."
    except Exception as e:
        return f"Error fetching website content: {e}"
        
        
def is_bot_mentioned(text, bot_username):
    return bot_username.lower() in text.lower() or "gina" in text.lower()


# Initialize the Blenderbot model and tokenizer
tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-3B")
model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-3B")

# Set your Telegram Bot Token
TELEGRAM_API_TOKEN = "------"

def generate_text(prompt, model, tokenizer):
    print(prompt)
    input_ids = tokenizer.encode(prompt, return_tensors="pt", truncation=True)
    print("Input IDs: "+repr(input_ids))
    model.config.pad_token_id = model.config.eos_token_id
    attention_mask = torch.ones(input_ids.shape, dtype=torch.long)
    print("Attention Mask: "+repr(attention_mask))
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
    print("Output: "+repr(output))
    output_text = tokenizer.decode(output[0], skip_special_tokens=True)    
    sentences = re.split('(?<=[.?!])(?=\s|$)', output_text)
    output_text = sentences[0]+" "+sentences[1]
    return output_text
def reset():
    global conversation_history
    global central_dogma
    conversation_history=central_dogma
    
def synthesize_text(text):
    tts = gTTS(text, lang="en")
    tts.save("response.mp3")

    # Convert MP3 to OGG using pydub
    audio = AudioSegment.from_mp3("response.mp3")
    audio.export("response.ogg", format="ogg")  # Export as OGG

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I am Gina, your chatbot. You can send me a message and I will respond to you.")

def text_message(update: Update, context: CallbackContext):
    global conversation_history
    user_input = update.message.text
    bot_username = context.bot.username
    print(f"message received: {user_input}")
    if user_input=="#reset": 
        reset()
        return
    # Check if the bot is mentioned or if the message is a reply to Lina's message
    if (update.message.chat.type == 'private') or is_bot_mentioned(user_input, bot_username) or (update.message.reply_to_message and update.message.reply_to_message.from_user.username == bot_username):
        if update.message.text:
            user_input = user_input.replace("Dono", "").replace(bot_username, "").strip()  # Remove "Gina" and bot_username from the user input
                # Extract the URL from the user input using regex
            url_match = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', user_input)
            if url_match:
                reset()
                url = url_match.group()
                fetched_content_info = fetch_website_text(url)
                if fetched_content_info:
                    user_input += f". \n{fetched_content_info}\n"

            prompt = f"{user_input}"
            
        elif update.message.voice:
            # Download voice message
            voice_file = context.bot.getFile(update.message.voice.file_id)
            voice_file.download("received_voice_note.ogg")

            # Transcribe voice message
            user_input = recognize_speech("received_voice_note.ogg")
            prompt = f"Message: {user_input}\n"
        prompt=construct_blenderbot_prompt(conversation_history,prompt)
        print(prompt)
        generated_text = generate_text(prompt, model, tokenizer)
        print(generated_text)
        generated_text=strip_trailing_sentence(generated_text)
        update.message.reply_text(generated_text)
        conversation_history = conversation_history + "\n"+user_input+"\n"+generated_text
        print(conversation_history)
        #synthesize_text(generated_text)

        with open("response.ogg", "rb") as audio:
            update.message.reply_voice(
                audio,
                reply_to_message_id=update.message.reply_to_message.message_id if update.message.reply_to_message else None
            )


def error(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")


    
            
def main():
    print("init")
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
