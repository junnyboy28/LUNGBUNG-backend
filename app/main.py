from fastapi import FastAPI, File, UploadFile
from PIL import Image
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import pickle
from fastapi.middleware.cors import CORSMiddleware

from .models import XrayReportGenerator, CNNEncoder, TransformerDecoder
from .utils import transform_image, generate_report, generate_summary, generate_suggestions

# Load models and necessary components
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load report generation model
with open("models/model_checkpoints/vocab_info.pkl", "rb") as f:
    vocab_info = pickle.load(f)

encoder = CNNEncoder(embed_size=256).to(device)
decoder = TransformerDecoder(embed_size=256, hidden_size=512, vocab_size=vocab_info["vocab_size"]).to(device)

encoder.load_state_dict(torch.load("models/model_checkpoints/encoder.pth", map_location=device))
decoder.load_state_dict(torch.load("models/model_checkpoints/decoder.pth", map_location=device))

report_generator = XrayReportGenerator(encoder, decoder)
report_generator.eval()

# Load summarization model (T5)
t5_tokenizer = T5Tokenizer.from_pretrained("models/t5_tokenizer")
t5_model = T5ForConditionalGeneration.from_pretrained("models/t5_model").to(device)

# Load suggestions model
with open("models/model_checkpoints/suggestions.pkl", "rb") as f:
    suggestions_data = pickle.load(f)
suggestions_model = suggestions_data["model"]
suggestions_vectorizer = suggestions_data["vectorizer"]

app = FastAPI()

# Add this after creating your FastAPI app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://lungbung-frontend.vercel.app/"],  # Add your deployed URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_report(report_text):
    # Replace UNK tokens with more appropriate words or remove them
    cleaned_text = report_text.replace(" <UNK>", "")
    # Additional cleaning as needed
    return cleaned_text

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # 1. Open and transform the image
    image = Image.open(file.file).convert("RGB")
    transformed_image = transform_image(image)

    # 2. Generate X-ray report
    report = generate_report(report_generator, transformed_image, vocab_info, device)

    # 3. Generate summary from report
    summary = generate_summary(t5_model, t5_tokenizer, report, device)

    # 4. Generate suggestions from summary
    suggestions = generate_suggestions(suggestions_model, suggestions_vectorizer, summary)

    return {"report": report, "summary": summary, "suggestions": suggestions}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}