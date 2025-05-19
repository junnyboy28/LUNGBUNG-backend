from torchvision import transforms
import torch
import numpy as np

def transform_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(image).unsqueeze(0)

def generate_report(model, image, vocab_info, device, max_length=100):
    model.eval()
    with torch.no_grad():
        features = model.encoder(image.to(device))
    
    word2idx = vocab_info['word2idx']
    idx2word = vocab_info['idx2word']
    
    sampled_ids = []
    inputs = torch.tensor([word2idx['<START>']]).unsqueeze(0).to(device)
    
    for i in range(max_length):
        outputs = model.decoder(features, inputs)
        _, predicted = outputs.max(2)
        sampled_ids.append(predicted[:, -1].item())
        inputs = torch.cat((inputs, predicted[:, -1].unsqueeze(1)), dim=1)
        if sampled_ids[-1] == word2idx['<END>']:
            break
    
    sampled_caption = []
    for word_id in sampled_ids:
        word = idx2word[word_id]
        if word not in ['<START>', '<END>', '<PAD>']:
            sampled_caption.append(word)
    
    return ' '.join(sampled_caption)

def generate_summary(model, tokenizer, report, device, max_length=100):
    input_text = f"summarize: {report}"
    input_ids = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).input_ids.to(device)
    
    outputs = model.generate(
        input_ids,
        max_length=max_length,
        num_beams=4,
        early_stopping=True
    )
    
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary

def generate_suggestions(model, vectorizer, summary):
    features = vectorizer.transform([summary])
    suggestions = model.predict(features)[0] 
    return suggestions