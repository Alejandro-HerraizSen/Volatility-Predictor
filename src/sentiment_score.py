from transformers import BertTokenizer, BertForSequenceClassification
import torch

tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

labels = ["neutral","positive", "negative"]

def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

    predicted_class = torch.argmax(probs, dim=1).item()
    sentiment = labels[predicted_class]
    confidence = probs[0][predicted_class].item()

    return sentiment, confidence, probs[0].tolist()

if __name__ == "__main__":
    test_sentences = [
        "We delivered strong revenue growth this quarter.",
        "Margin improved and we are raising guidance.",
        "We face serious macroeconomic uncertainty.",
        "Demand remains stable."
    ]

    for text in test_sentences:
        sentiment, confidence, raw_probs = analyze_sentiment(text)
        print(f"\nText: {text}")
        print("Sentiment:", sentiment)
        print("Confidence:", confidence)
        print("Raw probabilities:", raw_probs)