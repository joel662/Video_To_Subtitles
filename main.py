import re
import whisper
from pydub import AudioSegment
import numpy as np
import io
import tqdm
import ollama

# Load the Whisper model (Change "small" to "medium" or "large" for better accuracy)
model = whisper.load_model("small")

def webm_to_srt(webm_path, srt_path="subtitles1.srt"):
    """
    Converts a WEBM video file to subtitles using Whisper and saves as an SRT file.
    
    Args:
        webm_path (str): Path to the input WEBM file.
        srt_path (str): Output path for the SRT file.
    
    Returns:
        List of subtitle segments.
    """
    print("Extracting audio from video...");
    audio = AudioSegment.from_file(webm_path, format="webm")
    audio_path = "audio.wav"
    audio.export(audio_path, format="wav")
    
    print("Transcribing audio...")
    result = model.transcribe(audio_path)
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
    result = model.transcribe(wav_path)
    segments = result["segments"]

    # Save subtitles to an SRT file
    print(f"Saving subtitles to {srt_path}...")
    with io.open(srt_path, "w", encoding="utf-8") as f:
        with tqdm.tqdm(total=len(segments), desc="Processing", unit="segments") as pbar:
            for i, segment in enumerate(segments):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)

                for j, sentence in enumerate(sentences):
                    if sentence.strip():
                        f.write(f"{i+1}\n{start} --> {end}\n{sentence.strip()}\n\n")
                        start = end
                        end = format_timestamp(segment["start"] + (j + 1) * 0.5)
                
                pbar.update(1)

    print(f"Subtitles saved successfully: {srt_path}")
    return segments

# Call the functions

webm_file = "Github Copilot Tips.webm"
subtitles = webm_to_srt(webm_file)
wav_file = convert_webm_to_wav(webm_file)
subtitles = wav_to_srt(wav_file)


"""
Function to improve grammer of srt file
"""
def improve_grammar(srt_path, improved_path="subtitles_improved.srt"):
    """
    Improves the grammar of subtitles using Grammarly and saves as an SRT file.
    
    Args:
        srt_path (str): Path to the input SRT file.
        improved_path (str): Output path for the improved SRT file.
    
    Returns:
        None
    """
    print("Improving grammar of subtitles...")

    with io.open(srt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    improved_lines = []
    subtitle_block = []
    
    for line in lines:
        if re.match(r"^\d+$", line.strip()) or "-->" in line:
            # If it's a subtitle number or timestamp, keep it unchanged
            improved_lines.append(line)
        elif line.strip():
            # Collect subtitle text
            subtitle_block.append(line.strip())
        else:
            if subtitle_block:
                # Join lines and improve grammar when a blank line is encountered
                text = " ".join(subtitle_block)
                improved_text = text  # Placeholder for grammar correction logic
                improved_lines.append(improved_text + "\n\n")
                subtitle_block = []

    # Save improved subtitles
    with io.open(improved_path, "w", encoding="utf-8") as f:
        f.writelines(improved_lines)

    print(f"Improved subtitles saved successfully: {improved_path}")

# Example usage
improve_grammar("subtitles.srt", "subtitles_improved.srt")


def translate_text_ollama(text, target_lang="French"):
    """
    Translates text using Ollama.
    
    Args:
        text (str): Text to translate.
        target_lang (str): Target language (default: French).
    
    Returns:
        str: Translated text.
    """
    prompt = f"Translate the following English text to {target_lang} in formal form:\n{text}"
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
srt_to_french("subtitles_improved.srt", "subtitles_fr.srt")