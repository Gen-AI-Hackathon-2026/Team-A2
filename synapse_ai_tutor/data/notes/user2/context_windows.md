# Context Windows

## Definition
A *context window* is the finite set of tokens (words, subwords, or symbols) that a model processes at one time to produce predictions or representations. In transformer‑based architectures, the window is typically defined by the maximum sequence length the model can attend to, while in recurrent or convolutional models it is governed by the receptive field or hidden state. Advanced models extend this notion to *dynamic* or *hierarchical* windows that adapt to document length or capture long‑range dependencies via memory or sparse attention.

## Why It Matters
- **Computational feasibility**: Transformers scale quadratically with sequence length; a bounded window keeps memory and time within limits.
- **Model expressiveness**: The window size determines the extent of contextual information a token can leverage, directly affecting tasks like language modeling, translation, or question answering.
- **Architectural innovation**: Techniques such as sliding windows, segment‑level recurrence, or sparse attention have driven the design of long‑document models (Longformer, Reformer, Performer), enabling practical handling of thousands of tokens.

## Example
Below is a minimal illustration of a sliding‑window attention mechanism in PyTorch, where each token attends only to a fixed window of its neighbors:

```python
import torch
import torch.nn as nn

class SlidingWindowAttention(nn.Module):
    def __init__(self, dim, window_size=5):
        super().__init__()
        self.window_size = window_size
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.out = nn.Linear(dim, dim)

    def forward(self, x):
        B, L, D = x.shape
        qkv = self.qkv(x).reshape(B, L, 3, D).permute(2, 0, 1, 3)
        q, k, v = qkv[0], qkv[1], qkv[2]

        # Pad for left/right windows
        pad = self.window_size // 2
        k_padded = torch.nn.functional.pad(k, (0,0,pad,pad))
        v_padded = torch.nn.functional.pad(v, (0,0,pad,pad))

        # Gather local windows
        k_windows = k_padded.unfold(1, self.window_size, 1)  # (B, L, W, D)
        v_windows = v_padded.unfold(1, self.window_size, 1)

        # Compute scaled dot‑product
        attn = torch.einsum('bld,bldw->blw', q, k_windows) / (D**0.5)
        attn = torch.softmax(attn, dim=-1)

        # Weighted sum of values
        out = torch.einsum('blw,bldw->bld', attn, v_windows)
        return self.out(out)

# Demo
x = torch.randn(2, 10, 64)  # batch, seq_len, dim
model = SlidingWindowAttention(64, window_size=5)
y = model(x)
print(y.shape)  # torch.Size([2, 10, 64])
```

This snippet shows how a fixed context window can be enforced in a transformer‑style attention layer, trading off full‑sequence context for computational tractability.

## Common Mistakes
1. **Assuming a larger window always improves performance** – Beyond a certain size, additional tokens may introduce noise or dilute attention, especially when the model is not trained to exploit long‑range dependencies.
2. **Neglecting positional encoding in windowed models** – Sliding windows can break the model’s ability to infer absolute positions unless relative or segment‑aware encodings are incorporated.
3. **Treating window size as a static hyperparameter** – Many advanced architectures adapt the window size dynamically (e.g., via hierarchical attention or memory‑augmented recurrence); fixing it can severely limit expressiveness.

## Connected Concepts
- **Sliding Window** → A technique that shifts a fixed‑size window across a sequence to compute local attention or convolutions.
- **Sparse Attention** → Reduces quadratic complexity by restricting attention to a subset of token pairs (e.g., block‑sparse, locality‑aware).
- **Relative Positional Encoding** → Encodes distances between tokens rather than absolute positions, enabling models to generalize across varying window sizes.
- **Memory‑Augmented Models** (e.g., Transformer‑XL, Compressive Transformer) → Store past hidden states beyond the current window, allowing recurrence over long sequences.
- **Segment‑Level Recurrence** → Aggregates information at a coarser granularity (e.g., sentence or paragraph) to extend effective context without increasing per‑token window size.

## Resources
1. **“Longformer: The Long‑Document Transformer”** – Beltagy et al., 2020. Introduces a sliding‑window attention pattern for long documents.
2. **“Transformer‑XL: Attentive Language Models Beyond a Fixed-Length Context”** – Dai et al., 2019. Presents recurrence and relative positional embeddings to extend context.
3. **“The Illustrated Transformer”** – Jay Alammar. A visual guide that explains attention windows, positional encodings, and extensions.

## Summary
Context windows define the scope of information a model can attend to at any step, balancing computational cost against expressive power. Advanced architectures employ dynamic, sparse, or memory‑augmented windows to handle long sequences, but careful design of positional encodings and window strategies is essential to avoid pitfalls. Understanding and manipulating context windows is thus central to building scalable, high‑performance language models.