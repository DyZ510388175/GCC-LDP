# GCC-LDP: Locally Differentially Private Graph Clustering via Structure-Preserving Graph Compression

This repository contains the implementation of the paper **"Locally Differentially Private Graph Clustering via Structure-Preserving Graph Compression".

GCC‑LDP is a privacy‑preserving graph clustering framework that:

- Introduces **Adjacency Set Vector (ASV)** encoding with Re‑Pair compression to significantly reduce encoding length and noise injection.
- Achieves **two‑round** decentralized graph aggregation, eliminating iterative error accumulation.
- Provides rigorous **LDP guarantees** with theoretical noise error bounds and utility preservation.
- Outperforms state‑of‑the‑art methods by **10% – 20%** in clustering quality (ARI/AMI) across real‑world datasets.


###  Dependencies
```
Package 	       Version         Purpose 
networkx   	       ≥2.6	      Graph operations
numpy	           ≥1.21    Numerical computations
scikit‑learn	   ≥1.0	    Evaluation metrics (ARI, AMI)
matplotlib         ≥3.4	       Visualisation
python‑louvain	   ≥0.16	    Louvain baseline
pandas	           ≥1.3      Data management
pyyaml	           ≥6.0	    Configuration parsing (optional)
scipy	           ≥1.7	     Scientific computing
```

**Install all required dependencies:**

```
bash
pip install -r requirements.txt
```

###  Datasets
We evaluate GCC‑LDP on multiple real‑world networks. All datasets are located in the dataset/ directory.


# GCC-LDP

Dependencies
networkx>=2.6

numpy>=1.21

scikit-learn>=1.0

matplotlib>=3.4

python-louvain>=0.16

pandas>=1.3

pyyaml>=6.0

📊 Datasets
We evaluate GCC-LDP on multiple real-world datasets:

Dataset	Nodes	Edges	Description
Karate	34	78	Zachary's Karate Club
Facebook	4,039	88,234	Facebook social network
Email	1,133	5,451	EU email network
Dolphins	62	159	Dolphin social network
Football	115	613	American college football
All datasets are located in the dataset/ directory.
