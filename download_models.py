import os
import gdown
import sys

def download_models():
    """Download models from Google Drive during deployment"""
    print("Creating model directories...")
    os.makedirs("models/model_checkpoints", exist_ok=True)
    os.makedirs("models/t5_model", exist_ok=True)
    os.makedirs("models/t5_tokenizer", exist_ok=True)
    
    print("Downloading model checkpoints...")
    gdown.download_folder(
        "https://drive.google.com/drive/folders/1tC40x5P7mXNUZfZNTr1n5tFYZU7rUMmP",
        output="models/model_checkpoints", 
        quiet=False
    )
    
    print("Downloading T5 model...")
    gdown.download_folder(
        "https://drive.google.com/drive/folders/1bAw7NDjKQsy8ySwju0HIEWu7JignED3Y",
        output="models/t5_model", 
        quiet=False
    )
    
    print("Downloading T5 tokenizer...")
    gdown.download_folder(
        "https://drive.google.com/drive/folders/13QY2Mc33IF-Pmv42FIU3zbrfsh1KoFXj",
        output="models/t5_tokenizer", 
        quiet=False
    )
    
    print("✅ All models downloaded successfully!")

if __name__ == "__main__":
    download_models()