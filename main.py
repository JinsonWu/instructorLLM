"""
    main.py - Main file for instructor

"""

import os
import gradio as gr
import pygame
import threading
from gtts import gTTS
from api import ResumeAPI
from speech import (
    compare_audio,
    compare_speech,
    speech_to_text,
)

AUDIO_FILE_PTH="./audio"
resume_api = ResumeAPI()

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Global variable to track the current audio file
assistant_audio_pth = None
user_audio_pth = None

# Function to handle sending messages
def send_message(message, chat_history):
    return {
        "role": "assistant",
        "content": message
    }

# generate assistant audio file by gTTS
def get_assistant_audio(sentence, lang="en"):
    global assistant_audio_pth
    assistant_audio_pth = os.path.join(AUDIO_FILE_PTH, sentence+".mp3")
    tts = gTTS(sentence, lang=lang)
    tts.save(assistant_audio_pth)
    return assistant_audio_pth

# auto update choices by sentences
def update_options(chatbot):
    new_options = [msg["content"] for msg in chatbot]
    return gr.Dropdown(choices=new_options, value=new_options[0], label="sentence", interactive=True)

def handle_user_audio(audio):
    global user_audio_pth
    if audio:
        user_audio_pth = audio
        return speech_to_text(audio)
    return ""

def handle_teacher_audio(audio):
    global assistant_audio_pth
    if audio:
        assistant_audio_pth = audio

def handle_assistant_audio(audio):
    global assistant_audio_pth
    if isinstance(audio, str):
        audio = get_assistant_audio(audio)
    if audio:
        assistant_audio_pth = audio
        threading.Thread(target=_play_audio_thread, args=(assistant_audio_pth,), daemon=True).start()

# Function to stop audio playback
def stop_audio():
    pygame.mixer.music.stop()

# Helper function to handle audio playback in a separate thread
def _play_audio_thread(file_path):
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
    except Exception as err:
        print(f"Error playing audio: {err}")

def analyze_audio():
    return compare_audio(user_audio_pth, assistant_audio_pth)

def analyze_speech(user_text, assistant_text):
    return compare_speech(user_text.strip(), assistant_text.strip())

# UI
with gr.Blocks() as demo:
    chat_history = gr.State([])

    with gr.Row():
        gr.Markdown("### Chat UI with Audio Playback")

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Chatbot",
                scale=1,
                type="messages",
                autoscroll=True,
            )
            chat_inference = gr.ChatInterface(
                fn=send_message,
                chatbot=chatbot,
                textbox=gr.Textbox(visible=False)
            )
        with gr.Column(scale=1):
            summary = gr.Textbox(placeholder="Script summary", label="Summary")
            api_submit_button = gr.Button("Create Script")

    with gr.Row():
        with gr.Column():
            sentences = gr.Dropdown(choices=[], label="sentence", interactive=True)
            assistant_audio_button = gr.Button("Play assistant audio")
            teacher_recording_button = gr.Audio(sources="microphone", type="filepath", label="Teacher recording")
            analyze_button = gr.Button("Analyze audio")
            analyze_text = gr.Textbox(placeholder="Analyzed feedback")
            compare_button = gr.Button("Compare button")
            compare_text = gr.Textbox(placeholder="Speech feedback")
        with gr.Column():
            user_recording_button = gr.Audio(sources="microphone", type="filepath", label="User recording")
            user_text = gr.Textbox(placeholder="User text")

    user_recording_button.change(
        handle_user_audio,
        inputs=[user_recording_button],
        outputs=[user_text],
    )

    teacher_recording_button.change(
        handle_teacher_audio,
        inputs=[teacher_recording_button],
        outputs=None
    )

    assistant_audio_button.click(
        handle_assistant_audio,
        inputs=[sentences],
        outputs=None
    )

    chatbot.change(
        update_options,
        inputs=[chatbot],
        outputs=[sentences]
    )

    api_submit_button.click(
        resume_api.create,
        inputs=[summary],
        outputs=[chatbot]
    )

    analyze_button.click(
        analyze_audio,
        inputs=None,
        outputs=[analyze_text]
    )

    compare_button.click(
        analyze_speech,
        inputs=[user_text, sentences],
        outputs=[compare_text]
    )

# Launch the app
demo.launch()
