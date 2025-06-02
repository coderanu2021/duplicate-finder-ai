import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

class DocumentClassifier(nn.Module):
    def __init__(self, model_name="bert-base-uncased", num_classes=2):
        super(DocumentClassifier, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(pooled_output)
        return logits
    
    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.forward(inputs["input_ids"], inputs["attention_mask"])
        return torch.softmax(outputs, dim=1) 