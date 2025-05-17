from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from openai import OpenAI
from dotenv import load_dotenv

from Prompts.prompt import generate_image_prompt_from_transcript
from Image_generation.image import generate_image_with_photomaker

load_dotenv()
app = FastAPI()

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
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
    except Exception as e:
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=f"Error saving uploaded files: {e}")

    # --- Transcription using Whisper ---
    transcript = ""
    try:
        with open(audio_path, "rb") as audio_file:
            transcription_response = client.audio.transcriptions.create(
                 file=audio_file,
                model="whisper-1",
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
        transcript = transcription_response.text

       
    except Exception as e:
        # Clean up temporary files and directory in case of error
        os.remove(image_path)
        os.remove(audio_path)
        os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=f"Error during transcription: {e}")

    # --- Generate Prompt ---
    prompt = ""
    try:
        prompt = generate_image_prompt_from_transcript(transcript)
      

    except Exception as e:
        # Clean up temporary files and directory in case of error
        os.remove(image_path)
        os.remove(audio_path)
        os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=f"Error generating prompt: {e}")


    
    generated_image_path = None
    try:
        generated_image_path = generate_image_with_photomaker(image_path=image_path, prompt=prompt)
      
    except Exception as e:
        os.remove(image_path)
        os.remove(audio_path)
        os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail=f"Error generating image: {e}")

    
    if generated_image_path and os.path.exists(generated_image_path):
        
        @app.after_request
        def cleanup(response):
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except OSError as e:
                    print(f"Error cleaning up directory {temp_dir}: {e}")
            return response

        return FileResponse(generated_image_path, media_type="image/png") # Adjust media_type as needed
    else:
        # Clean up temporary files and directory
        if os.path.exists(image_path): # In case simulation didn't overwrite image_path
             os.remove(image_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(temp_dir):
             os.rmdir(temp_dir)
        raise HTTPException(status_code=500, detail="Failed to generate or find image.")

    

        raise HTTPException(status_code=500, detail="Failed to generate or find image.") 