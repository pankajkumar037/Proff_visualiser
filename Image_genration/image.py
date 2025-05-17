import replicate
import os
from PIL import Image
import requests
from io import BytesIO
from dotenv import load_dotenv
import uuid

load_dotenv()

api_token = os.getenv('REPLICATE_API_TOKEN')
if not api_token:
    raise ValueError("REPLICATE_API_TOKEN environment variable not set.")

def generate_image_with_photomaker(
    image_path: str,
    prompt: str,
    output_dir: str = "output"
) -> str | None:

    client = replicate.Client(api_token=api_token)

    try:
        print("Calling Replicate API...")
        output = client.run(
            "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
            input={
                "prompt": f"imagine me {prompt} img",
                "num_steps": 40,
                "style_name": "Photographic (Default)",
                "input_image": open(image_path, "rb"),
                "num_outputs": 1,
                "guidance_scale": 5,
                "negative_prompt": "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
                "style_strength_ratio": 20
            }
        )
        print("Replicate API call successful.")

        if not output or not isinstance(output, list) or not output[0]:
             raise ValueError("Replicate API did not return a valid output URL.")

        output_url = output[0]
        print(f"Generated image URL: {output_url}")

        if hasattr(output_url, 'url'):
             output_url = output_url.url
        elif not isinstance(output_url, str):
             raise TypeError(f"Expected output URL to be a string, but got {type(output_url)}")

        print("Fetching image from URL...")
        response = requests.get(output_url)
        response.raise_for_status()
        print("Image fetched successfully.")

        img = Image.open(BytesIO(response.content))

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        filename = f"generated_image_{uuid.uuid4().hex}.jpg"
        output_path = os.path.join(output_dir, filename)

        img.save(output_path)
        print(f"Image saved to: {output_path}")

        return output_path

    except Exception as e:
        print(f"An error occurred during image generation or saving: {e}")
        return None

# if __name__ == "__main__":

#     your_image_path = r"C:\Users\panka\OneDrive\Desktop\Cograd\Proff_visualiser\data.jpg"
#     your_prompt = "a person becoming a doctor"
#     your_output_directory = "generated_images"

#     print(f"Attempting to generate image for prompt: '{your_prompt}' using image: '{your_image_path}'")

#     generated_image_path = generate_image_with_photomaker(
#         image_path=your_image_path,
#         prompt=your_prompt
#     )

#     if generated_image_path:
#         print(f"Successfully generated and saved image to: {generated_image_path}")
#         try:
#             saved_img = Image.open(generated_image_path)
#         except FileNotFoundError:
#             print(f"Error: Saved image file not found at {generated_image_path}")
#         except Exception as e:
#             print(f"Error opening saved image: {e}")

#     else:
#         print("Image generation failed.")
