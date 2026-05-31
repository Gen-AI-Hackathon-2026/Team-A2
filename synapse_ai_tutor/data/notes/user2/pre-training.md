# Pre-training

## Definition
Pre‑training is a self‑supervised learning stage where a neural network is exposed to a large, unlabeled corpus to learn general linguistic or domain‑specific representations. The model optimizes a proxy objective (e.g., masked language modeling, next‑token prediction) before being fine‑tuned on a downstream supervised task. This two‑step paradigm leverages vast amounts of data to reduce the need for labeled examples.

## Why It Matters
- **Data Efficiency**: By learning rich representations from unlabeled data, models require far fewer labeled samples to achieve state‑of‑the‑art performance on specific tasks.  
- **Transferability**: Pre‑trained weights capture universal language patterns that can be adapted to diverse downstream tasks (classification, generation, question answering).  
- **Robustness & Generalization**: Self‑supervised objectives expose the model to varied contexts, improving its ability to generalize to unseen data and reducing overfitting.

## Example
A common pre‑training pipeline is **Masked Language Modeling (MLM)** used by BERT. Below is a minimal example using Hugging Face’s `transformers` library to pre‑train a tiny BERT‑style model on a synthetic dataset.

```python
import torch
from transformers import BertTokenizer, BertForMaskedLM, DataCollatorForLanguageModeling
from datasets import load_dataset

# Load a toy dataset (replace with a real corpus)
dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train[:1%]")

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
tokenizer.add_special_tokens({"pad_token": "[PAD]"})

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
tokenized_datasets.set_format(type="torch", columns=["input_ids", "attention_mask"])

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)

model = BertForMaskedLM.from_pretrained("bert-base-uncased")
model.resize_token_embeddings(len(tokenizer))

# Training loop (simplified)
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
model.train()

for epoch in range(3):
    for batch in torch.utils.data.DataLoader(tokenized_datasets, batch_size=8, shuffle=True, collate_fn=data_collator):
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
    print(f"Epoch {epoch+1} loss: {loss.item():.4f}")
```

*Note*: In practice, pre‑training is performed on billions of tokens with distributed training; the code above is illustrative.

## Common Mistakes
1. **Treating Pre‑training as a One‑Off** – Assuming a single pre‑training run suffices for all downstream domains; in reality, domain adaptation or continual pre‑training often yields better results.  
2. **Ignoring the Proxy Objective** – Using a poorly chosen self‑supervised task (e.g., trivial token masking) that fails to capture useful linguistic structure.  
3. **Overfitting on Small Corpora** – Pre‑training on a limited dataset without regularization can lead to memorization rather than generalization.

## Connected Concepts
- **Transfer Learning** → Pre‑training supplies a strong initialization that is fine‑tuned on target tasks.  
- **Self‑Supervised Learning** → The core principle behind pre‑training; models learn from the data itself without labels.  
- **Domain Adaptation** → Techniques like continued pre‑training on domain‑specific corpora to bridge distribution gaps.  
- **Continual Learning** → Extending pre‑training to sequentially incorporate new data while retaining prior knowledge.  
- **Language Model Fine‑Tuning** → The downstream stage where pre‑trained weights are adapted to a specific supervised objective.

## Resources
1. **“BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding”** – Devlin et al., 2019.  
2. **“Don’t Stop Pretraining: Adapt Language Models to Domains and Tasks”** – Gururangan et al., 2020.  
3. **Hugging Face Transformers Documentation** – Comprehensive tutorials on pre‑training and fine‑tuning pipelines.

## Summary
Pre‑training equips language models with universal representations by leveraging massive unlabeled corpora through self‑supervised objectives. This foundation dramatically improves data efficiency and generalization for downstream tasks, making it a cornerstone of modern NLP pipelines.