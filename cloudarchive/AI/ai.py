from diffusers import StableDiffusionPipeline
import torch
import base64
import io

# Инициализация модели
model_id = "CompVis/stable-diffusion-v1-4"
pipeline = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipeline.enable_xformers_memory_efficient_attention()
pipeline = pipeline.to("cuda")

def generate_image(prompt):
    # Генерация изображения
    image = pipeline(prompt, height=512, width=512).images[0]
    
    # Преобразуем изображение в формат base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return img_str