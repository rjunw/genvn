# ------------------------------------------------------------------------
# MultiModal Embeddings
# ------------------------------------------------------------------------

import torch 
from transformers import AutoProcessor, AutoModel, AutoTokenizer
from torchvision import transforms 
from PIL import Image

class ImageTextEmbedder:
    def __init__(self, model_id: str, device: str = "cpu"):
        self.model_id = model_id

        try:
            self.processor = AutoProcessor.from_pretrained(model_id)
            self.model = AutoModel.from_pretrained(model_id).to(device)
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.device = device
        except Exception as e:
            print(f"Failed to load model: {e}")

    def embed_image(self, image):
        with torch.no_grad():
            inputs = self.processor(
                images = image,
                return_tensors="pt"
            )
            image_embeddings = self.model.get_image_features(**inputs)
            return image_embeddings

    def embed_text(self, text):
        with torch.no_grad():
            inputs = self.tokenizer(
                [text],
                return_tensors="pt"
            )
            text_embeddings = self.model.get_text_features(**inputs)
            return text_embeddings

class AudioTextEmbedder:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModel.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

    def embed_audio(self, audio):
        pass

    def embed_text(self, text):
        pass

if __name__ == "__main__":
    model_id = "google/siglip2-large-patch16-256"
    embedder = ImageTextEmbedder(model_id=model_id, device="cpu")


    image_1 = Image.open("backend/data/assets/bg/uncle_mugen_bg/pack1/Assorted/kitchen_day.webp").convert('RGB')
    image_embedding_1 = embedder.embed_image(image_1)
    print(image_embedding_1.shape)

    image_2 = Image.open("backend/data/assets/bg/uncle_mugen_bg/pack1/Assorted/Janet Lim Napoles International Airport.webp").convert('RGB')
    image_embedding_2 = embedder.embed_image(image_2)

    text_1 = "kitchen"
    text_embedding_1 = embedder.embed_text(text_1)
    print(text_embedding_1.shape)

    text_2 = "airport"
    text_embedding_2 = embedder.embed_text(text_2)

    # calculate cosine similarity for kitchen
    similarity_1 = torch.nn.functional.cosine_similarity(image_embedding_1, text_embedding_1)
    similarity_2 = torch.nn.functional.cosine_similarity(image_embedding_1, text_embedding_2)
    print(f"KITCHEN:\n{text_1}: {similarity_1}, {text_2}: {similarity_2}")

    # calculate cosine similarity for airport
    similarity_1 = torch.nn.functional.cosine_similarity(image_embedding_2, text_embedding_1)
    similarity_2 = torch.nn.functional.cosine_similarity(image_embedding_2, text_embedding_2)
    print(f"AIRPORT:\n{text_1}: {similarity_1}, {text_2}: {similarity_2}")

    