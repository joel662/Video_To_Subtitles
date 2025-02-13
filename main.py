import re
import whisper
from pydub import AudioSegment
import numpy as np
import io
import tqdm
import ollama

# Load the Whisper model (Change "small" to "medium" or "large" for better accuracy)
model = whisper.load_model("small")

def convert_webm_to_wav(webm_path, wav_path="audio.wav"):
    """
    Converts a WEBM audio file to WAV format.
    
    Args:
        webm_path (str): Path to the input WEBM file.
        wav_path (str): Path to save the converted WAV file.
    
    Returns:
        str: Path to the converted WAV file.
    """
    print(f"Converting {webm_path} to WAV...")
    audio = AudioSegment.from_file(webm_path, format="webm")
    audio = audio.set_frame_rate(16000).set_channels(1)  # Convert to 16kHz mono
    audio.export(wav_path, format="wav")
    print("Conversion complete.")
    return wav_path

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def wav_to_srt(wav_path, srt_path="subtitles.srt"):
    """
    Converts a WAV file to subtitles using Whisper and saves as an SRT file.
    
    Args:
        wav_path (str): Path to the WAV file.
        srt_path (str): Output path for the SRT file.
    
    Returns:
        List of subtitle segments.
    """
    print("Transcribing audio...")
    
    # Transcribe audio with progress bar
    with tqdm.tqdm(desc="Processing", unit="frames") as pbar:
        result = model.transcribe(wav_path)
        pbar.update()

    # Extract segments
    segments = result["segments"]

    # Save subtitles to an SRT file
    print(f"Saving subtitles to {srt_path}...")
    with io.open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()

            f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")

    print(f"Subtitles saved successfully: {srt_path}")
    return segments


 

# Call the functions
webm_file = "Github Copilot Tips.webm"
wav_file = convert_webm_to_wav(webm_file)
subtitles = wav_to_srt(wav_file)

def improve_text_ollama(text):
    """
    Uses Ollama to enhance subtitle clarity and accuracy.
    """
    prompt = f"Improve the clarity and grammar of the following subtitle text while keeping its meaning, don't change the entire text:\n{text}"
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

def improve_srt(srt_path, output_srt_path="subtitles_improved.srt"):
    """
    Improves subtitle clarity using Ollama while keeping timestamps and numbering intact.
    """
    print("Improving subtitles...")

    with io.open(srt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    improved_lines = []
    subtitle_block = []

    for line in lines:
        if re.match(r"^\d+$", line.strip()) or "-->" in line:
            # Keep subtitle number and timestamps unchanged
            improved_lines.append(line)
        elif line.strip():
            # Collect subtitle text
            subtitle_block.append(line.strip())
        else:
            if subtitle_block:
                # Join lines, improve text, and add improved subtitle
                english_text = " ".join(subtitle_block)
                improved_text = improve_text_ollama(english_text)
                improved_lines.append(improved_text + "\n\n")
                subtitle_block = []

    # Save the improved subtitles
    with io.open(output_srt_path, "w", encoding="utf-8") as f:
        f.writelines(improved_lines)

    print(f"Improved subtitles saved successfully: {output_srt_path}")

# Example usage
srt_file = "subtitles.srt"  # Change this to your subtitle file
improve_srt(srt_file, "subtitles_improved.srt")


def translate_text_ollama(text, target_lang="French"):
    """
    Translates text using Ollama.
    
    Args:
        text (str): Text to translate.
        target_lang (str): Target language (default: French).
    
    Returns:
        str: Translated text.
    """
    prompt = f"Translate the following English text to {target_lang}:\n{text}"
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

def srt_to_french(srt_path, french_path="subtitles_fr.srt"):
    """
    Translates English subtitles to French using Ollama and saves as an SRT file.
    
    Args:
        srt_path (str): Path to the input SRT file.
        french_path (str): Output path for the French SRT file.
    
    Returns:
        None
    """
    print("Translating subtitles to French...")

    with io.open(srt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    translated_lines = []
    subtitle_block = []
    
    for line in lines:
        if re.match(r"^\d+$", line.strip()) or "-->" in line:
            # If it's a subtitle number or timestamp, keep it unchanged
            translated_lines.append(line)
        elif line.strip():
            # Collect subtitle text
            subtitle_block.append(line.strip())
        else:
            if subtitle_block:
                # Join lines and translate when a blank line is encountered
                english_text = " ".join(subtitle_block)
                translated_text = translate_text_ollama(english_text)
                translated_lines.append(translated_text + "\n\n")
                subtitle_block = []

    # Save translated subtitles
    with io.open(french_path, "w", encoding="utf-8") as f:
        f.writelines(translated_lines)

    print(f"French subtitles saved successfully: {french_path}")

# Example usage
srt_to_french("subtitles.srt", "subtitles_fr.srt")