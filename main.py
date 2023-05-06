import os
import json
import torch
import spacy
from gtts import gTTS
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration, AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from textstat import flesch_reading_ease

# Global variables
central_dogma = "My name is Slenderman, I am 2003 years old, I like long walks in the woods at night and the taste of teenager flesh."

# ----------------------------------------
# ROBERTA'S SEGMENT
# ----------------------------------------

# Loding Roberta

    # a) Get predictions
nlp = pipeline('question-answering', model="deepset/tinyroberta-squad2", tokenizer="deepset/tinyroberta-squad2")

    # b) Load model & tokenizer
r_model = AutoModelForQuestionAnswering.from_pretrained("deepset/tinyroberta-squad2")
r_tokenizer = AutoTokenizer.from_pretrained("deepset/tinyroberta-squad2")

#Making Roberta Answer

def roberta_answers(prompt):
    user_input=prompt
    QA_input = {
        'question': user_input,
        'context': central_dogma
    }
    res = nlp(QA_input)
    print(res)
    print(res['answer'])



# ----------------------------------------
# BLENDERBOT'S SEGMENT
# ----------------------------------------

# Loading Blenderbot
bbot_model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-3B")
bbot_tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-3B")


# Making Blenderbot answer

def blenderbot_answers(prompt):
    
    # Switch model and tokenizer to Blenderbot
    model = bbot_model
    tokenizer = bbot_tokenizer
    
    # Collect user input
    user_input=prompt
    
    
    # Encore user input 
    input_ids = tokenizer.encode(user_input, return_tensors="pt", truncation=True)
   

   # Tokenize the prompt and convert to string
    tokenized_text = tokenizer.decode(input_ids[0])
    
    # Check if the tokenized text ends with '</s>'
    if not tokenized_text.endswith('</s>'):
        # Append '</s>' to the tokenized text
        tokenized_text += '</s>'
        # Re-encode the updated tokenized text
        input_ids = tokenizer.encode(tokenized_text, return_tensors="pt")
    
    model.config.pad_token_id = model.config.eos_token_id
    attention_mask = torch.ones(input_ids.shape, dtype=torch.long)

    # Set the stop token for BlenderBot
    stop_token_id = tokenizer.eos_token_id
    
    # end new edits
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
    print(output_text)
    
# ----------------------------------------
# TOOLS
# ----------------------------------------

# User input complexity test
def complexity_test(prompt): 
    score = flesch_reading_ease(prompt)
    print("\n\n\n Complexity score: "+str(score)+"\n\n\n")
    return score


# Route question to the appropriate model depending on prompt complexity
def grade_and_route(prompt):
    score = complexity_test(prompt)
    if score >= 70:
        roberta_answers(prompt)
    else:
        blenderbot_answers(prompt)
        

# ----------------------------------------
# RUN THE DAMN THING
# ----------------------------------------

while True:
    user_input=input("> ")
    grade_and_route(user_input)
