# Professional Visualization Generator

This application allows users to upload their photo and an audio recording of their desired profession, and generates a visualization of them in that professional role using AI.

## Features

- Audio transcription using OpenAI's Whisper API
- Professional prompt generation based on transcribed text
- Image generation using PhotoMaker
- FastAPI backend with CORS support
- Simple web interface for testing

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pankajkumar037/Proff_visualiser.git
cd Proff_visualiser
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
REPLICATE_API_TOKEN=your_api_key_here
```

## Project Structure

```
.
├── main.py                 # FastAPI backend
├── app.py                  # Alternative FastAPI implementation
├── Prompts/
│   └── prompt.py          # Prompt generation logic
├── Image_generation/
│   └── image.py           # Image generation logic
├── requirements.txt       # Python dependencies
├── prompt_map.json       # Mapping of professions to prompts

```

## Usage

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Open the test interface:
   
     python -m http.server 8080
     ```
     Then open `http://localhost:8080` in your browser

3. Using the interface:
   - Upload a photo of yourself
   - Upload an audio recording (e.g., saying "I want to be a doctor")
   - Click "Generate Visualization"
   - Wait for the processing to complete
   - View the generated image

## API Endpoints

### POST /generate_visualization/
Accepts multipart form data with:
- `image_file`: Photo of the user
- `audio_file`: Audio recording

Returns:
- Generated image file

## Error Handling

The application includes comprehensive error handling for:
- File upload issues
- Audio transcription errors
- Prompt generation failures
- Image generation problems

## Development

To modify the application:

1. Backend (FastAPI):
   - Edit `main.py` for API endpoints
   - Modify `Prompts/prompt.py` for prompt generation logic
   - Update `Image_generation/image.py` for image generation


