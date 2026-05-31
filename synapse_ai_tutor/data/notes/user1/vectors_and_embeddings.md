# Vectors & Embeddings

## Definition  
Vectors are ordered lists of numbers that can represent data in a numerical form.  
Embeddings are special vectors produced by machine‑learning models that capture the meaning of words, sentences, or whole documents in a way that similar items have similar vectors.

## Why It Matters  
- **Machine‑learning ready:** Algorithms need numbers; embeddings translate text into numbers that models can process.  
- **Semantic similarity:** Two sentences that mean the same thing will have close embeddings, enabling tasks like search, clustering, or recommendation.  
- **Efficiency:** Dense vectors (e.g., 300‑dimensional) are compact compared to sparse one‑hot encodings, speeding up training and inference.

## Example  
Below is a simple example using the `sentence-transformers` library to embed two sentences and compute their cosine similarity.

```python
# Install the library (run once)
# pip install sentence-transformers

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load a pre‑trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Sentences to embed
sentences = [
    "The cat sits on the mat.",
    "A feline is resting on a rug."
]

# Get embeddings (shape: [2, 384])
embeddings = model.encode(sentences)

# Compute cosine similarity
sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
print(f"Cosine similarity: {sim:.3f}")   # e.g., 0.93 → very similar
```

**What happens?**  
1. Each sentence is turned into a 384‑dimensional vector.  
2. The dot product of the two vectors (after normalizing) gives a score between –1 and 1; higher means more similar.

## Common Mistakes  
1. **Thinking embeddings are interpretable word‑by‑word** – the numbers themselves don’t have obvious meanings; they’re just useful for math.  
2. **Using too few dimensions** – low‑dimensional embeddings may lose nuance; too many can be noisy and slow.  
3. **Assuming embeddings are always perfect** – they’re learned from data, so biases or errors in training data can affect them.

## Connected Concepts  
- **Word Embedding** → Represents individual words (e.g., Word2Vec, GloVe).  
- **Sentence/Document Embedding** → Encodes longer texts; often built on top of word embeddings or directly by transformer models.  
- **Cosine Similarity** → A common distance metric to compare embeddings.  
- **Dimensionality Reduction** → Techniques like PCA or t‑SNE help visualize high‑dimensional embeddings.  
- **Attention Mechanism** → Learns which parts of a sentence are important, producing context‑aware embeddings in transformers.

## Resources  
1. **Book:** *Natural Language Processing with Python* (O’Reilly) – chapters on vector space models.  
2. **Tutorial:** Hugging Face “Embeddings” guide – step‑by‑step examples in Python.  
3. **Paper:** “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding” – foundational for modern sentence embeddings.

## Summary  
Vectors convert text into numbers; embeddings are learned vectors that preserve meaning, enabling similarity calculations and efficient machine‑learning processing. By understanding how to generate and use embeddings, beginners can unlock powerful NLP capabilities.