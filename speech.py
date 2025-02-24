"""
    speech.py - Handler for speech related functions.

"""

import librosa
import mlx_whisper
import numpy as np
import chinese_converter as cc
from difflib import SequenceMatcher

edge_word_table = {
    "了": "<|SC1|>"
}

# Function to extract pitch and energy
def analyze_audio(audio_path):
    y, sr = librosa.load(audio_path)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    energy = np.sum(magnitudes, axis=0)
    
    # Compute average pitch and energy
    pitch = pitches[pitches > 0].mean()
    avg_energy = np.mean(energy)
    
    return pitch, avg_energy, y, sr

# Function to compare pitch and energy with reference
def compare_audio(user_audio_path, ref_audio_path):
    user_pitch, user_energy, _, _ = analyze_audio(user_audio_path)
    ref_pitch, ref_energy, _, _ = analyze_audio(ref_audio_path)
    
    # Intonation advice
    pitch_diff = abs(user_pitch - ref_pitch)
    energy_diff = abs(user_energy - ref_energy)
    
    intonation_feedback = f"Your pitch differs by {pitch_diff:.2f} Hz. "
    if pitch_diff > 20:
        intonation_feedback += "Try matching the intonation more closely."
    else:
        intonation_feedback += "Good job on the intonation!"
    
    energy_feedback = f"Your energy differs by {energy_diff:.2f}. "
    if energy_diff > 10:
        energy_feedback += "Consider adjusting your loudness for better emphasis."
    else:
        energy_feedback += "Your loudness is consistent with the reference."
    
    print(f"Intonation feedback: {intonation_feedback}")
    print(f"Energy feedback: {energy_feedback}")
    return f"{intonation_feedback}\n{energy_feedback}"

def remove_punctuation(text):
    punc = "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."
    return "".join([t for t in text if t not in punc])

# Function to compare text similarity
def compare_speech(user_text, assistant_text):
    # Compute similarity
    user_text = remove_punctuation(user_text)
    assistant_text = remove_punctuation(assistant_text)
    similarity = SequenceMatcher(None, user_text, assistant_text).ratio()
    feedback = []
    
    # if similarity < 0.8:
        # Keyword feedback
    # reference_keywords = [t for t in assistant_text]
    # user_keywords = [t for t in user_text]
    reference_keywords = assistant_text.strip().split(" ")
    user_keywords = user_text.strip().split(" ")
    missing_keywords = ", ".join(set([t for t in reference_keywords if t not in user_keywords]))
    extra_keywords = ", ".join(set([t for t in user_keywords if not t in reference_keywords]))

    if missing_keywords:
        feedback.append(f'Missing keywords: {", ".join(missing_keywords)}')
    if extra_keywords:
        feedback.append(f'Extra keywords: {", ".join(extra_keywords)}')

    else:
        feedback.append("Great job! Your speech closely matches the reference.")

    # Overall advice
    advice = " ".join(feedback)
    similarity_score = f"Similarity Score: {similarity:.2f}"
    return f"{similarity_score}\n{advice}"

# speech recognition
def speech_to_text(audio_pth):
    result = mlx_whisper.transcribe(
        audio_pth,
        path_or_hf_repo="mlx-community/whisper-large-v3-turbo"
    )
    text = result["text"]
    print(f"User text: {text}")
    return text

# handle exemptions
def map_edge_words(text):
    for key, value in edge_word_table.items():
        text = text.replace(key, value)
    return text

# handle exemptions
def remap_edge_words(text):
    for key, value in edge_word_table.items():
        text = text.replace(value, key)
    return text

# zh-ch conversion
def zh_ch_convert(text, zh_ch):
    _text = map_edge_words(text)
    new_text = cc.to_simplified(_text) if zh_ch == "ch" else cc.to_traditional(_text)
    return remap_edge_words(new_text)