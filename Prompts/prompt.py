import difflib
import re
import os
from openai import OpenAI
from dotenv import load_dotenv
import json


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

json_file_path = 'prompt_map.json'


with open(json_file_path, 'r', encoding='utf-8') as f:
    prompt_map = json.load(f)


def profession_to_prompt_from_map(profession: str) -> str | None:
    profession = profession.strip().lower()
    best_match = difflib.get_close_matches(profession, prompt_map.keys(), n=1, cutoff=0.8)
    if best_match:
        return prompt_map[best_match[0]]
    return None

def generate_prompt_with_openai(profession: str) -> str:
    try:
        client = OpenAI(api_key=openai_api_key)
        openai_prompt_text = f"Create a detailed, visually descriptive prompt for an image generation model depicting a professional working as a {profession}. Focus on their appearance, typical setting, and relevant objects. Make it suitable for generating a realistic image. Example: 'A confident doctor in a white coat, stethoscope around neck, standing in a hospital'."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates image prompts."},
                {"role": "user", "content": openai_prompt_text}
            ],
            max_tokens=100, 
            temperature=0.7
        )

        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            raise Exception("Empty response from OpenAI")

    except Exception as e:
        print(f"[OpenAI ERROR] {e}")
        return f"A professional working as a {profession.capitalize()} in a modern setting"


def extract_profession_from_transcript(transcript: str, potential_professions: list[str]) -> str | None:
    transcript_lower = transcript.lower()
    potential_professions_sorted = sorted(potential_professions, key=len, reverse=True)
    for profession_term in potential_professions_sorted:
        pattern = r"\b(?:a |an |the )?" + re.escape(profession_term.lower()) + r"(?:s)?\b"
        if re.search(pattern, transcript_lower):
            return profession_term
    return None

# Main function to generate the image prompt
def generate_image_prompt_from_transcript(transcript: str) -> str:
    if not transcript:
        return "A professional person in a work setting"

    potential_professions = list(prompt_map.keys())
    extracted_profession = extract_profession_from_transcript(transcript, potential_professions)

    if extracted_profession:
        prompt = profession_to_prompt_from_map(extracted_profession)
        if prompt:
            return prompt
        else:
            return generate_prompt_with_openai(extracted_profession, openai_api_key)
    else:
        return "A professional person in a work setting"






