import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

class RiskEngine:
    def __init__(self):
        # Using ProsusAI/finbert for domain-specific financial sentiment
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        
        self.event_keywords = {
            "Geopolitical": ["war", "sanctions", "tariff", "conflict", "geopolitical", "election"],
            "Macroeconomic": ["inflation", "interest rate", "fed", "recession", "gdp", "central bank"],
            "Credit Event": ["default", "downgrade", "bankruptcy", "debt", "liquidity crisis"],
            "Merger/Acquisition": ["acquisition", "merger", "buyout", "takeover", "deal"],
            "Product Launch": ["launch", "unveil", "product", "innovation", "release"]
        }

    def analyze_text(self, text: str, company: str = "Market") -> dict:
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1).detach().numpy()[0]
        
        # Labels: [positive, negative, neutral]
        sentiment_score = float(probs[0] - probs[1])  # Range: -1.0 to 1.0
        
        # Event Classification (Keyword matching fallback / zero-shot equivalent)
        text_lower = text.lower()
        detected_event = "General Market"
        for event, keywords in self.event_keywords.items():
            if any(k in text_lower for k in keywords):
                detected_event = event
                break
                
        # Impact Score Calculation (1 to 10 scale based on sentiment magnitude and risk event presence)
        base_impact = abs(sentiment_score) * 7
        event_weight = 3.0 if detected_event in ["Geopolitical", "Credit Event"] else 1.5
        impact_score = min(10.0, round(base_impact + event_weight, 1))

        return {
            "company": company,
            "text": text,
            "sentiment_score": round(sentiment_score, 3),
            "event_classification": detected_event,
            "impact_score": impact_score
        }