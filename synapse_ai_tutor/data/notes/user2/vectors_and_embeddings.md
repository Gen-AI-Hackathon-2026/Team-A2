# Vectors & Embeddings

## Definition  
Vectors are ordered lists of numbers that represent data in a mathematical space.  
Embeddings are special vectors that encode the meaning of words, sentences, or whole documents so that similar items lie close together in that space.

## Why It Matters  
- **Feature representation** – Machine learning models need numeric input; embeddings turn text into usable features.  
- **Semantic similarity** – Distance or similarity between embeddings lets us find related words or documents.  
- **Transfer learning** – Pre‑trained embeddings capture knowledge from large corpora, boosting performance on downstream tasks with little data.

## Example  
Below we use the `sentence-transformers` library to embed two sentences and compute their cosine similarity.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load a pre‑trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = ["The cat sits on the mat.", "A dog is sleeping on the rug."]
embeddings = model.encode(sentences)

# Compute cosine similarity
def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

sim = cosine_sim(embeddings[0], embeddings[1])
print(f"Cosine similarity: {sim:.3f}")
```

Running this code typically outputs a similarity around **0.8–0.9**, reflecting the semantic closeness of the two sentences.

## Common Mistakes  
1. **Treating raw vectors as “meaningful”** – Random numeric vectors have no semantic content; only learned embeddings do.  
2. **Ignoring vector normalization** – Many similarity measures (e.g., cosine) assume unit‑length vectors; otherwise distances become misleading.  
3. **Assuming embeddings are perfect** – They capture patterns from training data but can miss nuances, exhibit biases, or fail on out‑of‑domain text.

## Connected Concepts  
- **Word Embedding** → Basic building block; maps individual words to vectors (e.g., Word2Vec, GloVe).  
- **Sentence Embedding** → Extends word embeddings to whole sentences or paragraphs (e.g., SentenceTransformers).  
- **Cosine Similarity** → Common metric to compare embeddings and retrieve similar items.  
- **Transformer Architecture** → Uses attention to generate query/key/value embeddings for each token.  
- **Neural Networks** → Underlie most embedding models, learning representations through back‑propagation.

## Resources  
1. **“Word2Vec: A Modern Approach”** – Original paper by Mikolov et al. (2013).  
2. **Stanford CS224n – Natural Language Processing with Deep Learning** – Lecture notes on embeddings.  
3. **Hugging Face Transformers Documentation** – Tutorials on using pre‑trained embedding models.

## Summary  
Vectors provide a numeric form for data, and embeddings are learned vectors that capture meaning. They enable models to process text, measure similarity, and transfer knowledge across tasks. Understanding how embeddings work is foundational for modern NLP and many AI applications.