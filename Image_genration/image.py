import replicate
import os
from PIL import Image
import requests
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()



api_token = os.getenv('REPLICATE_API_TOKEN')
if not api_token:
    raise ValueError("REPLICATE_API_TOKEN environment variable not set.")

def generate_image_with_photomaker(image_path: str, prompt: str, api_token: str) -> Image.Image:
    """
    Generates an image using the Replicate Photomaker model.

    Args:
        image_path: The local path to the input image.
        prompt: The text prompt for image generation.
        api_token: Your Replicate API token.

    Returns:
        A PIL Image object of the generated image.
    """
    # Pass the api_token directly to the client constructor
    client = replicate.Client(api_token=api_token)

    try:
        # Run the Replicate model
        output = client.run(
            "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a9570fe4",
            input={
                "prompt": f"imagine me {prompt} img", # Using f-string as in your provided code
                "num_steps": 40,
                "style_name": "Photographic (Default)",
                "input_image": open(image_path, "rb"),
                "num_outputs": 1,
                "guidance_scale": 5,
                "negative_prompt": "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
                "style_strength_ratio": 20
            }
        )

        # Get the URL of the generated image
        # The output is a list, and the first element is expected to be the URL
        if not output or not isinstance(output, list) or not output[0]:
             raise ValueError("Replicate API did not return a valid output URL.")

        output_url = output[0]

        # Ensure the output is a string URL
        if hasattr(output_url, 'url'):
             output_url = output_url.url
        elif not isinstance(output_url, str):
             raise TypeError(f"Expected output URL to be a string, but got {type(output_url)}")

        # Fetch the image from the URL
        response = requests.get(output_url)
        response.raise_for_status() # Raise an exception for bad status codes

        # Open the image using PIL
        img = Image.open(BytesIO(response.content))

        return img

    except Exception as e:
        print(f"An error occurred: {e}")
        # You might want to return None or raise the exception depending on how you want to handle errors
        return None

if __name__ == "__main__":

    your_image_path = r"C:\Users\panka\OneDrive\Desktop\Cograd\Proff_visualiser\data.jpg" # Replace with your image path
    your_prompt = "a person becoming a doctor" # Replace with your desired prompt

    # Pass the retrieved api_token to the function
    generated_image = generate_image_with_photomaker(image_path=your_image_path, prompt=your_prompt, api_token=api_token)

    if generated_image:
        # You can display the image
        # generated_image.show()

        # Or save the image
        generated_image.save("generated_image_function.jpg")
        print("Image saved as generated_image_function.jpg")
    else:
        print("Image generation failed.")
