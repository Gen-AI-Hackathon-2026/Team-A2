# Transformers

## Definition
Transformers are a class of neural network architectures that rely exclusively on self‑attention mechanisms to process sequences, eschewing recurrence and convolution. They map an input sequence to an output sequence in parallel, enabling massive parallelization and long‑range dependency modeling. The core building block, the Transformer encoder or decoder layer, stacks multi‑head self‑attention with position‑wise feed‑forward networks, all wrapped in residual connections and layer normalization.

## Why It Matters
- **Scalability & Parallelism**: Self‑attention allows all token pairs to be processed simultaneously, making Transformers highly GPU‑efficient and enabling training on billions of parameters.  
- **Long‑Range Context**: Unlike RNNs, Transformers can attend to any token in the sequence regardless of distance, which is crucial for tasks like document summarization or code generation.  
- **Foundation for LLMs**: Modern large language models (GPT‑4, PaLM, LLaMA) are built on Transformer backbones; understanding them is essential to innovate or debug these systems.

## Example
A minimal token‑by‑token generation loop using Hugging Face’s `transformers` library, illustrating the autoregressive nature of decoder‑only Transformers.

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "gpt2-medium"          # 345M parameters
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

prompt = "The quick brown fox"
input_ids = tokenizer(prompt, return_tensors="pt").input_ids

generated = input_ids.clone()
max_new_tokens = 20

for _ in range(max_new_tokens):
    outputs = model(generated)
    next_token_logits = outputs.logits[:, -1, :]
    # Greedy decoding
    next_token_id = torch.argmax(next_token_logits, dim=-1, keepdim=True)
    generated = torch.cat([generated, next_token_id], dim=-1)

print(tokenizer.decode(generated[0], skip_special_tokens=True))
```

*What it shows*: Each iteration appends the newly predicted token to the prompt and re‑feeds the entire sequence to the model—exactly how Transformer LLMs generate text.

## Common Mistakes
1. **Assuming Transformers are inherently sequential** – They process all positions in parallel; the autoregressive behavior only appears during inference, not training.  
2. **Neglecting positional encodings** – Without them, the model cannot distinguish token order, leading to meaningless outputs.  
3. **Overlooking the quadratic memory cost** – Self‑attention scales as *O(n²)* in sequence length; many practitioners ignore this when working with very long inputs.

## Connected Concepts
- **Self‑Attention** → The core operation that lets each token weigh every other token’s contribution.  
- **Multi‑Head Attention** → Parallel attention heads capture diverse relational patterns.  
- **Positional Encoding** → Injects sequence order into token embeddings, enabling order awareness.  
- **Layer Normalization & Residual Connections** → Stabilize training and allow deeper stacks.  
- **Decoder‑Only vs Encoder‑Decoder** → Different architectural variants (GPT vs BERT/Seq2Seq) tailored to generation or understanding tasks.

## Resources
1. **"Attention Is All You Need" (Vaswani et al., 2017)** – The seminal paper introducing the Transformer architecture.  
2. **"The Illustrated Transformer" (Jay Alammar)** – A visual, intuitive walkthrough of the model’s components.  
3. **Hugging Face Course – Transformers** – Practical tutorials and code labs for building and fine‑tuning Transformer models.

## Summary
Transformers revolutionized sequence modeling by replacing recurrence with self‑attention, enabling efficient parallel training and capturing long‑range dependencies. Their architecture underpins today’s state‑of‑the‑art language models, making a deep understanding of attention, positional encoding, and the decoder‑only paradigm essential for advanced AI research and applications.