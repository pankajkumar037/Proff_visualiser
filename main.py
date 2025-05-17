from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from openai import OpenAI
from dotenv import load_dotenv
import logging

from Prompts.prompt import generate_image_prompt_from_transcript
from Image_generation.image import generate_image_with_photomaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/")
async def read_root():
    return {"message": "FastAPI backend is running"}

@app.post("/generate_visualization/")
async def generate_visualization(image_file: UploadFile = File(...), audio_file: UploadFile = File(...)):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)

    image_path = os.path.join(temp_dir, image_file.filename)
    audio_path = os.path.join(temp_dir, audio_file.filename)

    try:
        # Save uploaded files
        logger.info(f"Saving uploaded files: {image_file.filename}, {audio_file.filename}")
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # Transcription using Whisper
        logger.info("Starting audio transcription")
        try:
            with open(audio_path, "rb") as audio_file:
                transcription_response = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            transcript = transcription_response.text
            logger.info(f"Transcription successful: {transcript}")
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")

        # Generate prompt
        logger.info("Generating prompt from transcript")
        try:
            prompt = generate_image_prompt_from_transcript(transcript)
            print(prompt)
            logger.info(f"Generated prompt: {prompt}")
        except Exception as e:
            logger.error(f"Prompt generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")

        # Generate image
        logger.info("Generating image")
        try:
            generated_image_path = generate_image_with_photomaker(image_path=image_path, prompt=prompt)
            logger.info(f"Image generated at: {generated_image_path}")
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")

        # Return generated image
        if generated_image_path and os.path.exists(generated_image_path):
            return FileResponse(generated_image_path, media_type="image/png")
        else:
            raise HTTPException(status_code=500, detail="Generated image file not found")

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        # Cleanup temporary files
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}") 