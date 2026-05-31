# Neural Networks

## Definition
A neural network is a computational model composed of interconnected layers of artificial neurons, each performing a weighted sum followed by a non‑linear activation. When at least one hidden layer is present, the model becomes a multi‑layer perceptron (MLP), capable of approximating any continuous function on a compact domain (Universal Approximation Theorem). The network learns by adjusting its weights through gradient‑based optimization to minimize a loss function on training data.

## Why It Matters
- **Expressive Power**: With enough hidden units, shallow MLPs can model complex, non‑linear relationships, forming the foundation for modern deep learning architectures.
- **End‑to‑End Learning**: Neural networks can ingest raw data (images, text, audio) and learn hierarchical feature representations without handcrafted engineering.
- **Optimization Landscape**: Studying neural networks reveals insights into non‑convex optimization, over‑parameterization, and generalization, influencing both theory and practice in machine learning.

## Example
A classic shallow neural network for classifying handwritten digits (MNIST) with one hidden layer:

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms

# Data loader
train_loader = torch.utils.data.DataLoader(
    datasets.MNIST('.', train=True, download=True,
                   transform=transforms.ToTensor()),
    batch_size=64, shuffle=True)

# Shallow MLP
class ShallowMLP(nn.Module):
    def __init__(self, hidden_dim=128):
        super().__init__()
        self.fc1 = nn.Linear(28*28, hidden_dim)   # Input → hidden
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, 10)      # Hidden → output

    def forward(self, x):
        x = x.view(x.size(0), -1)                 # Flatten
        x = self.relu(self.fc1(x))
        return self.fc2(x)

model = ShallowMLP()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# Training loop (single epoch for brevity)
for images, labels in train_loader:
    optimizer.zero_grad()
    outputs = model(images)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()
```

This network demonstrates the core components: fully connected layers, ReLU activations, and back‑propagation.

## Common Mistakes
1. **Confusing “shallow” with “simple”** – A shallow network can still be highly expressive; its depth is not the sole determinant of power.
2. **Assuming any activation works** – Certain activations (e.g., ReLU) avoid vanishing gradients; using sigmoid or tanh in deep networks often hampers training.
3. **Neglecting weight initialization** – Poor initialization can lead to dead neurons or exploding gradients, especially with ReLU or large hidden layers.

## Connected Concepts
- **Universal Approximation Theorem** → Guarantees that a single hidden layer with enough neurons can approximate any continuous function.
- **Back‑Propagation** → The algorithm that efficiently computes gradients for training neural networks.
- **Regularization (Dropout, L2)** → Techniques to prevent over‑fitting in MLPs and deeper architectures.
- **Activation Functions (ReLU, GELU, Swish)** → Non‑linearities that enable networks to learn complex patterns.
- **Gradient Descent Variants (Adam, RMSProp)** → Optimizers that adapt learning rates for faster convergence.

## Resources
1. **Goodfellow, Bengio & Courville – *Deep Learning*** (MIT Press, 2016) – Chapters 1–3 cover MLP fundamentals and theory.
2. **He, Zhang, Ren & Sun – “Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification” (2015)** – Empirical study on ReLU and its variants.
3. **Andrew Ng – *Deep Learning Specialization* (Coursera)** – Video lectures that include hands‑on MLP implementation and theory.

## Summary
Neural networks, particularly shallow multi‑layer perceptrons, form the bedrock of modern AI by providing a flexible, learnable mapping from inputs to outputs. Their expressive capacity, coupled with gradient‑based training, enables end‑to‑end learning across diverse domains. Mastery of their architecture, training dynamics, and common pitfalls equips practitioners to build robust, scalable models.