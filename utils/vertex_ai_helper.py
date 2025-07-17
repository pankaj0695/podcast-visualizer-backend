import os
import tempfile
import base64
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.preview.vision_models import ImageGenerationModel

def setup_vertex_ai():
    """Set up Vertex AI credentials and return initialized model"""
    # Set up Vertex AI credentials
    credentials_base64 = os.environ.get("GOOGLE_CREDENTIALS_JSON_BASE64")
    if not credentials_base64:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON_BASE64 not found in environment variables")
    
    key_file_path = os.path.join(tempfile.gettempdir(), "key.json")
    with open(key_file_path, "w") as f:
        f.write(base64.b64decode(credentials_base64).decode("utf-8"))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path
    
    project_id = os.environ.get("GCP_PROJECT_ID")
    location = os.environ.get("LOCATION")
    vertexai.init(project=project_id, location=location)
    
    return GenerativeModel("gemini-2.5-flash")

def generate_content_with_vertex_ai(prompt):
    """Generate content using Vertex AI Gemini model"""
    model = setup_vertex_ai()
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_images_with_vertex_ai(prompts):
    """Generate images using Vertex AI Imagen model"""
    # Setup Vertex AI with specific project for image generation
    vertexai.init(project="massive-graph-465922-i8", location="us-central1")
    generation_model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-preview-06-06")
    
    generated_images = []
    for i, prompt in enumerate(prompts):
        try:
            images = generation_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="9:16",
                negative_prompt="",
                person_generation="allow_all",
                safety_filter_level="block_few",
                add_watermark=True,
            )
            # Save image locally
            image_path = f"ai_image_{i}.png"
            images[0].save(image_path)
            generated_images.append(image_path)
        except Exception as e:
            print(f"⚠️ Failed to generate image for prompt: {prompt[:50]}... Error: {e}")
            continue
    
    return generated_images
