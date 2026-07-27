# GCC-LDP: Locally Differentially Private Graph Clustering via Structure-Preserving Graph Compression

This repository contains the implementation of the paper **"Locally Differentially Private Graph Clustering via Structure-Preserving Graph Compression".

GCC‑LDP is a privacy‑preserving graph clustering framework that:

- Introduces **Adjacency Set Vector (ASV)** encoding with Re‑Pair compression to significantly reduce encoding length and noise injection.
- Achieves **two‑round** decentralized graph aggregation, eliminating iterative error accumulation.
- Provides rigorous **LDP guarantees** with theoretical noise error bounds and utility preservation.
- Achieves **10%-20%** improvements over existing LDP graph clustering baselines in ARI and AMI.


###  Dependencies
```
Package 	       Version         Purpose 
networkx   	       ≥2.6	      Graph operations
numpy	           ≥1.21    Numerical computations
scikit‑learn	   ≥1.0	    Evaluation metrics (ARI, AMI)
matplotlib         ≥3.4	       Visualisation
python‑louvain	   ≥0.16	   Louvain baseline
pandas	           ≥1.3       Data management
pyyaml	           ≥6.0	    Configuration parsing (optional)
scipy	           ≥1.7	     Scientific computing
```

**Install all required dependencies:**

```
bash
cd LDP_graphcluster
pip install -r requirements.txt
```

###  Datasets
We evaluate GCC‑LDP on multiple real‑world networks. All datasets are located in the dataset/ directory.
| Dataset	 | Nodes  | 	Edges	 | Description |
|-------|-------|-------|-------|
| Karate | 34 | 78 |Social network |
| Facebook | 4, 039 | 88, 234 |Social network |
| Email | 1, 133 | 10, 903 |Communication network |
| PT | 1, 912 | 31, 299 |Social network |
| DBLP | 317, 080 | 1, 049, 866 |Social network |

Note: For custom datasets, place your edge‑list file (.txt) in the dataset/ folder.

### Quick Start
**Run full comparison experiment (all baselines)**
```
python run_comparison_LDP.py
```
This will execute LDPGen, LF‑GDPR, GCC‑LDP (and optionally Wdt‑SCAN/GC‑NLDP if integrated) on the specified dataset and output evaluation metrics.


**Run GCC‑LDP only**
```
python run_GCC_LDP.py
```

**Customise parameters**
Edit the following variables directly in the run_comparison_LDP.py script:
| Variable	 | Description  | 	Example	 | 
|-------|-------|-------|
| privacy_budget | Total privacy budget ε | 1 |
| filename | Dataset name (without extension) | 'facebook' |
| threshold_d | Peripheral node degree threshold | 20 |
| threshold_beta | Connection strength threshold | 0.2 |

These parameters are dataset‑dependent; optimal values are reported in the paper (Section 5.4).

**Privacy Budget Allocation**
Different methods use different privacy accounting models:
| Method	| Total ϵ | Internal Components | Privacy Level | Component Budget |
|-------|-------|-------|-------|
| LF‑GDPR | ϵ | Edge perturbation + Degree perturbation | Edge‑level | ϵ/2 +ϵ/2  |
| LDPGen | ϵ | K iterative rounds | Edge‑level | ϵ/K |
| Wdt‑SCAN | ϵ | Optimal degree vector length +  Clustering | Edge‑level | 2ϵ/3 + ϵ/3 |
| GC‑NLDP | ϵ | Initial clustering + Feedback refinement| Node‑level | ϵ/2 +ϵ/2 |
| GCC‑LDP | ϵ | AEM compression + Aggregation | Edge‑level | 2ϵ/3 + ϵ/3 |


LF-GDPR allocates ϵ/2 to each mechanism because it simultaneously protects two types of graph information: edge connectivity and node degree. According to the sequential composition theorem of differential privacy, the total privacy loss is the sum of the budgets consumed by both mechanisms. Therefore, assigning ϵ/2 to each mechanism guarantees an overall privacy budget of ϵ.

**Baselines**
We compare GCC‑LDP against the following state‑of‑the‑art methods, all implemented in the graph/ directory:
| Method	| Description	| 	Reference	 |  	  
|-------|-------|-------|
| LF‑GDPR | Adjacency‑bit‑vector graph metric estimation with Louvain | Ye et al., TKDE 2022 |
| LDPGen | Degree‑vector based LDP graph clustering with K‑means | Qin et al., CCS 2017 |
| GC‑NLDP | Adjacency‑bit‑vector with cyclic feedback loop | Fu et al., CS 2023 |
| Wdt‑SCAN | Degree‑vector with Pareto‑based node partitioning | Hou et al., CS 2023 |

All baseline implementations are provided with their original parameter settings as specified in the respective papers.

**Download Links**
Most datasets can be downloaded from https://snap.stanford.edu/data/



