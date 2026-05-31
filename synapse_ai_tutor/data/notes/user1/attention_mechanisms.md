# Attention Mechanisms

## Definition  
Attention mechanisms let a model weigh the relevance of each element in an input sequence when computing the representation for a target token. In practice, this is realized by computing a set of **query**, **key**, and **value** vectors, scoring each key against the query (often via a scaled dot‑product), normalizing the scores with softmax, and forming a weighted sum of the values. The resulting context vector is then combined with the query to produce the output for the current position.

## Why It Matters  
- **Captures Long‑Range Dependencies**: Unlike fixed‑size hidden states in RNNs, attention can directly connect distant tokens, enabling efficient modeling of long‑range relationships.  
- **Parallelizable**: Attention operates on all positions simultaneously, allowing full GPU parallelism and drastically faster training than sequential RNNs.  
- **Interpretability & Debugging**: Attention weights can be visualized to understand which tokens influence a prediction, aiding model debugging and trust.

## Example  
Below is a minimal PyTorch implementation of a single‑head scaled dot‑product attention layer, followed by a quick test on a toy sequence.

```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(q, k, v, mask=None):
    """
    q, k, v: tensors of shape (batch, seq_len, dim)
    mask: optional mask of shape (batch, seq_len, seq_len)
    """
    d_k = q.size(-1)
    scores = torch.matmul(q, k.transpose(-2, -1)) / d_k**0.5  # (batch, seq_len, seq_len)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    attn_weights = F.softmax(scores, dim=-1)
    return torch.matmul(attn_weights, v), attn_weights

# Toy data
batch, seq_len, dim = 2, 5, 4
q = torch.randn(batch, seq_len, dim)
k = torch.randn(batch, seq_len, dim)
v = torch.randn(batch, seq_len, dim)

context, attn = scaled_dot_product_attention(q, k, v)
print("Context shape:", context.shape)          # (2, 5, 4)
print("Attention shape:", attn.shape)          # (2, 5, 5)
```

In a Transformer encoder, this single‑head attention is replicated across multiple heads (`MultiHeadAttention`) and stacked with feed‑forward layers, layer normalization, and residual connections.

## Common Mistakes  
1. **Ignoring the Scaling Factor** – Forgetting to divide by √d_k leads to vanishing gradients for large dimensions.  
2. **Treating Attention as a Memory Module** – Attention does not store past states; it re‑weights the current input representations.  
3. **Assuming More Heads Always Help** – Adding heads without enough data or proper regularization can cause over‑parameterization and degrade performance.

## Connected Concepts  
- **Transformer Architecture** → The entire model is built around stacked self‑attention and feed‑forward sub‑layers.  
- **Positional Encoding** → Supplies order information that attention alone cannot capture.  
- **Multi‑Head Attention** → Parallel attention heads allow the model to attend to different sub‑spaces simultaneously.  
- **Causal (Masked) Attention** → Enforces autoregressive generation by masking future tokens.  
- **Relative Position Attention** → Augments absolute positional encodings to better generalize to longer sequences.

## Resources  
1. **“Attention Is All You Need”** – Vaswani et al., 2017 (original Transformer paper).  
2. **The Illustrated Transformer** – Jay Alammar (blog + visualizations).  
3. **“Transformers: State-of-the-Art NLP”** – Lewis, Liu, & Goyal, 2020 (book chapter on attention).  

## Summary  
Attention mechanisms transform sequence modeling by letting each token dynamically focus on relevant parts of the input. They provide parallelism, long‑range context, and interpretability, forming the core of modern architectures like Transformers. Mastering attention—including its scaling, multi‑head variants, and positional strategies—is essential for building state‑of‑the‑art NLP and vision models.