# Sources

The skill folder contains material taken from published papers, kept as style references for the drawing
agent:

- **485 exemplar figures** in `skills/figgenie-paper-diagram/assets/exemplars/figures/`. Each one is the
  figure as extracted from the paper's PDF or from the authors' source (`print.png`, `source.svg`,
  `preview.png`), next to our own annotations (`manifest.json`, `semantics.json`).
- **2,764 parts** in `skills/figgenie-paper-diagram/assets/symbols/`, cut out of 976 figures. Every
  entry of `index.json` names the figure it was cut from. The other 89 parts of the library are original.
- **7 figures of 1 named style** in `skills/figgenie-paper-diagram/assets/exemplars/styles/`, the
  look a style reproduces on request, kept the same way (listed under *Named styles* at the end).

This material comes from the 638 papers listed below and belongs to their authors and publishers. It is
**not covered by this repository's MIT License**. FigGenie is not affiliated with the authors, and they do not
endorse it.

The licence column gives the Creative Commons licence stated in the paper's PDF, where there is one
([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) or a variant). For the other papers no licence is
claimed. Exemplar figures were cropped from the page and are otherwise unchanged; parts were cut out of
figures.

**Removal requests.** If you are an author or rights holder and want your material removed, email ahawkinthesky@outlook.com
or open an issue at https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill/issues. We will take it down.

| Paper | Authors | Venue | Exemplar figures | Parts cut from | Licence | Link |
|---|---|---|---|---|---|---|
| *Welder: Scheduling Deep Learning Memory Access via Tile-graph* | Yining Shi et al. | OSDI '23 | Fig. 3 | Fig. 4 |  | <https://www.usenix.org/conference/osdi23/presentation/shi> |
| *Replicating Persistent Memory Key-Value Stores with Efficient RDMA Abstraction* | Qing Wang et al. | OSDI '23 | Fig. 4, 5 | Fig. 4, 5 |  | <https://www.usenix.org/conference/osdi23/presentation/wang-qing> |
| *An Extensible Orchestration and Protection Framework for Confidential Cloud Computing* | Adil Ahmad et al. | OSDI '23 |  | Fig. 1 |  | <https://www.usenix.org/conference/osdi23/presentation/ahmad> |
| *Cilantro: Performance-Aware Resource Allocation for General Objectives via Online Feedback* | Romil Bhardwaj et al. | OSDI '23 | Fig. 2, 3, 12 |  |  | <https://www.usenix.org/conference/osdi23/presentation/bhardwaj> |
| *Verifying vMVCC, a high-performance transaction library using multi-version concurrency control* | Yun-Sheng Chang et al. | OSDI '23 |  | Fig. 2 |  | <https://www.usenix.org/conference/osdi23/presentation/chang> |
| *Security and Performance in the Delegated User-level Virtualization* | Jiahao Chen et al. | OSDI '23 | Fig. 1 | Fig. 3, 5 |  | <https://www.usenix.org/conference/osdi23/presentation/chen> |
| *Optimizing Dynamic Neural Networks with Brainstorm* | Weihao Cui et al. | OSDI '23 |  | Fig. 1, 5, 7, 10 |  | <https://www.usenix.org/conference/osdi23/presentation/cui> |
| *Accountable authentication with privacy protection: The Larch system for universal login* | Emma Dauterman et al. | OSDI '23 | Fig. 2 | Fig. 2 |  | <https://www.usenix.org/conference/osdi23/presentation/dauterman> |
| *Automated Verification of Idempotence for Stateful Serverless Applications* | Haoran Ding et al. | OSDI '23 |  | Fig. 7 |  | <https://www.usenix.org/conference/osdi23/presentation/ding> |
| *Conveyor: One-Tool-Fits-All Continuous Software Deployment at Meta* | Boris Grubic et al. | OSDI '23 | Fig. 4 |  |  | <https://www.usenix.org/conference/osdi23/presentation/grubic> |
| *Sharding the State Machine: Automated Modular Reasoning for Complex Concurrent Systems* | Travis Hance et al. | OSDI '23 | Fig. 9 | Fig. 9 |  | <https://www.usenix.org/conference/osdi23/presentation/hance> |
| *Hydro: Surrogate-Based Hyperparameter Tuning Service in Datacenters* | Qinghao Hu et al. | OSDI '23 | Fig. 4 | Fig. 4, 7 |  | <https://www.usenix.org/conference/osdi23/presentation/hu> |
| *Detecting Transactional Bugs in Database Engines via Graph-Based Oracle Construction* | Zu-Ming Jiang et al. | OSDI '23 | Fig. 2, 6 | Fig. 1, 2, 6, 9, 13, 17 |  | <https://www.usenix.org/conference/osdi23/presentation/jiang> |
| *Flor: An Open High Performance RDMA Framework Over Heterogeneous RNICs* | Qiang Li et al. | OSDI '23 |  | Fig. 14 |  | <https://www.usenix.org/conference/osdi23/presentation/li-qiang> |
| *Spoq: Scaling Machine-Checkable Systems Verification in Coq* | Xupeng Li et al. | OSDI '23 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi23/presentation/li-xupeng> |
| *AlpaServe: Statistical Multiplexing with Model Parallelism for Deep Learning Serving* | Zhuohan Li et al. | OSDI '23 | Fig. 3 |  |  | <https://www.usenix.org/conference/osdi23/presentation/li-zhouhan> |
| *NCC: Natural Concurrency Control for Strictly Serializable Datastores by Avoiding the Timestamp-Inversion Pitfall* | Haonan Lu et al. | OSDI '23 | Fig. 1 | Fig. 2 |  | <https://www.usenix.org/conference/osdi23/presentation/lu> |
| *SMART: A High-Performance Adaptive Radix Tree for Disaggregated Memory* | Xuchuan Luo et al. | OSDI '23 | Fig. 8 | Fig. 8 |  | <https://www.usenix.org/conference/osdi23/presentation/luo> |
| *Hyrax: Fail-in-Place Server Operation in Cloud Platforms* | Jialun Lyu et al. | OSDI '23 | Fig. 10 | Fig. 6 |  | <https://www.usenix.org/conference/osdi23/presentation/lyu> |
| *ScaleDB: A Scalable, Asynchronous In-Memory Database* | Syed Akbar Mehdi et al. | OSDI '23 |  | Fig. 4, 6 |  | <https://www.usenix.org/conference/osdi23/presentation/mehdi> |
| *eZNS: An Elastic Zoned Namespace for Commodity ZNS SSDs* | Jaehong Min et al. | OSDI '23 | Fig. 3 | Fig. 1 |  | <https://www.usenix.org/conference/osdi23/presentation/min> |
| *Relational Debugging - Pinpointing Root Causes of Performance Problems* | Xiang (Jenny) Ren et al. | OSDI '23 | Fig. 3 | Fig. 4 |  | <https://www.usenix.org/conference/osdi23/presentation/ren> |
| *Ensō: A Streaming Interface for NIC-Application Communication* | Hugo Sadok et al. | OSDI '23 | Fig. 6 |  |  | <https://www.usenix.org/conference/osdi23/presentation/sadok> |
| *MGG: Accelerating Graph Neural Networks with Fine-Grained Intra-Kernel Communication-Computation Pipelining on Multi-GPU Platforms* | Yuke Wang et al. | OSDI '23 | Fig. 1 |  |  | <https://www.usenix.org/conference/osdi23/presentation/wang-yuke> |
| *SEPH: Scalable, Efficient, and Predictable Hashing on Persistent Memory* | Chao Wang et al. | OSDI '23 |  | Fig. 5, 6 |  | <https://www.usenix.org/conference/osdi23/presentation/wang-chao> |
| *BWoS: Formally Verified Block-based Work Stealing for Parallel Processing* | Jiawei Wang et al. | OSDI '23 |  | Fig. 4, 5, 7, 8 |  | <https://www.usenix.org/conference/osdi23/presentation/wang-jiawei> |
| *Characterizing Off-path SmartNIC for Accelerating Distributed Systems* | Xingda Wei et al. | OSDI '23 | Fig. 1, 4 | Fig. 1, 2, 4 |  | <https://www.usenix.org/conference/osdi23/presentation/wei-smartnic> |
| *No Provisioned Concurrency: Fast RDMA-codesigned Remote Fork for Serverless Computing* | Xingda Wei et al. | OSDI '23 | Fig. 10 | Fig. 9, 10, 11 |  | <https://www.usenix.org/conference/osdi23/presentation/wei-rdma> |
| *Cocktailer: Analyzing and Optimizing Dynamic Control Flow in Deep Learning* | Chen Zhang et al. | OSDI '23 | Fig. 4 |  |  | <https://www.usenix.org/conference/osdi23/presentation/zhang-chen> |
| *VBASE: Unifying Online Vector Similarity Search and Relational Queries via Relaxed Monotonicity* | Qianxi Zhang et al. | OSDI '23 |  | Fig. 5 |  | <https://www.usenix.org/conference/osdi23/presentation/zhang-qianxi> |
| *Effectively Scheduling Computational Graphs of Deep Neural Networks toward Their Domain-Specific Accelerators* | Jie Zhao et al. | OSDI '23 |  | Fig. 2, 5, 6, 7, 9 |  | <https://www.usenix.org/conference/osdi23/presentation/zhao> |
| *EINNET: Optimizing Tensor Programs with Derivation-Based Transformations* | Liyan Zheng et al. | OSDI '23 | Fig. 3 | Fig. 15 |  | <https://www.usenix.org/conference/osdi23/presentation/zheng> |
| *Microkernel Goes General: Performance and Compatibility in the HongMeng Production Microkernel* | Haibo Chen et al. | OSDI '24 | Fig. 9 | Fig. 5, 7 |  | <https://www.usenix.org/conference/osdi24/presentation/chen-haibo> |
| *Data-flow Availability: Achieving Timing Assurance in Autonomous Systems* | Ao Li and Ning Zhang | OSDI '24 | Fig. 11 | Fig. 11 |  | <https://www.usenix.org/conference/osdi24/presentation/li> |
| *Fairness in Serving Large Language Models* | Ying Sheng et al. | OSDI '24 | Fig. 2 | Fig. 2 |  | <https://www.usenix.org/conference/osdi24/presentation/sheng> |
| *Anvil: Verifying Liveness of Cluster Management Controllers* | Xudong Sun et al. | OSDI '24 |  | Fig. 5 |  | <https://www.usenix.org/conference/osdi24/presentation/sun-xudong> |
| *Chop Chop: Byzantine Atomic Broadcast to the Network Limit* | Martina Camaioni et al. | OSDI '24 | Fig. 4, 6 | Fig. 6 |  | <https://www.usenix.org/conference/osdi24/presentation/camaioni> |
| *Secret Key Recovery in a Global-Scale End-to-End Encryption System* | Graeme Connell et al. | OSDI '24 |  | Fig. 1 |  | <https://www.usenix.org/conference/osdi24/presentation/connell> |
| *When will my ML Job finish? Toward providing Completion Time Estimates through Predictability-Centric Scheduling* | Abdullah Bin Faisal et al. | OSDI '24 | Fig. 2 |  |  | <https://www.usenix.org/conference/osdi24/presentation/bin-faisal> |
| *ServerlessLLM: Low-Latency Serverless Inference for Large Language Models* | Yao Fu et al. | OSDI '24 | Fig. 1, 3, 5 | Fig. 4, 5 |  | <https://www.usenix.org/conference/osdi24/presentation/fu> |
| *Automatically Reasoning About How Systems Code Uses the CPU Cache* | Rishabh R. Iyer, Katerina J. Argyraki and George Candea | OSDI '24 |  | Fig. 5 |  | <https://www.usenix.org/conference/osdi24/presentation/iyer> |
| *Flock: A Framework for Deploying On-Demand Distributed Trust* | Darya Kaviani et al. | OSDI '24 | Fig. 4 |  |  | <https://www.usenix.org/conference/osdi24/presentation/kaviani> |
| *Optimizing Resource Allocation in Hyperscale Datacenters: Scalability, Usability, and Experiences* | Neeraj Kumar et al. | OSDI '24 |  | Fig. 2 |  | <https://www.usenix.org/conference/osdi24/presentation/kumar> |
| *Sabre: Hardware-Accelerated Snapshot Compression for Serverless MicroVMs* | Nikita Lazarev et al. | OSDI '24 | Fig. 7 |  |  | <https://www.usenix.org/conference/osdi24/presentation/lazarev> |
| *InfiniGen: Efficient Generative Inference of Large Language Models with Dynamic KV Cache Management* | Wonbeom Lee et al. | OSDI '24 | Fig. 9 | Fig. 9 |  | <https://www.usenix.org/conference/osdi24/presentation/lee> |
| *Parrot: Efficient Serving of LLM-based Applications with Semantic Variable* | Chaofan Lin et al. | OSDI '24 | Fig. 6 | Fig. 9 |  | <https://www.usenix.org/conference/osdi24/presentation/lin-chaofan> |
| *ChameleonAPI: Automatic and Efficient Customization of Neural Networks for ML Applications* | Yuhan Liu et al. | OSDI '24 |  | Fig. 4 |  | <https://www.usenix.org/conference/osdi24/presentation/liu> |
| *DRust: Language-Guided Distributed Shared Memory with Fine Granularity, Full Transparency, and Ultra Efficiency* | Haoran Ma et al. | OSDI '24 |  | Fig. 1, 2 |  | <https://www.usenix.org/conference/osdi24/presentation/ma-haoran> |
| *FairyWREN: A Sustainable Cache for Emerging Write-Read-Erase Flash Interfaces* | Sara McAllister et al. | OSDI '24 |  | Fig. 7, 9, 10 |  | <https://www.usenix.org/conference/osdi24/presentation/mcallister> |
| *Massively Parallel Multi-Versioned Transaction Processing* | Shujian Qian and Ashvin Goel | OSDI '24 |  | Fig. 1, 3 |  | <https://www.usenix.org/conference/osdi24/presentation/qian> |
| *Burstable Cloud Block Storage with Data Processing Units* | Junyi Shu et al. | OSDI '24 | Fig. 9 | Fig. 9 |  | <https://www.usenix.org/conference/osdi24/presentation/shu> |
| *High-throughput and Flexible Host Networking for Accelerated Computing* | Athinagoras Skiadopoulos et al. | OSDI '24 | Fig. 6 |  |  | <https://www.usenix.org/conference/osdi24/presentation/skiadopoulos> |
| *Validating the eBPF Verifier via State Embedding* | Hao Sun and Zhendong Su | OSDI '24 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi24/presentation/sun-hao> |
| *Llumnix: Dynamic Scheduling for Large Language Model Serving* | Biao Sun et al. | OSDI '24 | Fig. 8 | Fig. 1, 2, 8 |  | <https://www.usenix.org/conference/osdi24/presentation/sun-biao> |
| *Ransom Access Memories: Achieving Practical Ransomware Protection in Cloud with DeftPunk* | Zhongyu Wang et al. | OSDI '24 | Fig. 1 |  |  | <https://www.usenix.org/conference/osdi24/presentation/wang-zhongyu> |
| *IntOS: Persistent Embedded Operating System and Language Support for Multi-threaded Intermittent Computing* | Yilun Wu et al. | OSDI '24 | Fig. 1 | Fig. 3, 4, 5 |  | <https://www.usenix.org/conference/osdi24/presentation/wu-yilun> |
| *dLoRA: Dynamically Orchestrating Requests and Adapters for LoRA LLM Serving* | Bingyang Wu et al. | OSDI '24 | Fig. 3 | Fig. 4, 8 |  | <https://www.usenix.org/conference/osdi24/presentation/wu-bingyang> |
| *Nomad: Non-Exclusive Memory Tiering via Transactional Page Migration* | Lingfeng Xiang et al. | OSDI '24 |  | Fig. 3, 4 |  | <https://www.usenix.org/conference/osdi24/presentation/xiang> |
| *Beaver: Practical Partial Snapshots for Distributed Cloud Services* | Liangcheng Yu et al. | OSDI '24 |  | Fig. 9, 15, 17 |  | <https://www.usenix.org/conference/osdi24/presentation/yu> |
| *Enabling Tensor Language Model to Assist in Generating High-Performance Tensor Programs for Deep Learning* | Yi Zhai et al. | OSDI '24 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi24/presentation/zhai> |
| *Motor: Enabling Multi-Versioning for Distributed Transactions on Disaggregated Memory* | Ming Zhang, Yu Hua and Zhijun Yang | OSDI '24 |  | Fig. 5 |  | <https://www.usenix.org/conference/osdi24/presentation/zhang-ming> |
| *Fast and Scalable In-network Lock Management Using Lock Fission* | Hanze Zhang et al. | OSDI '24 | Fig. 2 | Fig. 1 |  | <https://www.usenix.org/conference/osdi24/presentation/zhang-hanze> |
| *DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving* | Yinmin Zhong et al. | OSDI '24 | Fig. 6 | Fig. 6 |  | <https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin> |
| *VeriSMo: A Verified Security Module for Confidential VMs* | Ziqiao Zhou et al. | OSDI '24 | Fig. 4 | Fig. 4 |  | <https://www.usenix.org/conference/osdi24/presentation/zhou> |
| *MonoNN: Enabling a New Monolithic Optimization Space for Neural Network Inference Tasks on Modern GPU-Centric Architectures* | Donglin Zhuang et al. | OSDI '24 | Fig. 6 | Fig. 6, 7, 9 |  | <https://www.usenix.org/conference/osdi24/presentation/zhuang> |
| *Using Dynamically Layered Definite Releases for Verifying the RefFS File System* | Mo Zou et al. | OSDI '24 |  | Fig. 4, 6, 8 |  | <https://www.usenix.org/conference/osdi24/presentation/zou> |
| *Tintin: A Unified Hardware Performance Profiling Infrastructure to Uncover and Manage Uncertainty* | Ao Li et al. | OSDI '25 | Fig. 7 |  |  | <https://www.usenix.org/conference/osdi25/presentation/li> |
| *WLB-LLM: Workload-Balanced 4D Parallelism for Large Language Model Training* | Zheng Wang et al. | OSDI '25 | Fig. 2, 4 | Fig. 4, 9, 11 |  | <https://www.usenix.org/conference/osdi25/presentation/wang-zheng> |
| *EMT: An OS Framework for New Memory Translation Architectures* | Siyuan Chai et al. | OSDI '25 | Fig. 5 |  |  | <https://www.usenix.org/conference/osdi25/presentation/chai-siyuan> |
| *Fork in the Road: Reflections and Optimizations for Cold Start Latency in Production Serverless Systems* | Xiaohu Chai et al. | OSDI '25 |  | Fig. 7, 10 |  | <https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu> |
| *PipeThreader: Software-Defined Pipelining for Efficient DNN Execution* | Yu Cheng et al. | OSDI '25 | Fig. 3 | Fig. 6 |  | <https://www.usenix.org/conference/osdi25/presentation/cheng> |
| *Decentralized, Epoch-based F2FS Journaling with Fine-grained Crash Recovery* | Yaotian Cui et al. | OSDI '25 | Fig. 7 | Fig. 7 |  | <https://www.usenix.org/conference/osdi25/presentation/cui> |
| *QiMeng-Xpiler: Transcompiling Tensor Programs for Deep Learning Systems with a Neural-Symbolic Approach* | Shouyang Dong et al. | OSDI '25 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi25/presentation/dong> |
| *Picsou: Enabling Replicated State Machines to Communicate Efficiently* | Reginald Frank et al. | OSDI '25 | Fig. 2 | Fig. 2 |  | <https://www.usenix.org/conference/osdi25/presentation/frank> |
| *QOS: Quantum Operating System* | Emmanouil Giortamis et al. | OSDI '25 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi25/presentation/giortamis> |
| *KPerfIR: Towards a Open and Compiler-centric Ecosystem for GPU Kernel Performance Tooling on Modern AI Workloads* | Yue Guan et al. | OSDI '25 | Fig. 1, 6, 8 | Fig. 1, 6, 8 |  | <https://www.usenix.org/conference/osdi25/presentation/guan> |
| *Achieving Low-Latency Graph-Based Vector Search via Aligning Best-First Search Algorithm with SSD* | Hao Guo and Youyou Lu | OSDI '25 |  | Fig. 9 |  | <https://www.usenix.org/conference/osdi25/presentation/guo> |
| *WaferLLM: Large Language Model Inference at Wafer Scale* | Congjie He et al. | OSDI '25 |  | Fig. 7 |  | <https://www.usenix.org/conference/osdi25/presentation/he> |
| *Neutrino: Fine-grained GPU Kernel Profiling via Programmable Probing* | Songlin Huang and Chenshu Wu | OSDI '25 |  | Fig. 5 |  | <https://www.usenix.org/conference/osdi25/presentation/huang-songlin> |
| *Training with Confidence: Catching Silent Errors in Deep Learning Training with Automated Proactive Checks* | Yuxuan Jiang et al. | OSDI '25 |  | Fig. 1, 3 |  | <https://www.usenix.org/conference/osdi25/presentation/jiang> |
| *Understanding Stragglers in Large Model Training Using What-if Analysis* | Jinkun Lin et al. | OSDI '25 |  | Fig. 2 |  | <https://www.usenix.org/conference/osdi25/presentation/lin-jinkun> |
| *Tiered Memory Management Beyond Hotness* | Jinshu Liu et al. | OSDI '25 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi25/presentation/liu> |
| *Deriving Semantic Checkers from Tests to Detect Silent Failures in Production Distributed Systems* | Chang Lou et al. | OSDI '25 |  | Fig. 11 |  | <https://www.usenix.org/conference/osdi25/presentation/lou> |
| *Quake: Adaptive Indexing for Vector Search* | Jason Mohoney et al. | OSDI '25 |  | Fig. 2 |  | <https://www.usenix.org/conference/osdi25/presentation/mohoney> |
| *Principles and Methodologies for Serial Performance Optimization* | Sujin Park et al. | OSDI '25 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi25/presentation/park-sujin> |
| *DecDEC: A Systems Approach to Advancing Low-Bit LLM Quantization* | Yeonhong Park et al. | OSDI '25 | Fig. 6, 8, 11 | Fig. 8, 11 |  | <https://www.usenix.org/conference/osdi25/presentation/park-yeonhong> |
| *Disentangling the Dual Role of NIC Receive Rings* | Boris Pismenny, Adam Morrison and Dan Tsafrir | OSDI '25 |  | Fig. 8 |  | <https://www.usenix.org/conference/osdi25/presentation/pismenny> |
| *Enabling Efficient GPU Communication over Multiple NICs with FuseLink* | Zhenghang Ren et al. | OSDI '25 | Fig. 4 | Fig. 5 |  | <https://www.usenix.org/conference/osdi25/presentation/ren> |
| *Mako: Speculative Distributed Transactions with Geo-Replication* | Weihai Shen et al. | OSDI '25 |  | Fig. 5 |  | <https://www.usenix.org/conference/osdi25/presentation/shen-weihai> |
| *Scalio: Scaling up DPU-based JBOF Key-value Store with NVMe-oF Target Offload* | Xun Sun et al. | OSDI '25 | Fig. 9 | Fig. 9 |  | <https://www.usenix.org/conference/osdi25/presentation/sun> |
| *To PRI or Not To PRI, That's the question* | Yun Wang et al. | OSDI '25 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi25/presentation/wang-yun> |
| *ZEN: Empowering Distributed Training with Sparsity-driven Data Synchronization* | Zhuang Wang et al. | OSDI '25 |  | Fig. 5, 6, 7, 9 |  | <https://www.usenix.org/conference/osdi25/presentation/wang-zhuang> |
| *Mirage: A Multi-Level Superoptimizer for Tensor Programs* | Mengdi Wu et al. | OSDI '25 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi25/presentation/wu-mengdi> |
| *Decouple and Decompose: Scaling Resource Allocation with DeDe* | Zhiying Xu, Minlan Yu and Francis Y. Yan | OSDI '25 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi25/presentation/xu> |
| *BlitzScale: Fast and Live Large Model Autoscaling with O(1) Host Caching* | Dingyan Zhang et al. | OSDI '25 | Fig. 5, 6, 10 | Fig. 6, 7, 14 |  | <https://www.usenix.org/conference/osdi25/presentation/zhang-dingyan> |
| *Extending Applications Safely and Efficiently* | Yusheng Zheng et al. | OSDI '25 | Fig. 4 |  |  | <https://www.usenix.org/conference/osdi25/presentation/zheng-yusheng> |
| *No Buffer, No Bottleneck: Efficient Zero-Copy KV Cache Offloading for Long-Context LLMs* | Shutian Luo and Haiying Shen | OSDI '26 |  | Fig. 8, 9 |  | <https://www.usenix.org/conference/osdi26/presentation/luo> |
| *Simple Is Better: Multiplication May Be All You Need for LLM Request Scheduling* | Dingyan Zhang et al. | OSDI '26 |  | Fig. 1 |  | <https://www.usenix.org/conference/osdi26/presentation/zhang-dingyan> |
| *Prism: Cost-Efficient Multi-LLM Serving via GPU Memory Ballooning* | Shan Yu et al. | OSDI '26 | Fig. 3 |  |  | <https://www.usenix.org/conference/osdi26/presentation/yu-shan> |
| *Break On Through to the Other Side: Pooling Memory Elastically with RamRyder* | Yanbo Zhou et al. | OSDI '26 | Fig. 7 | Fig. 8 |  | <https://www.usenix.org/conference/osdi26/presentation/zhou-yanbo> |
| *MAC: Metadata Acceleration for Sustainable Performance in Big-Data Systems with CXL DRAM* | Dusol Lee et al. | OSDI '26 |  | Fig. 1, 5 |  | <https://www.usenix.org/conference/osdi26/presentation/lee> |
| *USEC: A User-Requirement-Driven Mandatory Access Control Framework for Operating Systems (Operational Systems)* | Yu Jiang et al. | OSDI '26 |  | Fig. 2, 3 |  | <https://www.usenix.org/conference/osdi26/presentation/jiang-yu> |
| *Ichnaea: A Framework for Precise Tracking of Memory Objects* | Samad Haque et al. | OSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi26/presentation/haque> |
| *Hetu v2: A General and Scalable Deep Learning System with Hierarchical and Heterogeneous Single Program Multiple Data Annotations* | Haoyang Li et al. | OSDI '26 |  | Fig. 3, 4, 11, 12 |  | <https://www.usenix.org/conference/osdi26/presentation/li-haoyang> |
| *Syncopate: Efficient Multi-GPU AI Kernels via Automatic Chunk-Centric Compute-Communication Overlap* | Xinwei Qiang et al. | OSDI '26 | Fig. 7 | Fig. 1, 3, 7 |  | <https://www.usenix.org/conference/osdi26/presentation/qiang> |
| *Cocoon: A System Architecture for Differentially Private Training with Correlated Noises* | Donghwan Kim et al. | OSDI '26 | Fig. 7, 8 | Fig. 7, 9, 13 |  | <https://www.usenix.org/conference/osdi26/presentation/kim-donghwan> |
| *ValScope: Value-Semantics-Aware Metamorphic Testing for Detecting Logical Bugs in DBMSs* | Li Lin, Liehang Chen and Rongxin Wu | OSDI '26 |  | Fig. 4 |  | <https://www.usenix.org/conference/osdi26/presentation/lin-li> |
| *Breaking the Reward Barrier: Accelerating Tree-of-Thought Reasoning via Speculative Exploration* | Shuzhang Zhong et al. | OSDI '26 | Fig. 3, 9 | Fig. 3, 9 |  | <https://www.usenix.org/conference/osdi26/presentation/zhong> |
| *Controlling Opaque-Component Effects with Semisolates and Try* | Evangelos Lamprou et al. | OSDI '26 | Fig. 2 |  |  | <https://www.usenix.org/conference/osdi26/presentation/lamprou> |
| *SBB: Eliminating Centralized Bottlenecks in Userspace Network Runtime* | Kang Hu et al. | OSDI '26 |  | Fig. 5 |  | <https://www.usenix.org/conference/osdi26/presentation/hu-kang> |
| *What Are You (M)Waiting For: The Hidden Cost of Idle in the Hyperscale Cloud (Operational Systems)* | Yun Wang et al. | OSDI '26 |  | Fig. 10 |  | <https://www.usenix.org/conference/osdi26/presentation/wang-yun> |
| *Xkernel: Principled Performance Tunability of Operating System Kernels* | Zhongjie Chen et al. | OSDI '26 | Fig. 2 | Fig. 2, 3, 4, 5 |  | <https://www.usenix.org/conference/osdi26/presentation/chen-zhongjie> |
| *Murakkab: Resource-Efficient Agentic Workflow Orchestration in Cloud Platforms* | Gohar Irfan Chaudhry et al. | OSDI '26 |  | Fig. 5, 6 |  | <https://www.usenix.org/conference/osdi26/presentation/chaudhry> |
| *StriaTrace: Efficient Tracing and Diagnosis for Online LLM Inference (Operational Systems)* | Haonan Wu et al. | OSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi26/presentation/wu-haonan> |
| *hS: Speculative Script Reordering at Subprocess Granularity* | Georgios Liargkovas et al. | OSDI '26 |  | Fig. 4 |  | <https://www.usenix.org/conference/osdi26/presentation/liargkovas> |
| *A Compilation-Based Under-Constrained Execution Engine* | Mingjun Yin et al. | OSDI '26 | Fig. 5 | Fig. 5, 6 |  | <https://www.usenix.org/conference/osdi26/presentation/yin> |
| *Efficient and Scalable Synchronization via Generalized Cache Coherence* | Yanpeng Yu et al. | OSDI '26 | Fig. 1, 6 | Fig. 7, 8 |  | <https://www.usenix.org/conference/osdi26/presentation/yu-yanpeng> |
| *DeLFS: A Decentralized Log-Structured File System for Manycores* | Taehwan Ahn et al. | OSDI '26 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi26/presentation/ahn> |
| *Weave: Efficient Co-Scheduling for Disaggregated RL Post-Training* | Tianyuan Wu et al. | OSDI '26 | Fig. 1 | Fig. 6, 7, 9 |  | <https://www.usenix.org/conference/osdi26/presentation/wu-tianyuan> |
| *RLinf: Flexible and Efficient Large-Scale Reinforcement Learning via Macro-to-Micro Flow Transformation* | Chao Yu et al. | OSDI '26 | Fig. 4 | Fig. 4 |  | <https://www.usenix.org/conference/osdi26/presentation/yu-chao> |
| *DynaRL: Flexible and Dynamic Scheduling of Large-Scale Reinforcement Learning Training* | Yuanqing Wang et al. | OSDI '26 |  | Fig. 9 |  | <https://www.usenix.org/conference/osdi26/presentation/wang-yuanqing> |
| *RollArt: Disaggregated Multi-Task Agentic RL Training at Scale* | Wei Gao et al. | OSDI '26 | Fig. 8 |  |  | <https://www.usenix.org/conference/osdi26/presentation/gao> |
| *Seer: Online Context Learning for Fast Synchronous LLM Reinforcement Learning* | Ruoyu Qin et al. | OSDI '26 | Fig. 5 | Fig. 5 |  | <https://www.usenix.org/conference/osdi26/presentation/qin> |
| *Harvesting Sub-Microsecond CXL Memory Stalls with LiteSwitch* | Nanqinqin Li et al. | OSDI '26 | Fig. 2 | Fig. 2 |  | <https://www.usenix.org/conference/osdi26/presentation/li-nanqinqin> |
| *Duhu: Shared Disaggregated Memory for Distributed Data Processing Frameworks* | Qiutong Men et al. | OSDI '26 |  | Fig. 4 |  | <https://www.usenix.org/conference/osdi26/presentation/men> |
| *Blowfish: Elastic Virtual Machine Memory for Disaggregated Memory* | Yulong Zhang et al. | OSDI '26 | Fig. 2 |  |  | <https://www.usenix.org/conference/osdi26/presentation/zhang-yulong> |
| *Espresso: Constructing Cost-Efficient CXL JBOF via Inter-SSD Computing Resource Sharing* | Shushu Yi et al. | OSDI '26 | Fig. 2, 5 |  |  | <https://www.usenix.org/conference/osdi26/presentation/yi> |
| *FORGE: Mitigating Synchronization Amplification for Memory-Disaggregated Caching Systems* | Zhijun Yang et al. | OSDI '26 | Fig. 1 | Fig. 9, 10 |  | <https://www.usenix.org/conference/osdi26/presentation/yang-zhijun> |
| *Accelerating Confidential Databases with Crypto-Free Mappings* | Wenxuan Huang, Zhanbo Wang and Mingyu Li | OSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi26/presentation/huang-wenxuan> |
| *JANUS: Cross-World, Cooperative Nested Virtualization for Secure Containers* | Jiangshan Lai et al. | OSDI '26 | Fig. 7, 9 | Fig. 4, 10 |  | <https://www.usenix.org/conference/osdi26/presentation/lai> |
| *μUSB: Practical and Safe USB Driver Reuse for Arm TrustZone* | Xuankai Zhang et al. | OSDI '26 |  | Fig. 11 |  | <https://www.usenix.org/conference/osdi26/presentation/zhang-xuankai> |
| *UEP: Portable Expert-Parallel Communication* | Ziming Mao et al. | OSDI '26 | Fig. 5 | Fig. 6 |  | <https://www.usenix.org/conference/osdi26/presentation/mao-ziming-uep> |
| *BatchGen: An Architecture for Scalable and Efficient Batch Inference* | Tairan Xu et al. | OSDI '26 | Fig. 1, 8 | Fig. 3, 4, 5, 8 |  | <https://www.usenix.org/conference/osdi26/presentation/xu-tairan> |
| *UCCL-Tran: An Extensible Software Transport Layer for GPU Networking* | Yang Zhou et al. | OSDI '26 | Fig. 2 | Fig. 1, 3, 5 |  | <https://www.usenix.org/conference/osdi26/presentation/zhou-yang> |
| *Kareus: Joint Reduction of Dynamic and Static Energy in Large Model Training* | Ruofan Wu, Jae-Won Chung and Mosharaf Chowdhury | OSDI '26 | Fig. 5, 8 | Fig. 5, 8, 9 |  | <https://www.usenix.org/conference/osdi26/presentation/wu-ruofan> |
| *Quota Marketplace: Dynamic Pricing for Efficient Allocation of ML Training Resources* | Balasubramanian Sivan et al. | OSDI '26 | Fig. 2 | Fig. 2 |  | <https://www.usenix.org/conference/osdi26/presentation/sivan> |
| *Bodega: Localized Linearizable Reads at Anywhere Anytime via Roster Leases* | Guanzhou Hu, Andrea C. Arpaci-Dusseau and Remzi H. Arpaci-Dusseau | OSDI '26 |  | Fig. 4 |  | <https://www.usenix.org/conference/osdi26/presentation/hu-guanzhou> |
| *Jetpack: Consensus Made Generally Fast* | Ze Tang et al. | OSDI '26 | Fig. 6 | Fig. 6, 14 |  | <https://www.usenix.org/conference/osdi26/presentation/tang> |
| *Safeguarding LLM Training at Scale: Online SDC Detection and Insights from 35 Million GPU Hours* | Kinman Lei et al. | OSDI '26 | Fig. 3 | Fig. 7, 8, 10 |  | <https://www.usenix.org/conference/osdi26/presentation/lei> |
| *RobustRL: Role-Based Fault Tolerance System for RL Post-Training* | Zhenqian Chen et al. | OSDI '26 |  | Fig. 5, 9 |  | <https://www.usenix.org/conference/osdi26/presentation/chen-zhenqian> |
| *Oxbow: A Coordinated Architecture for Multi-Component File Systems* | Jongyul Kim et al. | OSDI '26 |  | Fig. 4, 5, 6 |  | <https://www.usenix.org/conference/osdi26/presentation/kim-jongyul> |
| *Umap: Revisiting Memory-Mapped I/O on Distributed File Systems for Efficient Matrix Access (Operational Systems)* | Yongchao He et al. | OSDI '26 | Fig. 5, 8 | Fig. 6, 7, 8 |  | <https://www.usenix.org/conference/osdi26/presentation/he-yongchao> |
| *CoPilotIO: CPU as a Co-Pilot for GPU I/O to Free GPU Compute* | Guanyi Chen et al. | OSDI '26 |  | Fig. 1, 4, 5 |  | <https://www.usenix.org/conference/osdi26/presentation/chen-guanyi> |
| *RoCE BALBOA: Service-Enhanced RDMA Offload Engine for Data Center SmartNICs* | Maximilian Jakob Heer et al. | OSDI '26 | Fig. 3 |  |  | <https://www.usenix.org/conference/osdi26/presentation/heer> |
| *DPA-Store: An Ordered Network Data Path Key-Value Store* | Frederic Schimmelpfennig et al. | OSDI '26 | Fig. 2, 3, 6 | Fig. 6 |  | <https://www.usenix.org/conference/osdi26/presentation/schimmelpfennig> |
| *FARLock: Asymmetric RDMA Locking Made Fair* | Yuehao Hu et al. | OSDI '26 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi26/presentation/hu-yuehao> |
| *Disentangling Graph Dependencies for Efficient Billion-Scale GPU Vector Search* | Haoru Zhao et al. | OSDI '26 | Fig. 3 | Fig. 3 |  | <https://www.usenix.org/conference/osdi26/presentation/zhao> |
| *Efficient GPU-Centric Evolving Graph Processing at Scale* | Yunmo Zhang et al. | OSDI '26 |  | Fig. 1, 7 |  | <https://www.usenix.org/conference/osdi26/presentation/zhang-yunmo> |
| *Pluto: High-Performance, Memory-Efficient Distributed Graph Analytics through Advanced Mirroring* | Ying-Wei Wu, Christopher J. Rossbach and Mattan Erez | OSDI '26 |  | Fig. 2, 4, 6 |  | <https://www.usenix.org/conference/osdi26/presentation/wu-ying-wei> |
| *The Clustering Strikes Back: Building Cost-Effective and High-Performance ANNS at Scale with Helmsman (Operational Systems)* | Yuchen Huang et al. | OSDI '26 | Fig. 2 | Fig. 5, 8 |  | <https://www.usenix.org/conference/osdi26/presentation/huang-yuchen> |
| *WiseCode: Breaking the Scalability Barriers of Wide-Stripe Vector Codes* | Sijie Cai, Guangyan Zhang and Xiao Niu | OSDI '26 | Fig. 1 | Fig. 19 |  | <https://www.usenix.org/conference/osdi26/presentation/cai> |
| *M3U: Scalable Kernel Memory Management for Efficient Post-Copy Live Migration of High-End Virtual Machines* | Yizhe Xu et al. | OSDI '26 | Fig. 7 | Fig. 11 |  | <https://www.usenix.org/conference/osdi26/presentation/xu-yizhe> |
| *Compaction-Free Memory Defragmentation for Virtualization via Infinite Guest Physical Address Space* | Peixin Zeng et al. | OSDI '26 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi26/presentation/zeng> |
| *Inside Out: A Paradigm Shift in VM Introspection* | Dufy Teguia et al. | OSDI '26 | Fig. 1 |  |  | <https://www.usenix.org/conference/osdi26/presentation/teguia> |
| *vBOIDs: Taming Chaos via Coarse-Grained Scheduling Abstraction for Containers* | Kaesi Manakkal et al. | OSDI '26 |  | Fig. 5 |  | <https://www.usenix.org/conference/osdi26/presentation/manakkal> |
| *Efficient LLM Serving on Commodity GPU Clusters with Data-Reduced Cross-Instance Orchestration* | Jiangsu Du et al. | OSDI '26 | Fig. 1, 5 | Fig. 2, 7 |  | <https://www.usenix.org/conference/osdi26/presentation/du> |
| *Kairox: Adaptive GPU-CPU Hybrid LLM Inference via Online Neuron Balancing* | Yapeng Jiang et al. | OSDI '26 |  | Fig. 1 |  | <https://www.usenix.org/conference/osdi26/presentation/jiang-yapeng> |
| *ADAngel: Accelerating Arbitrary-Precision Quantized LLMs with Adaptive Computing Mapping* | Yao Liu et al. | OSDI '26 | Fig. 2 |  |  | <https://www.usenix.org/conference/osdi26/presentation/liu-yao> |
| *TileLoom: Automatic Dataflow Planning for Tile-Based Languages on Spatial Dataflow Accelerators* | Wei Li et al. | OSDI '26 |  | Fig. 4 |  | <https://www.usenix.org/conference/osdi26/presentation/li-wei> |
| *MPK: A Compiler and Runtime for Mega-Kernelizing Tensor Programs* | Xinhao Cheng et al. | OSDI '26 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi26/presentation/cheng> |
| *VTC: DNN Compilation with Virtual Tensors for Data Movement Elimination* | Muyan Hu et al. | OSDI '26 |  | Fig. 7 |  | <https://www.usenix.org/conference/osdi26/presentation/hu-muyan> |
| *Stop Pretending to Be Busy: A Case for Serverless Paradigms in Co-Located Batch Workloads (Operational Systems)* | Xiaohu Chai et al. | OSDI '26 |  | Fig. 11 |  | <https://www.usenix.org/conference/osdi26/presentation/chai> |
| *Distributed Speculative Execution for Resilient Cloud Applications* | Tianyu Li et al. | OSDI '26 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi26/presentation/li-tianyu> |
| *TrainMover: An Interruption-Resilient Runtime for ML Training* | ChonLam Lao et al. | OSDI '26 | Fig. 3 | Fig. 3, 4, 6, 7 |  | <https://www.usenix.org/conference/osdi26/presentation/lao> |
| *Heterogeneity at Hyperscale: Characterization and Scheduling of Large Production AI Clusters at Alibaba (Operational Systems)* | Suyi Li et al. | OSDI '26 |  | Fig. 15 |  | <https://www.usenix.org/conference/osdi26/presentation/li-suyi> |
| *Merlin: An Efficient Adaptive Cache Eviction Algorithm via Fine-Grained Characterization* | Liujia Li et al. | OSDI '26 |  | Fig. 6, 7 |  | <https://www.usenix.org/conference/osdi26/presentation/li-liujia> |
| *Learning-Augmented Heuristics: Simple Yet Smart, Robust and Interpretable Cache Eviction* | Haocheng Xia et al. | OSDI '26 |  | Fig. 4, 5 |  | <https://www.usenix.org/conference/osdi26/presentation/xia> |
| *Inference in the Shadows: Taming Memory Bandwidth Contention in Mobile LLM Inference with Sereno* | Tong Xin et al. | OSDI '26 |  | Fig. 4 |  | <https://www.usenix.org/conference/osdi26/presentation/xin> |
| *LifeLine: An Object-Page Lifetime Alignment GC Enabling Minimal Memory Copying for Mobile Devices* | Jiacheng Huang et al. | OSDI '26 | Fig. 12 | Fig. 12 |  | <https://www.usenix.org/conference/osdi26/presentation/huang-jiacheng> |
| *Unleash All Cores: Asymmetry-Aware Scalable DNN Inference on Mobile CPUs* | Qianlong Sang et al. | OSDI '26 |  | Fig. 6 |  | <https://www.usenix.org/conference/osdi26/presentation/sang> |
| *Surviving the Impossible Trinity: Revisiting CPU Scheduling Problem on Modern COTS Mobile Devices (Operational Systems)* | Jun Xiao et al. | OSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi26/presentation/xiao> |
| *qTPU: Hybrid Tensor Networks for Quantum-Classical Acceleration* | Nathaniel Tornow et al. | OSDI '26 |  | Fig. 4, 6, 8 |  | <https://www.usenix.org/conference/osdi26/presentation/tornow> |
| *Drs.NAS: Ultra-Efficient Neural Architecture Search for Recommendation Systems* | Ruixuan Wang and Xun Jiao | OSDI '26 | Fig. 1 |  |  | <https://www.usenix.org/conference/osdi26/presentation/wang-ruixuan> |
| *Svalinn: Overload Control in Large-Scale Servers with Multiple Resource Bottlenecks* | Bhaskar Subhash Pardeshi, Peidi Song and Ahmed Saeed | OSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/osdi26/presentation/pardeshi> |
| *PeeR: First-Class Scheduling for Latency-Critical eBPF Applications* | Jeremy Carin et al. | OSDI '26 |  | Fig. 3, 4 |  | <https://www.usenix.org/conference/osdi26/presentation/carin> |
| *RT: Regular Types for the Streaming Shell* | Zekai Li et al. | OSDI '26 | Fig. 7 | Fig. 7 |  | <https://www.usenix.org/conference/osdi26/presentation/li-zekai> |
| *Boomerang: Metadata-Private Messaging under Hardware Trust* | Peipei Jiang et al. | NSDI '23 | Fig. 7 | Fig. 4, 5, 7 |  | <https://www.usenix.org/conference/nsdi23/presentation/jiang> |
| *Remote Procedure Call as a Managed System Service* | Jingrong Chen et al. | NSDI '23 | Fig. 1, 2 | Fig. 1, 2 |  | <https://www.usenix.org/conference/nsdi23/presentation/chen-jingrong> |
| *SLNet: A Spectrogram Learning Neural Network for Deep Wireless Sensing* | Zheng Yang et al. | NSDI '23 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi23/presentation/yang-zheng> |
| *LemonNFV: Consolidating Heterogeneous Network Functions at Line Speed* | Hao Li et al. | NSDI '23 | Fig. 5 | Fig. 5 |  | <https://www.usenix.org/conference/nsdi23/presentation/li-hao> |
| *SHEPHERD: Serving DNNs in the Wild* | Hong Zhang et al. | NSDI '23 | Fig. 1 | Fig. 1 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhang-hong> |
| *Boggart: Towards General-Purpose Acceleration of Retrospective Video Analytics* | Neil Agarwal and Ravi Netravali | NSDI '23 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi23/presentation/agarwal-neil> |
| *CausalSim: A Causal Framework for Unbiased Trace-Driven Simulation* | Abdullah Omar Alomar et al. | NSDI '23 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi23/presentation/alomar> |
| *Bolt: Sub-RTT Congestion Control for Ultra-Low Latency* | Serhat Arslan et al. | NSDI '23 |  | Fig. 7 |  | <https://www.usenix.org/conference/nsdi23/presentation/arslan> |
| *Disaggregating Stateful Network Functions* | Deepak Bansal et al. | NSDI '23 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi23/presentation/bansal> |
| *Protego: Overload Control for Applications with Unpredictable Lock Contention* | Inho Cho et al. | NSDI '23 | Fig. 4 | Fig. 1, 4 |  | <https://www.usenix.org/conference/nsdi23/presentation/cho-inho> |
| *Hydra: Serialization-Free Network Ordering for Strongly Consistent Distributed Applications* | Inho Choi et al. | NSDI '23 |  | Fig. 1 |  | <https://www.usenix.org/conference/nsdi23/presentation/choi> |
| *LinkLab 2.0: A Multi-tenant Programmable IoT Testbed for Experimentation with Edge-Cloud Integration* | Wei Dong et al. | NSDI '23 | Fig. 1, 5 |  |  | <https://www.usenix.org/conference/nsdi23/presentation/dong> |
| *Scalable Distributed Massive MIMO Baseband Processing* | Junzhi Gong, Anuj Kalia and Minlan Yu | NSDI '23 | Fig. 3 |  |  | <https://www.usenix.org/conference/nsdi23/presentation/gong> |
| *ExoPlane: An Operating System for On-Rack Switch Resource Augmentation* | Daehyeok Kim, Vyas Sekar and Srinivasan Seshan | NSDI '23 | Fig. 3 | Fig. 5, 6, 8 |  | <https://www.usenix.org/conference/nsdi23/presentation/kim-daehyeok> |
| *Understanding RDMA Microarchitecture Resources for Performance Isolation* | Xinhao Kong et al. | NSDI '23 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi23/presentation/kong> |
| *OneWAN is better than two: Unifying a split WAN architecture* | Umesh Krishnaswamy et al. | NSDI '23 |  | Fig. 1, 6 |  | <https://www.usenix.org/conference/nsdi23/presentation/krishnaswamy> |
| *ModelKeeper: Accelerating DNN Training via Automated Training Warmup* | Fan Lai et al. | NSDI '23 | Fig. 7 |  |  | <https://www.usenix.org/conference/nsdi23/presentation/lai-fan> |
| *StarryNet: Empowering Researchers to Evaluate Futuristic Integrated Space and Terrestrial Networks* | Zeqi Lai et al. | NSDI '23 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi23/presentation/lai-zeqi> |
| *RF-Bouncer: A Programmable Dual-band Metasurface for Sub-6 Wireless Networks* | Xinyi Li et al. | NSDI '23 |  | Fig. 36 |  | <https://www.usenix.org/conference/nsdi23/presentation/li-xinyi> |
| *Dashlet: Taming Swipe Uncertainty for Robust Short Video Streaming* | Zhuqi Li et al. | NSDI '23 | Fig. 11, 13 | Fig. 11, 13, 14 |  | <https://www.usenix.org/conference/nsdi23/presentation/li-zhuqi> |
| *RF-Chord: Towards Deployable RFID Localization System for Logistic Networks* | Bo Liang et al. | NSDI '23 | Fig. 2 | Fig. 2, 3 |  | <https://www.usenix.org/conference/nsdi23/presentation/liang-bo> |
| *RingLeader: Efficiently Offloading Intra-Server Orchestration to NICs* | Jiaxin Lin et al. | NSDI '23 | Fig. 4, 6 |  |  | <https://www.usenix.org/conference/nsdi23/presentation/lin> |
| *BGL: GPU-Efficient GNN Training by Optimizing Graph Data I/O and Preprocessing* | Tianfeng Liu et al. | NSDI '23 | Fig. 4, 7 | Fig. 1, 4 |  | <https://www.usenix.org/conference/nsdi23/presentation/liu-tianfeng> |
| *Better Together: Jointly Optimizing ML Collective Scheduling and Execution Planning using SYNDICATE* | Kshiteej Mahajan et al. | NSDI '23 | Fig. 5 | Fig. 3, 6 |  | <https://www.usenix.org/conference/nsdi23/presentation/mahajan> |
| *Sketchovsky: Enabling Ensembles of Sketches on Programmable Switches* | Hun Namkung et al. | NSDI '23 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi23/presentation/namkung> |
| *Practical Intent-driven Routing Configuration Synthesis* | Sivaramakrishnan Ramanathan et al. | NSDI '23 |  | Fig. 4, 5 |  | <https://www.usenix.org/conference/nsdi23/presentation/ramanathan> |
| *Nu: Achieving Microsecond-Scale Resource Fungibility with Logical Processes* | Zhenyuan Ruan et al. | NSDI '23 | Fig. 2 | Fig. 2 |  | <https://www.usenix.org/conference/nsdi23/presentation/ruan> |
| *Tambur: Efficient loss recovery for videoconferencing via streaming codes* | Michael Rudow et al. | NSDI '23 |  | Fig. 7 |  | <https://www.usenix.org/conference/nsdi23/presentation/rudow> |
| *A High-Speed Stateful Packet Processing Approach for Tbps Programmable Switches* | Mariano Scazzariello et al. | NSDI '23 | Fig. 4 |  |  | <https://www.usenix.org/conference/nsdi23/presentation/scazzariello> |
| *DChannel: Accelerating Mobile Applications With Parallel High-bandwidth and Low-latency Channels* | William Sentosa et al. | NSDI '23 | Fig. 1 |  |  | <https://www.usenix.org/conference/nsdi23/presentation/sentosa> |
| *Understanding the impact of host networking elements on traffic bursts* | Erfan Sharafzadeh, Sepehr Abdous and Soudeh Ghorbani | NSDI '23 | Fig. 2, 3 |  |  | <https://www.usenix.org/conference/nsdi23/presentation/sharafzadeh> |
| *Enabling Users to Control their Internet* | Ammar Tahir and Radhika Mittal | NSDI '23 | Fig. 4 | Fig. 4 |  | <https://www.usenix.org/conference/nsdi23/presentation/tahir> |
| *CellDAM: User-Space, Rootless Detection and Mitigation for 5G Data Plane* | Zhaowei Tan et al. | NSDI '23 |  | Fig. 4 |  | <https://www.usenix.org/conference/nsdi23/presentation/tan> |
| *TopoOpt: Co-optimizing Network Topology and Parallelization Strategy for Distributed Training Jobs* | Weiyang Wang et al. | NSDI '23 | Fig. 23 | Fig. 29 |  | <https://www.usenix.org/conference/nsdi23/presentation/wang-weiyang> |
| *SRNIC: A Scalable Architecture for RDMA NICs* | Zilong Wang et al. | NSDI '23 | Fig. 4, 6 | Fig. 3, 8 |  | <https://www.usenix.org/conference/nsdi23/presentation/wang-zilong> |
| *Canvas: Isolated and Adaptive Swapping for Multi-Applications on Remote Memory* | Chenxi Wang et al. | NSDI '23 | Fig. 1, 7 | Fig. 1, 7, 8 |  | <https://www.usenix.org/conference/nsdi23/presentation/wang-chenxi> |
| *Transparent GPU Sharing in Container Clouds for Deep Learning Workloads* | Bingyang Wu et al. | NSDI '23 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi23/presentation/wu> |
| *SkyPilot: An Intercloud Broker for Sky Computing* | Zongheng Yang et al. | NSDI '23 | Fig. 3 |  |  | <https://www.usenix.org/conference/nsdi23/presentation/yang-zongheng> |
| *Zeus: Understanding and Optimizing GPU Energy Consumption of DNN Training* | Jie You, Jae-Won Chung and Mosharaf Chowdhury | NSDI '23 | Fig. 3 | Fig. 3 |  | <https://www.usenix.org/conference/nsdi23/presentation/you> |
| *Following the Data, Not the Function: Rethinking Function Orchestration in Serverless Computing* | Minchen Yu et al. | NSDI '23 | Fig. 1, 8 | Fig. 3, 8 |  | <https://www.usenix.org/conference/nsdi23/presentation/yu> |
| *VeCare: Statistical Acoustic Sensing for Automotive In-Cabin Monitoring* | Yi Zhang et al. | NSDI '23 |  | Fig. 6 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhang-yi> |
| *Fast, Approximate Vector Queries on Very Large Unstructured Datasets* | Zili Zhang et al. | NSDI '23 |  | Fig. 7, 9 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhang-zili> |
| *Acoustic Sensing and Communication Using Metasurface* | Yongzhao Zhang et al. | NSDI '23 |  | Fig. 2, 3 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhang-yongzhao> |
| *The Benefit of Hindsight: Tracing Edge-Cases in Distributed Systems* | Lei Zhang et al. | NSDI '23 | Fig. 1, 2 | Fig. 1, 2 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhang-lei> |
| *SlimWiFi: Ultra-Low-Power IoT Radio Architecture Enabled by Asymmetric Communication* | Renjie Zhao et al. | NSDI '23 | Fig. 12 | Fig. 2, 7, 22 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhao-renjie> |
| *Flattened Clos: Designing High-performance Deadlock-free Expander Data Center Networks Using Graph Contraction* | Shizhen Zhao et al. | NSDI '23 |  | Fig. 2, 11 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhao-shizhen> |
| *Addax: A fast, private, and accountable ad exchange infrastructure* | Ke Zhong et al. | NSDI '23 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhong> |
| *Arya: Arbitrary Graph Pattern Mining with Decomposition-based Sampling* | Zeying Zhu, Kan Wu and Zaoxing Liu | NSDI '23 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi23/presentation/zhu> |
| *Flow Scheduling with Imprecise Knowledge* | Wenxin Li et al. | NSDI '24 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi24/presentation/li-wenxin> |
| *OctoSketch: Enabling Real-Time, Continuous Network Monitoring over Multiple Cores* | Yinda Zhang, Peiqing Chen and Zaoxing Liu | NSDI '24 | Fig. 1 | Fig. 2, 8, 9 |  | <https://www.usenix.org/conference/nsdi24/presentation/zhang-yinda> |
| *MadEye: Boosting Live Video Analytics Accuracy with Adaptive Camera Configurations* | Mike Wong et al. | NSDI '24 | Fig. 8 | Fig. 8 |  | <https://www.usenix.org/conference/nsdi24/presentation/wong> |
| *Towards Domain-Specific Network Transport for Distributed DNN Training* | Hao Wang et al. | NSDI '24 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi24/presentation/wang-hao> |
| *Reverie: Low Pass Filter-Based Switch Buffer Sharing for Datacenters with RDMA and TCP Traffic* | Vamsi Addanki et al. | NSDI '24 |  | Fig. 13 |  | <https://www.usenix.org/conference/nsdi24/presentation/addanki-reverie> |
| *Credence: Augmenting Datacenter Switch Buffer Sharing with ML Predictions* | Vamsi Addanki, Maciej Pacut and Stefan Schmid | NSDI '24 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi24/presentation/addanki-credence> |
| *Towards provably performant congestion control* | Anup Agarwal et al. | NSDI '24 |  | Fig. 6, 14 |  | <https://www.usenix.org/conference/nsdi24/presentation/agarwal-anup> |
| *BBQ: A Fast and Scalable Integer Priority Queue for Hardware Packet Scheduling* | Nirav Atre, Hugo Sadok and Justine Sherry | NSDI '24 |  | Fig. 3, 16 |  | <https://www.usenix.org/conference/nsdi24/presentation/atre> |
| *Application-Level Service Assurance with 5G RAN Slicing* | Arjun Balasingam, Manikanta Kotaru and Paramvir Bahl | NSDI '24 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi24/presentation/balasingam> |
| *TANGO: Secure Collaborative Route Control across the Public Internet* | Henry Birge-Lee et al. | NSDI '24 | Fig. 4 | Fig. 14 |  | <https://www.usenix.org/conference/nsdi24/presentation/birge-lee> |
| *A High-Performance Design, Implementation, Deployment, and Evaluation of The Slim Fly Network* | Nils Blach et al. | NSDI '24 |  | Fig. 2, 3, 4, 15 |  | <https://www.usenix.org/conference/nsdi24/presentation/blach> |
| *mmComb: High-speed mmWave Commodity WiFi Backscatter* | Yoon Chae et al. | NSDI '24 |  | Fig. 3, 4, 9, 10, 14 |  | <https://www.usenix.org/conference/nsdi24/presentation/chae> |
| *GRACE: Loss-Resilient Real-Time Video through Neural Codecs* | Yihua Cheng et al. | NSDI '24 | Fig. 3, 5, 7, 23 | Fig. 5, 6, 7 |  | <https://www.usenix.org/conference/nsdi24/presentation/cheng> |
| *VILAM: Infrastructure-assisted 3D Visual Localization and Mapping for Autonomous Driving* | Jiahe Cui et al. | NSDI '24 |  | Fig. 3, 4, 5 |  | <https://www.usenix.org/conference/nsdi24/presentation/cui> |
| *Orthcatter: High-throughput In-band OFDM Backscatter with Over-the-Air Code Division* | Caihui Du et al. | NSDI '24 |  | Fig. 1, 2, 4, 6 |  | <https://www.usenix.org/conference/nsdi24/presentation/du> |
| *Parcae: Proactive, Liveput-Optimized DNN Training on Preemptible Instances* | Jiangfei Duan et al. | NSDI '24 | Fig. 6, 7 | Fig. 7 |  | <https://www.usenix.org/conference/nsdi24/presentation/duan> |
| *Empower Programmable Pipeline for Advanced Stateful Packet Processing* | Yong Feng et al. | NSDI '24 | Fig. 9 | Fig. 9 |  | <https://www.usenix.org/conference/nsdi24/presentation/feng-yong> |
| *Cloudy with a Chance of Cyberattacks: Dangling Resources Abuse on Cloud Platforms* | Jens Frieß et al. | NSDI '24 |  | Fig. 13 |  | <https://www.usenix.org/conference/nsdi24/presentation/friess> |
| *Sirius: Composing Network Function Chains into P4-Capable Edge Gateways* | Jiaqi Gao et al. | NSDI '24 | Fig. 1 | Fig. 3 |  | <https://www.usenix.org/conference/nsdi24/presentation/gao-jiaqi> |
| *Understanding Routable PCIe Performance for Composable Infrastructures* | Wentao Hou et al. | NSDI '24 | Fig. 12 |  |  | <https://www.usenix.org/conference/nsdi24/presentation/hou> |
| *Characterization of Large Language Model Development in the Datacenter* | Qinghao Hu et al. | NSDI '24 | Fig. 1 | Fig. 1 |  | <https://www.usenix.org/conference/nsdi24/presentation/hu> |
| *Leo: Online ML-based Traffic Classification at Multi-Terabit Line Rate* | Syed Usman Jafri et al. | NSDI '24 |  | Fig. 5, 6, 16 |  | <https://www.usenix.org/conference/nsdi24/presentation/jafri> |
| *Seer: Enabling Future-Aware Online Caching in Networked Systems* | Jason Lei and Vishal Shrivastav | NSDI '24 |  | Fig. 1, 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/lei> |
| *ExChain: Exception Dependency Analysis for Root Cause Diagnosis* | Ao Li et al. | NSDI '24 |  | Fig. 4 |  | <https://www.usenix.org/conference/nsdi24/presentation/li-ao> |
| *Cyclops: A Nanomaterial-based, Battery-Free Intraocular Pressure (IOP) Monitoring System inside Contact Lens* | Liyao Li et al. | NSDI '24 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/li-liyao> |
| *Reasoning about Network Traffic Load Property at Production Scale* | Ruihan Li et al. | NSDI '24 |  | Fig. 5, 7 |  | <https://www.usenix.org/conference/nsdi24/presentation/li-ruihan> |
| *CAPA: An Architecture For Operating Cluster Networks With High Availability* | Bingzhe Liu et al. | NSDI '24 | Fig. 3 |  |  | <https://www.usenix.org/conference/nsdi24/presentation/liu-bingzhe> |
| *Harmonic: Hardware-assisted RDMA Performance Isolation for Public Clouds* | Jiaqi Lou et al. | NSDI '24 | Fig. 2, 5 |  |  | <https://www.usenix.org/conference/nsdi24/presentation/lou> |
| *POSEIDON: A Consolidated Virtual Network Controller that Manages Millions of Tenants via Config Tree* | Biao Lyu et al. | NSDI '24 |  | Fig. 7 |  | <https://www.usenix.org/conference/nsdi24/presentation/lyu> |
| *Klonet: an Easy-to-Use and Scalable Platform for Computer Networks Education* | Tie Ma et al. | NSDI '24 | Fig. 3 | Fig. 1, 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/ma> |
| *Finding Adversarial Inputs for Heuristics using Multi-level Optimization* | Pooria Namyar et al. | NSDI '24 | Fig. 5 | Fig. 10, 23 |  | <https://www.usenix.org/conference/nsdi24/presentation/namyar-finding> |
| *Solving Max-Min Fair Resource Allocations Quickly on Large Graphs* | Pooria Namyar et al. | NSDI '24 | Fig. 5, 18 | Fig. 18 |  | <https://www.usenix.org/conference/nsdi24/presentation/namyar-solving> |
| *Automatic Parallelization of Software Network Functions* | Francisco Pereira, Fernando M. V. Ramos and Luis Pedrosa | NSDI '24 |  | Fig. 2, 4 |  | <https://www.usenix.org/conference/nsdi24/presentation/pereira> |
| *CASSINI: Network-Aware Job Scheduling in Machine Learning Clusters* | Sudarsanan Rajasekaran, Manya Ghobadi and Aditya Akella | NSDI '24 | Fig. 9 | Fig. 4, 9 |  | <https://www.usenix.org/conference/nsdi24/presentation/rajasekaran> |
| *SwiftPaxos: Fast Geo-Replicated State Machines* | Fedor Ryabinin, Alexey Gotsman and Pierre Sutra | NSDI '24 |  | Fig. 6 |  | <https://www.usenix.org/conference/nsdi24/presentation/ryabinin> |
| *Swing: Short-cutting Rings for Higher Bandwidth Allreduce* | Daniele De Sensi et al. | NSDI '24 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/de-sensi> |
| *MESSI: Behavioral Testing of BGP Implementations* | Rathin Singha et al. | NSDI '24 | Fig. 7 | Fig. 7 |  | <https://www.usenix.org/conference/nsdi24/presentation/singha> |
| *OPPerTune: Post-Deployment Configuration Tuning of Services Made Easy* | Gagan Somashekar et al. | NSDI '24 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/somashekar> |
| *AutoSketch: Automatic Sketch-Oriented Compiler for Query-driven Network Telemetry* | Haifeng Sun et al. | NSDI '24 |  | Fig. 3, 13 |  | <https://www.usenix.org/conference/nsdi24/presentation/sun> |
| *NN-Defined Modulator: Reconfigurable and Portable Software Modulator on IoT Gateways* | Jiazhao Wang et al. | NSDI '24 | Fig. 7, 11, 22 | Fig. 5, 6, 7, 11 |  | <https://www.usenix.org/conference/nsdi24/presentation/wang-jiazhao> |
| *Autothrottle: A Practical Bi-Level Approach to Resource Management for SLO-Targeted Microservices* | Zibo Wang et al. | NSDI '24 | Fig. 2 | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/wang-zibo> |
| *Pudica: Toward Near-Zero Queuing Delay in Congestion Control for Cloud Gaming* | Shibo Wang et al. | NSDI '24 | Fig. 1 |  |  | <https://www.usenix.org/conference/nsdi24/presentation/wang-shibo> |
| *The Eternal Tussle: Exploring the Role of Centralization in IPFS* | Yiluo Wei et al. | NSDI '24 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi24/presentation/wei> |
| *Efficient Exposure of Partial Failure Bugs in Distributed Systems with Inferred Abstract States* | Haoze Wu, Jia Pan and Peng Huang | NSDI '24 |  | Fig. 1, 7 |  | <https://www.usenix.org/conference/nsdi24/presentation/wu-haoze> |
| *Load is not what you should balance: Introducing Prequal* | Bartek Wydrowski et al. | NSDI '24 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/wydrowski> |
| *Brain-on-Switch: Towards Advanced Intelligent Network Data Plane via NN-Driven Traffic Analysis at Line-Speed* | Jinzhu Yan et al. | NSDI '24 | Fig. 2, 3 | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/yan> |
| *Horus: Granular In-Network Task Scheduler for Cloud Datacenters* | Parham Yassini et al. | NSDI '24 | Fig. 1 |  |  | <https://www.usenix.org/conference/nsdi24/presentation/yassini> |
| *BFMSense: WiFi Sensing Using Beamforming Feedback Matrix* | Enze Yi et al. | NSDI '24 | Fig. 7 |  |  | <https://www.usenix.org/conference/nsdi24/presentation/yi> |
| *Sidekick: In-Network Assistance for Secure End-to-End Transport Protocols* | Gina Yuan et al. | NSDI '24 |  | Fig. 1 |  | <https://www.usenix.org/conference/nsdi24/presentation/yuan> |
| *Jolteon: Unleashing the Promise of Serverless for Serverless Workflows* | Zili Zhang, Chao Jin and Xin Jin | NSDI '24 |  | Fig. 7 |  | <https://www.usenix.org/conference/nsdi24/presentation/zhang-zili-jolteon> |
| *MuCache: A General Framework for Caching in Microservice Graphs* | Haoran Zhang et al. | NSDI '24 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/zhang-haoran> |
| *Fast Vector Query Processing for Large Datasets Beyond GPU Memory with Reordered Pipelining* | Zili Zhang et al. | NSDI '24 |  | Fig. 1 |  | <https://www.usenix.org/conference/nsdi24/presentation/zhang-zili-pipelining> |
| *Revisiting Congestion Control for Lossless Ethernet* | Yiran Zhang et al. | NSDI '24 | Fig. 5 | Fig. 5, 6 |  | <https://www.usenix.org/conference/nsdi24/presentation/zhang-yiran> |
| *Habitus: Boosting Mobile Immersive Content Delivery through Full-body Pose Tracking and Multipath Networking* | Anlan Zhang et al. | NSDI '24 | Fig. 2 |  |  | <https://www.usenix.org/conference/nsdi24/presentation/zhang-anlan> |
| *TECC: Towards Efficient QUIC Tunneling via Collaborative Transmission Control* | Jiaxing Zhang et al. | NSDI '24 | Fig. 5 | Fig. 8 |  | <https://www.usenix.org/conference/nsdi24/presentation/zhang-jiaxing> |
| *SIEVE is Simpler than LRU: an Efficient Turn-Key Eviction Algorithm for Web Caches* | Yazhuo Zhang et al. | NSDI '24 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/zhang-yazhuo> |
| *EPVerifier: Accelerating Update Storms Verification with Edge-Predicate* | Chenyang Zhao et al. | NSDI '24 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi24/presentation/zhao> |
| *Achieving Wire-Latency Storage Systems by Exploiting Hardware ACKs* | Qing Wang et al. | NSDI '25 |  | Fig. 1, 5 |  | <https://www.usenix.org/conference/nsdi25/presentation/wang-qing> |
| *Mitigating Scalability Walls of RDMA-based Container Networks* | Wei Liu et al. | NSDI '25 |  | Fig. 21 |  | <https://www.usenix.org/conference/nsdi25/presentation/liu-wei> |
| *Everything Matters in Programmable Packet Scheduling* | Albert Gran Alcoz et al. | NSDI '25 |  | Fig. 16, 19 |  | <https://www.usenix.org/conference/nsdi25/presentation/alcoz> |
| *Tooth: Toward Optimal Balance of Video QoE and Redundancy Cost by Fine-Grained FEC in Cloud Gaming Streaming* | Congkai An et al. | NSDI '25 | Fig. 15 |  |  | <https://www.usenix.org/conference/nsdi25/presentation/an> |
| *Preventing Network Bottlenecks: Accelerating Datacenter Services with Hotspot-Aware Placement for Compute and Storage* | Hamid Hajabdolali Bazzaz et al. | NSDI '25 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi25/presentation/bazzaz> |
| *eTran: Extensible Kernel Transport with eBPF* | Zhongjie Chen et al. | NSDI '25 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi25/presentation/chen-zhongjie> |
| *Minder: Faulty Machine Detection for Large-scale Distributed Model Training* | Yangtao Deng et al. | NSDI '25 | Fig. 7 | Fig. 7 |  | <https://www.usenix.org/conference/nsdi25/presentation/deng> |
| *PRED: Performance-oriented Random Early Detection for Consistently Stable Performance in Datacenters* | Xinle Du et al. | NSDI '25 |  | Fig. 6, 9 |  | <https://www.usenix.org/conference/nsdi25/presentation/du> |
| *DISC: Backpressure Mitigation In Multi-tier Applications With Distributed Shared Connection* | Brice Ekane et al. | NSDI '25 |  | Fig. 8 |  | <https://www.usenix.org/conference/nsdi25/presentation/ekane> |
| *The Benefits and Limitations of User Interrupts for Preemptive Userspace Scheduling* | Linsong Guo et al. | NSDI '25 |  | Fig. 3, 4 |  | <https://www.usenix.org/conference/nsdi25/presentation/guo> |
| *Efficient Multi-WAN Transport for 5G with OTTER* | Mary Hogan et al. | NSDI '25 | Fig. 4 |  |  | <https://www.usenix.org/conference/nsdi25/presentation/hogan> |
| *Smart Casual Verification of the Confidential Consortium Framework* | Heidi Howard et al. | NSDI '25 | Fig. 1 | Fig. 1 |  | <https://www.usenix.org/conference/nsdi25/presentation/howard> |
| *Ladder: A Convergence-based Structured DAG Blockchain for High Throughput and Low Latency* | Dengcheng Hu et al. | NSDI '25 |  | Fig. 3, 4 |  | <https://www.usenix.org/conference/nsdi25/presentation/hu> |
| *Building an Elastic Block Storage over EBOFs Using Shadow Views* | Sheng Jiang and Ming Liu | NSDI '25 | Fig. 1 | Fig. 3 |  | <https://www.usenix.org/conference/nsdi25/presentation/jiang> |
| *Understanding and Profiling NVMe-over-TCP Using ntprof* | Yuyuan Kang and Ming Liu | NSDI '25 | Fig. 4 | Fig. 4 |  | <https://www.usenix.org/conference/nsdi25/presentation/kang> |
| *SuperServe: Fine-Grained Inference Serving for Unpredictable Workloads* | Alind Khare et al. | NSDI '25 | Fig. 7 | Fig. 3, 7 |  | <https://www.usenix.org/conference/nsdi25/presentation/khare> |
| *Pushing the Limits of In-Network Caching for Key-Value Stores* | Gyuyeong Kim | NSDI '25 | Fig. 6 | Fig. 6 |  | <https://www.usenix.org/conference/nsdi25/presentation/kim> |
| *Beehive: A Scalable Disaggregated Memory Runtime Exploiting Asynchrony of Multithreaded Programs* | Quanxi Li et al. | NSDI '25 | Fig. 1, 3 | Fig. 1 |  | <https://www.usenix.org/conference/nsdi25/presentation/li-quanxi> |
| *Dissecting and Streamlining the Interactive Loop of Mobile Cloud Gaming* | Yang Li et al. | NSDI '25 | Fig. 2, 19 |  |  | <https://www.usenix.org/conference/nsdi25/presentation/li-yang> |
| *NDD: A Decision Diagram for Network Verification* | Zechun Li et al. | NSDI '25 | Fig. 4 | Fig. 22 |  | <https://www.usenix.org/conference/nsdi25/presentation/li-zechun> |
| *PreAcher: Secure and Practical Password Pre-Authentication by Content Delivery Networks* | Shihan Lin et al. | NSDI '25 |  | Fig. 1 |  | <https://www.usenix.org/conference/nsdi25/presentation/lin-shihan> |
| *ONCache: A Cache-Based Low-Overhead Container Overlay Network* | Shengkai Lin et al. | NSDI '25 | Fig. 10 | Fig. 11 |  | <https://www.usenix.org/conference/nsdi25/presentation/lin-shengkai> |
| *Unlocking ECMP Programmability for Precise Traffic Control* | Yadong Liu et al. | NSDI '25 |  | Fig. 3, 5 |  | <https://www.usenix.org/conference/nsdi25/presentation/liu-yadong> |
| *Pyrrha: Congestion-Root-Based Flow Control to Eliminate Head-of-Line Blocking in Datacenter* | Kexin Liu et al. | NSDI '25 |  | Fig. 6 |  | <https://www.usenix.org/conference/nsdi25/presentation/liu-kexin> |
| *One-Size-Fits-None: Understanding and Enhancing Slow-Fault Tolerance in Modern Distributed Systems* | Ruiming Lu et al. | NSDI '25 | Fig. 7, 9 | Fig. 9, 19, 21 |  | <https://www.usenix.org/conference/nsdi25/presentation/lu> |
| *Securing Public Cloud Networks with Efficient Role-based Micro-Segmentation* | Sathiya Kumaran Mani et al. | NSDI '25 | Fig. 4 | Fig. 4, 6 |  | <https://www.usenix.org/conference/nsdi25/presentation/mani> |
| *Enhancing Network Failure Mitigation with Performance-Aware Ranking* | Pooria Namyar et al. | NSDI '25 | Fig. 5 |  |  | <https://www.usenix.org/conference/nsdi25/presentation/namyar> |
| *A Layered Formal Methods Approach to Answering Queue-related Queries* | Divya Raghunathan, Maria Apostolaki and Aarti Gupta | NSDI '25 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi25/presentation/raghunathan> |
| *Quicksand: Harnessing Stranded Datacenter Resources with Granular Computing* | Zhenyuan Ruan et al. | NSDI '25 | Fig. 2 |  |  | <https://www.usenix.org/conference/nsdi25/presentation/ruan> |
| *GRANNY: Granular Management of Compute-Intensive Applications in the Cloud* | Carlos Segarra et al. | NSDI '25 | Fig. 2, 4 | Fig. 1 |  | <https://www.usenix.org/conference/nsdi25/presentation/segarra> |
| *PAPAYA Federated Analytics Stack: Engineering Privacy, Scalability and Practicality* | Harish Srinivas et al. | NSDI '25 |  | Fig. 4 |  | <https://www.usenix.org/conference/nsdi25/presentation/srinivas> |
| *ByteCheckpoint: A Unified Checkpointing System for Large Foundation Model Development* | Borui Wan et al. | NSDI '25 |  | Fig. 2, 3, 9 |  | <https://www.usenix.org/conference/nsdi25/presentation/wan-borui> |
| *SimAI: Unifying Architecture Design and Performance Tuning for Large-Scale Large Language Model Training with Scalability and Precision* | Xizheng Wang et al. | NSDI '25 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi25/presentation/wang-xizheng-simai> |
| *Region-based Content Enhancement for Efficient Video Analytics at the Edge* | Weijun Wang et al. | NSDI '25 | Fig. 12 | Fig. 7, 12 |  | <https://www.usenix.org/conference/nsdi25/presentation/wang-weijun> |
| *ODRP: On-Demand Remote Paging with Programmable RDMA* | Zixuan Wang et al. | NSDI '25 |  | Fig. 2, 5, 6 |  | <https://www.usenix.org/conference/nsdi25/presentation/wang-zixuan> |
| *OptiReduce: Resilient and Tail-Optimal AllReduce for Distributed Deep Learning in the Cloud* | Ertza Warraich et al. | NSDI '25 | Fig. 4 | Fig. 4, 6 |  | <https://www.usenix.org/conference/nsdi25/presentation/warraich> |
| *Building Massive MIMO Baseband Processing on a Single-Node Supercomputer* | Xincheng Xie et al. | NSDI '25 | Fig. 7 |  |  | <https://www.usenix.org/conference/nsdi25/presentation/xie> |
| *Rajomon: Decentralized and Coordinated Overload Control for Latency-Sensitive Microservices* | Jiali Xing et al. | NSDI '25 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi25/presentation/xing> |
| *State-Compute Replication: Parallelizing High-Speed Stateful Packet Processing* | Qiongwen Xu et al. | NSDI '25 |  | Fig. 3, 12 |  | <https://www.usenix.org/conference/nsdi25/presentation/xu-qiongwen> |
| *Vegeta: Enabling Parallel Smart Contract Execution in Leaderless Blockchains* | Tianjing Xu et al. | NSDI '25 |  | Fig. 1, 4, 5, 6 |  | <https://www.usenix.org/conference/nsdi25/presentation/xu-tianjing> |
| *GPU-Disaggregated Serving for Deep Learning Recommendation Models at Scale* | Lingyun Yang et al. | NSDI '25 | Fig. 5, 7 | Fig. 12 |  | <https://www.usenix.org/conference/nsdi25/presentation/yang> |
| *Learning Production-Optimized Congestion Control Selection for Alibaba Cloud CDN* | Xuan Zeng et al. | NSDI '25 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi25/presentation/zeng> |
| *On Temporal Verification of Stateful P4 Programs* | Delong Zhang, Chong Ye and Fei He | NSDI '25 |  | Fig. 7 |  | <https://www.usenix.org/conference/nsdi25/presentation/zhang-delong> |
| *White-Boxing RDMA with Packet-Granular Software Control* | Chenxingyu Zhao et al. | NSDI '25 |  | Fig. 6, 7 |  | <https://www.usenix.org/conference/nsdi25/presentation/zhao-chenxingyu> |
| *When P4 Meets Run-to-completion Architecture* | Hao Zheng et al. | NSDI '25 | Fig. 4 |  |  | <https://www.usenix.org/conference/nsdi25/presentation/zheng-hao> |
| *High-level Programming for Application Networks* | Xiangfeng Zhu et al. | NSDI '25 |  | Fig. 2, 6 |  | <https://www.usenix.org/conference/nsdi25/presentation/zhu> |
| *FRCC: Towards Provably Fair and Robust Congestion Control* | Anup Agarwal, Venkat Arun and Srinivasan Seshan | NSDI '26 |  | Fig. 13 |  | <https://www.usenix.org/conference/nsdi26/presentation/agarwal-anup> |
| *Uber's Failover Architecture: Reconciling Reliability and Efficiency in Hyperscale Microservice Infrastructure* | Mayank Bansal et al. | NSDI '26 | Fig. 1 | Fig. 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/bansal> |
| *Themis: Detecting Distributed Concurrency Bugs through RPC-Driven Race-Directed Test Generation and Fuzzing* | Hongchen Cao et al. | NSDI '26 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi26/presentation/cao> |
| *Net-P4ct: Enhanced WAN Bandwidth Fair Sharing Using P4 Programmable Switches* | Haoran Chen et al. | NSDI '26 |  | Fig. 6 |  | <https://www.usenix.org/conference/nsdi26/presentation/chen> |
| *FLARE: Anomaly Diagnostics for Divergent LLM Training in GPU Clusters of Thousand-Plus Scale* | Weihao Cui et al. | NSDI '26 | Fig. 5 | Fig. 2, 5, 6 |  | <https://www.usenix.org/conference/nsdi26/presentation/cui> |
| *Mitigating CPU Frontend for Complex Data Plane Applications* | Yihan Dang et al. | NSDI '26 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi26/presentation/dang> |
| *A Systematic Threat Analysis and Practical Attacks on Automated Frequency Coordination Systems* | Yilu Dong et al. | NSDI '26 | Fig. 1 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/dong> |
| *Bifrost: Alibaba's Next-Generation VPC Network with High-Performance Multipath Reliable Transport* | Zihao Fan et al. | NSDI '26 | Fig. 10 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/fan> |
| *PlanetServe: A Decentralized, Scalable, and Privacy-Preserving Overlay for Democratizing Large Language Model Serving* | Fei Fang et al. | NSDI '26 | Fig. 4 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/fang> |
| *Sparse Checkpointing for Fast and Reliable MoE Training* | Swapnil Gandhi and Christos Kozyrakis | NSDI '26 | Fig. 9 | Fig. 3, 14 |  | <https://www.usenix.org/conference/nsdi26/presentation/gandhi> |
| *FENIX: Enabling In-Network DNN Inference with FPGA-Enhanced Programmable Switches* | Xiangyu Gao et al. | NSDI '26 |  | Fig. 5, 7 |  | <https://www.usenix.org/conference/nsdi26/presentation/gao> |
| *Who Watches the Watchers? On the Reliability of Softwarizing Cloud Application Management* | Jiawei Tyler Gu et al. | NSDI '26 |  | Fig. 1 |  | <https://www.usenix.org/conference/nsdi26/presentation/gu> |
| *ZOC: Elastic and Cost-Efficient Virtual SmartNIC Architecture for Cloud Physical Machines* | Naixuan Guan et al. | NSDI '26 | Fig. 2, 5 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/guan-naixuan> |
| *EROICA: Online Performance Troubleshooting for Large-scale Model Training* | Yu Guan et al. | NSDI '26 | Fig. 1, 2, 8 | Fig. 1, 8 |  | <https://www.usenix.org/conference/nsdi26/presentation/guan-yu> |
| *Skyline: A Cloud Centric Internet Monitoring Engine* | Shixian Guo et al. | NSDI '26 |  | Fig. 3, 5, 15 |  | <https://www.usenix.org/conference/nsdi26/presentation/guo-shixian> |
| *Building A CSFQ-Inspired Transport for Switched CXL Memory Pooling* | Zerui Guo, Emily Shriver and Ming Liu | NSDI '26 | Fig. 1 | Fig. 1 |  | <https://www.usenix.org/conference/nsdi26/presentation/guo-zerui> |
| *MoCE: A Mixture-of-Context Aware Experts Framework for Troubleshooting Internet-scale Services* | Vipul Harsh et al. | NSDI '26 | Fig. 3, 8 | Fig. 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/harsh> |
| *Making Logic a First-Class Citizen in Generative ML for Networking* | Hongyu Hè, Minhao Jin and Maria Apostolaki | NSDI '26 | Fig. 3 | Fig. 2, 3 |  | <https://www.usenix.org/conference/nsdi26/presentation/he> |
| *Stimpack: An Adaptive Rendering Optimization System for Scalable Cloud Gaming* | Jin Heo et al. | NSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi26/presentation/heo> |
| *Come Hell or Still Water: Alleviating Tail Latency in Cloud Block Store* | Chaolei Hu et al. | NSDI '26 | Fig. 8 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/hu-chaolei> |
| *Lemonshark: Asynchronous DAG-BFT With Early Finality* | Michael Yiqing Hu et al. | NSDI '26 | Fig. 5, 9, 18 | Fig. 14 |  | <https://www.usenix.org/conference/nsdi26/presentation/hu-michael> |
| *Fractal: Fault-Tolerant Shell-Script Distribution* | Zhicheng Huang et al. | NSDI '26 | Fig. 3 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/huang> |
| *CCC: Re-architecting Delay-based Congestion Control in Datacenter Networks* | Wanchun Jiang et al. | NSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi26/presentation/jiang> |
| *RASC: Enhancing Observability & Programmability in Smart Spaces* | Anna Karanika et al. | NSDI '26 |  | Fig. 2, 3, 8 |  | <https://www.usenix.org/conference/nsdi26/presentation/karanika> |
| *Heuristic Analysis from Source Code via Symbolic-Guided Optimization* | Pantea Karimi et al. | NSDI '26 |  | Fig. 3, 5 |  | <https://www.usenix.org/conference/nsdi26/presentation/karimi> |
| *Latency-Aware Caching with Delayed Hits: From Bursty Traffic to Pipeline Architectures* | Nadav Keren, Gil Einziger and Gabriel Scalosub | NSDI '26 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi26/presentation/keren> |
| *CrossCheck: Input Validation for WAN Control Systems* | Alexander Krentsel et al. | NSDI '26 |  | Fig. 13 |  | <https://www.usenix.org/conference/nsdi26/presentation/krentsel> |
| *QCON: Seamless QoE-Aware 5G Streaming via Multi-Connectivity* | Goodsol Lee et al. | NSDI '26 | Fig. 7 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/lee> |
| *SyncWise: Error-Aware Time Synchronization for Reconfigurable Data Center Networks* | Yiming Lei et al. | NSDI '26 | Fig. 1 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/lei-syncwise> |
| *FAST: An Efficient Scheduler for All-to-All GPU Communication* | Yiran Lei et al. | NSDI '26 | Fig. 1 | Fig. 1, 3, 5, 6, 7 |  | <https://www.usenix.org/conference/nsdi26/presentation/lei-yiran> |
| *OpenOptics: Enabling Open Research and Implementation of Optical Data Center Networks* | Yiming Lei et al. | NSDI '26 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi26/presentation/lei-optical> |
| *Pilot Execution: Simulating Failure Recovery In Situ for Production Distributed Systems* | Zhenyu Li, Angting Cai and Chang Lou | NSDI '26 |  | Fig. 1, 3, 6 |  | <https://www.usenix.org/conference/nsdi26/presentation/li-zhenyu> |
| *Feedback-guided Adaptive Testing of Distributed Systems Designs* | Ao Li, Ankush Desai and Rohan Padhye | NSDI '26 |  | Fig. 1 |  | <https://www.usenix.org/conference/nsdi26/presentation/li> |
| *SwiftEP: Accelerating MoE Inference with Buffer Fusion and TMA Offloading* | Xingyi Li et al. | NSDI '26 |  | Fig. 1, 13 |  | <https://www.usenix.org/conference/nsdi26/presentation/li-xingyi> |
| *CStar Gateway: Augmenting Public Cloud Infrastructure for Heterogeneous Network Function Virtualization* | Haonan Li et al. | NSDI '26 |  | Fig. 2, 10 |  | <https://www.usenix.org/conference/nsdi26/presentation/li-haonan> |
| *SLATE: Service Layer Traffic Engineering* | Gangmuk Lim et al. | NSDI '26 |  | Fig. 4, 5, 15 |  | <https://www.usenix.org/conference/nsdi26/presentation/lim> |
| *DroidSpeak: KV Cache Sharing Across Fine-tuned Model Variants* | Yuhan Liu et al. | NSDI '26 | Fig. 1 | Fig. 1, 6 |  | <https://www.usenix.org/conference/nsdi26/presentation/liu-yuhan> |
| *Geminet: Learning the Duality-based Topology-Agnostic Update Operator for Lightweight Traffic Engineering in Changing Topologies* | Ximeng Liu et al. | NSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi26/presentation/liu-ximeng> |
| *Decoding RSSI Compression in RFID: Dynamic RCS Modeling and Tag-Intrinsic Power Metrics for Reliable Backscatter Networks* | Jia Liu et al. | NSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi26/presentation/liu-jia> |
| *HydraServe: Minimizing Cold Start Latency for Serverless LLM Serving in Public Clouds* | Chiheng Lou et al. | NSDI '26 | Fig. 3 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/lou> |
| *CascadeNet: Generating Network Traffic with High-Fidelity Temporal Patterns* | Runwei Lu et al. | NSDI '26 |  | Fig. 3 |  | <https://www.usenix.org/conference/nsdi26/presentation/lu-runwei> |
| *Agentix: An Efficient Serving Engine for LLM Agents as General Programs* | Michael Luo et al. | NSDI '26 | Fig. 8 | Fig. 19 |  | <https://www.usenix.org/conference/nsdi26/presentation/luo> |
| *A Fast Solver-Free Algorithm for Traffic Engineering in Large-Scale Data Center Network* | Yingming Mao et al. | NSDI '26 | Fig. 2, 4 | Fig. 2, 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/mao> |
| *MAE: More Adaptive Video Encoder for Consistent Low Latency in High-Quality Real-Time Communication* | Hua Meng et al. | NSDI '26 | Fig. 11 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/meng> |
| *Defeating Slow-and-Low Threats via Diffusion Model-based Generative Inference* | Seyed Mohammad Mehdi Mirnajafizadeh et al. | NSDI '26 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi26/presentation/mirnajafizadeh> |
| *FlexLLM: Token-Level Co-Serving of LLM Inference and Finetuning with SLO Guarantees* | Gabriele Oliaro et al. | NSDI '26 | Fig. 2, 4, 6 | Fig. 2, 4, 7 |  | <https://www.usenix.org/conference/nsdi26/presentation/oliaro> |
| *Syntra: Synthesizing Cross-Layer Controllers for Low-Latency Video Streaming* | Jia Pan et al. | NSDI '26 |  | Fig. 2 |  | <https://www.usenix.org/conference/nsdi26/presentation/pan> |
| *SPLIDT: Partitioned Decision Trees for Scalable Stateful Inference at Line Rate* | Murayyiam Parvez et al. | NSDI '26 |  | Fig. 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/parvez> |
| *KUBEDIRECT: Unleashing the Full Power of the Cluster Manager for Serverless Computing* | Sheng Qi et al. | NSDI '26 | Fig. 2 | Fig. 2 |  | <https://www.usenix.org/conference/nsdi26/presentation/qi> |
| *Phantora: Maximizing Code Reuse in Simulation-based Machine Learning System Performance Estimation* | Jianxing Qin et al. | NSDI '26 | Fig. 3 | Fig. 3, 5, 6 |  | <https://www.usenix.org/conference/nsdi26/presentation/qin> |
| *Remembrall: Leaning into Memory for Accurate Video Analytics on System-on-Chip GPUs* | Murali Ramanujam et al. | NSDI '26 |  | Fig. 8 |  | <https://www.usenix.org/conference/nsdi26/presentation/ramanujam> |
| *Cortex: Achieving Low-Latency, Cost-Efficient Remote Data Access For LLM via Semantic-Aware Knowledge Caching* | Chaoyi Ruan et al. | NSDI '26 | Fig. 1, 4 | Fig. 1, 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/ruan-cortex> |
| *Libra: Flexible Request Partitioning and Scheduling for Serving Unbalanced and Dynamic LLM Workloads* | Chaoyi Ruan et al. | NSDI '26 | Fig. 4 | Fig. 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/ruan-libra> |
| *Wallet: Confidential Serverless Computing* | Patrick Sabanic et al. | NSDI '26 | Fig. 6 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/sabanic> |
| *PD3: Prefetching Data with DPUs for Disaggregated Memory* | Sidharth Sankhe et al. | NSDI '26 |  | Fig. 3, 6 |  | <https://www.usenix.org/conference/nsdi26/presentation/sankhe> |
| *EZ-SAVE: Evaluation of Easy-to-Deploy Source Address Validation Policies* | Nicholas Scaglione et al. | NSDI '26 | Fig. 3 | Fig. 3 |  | <https://www.usenix.org/conference/nsdi26/presentation/scaglione> |
| *Queue-Mem: Energy-Efficient Hardware Storage for Advanced Network Function Acceleration* | Mariano Scazzariello et al. | NSDI '26 |  | Fig. 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/scazzariello> |
| *BURST: Seeking High-performance, Interoperability and Scalability in Soft-RDMA* | Huijun Shen et al. | NSDI '26 |  | Fig. 7 |  | <https://www.usenix.org/conference/nsdi26/presentation/shen> |
| *SYMI: Efficient Mixture-of-Experts Training via Model and Optimizer State Decoupling* | Athinagoras Skiadopoulos et al. | NSDI '26 |  | Fig. 6 |  | <https://www.usenix.org/conference/nsdi26/presentation/skiadopoulos> |
| *ZooRoute: Enhancing Cloud-Scale Network Reliability via Candidate Path Provisioning and Overlay Proactive Rerouting* | Xiaoqing Sun et al. | NSDI '26 | Fig. 6, 13 | Fig. 8, 14 |  | <https://www.usenix.org/conference/nsdi26/presentation/sun> |
| *eXpressSFU: Toward Super-Scalable Video Conferencing with SmartNICs* | Tuan Tran et al. | NSDI '26 |  | Fig. 9 |  | <https://www.usenix.org/conference/nsdi26/presentation/tran> |
| *Enabling AI Network Cross-Layer Design and Operations with Arcadia: A Simulation Platform at Scale* | Zhaodong Wang et al. | NSDI '26 |  | Fig. 25 |  | <https://www.usenix.org/conference/nsdi26/presentation/wang-zhaodong> |
| *OneSidedMW: Managing Disaggregated Memory Efficiently, Flexibly, and Securely with RNIC Offloading* | Zixuan Wang et al. | NSDI '26 | Fig. 3 | Fig. 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/wang-zixuan> |
| *HCDN: Coordinated Stream Scheduling for Cost-Effective Live Video Delivery* | Liying Wang et al. | NSDI '26 |  | Fig. 1 |  | <https://www.usenix.org/conference/nsdi26/presentation/wang-liying> |
| *HyperEdge: An Edge CDN Infrastructure for Cost Efficient Video Streaming* | Dehui Wei et al. | NSDI '26 | Fig. 2 | Fig. 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/wei> |
| *Attack of the Bubbles: Straggler-Resilient Pipeline Parallelism for Large Model Training* | Tianyuan Wu et al. | NSDI '26 |  | Fig. 12 |  | <https://www.usenix.org/conference/nsdi26/presentation/wu-tianyuan> |
| *Offloading Cloud Network Services at Production Scale with SONiC DASH SmartSwitch* | Shaofeng Wu et al. | NSDI '26 | Fig. 1 | Fig. 2, 4 |  | <https://www.usenix.org/conference/nsdi26/presentation/wu-shaofeng> |
| *FastServe: Iteration-Level Preemptive Scheduling for Large Language Model Inference* | Bingyang Wu et al. | NSDI '26 |  | Fig. 3, 6 |  | <https://www.usenix.org/conference/nsdi26/presentation/wu-bingyang> |
| *REAL: Emulating Control Plane at Simulator's Cost* | Ze Xia et al. | NSDI '26 | Fig. 7 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/xia> |
| *ServeGen: Workload Characterization and Generation of Large Language Model Serving in Production* | Yuxing Xiang et al. | NSDI '26 |  | Fig. 18 |  | <https://www.usenix.org/conference/nsdi26/presentation/xiang-servegen> |
| *Slowpoke: End-to-end Throughput Optimization Modeling for Microservice Applications* | Yizheng Xie et al. | NSDI '26 | Fig. 4 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/xie> |
| *FalconFS: Distributed File System for Large-Scale Deep Learning Pipeline* | Jingwei Xu et al. | NSDI '26 | Fig. 7, 8 | Fig. 1, 7, 8 |  | <https://www.usenix.org/conference/nsdi26/presentation/xu> |
| *MuxTune: Efficient Multi-Task LLM Fine-Tuning in Multi-Tenant Datacenters via Spatial-Temporal Backbone Multiplexing* | Chunyu Xue et al. | NSDI '26 |  | Fig. 6, 8, 11 |  | <https://www.usenix.org/conference/nsdi26/presentation/xue-chunyu> |
| *KeepON: Supporting Deterministic Traffic on Standard NICs* | Chuanyu Xue et al. | NSDI '26 |  | Fig. 21 |  | <https://www.usenix.org/conference/nsdi26/presentation/xue-chuanyu> |
| *MORP4: A Dynamic Network Telescope* | Iliana Xygkou et al. | NSDI '26 |  | Fig. 15 |  | <https://www.usenix.org/conference/nsdi26/presentation/xygkou> |
| *Diagnosing and Repairing Distributed Routing Configurations Using Selective Symbolic Simulation* | Rulan Yang et al. | NSDI '26 | Fig. 4, 7 | Fig. 4, 6, 7 |  | <https://www.usenix.org/conference/nsdi26/presentation/yang> |
| *HybridMesh: A Hardware-software Hybrid Approach for Accelerating Service Mesh Ingress* | Myoungsung You et al. | NSDI '26 | Fig. 1, 4 | Fig. 5 |  | <https://www.usenix.org/conference/nsdi26/presentation/you> |
| *Themis: Scheduling-Aware Buffer Management for HBM-Based Hybrid Buffers* | Zhiyu Zhang et al. | NSDI '26 | Fig. 8 | Fig. 2, 3, 8 |  | <https://www.usenix.org/conference/nsdi26/presentation/zhang-zhiyu> |
| *SmartNIC-Enabled Live Migration for Storage-Optimized VMs with PYROCUMULUS* | Jiechen Zhao et al. | NSDI '26 | Fig. 3, 4 |  |  | <https://www.usenix.org/conference/nsdi26/presentation/zhao-jiechen> |
| *Octopus: Enhancing CXL Memory Pods via Sparse Topology* | Yuhong Zhong et al. | NSDI '26 | Fig. 1 | Fig. 1 |  | <https://www.usenix.org/conference/nsdi26/presentation/zhong> |
| *AnyPro: Preference-Preserving Anycast Optimization based on Strategic AS-Path Prepending* | Minyuan Zhou et al. | NSDI '26 |  | Fig. 1, 3, 5, 11 |  | <https://www.usenix.org/conference/nsdi26/presentation/zhou-minyuan> |
| *Controlling Arbitrary Internet Queues with Titrate* | Anchengcheng Zhou et al. | NSDI '26 |  | Fig. 5 |  | <https://www.usenix.org/conference/nsdi26/presentation/zhou-titrate> |
| *Detecting and Diagnosing Errors in Serving Archived Web Pages* | Jingyuan Zhu, Huanchen Sun and Harsha V. Madhyastha | NSDI '26 |  | Fig. 7 |  | <https://www.usenix.org/conference/nsdi26/presentation/zhu-jingyuan> |
| *Bagpipe: Accelerating Deep Recommendation Model Training* | Saurabh Agarwal et al. | SOSP '23 | Fig. 5 |  |  | <https://doi.org/10.1145/3600006.3613142> |
| *Acto: Automatic End-to-End Testing for Operation Correctness of Cloud System Management* | Jiawei Tyler Gu et al. | SOSP '23 | Fig. 3 | Fig. 1 |  | <https://doi.org/10.1145/3600006.3613161> |
| *Mira: A Program-Behavior-Guided Far Memory System* | Zhiyuan Guo, Zijian He and Yiying Zhang | SOSP '23 | Fig. 2 |  |  | <https://doi.org/10.1145/3600006.3613157> |
| *Private Web Search with Tiptoe* | Alexandra Henzinger et al. | SOSP '23 |  | Fig. 2 |  | <https://doi.org/10.1145/3600006.3613134> |
| *PVM: Efficient Shadow Paging for Deploying Secure Containers in Cloud-native Environment* | Hang Huang et al. | SOSP '23 | Fig. 3 | Fig. 8 |  | <https://doi.org/10.1145/3600006.3613158> |
| *Oobleck: Resilient Distributed Training of Large Models Using Pipeline Templates* | Insu Jang et al. | SOSP '23 | Fig. 3, 4 | Fig. 3, 4, 7 |  | <https://doi.org/10.1145/3600006.3613152> |
| *Falcon: Fast OLTP Engine for Persistent Cache and Non-Volatile Memory* | Zhicheng Ji et al. | SOSP '23 |  | Fig. 1, 6 |  | <https://doi.org/10.1145/3600006.3613141> |
| *Turbo: Effective Caching in Differentially-Private Databases* | Kelly Kostopoulou et al. | SOSP '23 |  | Fig. 1, 2, 4, 5 |  | <https://doi.org/10.1145/3600006.3613174> |
| *Efficient Memory Management for Large Language Model Serving with PagedAttention* | Woosuk Kwon et al. | SOSP '23 | Fig. 4, 5 | Fig. 8, 10 |  | <https://doi.org/10.1145/3600006.3613165> |
| *Siloz: Leveraging DRAM Isolation Domains to Prevent Inter-VM Rowhammer* | Kevin Loughlin et al. | SOSP '23 |  | Fig. 3 |  | <https://doi.org/10.1145/3600006.3613143> |
| *Halfmoon: Log-Optimal Fault-Tolerant Stateful Serverless Computing* | Sheng Qi, Xuanzhe Liu and Xin Jin | SOSP '23 |  | Fig. 8 |  | <https://doi.org/10.1145/3600006.3613154> |
| *RackBlox: A Software-Defined Rack-Scale Storage System with Network-Storage Co-Design* | Benjamin Reidys et al. | SOSP '23 |  | Fig. 7 |  | <https://doi.org/10.1145/3600006.3613170> |
| *Ditto: An Elastic and Adaptive Memory-Disaggregated Caching System* | Jiacheng Shen et al. | SOSP '23 | Fig. 8 | Fig. 6, 8, 12 |  | <https://doi.org/10.1145/3600006.3613144> |
| *UGACHE: A Unified GPU Cache for Embedding-based Deep Learning* | Xiaoniu Song et al. | SOSP '23 |  | Fig. 7 |  | <https://doi.org/10.1145/3600006.3613169> |
| *Sia: Heterogeneity-aware, goodput-optimized ML-cluster scheduling* | Suhas Jayaram Subramanya et al. | SOSP '23 |  | Fig. 3 | CC BY 4.0 | <https://doi.org/10.1145/3600006.3613175> |
| *GEMINI: Fast Failure Recovery in Distributed Training with In-Memory Checkpoints* | Zhuang Wang et al. | SOSP '23 |  | Fig. 2 |  | <https://doi.org/10.1145/3600006.3613145> |
| *TreeSLS: A Whole-system Persistent Microkernel with Tree-structured State Checkpoint on NVM* | Fangnuo Wu et al. | SOSP '23 | Fig. 2 |  |  | <https://doi.org/10.1145/3600006.3613160> |
| *PIT: Optimization of Dynamic Sparse Deep Learning Models via Permutation Invariant Transformation* | Ningxin Zheng et al. | SOSP '23 |  | Fig. 4 |  | <https://doi.org/10.1145/3600006.3613139> |
| *Automated Verification of an In-Production DNS Authoritative Engine* | Naiqian Zheng et al. | SOSP '23 |  | Fig. 11 |  | <https://doi.org/10.1145/3600006.3613153> |
| *Enabling High-Performance and Secure Userspace NVM File Systems with the Trio Architecture* | Diyu Zhou et al. | SOSP '23 |  | Fig. 2 |  | <https://doi.org/10.1145/3600006.3613171> |
| *Reducing Energy Bloat in Large Model Training* | Jae-Won Chung et al. | SOSP '24 | Fig. 4 | Fig. 4 |  | <https://doi.org/10.1145/3694715.3695970> |
| *Apparate: Rethinking Early Exits to Tame Latency-Throughput Tensions in ML Serving* | Yinwei Dai et al. | SOSP '24 | Fig. 3, 7 | Fig. 3, 6 |  | <https://doi.org/10.1145/3694715.3695963> |
| *NOPE: Strengthening domain authentication with succinct proofs* | Zachary DeStefano et al. | SOSP '24 |  | Fig. 1, 2 |  | <https://doi.org/10.1145/3694715.3695962> |
| *ReCycle: Resilient Training of Large DNNs using Pipeline Adaptation* | Swapnil Gandhi et al. | SOSP '24 | Fig. 2, 7, 8 | Fig. 2, 7 |  | <https://doi.org/10.1145/3694715.3695960> |
| *Caribou: Fine-Grained Geospatial Shifting of Serverless Applications for Sustainability* | Viktor Urban Gsteiger et al. | SOSP '24 | Fig. 6 |  |  | <https://doi.org/10.1145/3694715.3695954> |
| *VPRI: Efficient I/O Page Fault Handling via Software-Hardware Co-Design for IaaS Clouds* | Kaijie Guo et al. | SOSP '24 |  | Fig. 12, 14 |  | <https://doi.org/10.1145/3694715.3695957> |
| *TrEnv: Transparently Share Serverless Execution Environments Across Different Functions and Nodes* | Jialiang Huang et al. | SOSP '24 | Fig. 9 | Fig. 2, 9 | CC BY 4.0 | <https://doi.org/10.1145/3694715.3695967> |
| *Improving DNN Inference Throughput Using Practical, Per-Input Compute Adaptation* | Anand Padmanabha Iyer et al. | SOSP '24 |  | Fig. 1 |  | <https://doi.org/10.1145/3694715.3695978> |
| *Skyloft: A General High-Efficient Scheduling Framework in User Space* | Yuekai Jia et al. | SOSP '24 | Fig. 3 | Fig. 3 |  | <https://doi.org/10.1145/3694715.3695973> |
| *Scaling Deep Learning Computation over the Inter-Core Connected Intelligence Processor with T10* | Yiqi Liu et al. | SOSP '24 | Fig. 3, 4 | Fig. 3, 4, 6, 7, 11 |  | <https://doi.org/10.1145/3694715.3695955> |
| *SWARM: Replicating Shared Disaggregated-Memory Data in No Time* | Antoine Murat et al. | SOSP '24 | Fig. 4 | Fig. 3 |  | <https://doi.org/10.1145/3694715.3695945> |
| *Efficient Reproduction of Fault-Induced Failures in Distributed Systems with Feedback-Driven Fault Injection* | Jia Pan et al. | SOSP '24 | Fig. 2 |  |  | <https://doi.org/10.1145/3694715.3695979> |
| *Fast & Safe IO Memory Protection* | Benny Rubin et al. | SOSP '24 |  | Fig. 1 |  | <https://doi.org/10.1145/3694715.3695943> |
| *PowerInfer: Fast Large Language Model Serving with a Consumer-grade GPU* | Yixin Song et al. | SOSP '24 | Fig. 1, 2, 7 | Fig. 1, 2, 7, 8 |  | <https://doi.org/10.1145/3694715.3695964> |
| *Tenplex: Dynamic Parallelism for Deep Learning using Parallelizable Tensor Collections* | Marcel Wagenländer et al. | SOSP '24 |  | Fig. 1, 6, 7, 8 |  | <https://doi.org/10.1145/3694715.3695975> |
| *LoongServe: Efficiently Serving Long-Context Large Language Models with Elastic Sequence Parallelism* | Bingyang Wu et al. | SOSP '24 | Fig. 1, 5 | Fig. 7, 8 |  | <https://doi.org/10.1145/3694715.3695948> |
| *DCP: Addressing Input Dynamism In Long-Context Training via Dynamic Context Parallelism* | Chenyu Jiang et al. | SOSP '25 | Fig. 11, 12 | Fig. 3, 8 |  | <https://doi.org/10.1145/3731569.3764849> |
| *Fast End-to-End Performance Simulation of Accelerated Hardware-Software Stacks* | Jiacheng Ma et al. | SOSP '25 | Fig. 1 |  |  | <https://doi.org/10.1145/3731569.3764825> |
| *Fawkes: Finding Data Durability Bugs in DBMSs via Recovered Data State Verification* | Zhiyong Wu et al. | SOSP '25 |  | Fig. 6, 8 | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764841> |
| *CHERIoT RTOS: An OS for Fine-Grained Memory-Safe Compartments on Low-Cost Embedded Devices* | Saar Amar et al. | SOSP '25 | Fig. 2 |  | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764844> |
| *ORQ: Complex Analytics on Private Data with Strong Security Guarantees* | Eli Baum et al. | SOSP '25 | Fig. 3 | Fig. 2, 3 |  | <https://doi.org/10.1145/3731569.3764833> |
| *The Design and Implementation of a Virtual Firmware Monitor* | Charly Castes et al. | SOSP '25 |  | Fig. 7, 8 | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764826> |
| *Atmosphere: Practical Verified Kernels with Rust and Verus* | Xiangdong Chen et al. | SOSP '25 | Fig. 1 |  | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764821> |
| *Characterizing Mobile SoC for Accelerating Heterogeneous LLM Inference* | Le Chen et al. | SOSP '25 | Fig. 7 | Fig. 2, 9, 11 |  | <https://doi.org/10.1145/3731569.3764808> |
| *KTransformers: Unleashing the Full Potential of CPU/GPU Hybrid Inference for MoE Models* | Hongtao Chen et al. | SOSP '25 | Fig. 5 |  | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764843> |
| *LithOS: An Operating System for Efficient Machine Learning on GPUs* | Patrick H. Coppock et al. | SOSP '25 | Fig. 2 |  | CC BY-NC-ND 4.0 | <https://doi.org/10.1145/3731569.3764818> |
| *Tai Chi: A General High-Efficiency Scheduling Framework for SmartNICs in Hyperscale Clouds* | Bang Di et al. | SOSP '25 | Fig. 1, 8 | Fig. 8 |  | <https://doi.org/10.1145/3731569.3764851> |
| *PrefillOnly: An Inference Engine for Prefill-only Workloads in Large Language Model Applications* | Kuntai Du et al. | SOSP '25 |  | Fig. 4 |  | <https://doi.org/10.1145/3731569.3764834> |
| *Tiga: Accelerating Geo-Distributed Transactions with Synchronized Clocks* | Jinkun Geng et al. | SOSP '25 |  | Fig. 16 |  | <https://doi.org/10.1145/3731569.3764854> |
| *Pie: A Programmable Serving System for Emerging LLM Applications* | In Gim et al. | SOSP '25 | Fig. 3 |  | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764814> |
| *How to Copy Memory? Coordinated Asynchronous Copy as a First-Class OS Service* | Jingkai He et al. | SOSP '25 |  | Fig. 7, 8 |  | <https://doi.org/10.1145/3731569.3764800> |
| *HedraRAG: Co-Optimizing Generation and Retrieval for Heterogeneous RAG Workflows* | Zhengding Hu et al. | SOSP '25 | Fig. 1 |  |  | <https://doi.org/10.1145/3731569.3764806> |
| *Analyzing and Enhancing ArckFS: An Anecdotal Example of Benefits of Artifact Evaluation* | Jonguk Jeon et al. | SOSP '25 |  | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3731569.3768291> |
| *Running Consistent Applications Closer to Users with Radical for Lower Latency* | Nicolaas Kaashoek et al. | SOSP '25 | Fig. 2 |  | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764831> |
| *Scalable Address Spaces using Concurrent Interval Skiplist* | Tae Woo Kim, Youngjin Kwon and Jeehoon Kang | SOSP '25 |  | Fig. 6 | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764807> |
| *μFork: Supporting POSIX fork Within a Single-Address-Space OS* | John Alistair Kressel, Hugo Lefeuvre and Pierre Olivier | SOSP '25 |  | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764809> |
| *Unlocking True Elasticity for the Cloud-Native Era with Dandelion* | Tom Kuchler et al. | SOSP '25 | Fig. 4 | Fig. 4 | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764803> |
| *Mantle: Efficient Hierarchical Metadata Management for Cloud Object Storage Services* | Jiahao Li et al. | SOSP '25 | Fig. 1, 2 | Fig. 7, 9 |  | <https://doi.org/10.1145/3731569.3764824> |
| *TrainVerify: Equivalence-Based Verification for Distributed LLM Training* | Yunchi Lu et al. | SOSP '25 |  | Fig. 4, 10 |  | <https://doi.org/10.1145/3731569.3764850> |
| *TRIP: Coercion-resistant Registration for E-Voting with Verifiability and Usability in Votegral* | Louis-Henri Merino et al. | SOSP '25 | Fig. 1, 3 | Fig. 1 |  | <https://doi.org/10.1145/3731569.3764837> |
| *Moirai: Optimizing Placement of Data and Compute in Hybrid Clouds* | Ziyue Qiu et al. | SOSP '25 | Fig. 3 | Fig. 4 |  | <https://doi.org/10.1145/3731569.3764802> |
| *Coyote v2: Raising the Level of Abstraction for Data Center FPGAs* | Benjamin Ramhorst et al. | SOSP '25 | Fig. 6 | Fig. 4 |  | <https://doi.org/10.1145/3731569.3764845> |
| *Tock: From Research To Securing 10 Million Computers* | Leon Schuermann et al. | SOSP '25 |  | Fig. 3 |  | <https://doi.org/10.1145/3731569.3764828> |
| *Tempo: Compiled Dynamic Deep Learning with Symbolic Dependence Graphs* | Pedro F. Silvestre and Peter R. Pietzuch | SOSP '25 | Fig. 14, 15 | Fig. 1, 3, 4, 5, 6, 11, 13, 14, 15, 16 |  | <https://doi.org/10.1145/3731569.3764840> |
| *Robust LLM Training Infrastructure at ByteDance* | Borui Wan et al. | SOSP '25 | Fig. 4, 5 | Fig. 5, 7 | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764838> |
| *PhoenixOS: Concurrent OS-level GPU Checkpoint and Restore with Validated Speculation* | Xingda Wei et al. | SOSP '25 | Fig. 3 | Fig. 1, 9 |  | <https://doi.org/10.1145/3731569.3764813> |
| *Aegaeon: Effective GPU Pooling for Concurrent LLM Serving on the Market* | Yuxing Xiang et al. | SOSP '25 |  | Fig. 9, 10 |  | <https://doi.org/10.1145/3731569.3764815> |
| *Quilt: Resource-aware Merging of Serverless Workflows* | Yuxuan Zhang and Sebastian Angel | SOSP '25 |  | Fig. 3 |  | <https://doi.org/10.1145/3731569.3764830> |
| *Jenga: Effective Memory Management for Serving LLM with Heterogeneity* | Chen Zhang et al. | SOSP '25 | Fig. 4, 5 |  |  | <https://doi.org/10.1145/3731569.3764823> |
| *DiffKV: Differentiated Memory Management for Large Language Models with Parallel KV Compaction* | Yanqi Zhang et al. | SOSP '25 | Fig. 7 |  |  | <https://doi.org/10.1145/3731569.3764810> |
| *CortenMM: Efficient Memory Management with Strong Correctness Guarantees* | Junyang Zhang et al. | SOSP '25 |  | Fig. 7 | CC BY-NC-ND 4.0 | <https://doi.org/10.1145/3731569.3764836> |
| *AutoMan: Facilitating Verified Distributed Systems Development Through Automatic Code Generation and Manual Optimizations* | Zihao Zhang et al. | SOSP '25 | Fig. 2 | Fig. 2 |  | <https://doi.org/10.1145/3731569.3764822> |
| *Oasis: Pooling PCIe Devices Over CXL to Boost Utilization* | Yuhong Zhong et al. | SOSP '25 | Fig. 5 | Fig. 7 | CC BY 4.0 | <https://doi.org/10.1145/3731569.3764812> |
| *Sleeping with One Eye Open: Fast, Sustainable Storage with Sandman* | Yanbo Zhou et al. | SOSP '25 | Fig. 6 | Fig. 7, 9, 10 |  | <https://doi.org/10.1145/3731569.3764804> |
| *Early Termination for Hyperdimensional Computing Using Inferential Statistics* | Pu (Luke) Yi et al. | ASPLOS '25 |  | Fig. 1 |  | <https://doi.org/10.1145/3669940.3707254> |
| *Mint: Cost-Efficient Tracing with All Requests Collection via Commonality and Variability Analysis* | Haiyu Huang et al. | ASPLOS '25 | Fig. 9 | Fig. 5, 6, 9 |  | <https://doi.org/10.1145/3669940.3707287> |
| *PipeLLM: Fast and Confidential Large Language Model Services with Speculative Pipelined Encryption* | Yifan Tan et al. | ASPLOS '25 | Fig. 9 | Fig. 5, 9 |  | <https://doi.org/10.1145/3669940.3707224> |
| *PartIR: Composing SPMD Partitioning Strategies for Machine Learning* | Sami Alabed et al. | ASPLOS '25 | Fig. 1 | Fig. 16 |  | <https://doi.org/10.1145/3669940.3707284> |
| *MoE-Lightning: High-Throughput MoE Inference on Memory-constrained GPUs* | Shiyi Cao et al. | ASPLOS '25 | Fig. 2 | Fig. 2 |  | <https://doi.org/10.1145/3669940.3707267> |
| *Instruction-Aware Cooperative TLB and Cache Replacement Policies* | Dimitrios Chasapis et al. | ASPLOS '25 |  | Fig. 7 |  | <https://doi.org/10.1145/3669940.3707247> |
| *H-Houdini: Scalable Invariant Learning* | Sushant Dinesh, Yongye Zhu and Christopher W. Fletcher | ASPLOS '25 |  | Fig. 6 |  | <https://doi.org/10.1145/3669940.3707263> |
| *Earth+: On-Board Satellite Imagery Compression Leveraging Historical Earth Observations* | Kuntai Du et al. | ASPLOS '25 | Fig. 6 |  |  | <https://doi.org/10.1145/3669940.3707222> |
| *Cinnamon: A Framework for Scale-Out Encrypted AI* | Siddharth Jayashankar et al. | ASPLOS '25 |  | Fig. 7 |  | <https://doi.org/10.1145/3669940.3707260> |
| *GraphPipe: Improving Performance and Scalability of DNN Training with Graph Pipeline Parallelism* | Byungsoo Jeon et al. | ASPLOS '25 | Fig. 3 | Fig. 3, 4, 10 |  | <https://doi.org/10.1145/3669940.3707220> |
| *ZRAID: Leveraging Zone Random Write Area (ZRWA) for Alleviating Partial Parity Tax in ZNS RAID* | Minwook Kim, Seongyeop Jeong and Jin-Soo Kim | ASPLOS '25 | Fig. 2 | Fig. 1, 4, 6 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707248> |
| *Enhancing CGRA Efficiency Through Aligned Compute and Communication Provisioning* | Zhaoying Li et al. | ASPLOS '25 | Fig. 9 | Fig. 1, 3, 4, 5, 6, 8, 9, 10 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707230> |
| *MVQ: Towards Efficient DNN Compression and Acceleration with Masked Vector Quantization* | Shuaiting Li et al. | ASPLOS '25 |  | Fig. 2, 4, 5, 6, 9 |  | <https://doi.org/10.1145/3669940.3707268> |
| *ByteFS: System Support for (CXL-based) Memory-Semantic Solid-State Drives* | Shaobo Li et al. | ASPLOS '25 | Fig. 4 | Fig. 4 |  | <https://doi.org/10.1145/3669940.3707250> |
| *MetaSapiens: Real-Time Neural Rendering with Efficiency-Aware Pruning and Accelerated Foveated Rendering* | Weikai Lin, Yu Feng and Yuhao Zhu | ASPLOS '25 | Fig. 1, 8 | Fig. 1, 2, 8 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707227> |
| *ReSBM: Region-based Scale and Minimal-Level Bootstrapping Management for FHE via Min-Cut* | Yan Liu et al. | ASPLOS '25 |  | Fig. 5 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707276> |
| *BatchZK: A Fully Pipelined GPU-Accelerated System for Batch Generation of Zero-Knowledge Proofs* | Tao Lu et al. | ASPLOS '25 | Fig. 3 | Fig. 5 |  | <https://doi.org/10.1145/3669940.3707270> |
| *Dilu: Enabling GPU Resourcing-on-Demand for Serverless DL Serving via Introspective Elasticity* | Cunchi Lv et al. | ASPLOS '25 | Fig. 1, 3 | Fig. 1 |  | <https://doi.org/10.1145/3669940.3707251> |
| *Helix: Serving Large Language Models over Heterogeneous GPUs and Network via Max-Flow* | Yixuan Mei et al. | ASPLOS '25 | Fig. 3 | Fig. 3 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707215> |
| *FSMoE: A Flexible and Scalable Training System for Sparse Mixture-of-Experts Models* | Xinglin Pan et al. | ASPLOS '25 |  | Fig. 1, 2 |  | <https://doi.org/10.1145/3669940.3707272> |
| *vAttention: Dynamic Memory Management for Serving LLMs without PagedAttention* | Ramya Prabhu et al. | ASPLOS '25 |  | Fig. 5 |  | <https://doi.org/10.1145/3669940.3707256> |
| *Accelerating Retrieval-Augmented Generation* | Derrick Quinn et al. | ASPLOS '25 | Fig. 5 | Fig. 5 |  | <https://doi.org/10.1145/3669940.3707264> |
| *MOAT: Securely Mitigating Rowhammer with Per-Row Activation Counters* | Moinuddin Qureshi and Salman Qazi | ASPLOS '25 |  | Fig. 7 |  | <https://doi.org/10.1145/3669940.3707278> |
| *Coach: Exploiting Temporal Patterns for All-Resource Oversubscription in Cloud Platforms* | Benjamin Reidys et al. | ASPLOS '25 | Fig. 13, 14, 16 | Fig. 13, 14, 16 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707226> |
| *DarwinGame: Playing Tournaments for Tuning Applications in Noisy Cloud Environments* | Rohan Basu Roy, Vijay Gadepally and Devesh Tiwari | ASPLOS '25 | Fig. 4 | Fig. 9 |  | <https://doi.org/10.1145/3669940.3707259> |
| *Copper and Wire: Bridging Expressiveness and Performance for Service Mesh Policies* | Divyanshu Saxena et al. | ASPLOS '25 |  | Fig. 4, 7 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707257> |
| *PCcheck: Persistent Concurrent Checkpointing for ML* | Foteini Strati, Michal Friedman and Ana Klimovic | ASPLOS '25 |  | Fig. 5 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707255> |
| *EDM: An Ultra-Low Latency Ethernet Fabric for Memory Disaggregation* | Weigao Su and Vishal Shrivastav | ASPLOS '25 | Fig. 1, 2, 4 | Fig. 1, 2 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707221> |
| *FleetIO: Managing Multi-Tenant Cloud Storage with Multi-Agent Reinforcement Learning* | Jinghan Sun et al. | ASPLOS '25 | Fig. 1, 5 |  |  | <https://doi.org/10.1145/3669940.3707229> |
| *Optimizing Datalog for the GPU* | Yihao Sun et al. | ASPLOS '25 | Fig. 4 | Fig. 1, 4 |  | <https://doi.org/10.1145/3669940.3707274> |
| *RTL Verification for Secure Speculation Using Contract Shadow Logic* | Qinhan Tan et al. | ASPLOS '25 | Fig. 1 |  |  | <https://doi.org/10.1145/3669940.3707243> |
| *pulse: Accelerating Distributed Pointer-Traversals on Disaggregated Memory* | Yupeng Tang et al. | ASPLOS '25 | Fig. 3 | Fig. 5 |  | <https://doi.org/10.1145/3669940.3707253> |
| *UniZK: Accelerating Zero-Knowledge Proof with Unified Hardware and Flexible Kernel Mapping* | Cheng Wang and Mingyu Gao | ASPLOS '25 |  | Fig. 3, 4 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707228> |
| *CRUSH: A Credit-Based Approach for Functional Unit Sharing in Dynamically Scheduled HLS* | Jiahui Xu and Lana Josipovic | ASPLOS '25 |  | Fig. 3, 4, 5 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707273> |
| *Optimizing Quantum Circuits, Fast and Slow* | Amanda Xu et al. | ASPLOS '25 |  | Fig. 4, 5 |  | <https://doi.org/10.1145/3669940.3707240> |
| *Design and Operation of Shared Machine Learning Clusters on Campus* | Kaiqiang Xu et al. | ASPLOS '25 | Fig. 1 |  |  | <https://doi.org/10.1145/3669940.3707266> |
| *Fast On-device LLM Inference with NPUs* | Daliang Xu et al. | ASPLOS '25 |  | Fig. 3, 7 |  | <https://doi.org/10.1145/3669940.3707239> |
| *Automatic Tracing in Task-Based Runtime Systems* | Rohan Yadav et al. | ASPLOS '25 |  | Fig. 4 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707237> |
| *Composing Distributed Computations Through Task and Kernel Fusion* | Rohan Yadav et al. | ASPLOS '25 |  | Fig. 1, 3 | CC BY 4.0 | <https://doi.org/10.1145/3669940.3707216> |
| *QECC-Synth: A Layout Synthesizer for Quantum Error Correction Codes on Sparse Architectures* | Keyi Yin et al. | ASPLOS '25 | Fig. 1 |  |  | <https://doi.org/10.1145/3669940.3707236> |
| *EXIST: Enabling Extremely Efficient Intra-Service Tracing Observability in Datacenters* | Xinkai Wang et al. | ASPLOS '25 | Fig. 7 | Fig. 5, 9 | CC BY-ND 4.0 | <https://doi.org/10.1145/3676641.3716283> |
| *Velosiraptor: Code Synthesis for Memory Translation* | Reto Achermann et al. | ASPLOS '25 | Fig. 1 | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3676641.3711998> |
| *Extended User Interrupts (xUI): Fast and Flexible Notification without Polling* | Berk Aydogmus et al. | ASPLOS '25 | Fig. 1 |  | CC BY-NC-ND 4.0 | <https://doi.org/10.1145/3676641.3716028> |
| *MoC-System: Efficient Fault Tolerance for Sparse Mixture-of-Experts Model Training* | Weilin Cai, Le Qin and Jiayi Huang | ASPLOS '25 | Fig. 1, 2, 3 | Fig. 4, 6, 8 |  | <https://doi.org/10.1145/3676641.3716006> |
| *OctoCache: Caching Voxels for Accelerating 3D Occupancy Mapping in Autonomous Systems* | Peiqing Chen et al. | ASPLOS '25 | Fig. 1 |  | CC BY 4.0 | <https://doi.org/10.1145/3676641.3716263> |
| *Orion: A Fully Homomorphic Encryption Framework for Deep Learning* | Austin Ebel, Karthik Garimella and Brandon Reagen | ASPLOS '25 | Fig. 2 | Fig. 2, 3, 6 |  | <https://doi.org/10.1145/3676641.3716008> |
| *ElasticMiter: Formally Verified Dataflow Circuit Rewrites* | Ayatallah Elakhras et al. | ASPLOS '25 | Fig. 5 | Fig. 5, 6, 9 | CC BY 4.0 | <https://doi.org/10.1145/3676641.3715993> |
| *Klotski: Efficient Mixture-of-Expert Inference via Expert-Aware Multi-Batch Pipeline* | Zhiyuan Fang et al. | ASPLOS '25 | Fig. 2, 6 | Fig. 2, 3, 6, 8 |  | <https://doi.org/10.1145/3676641.3716261> |
| *StreamGrid: Streaming Point Cloud Analytics via Compulsory Splitting and Deterministic Termination* | Yu Feng et al. | ASPLOS '25 |  | Fig. 7, 8, 9, 11 |  | <https://doi.org/10.1145/3676641.3716021> |
| *AMuLeT: Automated Design-Time Testing of Secure Speculation Countermeasures* | Bo Fu et al. | ASPLOS '25 | Fig. 5 | Fig. 1, 4, 5 |  | <https://doi.org/10.1145/3676641.3716247> |
| *TNIC: A Trusted NIC Architecture: A hardware-network substrate for building high-performance trustworthy distributed systems* | Dimitra Giantsidi et al. | ASPLOS '25 | Fig. 1, 2 | Fig. 3 |  | <https://doi.org/10.1145/3676641.3716277> |
| *Past-Future Scheduler for LLM Serving under SLA Guarantees* | Ruihao Gong et al. | ASPLOS '25 | Fig. 2 |  |  | <https://doi.org/10.1145/3676641.3716011> |
| *PIM Is All You Need: A CXL-Enabled GPU-Free System for Large Language Model Inference* | Yufeng Gu et al. | ASPLOS '25 | Fig. 3, 5, 9 | Fig. 3, 7, 10 | CC BY-NC-SA 4.0 | <https://doi.org/10.1145/3676641.3716267> |
| *PAPI: Exploiting Dynamic Parallelism in Large Language Model Decoding with a Processing-In-Memory-Enabled Computing System* | Yintao He et al. | ASPLOS '25 | Fig. 1, 5 | Fig. 1, 5 |  | <https://doi.org/10.1145/3676641.3716009> |
| *ShadowLoad: Injecting State into Hardware Prefetchers* | Lorenz Hetterich et al. | ASPLOS '25 |  | Fig. 1 |  | <https://doi.org/10.1145/3676641.3716020> |
| *CIPHERMATCH: Accelerating Homomorphic Encryption-Based String Matching via Memory-Efficient Data Packing and In-Flash Processing* | Mayank Kabra et al. | ASPLOS '25 | Fig. 6 | Fig. 1, 6 |  | <https://doi.org/10.1145/3676641.3716251> |
| *POD-Attention: Unlocking Full Prefill-Decode Overlap for Faster LLM Inference* | Aditya K. Kamath et al. | ASPLOS '25 | Fig. 5 | Fig. 5 | CC BY 4.0 | <https://doi.org/10.1145/3676641.3715996> |
| *Virtuoso: Enabling Fast and Accurate Virtual Memory Research via an Imitation-based Operating System Simulation Methodology* | Konstantinos Kanellopoulos et al. | ASPLOS '25 | Fig. 4 | Fig. 4, 5 |  | <https://doi.org/10.1145/3676641.3716027> |
| *Virgo: Cluster-level Matrix Unit Integration in GPUs for Scalability and Energy Efficiency* | Hansung Kim et al. | ASPLOS '25 | Fig. 1, 2 | Fig. 1, 2 | CC BY 4.0 | <https://doi.org/10.1145/3676641.3716281> |
| *Aqua: Network-Accelerated Memory Offloading for LLMs in Scale-Up GPU Domains* | Abhishek Vijaya Kumar, Gianni Antichi and Rachee Singh | ASPLOS '25 | Fig. 2 |  | CC BY 4.0 | <https://doi.org/10.1145/3676641.3715983> |
| *Harmonia: A Unified Framework for Heterogeneous FPGA Acceleration in the Cloud* | Luyang Li et al. | ASPLOS '25 |  | Fig. 8 |  | <https://doi.org/10.1145/3676641.3716259> |
| *COMET: Towards Practical W4A4KV4 LLMs Serving* | Lian Liu et al. | ASPLOS '25 | Fig. 5 |  |  | <https://doi.org/10.1145/3676641.3716252> |
| *Practical Federated Recommendation Model Learning Using ORAM with Controlled Privacy* | Jinyu Liu et al. | ASPLOS '25 |  | Fig. 1 |  | <https://doi.org/10.1145/3676641.3716014> |
| *Concurrency-Informed Orchestration for Serverless Functions* | Qichang Liu et al. | ASPLOS '25 |  | Fig. 1 | CC BY 4.0 | <https://doi.org/10.1145/3676641.3716253> |
| *MDPeek: Breaking Balanced Branches in SGX with Memory Disambiguation Unit Side Channels* | Chang Liu et al. | ASPLOS '25 | Fig. 2 | Fig. 8, 13 | CC BY 4.0 | <https://doi.org/10.1145/3676641.3716004> |
| *Systematic CXL Memory Characterization and Performance Analysis at Scale* | Jinshu Liu et al. | ASPLOS '25 |  | Fig. 2, 10, 13 |  | <https://doi.org/10.1145/3676641.3715987> |
| *PhasePrint:  Exposing Cloud FPGA Fingerprints by Inducing Timing Faults at Runtime* | Jubayer Mahmod and Matthew Hicks | ASPLOS '25 |  | Fig. 1, 3, 4 | CC BY 4.0 | <https://doi.org/10.1145/3676641.3716012> |
| *Skia: Exposing Shadow Branches* | Chrysanthos Pepi et al. | ASPLOS '25 |  | Fig. 4 | CC BY-SA 4.0 | <https://doi.org/10.1145/3676641.3716273> |
| *Pruner: A Draft-then-Verify Exploration Mechanism to Accelerate Tensor Program Tuning* | Liang Qiao et al. | ASPLOS '25 | Fig. 2 |  |  | <https://doi.org/10.1145/3676641.3716269> |
| *PICACHU: Plug-In CGRA Handling Upcoming Nonlinear Operations in LLMs* | Jiajun Qin et al. | ASPLOS '25 | Fig. 4, 5, 6 |  | CC BY 4.0 | <https://doi.org/10.1145/3676641.3716013> |
| *RESCQ: Realtime Scheduling for Continuous Angle Quantum Error Correction Architectures* | Sayam Sethi and Jonathan Mark Baker | ASPLOS '25 |  | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3676641.3716018> |
| *HetEC: Architectures for Heterogeneous Quantum Error Correction Codes* | Samuel A. Stein et al. | ASPLOS '25 |  | Fig. 4 |  | <https://doi.org/10.1145/3676641.3716001> |
| *TAPAS: Thermal- and Power-Aware Scheduling for LLM Inference in Cloud Platforms* | Jovan Stojkovic et al. | ASPLOS '25 | Fig. 17 | Fig. 17 |  | <https://doi.org/10.1145/3676641.3716025> |
| *M5: Mastering Page Migration and Memory Management for CXL-based Tiered Memory Systems* | Yan Sun et al. | ASPLOS '25 |  | Fig. 2, 5 |  | <https://doi.org/10.1145/3676641.3711999> |
| *CoServe: Efficient Collaboration-of-Experts (CoE) Model Inference with Limited Memory* | Jiashun Suo et al. | ASPLOS '25 | Fig. 7 | Fig. 3, 4, 7 |  | <https://doi.org/10.1145/3676641.3715986> |
| *Towards End-to-End Optimization of LLM-based Applications with Ayo* | Xin Tan et al. | ASPLOS '25 | Fig. 5, 6 | Fig. 6 |  | <https://doi.org/10.1145/3676641.3716278> |
| *CTXNL: A Software-Hardware Co-designed Solution for Efficient CXL-Based Transaction Processing* | Zhao Wang et al. | ASPLOS '25 |  | Fig. 10, 11 |  | <https://doi.org/10.1145/3676641.3716244> |
| *FlexSP: Accelerating Large Language Model Training via Flexible Sequence Parallelism* | Yujie Wang et al. | ASPLOS '25 | Fig. 3 | Fig. 3 |  | <https://doi.org/10.1145/3676641.3715998> |
| *Spindle: Efficient Distributed Training of Multi-Task Large Models via Wavefront Scheduling* | Yujie Wang et al. | ASPLOS '25 | Fig. 2, 6 | Fig. 2, 5, 6, 7 |  | <https://doi.org/10.1145/3676641.3715992> |
| *Micro Blossom: Accelerated Minimum-Weight Perfect Matching Decoding for Quantum Error Correction* | Yue Wu, Namitha Liyanage and Lin Zhong | ASPLOS '25 | Fig. 5 | Fig. 3, 5, 8 |  | <https://doi.org/10.1145/3676641.3716005> |
| *Fat-Tree QRAM: A High-Bandwidth Shared Quantum Random Access Memory for Parallel Queries* | Shifan Xu, Alvin Lu and Yongshan Ding | ASPLOS '25 | Fig. 1, 12, 13 | Fig. 1, 12, 13 | CC BY-NC 4.0 | <https://doi.org/10.1145/3676641.3716256> |
| *Be CIM or Be Memory: A Dual-mode-aware DNN Compiler for CIM Accelerators* | Shixin Zhao et al. | ASPLOS '25 | Fig. 2, 3, 7 | Fig. 2, 3, 7, 9, 10, 12, 15 |  | <https://doi.org/10.1145/3676641.3716248> |
| *Gigaflow: Pipeline-Aware Sub-Traversal Caching for Modern SmartNICs* | Annus Zulfiqar et al. | ASPLOS '25 | Fig. 5 |  | CC BY 4.0 | <https://doi.org/10.1145/3676641.3716000> |
| *Wave: Offloading Resource Management to SmartNIC Cores* | Jack Tigar Humphries et al. | ASPLOS '25 | Fig. 1 |  | CC BY 4.0 | <https://doi.org/10.1145/3676642.3736113> |
| *ASDR: Exploiting Adaptive Sampling and Data Reuse for CIM-based Instant Neural Rendering* | Fangxin Liu et al. | ASPLOS '25 | Fig. 11 | Fig. 1, 10, 14 |  | <https://doi.org/10.1145/3676642.3736117> |
| *PowerMove: Optimizing Compilation for Neutral Atom Quantum Computers with Zoned Architecture* | Jixuan Ruan et al. | ASPLOS '25 |  | Fig. 1, 2, 3, 5 |  | <https://doi.org/10.1145/3676642.3736128> |
| *HybridTier: an Adaptive and Lightweight CXL-Memory Tiering System* | Kevin Song et al. | ASPLOS '25 |  | Fig. 1, 8 |  | <https://doi.org/10.1145/3676642.3736119> |
| *Neuralink: Fast on-Device LLM Inference with Neuron Co-Activation Linking* | Tuowei Wang et al. | ASPLOS '25 |  | Fig. 7, 8 | CC BY-NC-SA 4.0 | <https://doi.org/10.1145/3676642.3736114> |
| *DejaVuzz: Disclosing Transient Execution Bugs with Dynamic Swappable Memory and Differential Information Flow Tracking Assisted Processor Fuzzing* | Jinyan Xu et al. | ASPLOS '25 |  | Fig. 2 |  | <https://doi.org/10.1145/3676642.3736115> |
| *PUSHtap: PIM-based In-Memory HTAP with Unified Data Storage Format* | Yilong Zhao et al. | ASPLOS '25 | Fig. 1 |  |  | <https://doi.org/10.1145/3676642.3736120> |
| *Dynamic Sparsity in Large-Scale Video DiT Training* | Xin Tan et al. | ASPLOS '26 | Fig. 1 |  |  | <https://doi.org/10.1145/3760250.3762216> |
| *Cheddar: A Swift Fully Homomorphic Encryption Library Designed for GPU Architectures* | Wonseok Choi, Jongmin Kim and Jung Ho Ahn | ASPLOS '26 |  | Fig. 4 | CC BY 4.0 | <https://doi.org/10.1145/3760250.3762223> |
| *TiNA: Tiered Network Buffer Architecture for Fast Networking in Chiplet-based CPUs* | Siddharth Agarwal et al. | ASPLOS '26 |  | Fig. 7 | CC BY-NC-ND 4.0 | <https://doi.org/10.1145/3760250.3762224> |
| *A Data-Driven Dynamic Execution Orchestration Architecture* | Zhenyu Bai et al. | ASPLOS '26 | Fig. 2 | Fig. 1, 2, 3, 5, 8, 20, 21, 23 | CC BY 4.0 | <https://doi.org/10.1145/3760250.3762226> |
| *NotebookOS: A Replicated Notebook Platform for Interactive Training with On-Demand GPUs* | Benjamin Carver et al. | ASPLOS '26 | Fig. 1, 3, 6 | Fig. 1, 6 | CC BY 4.0 | <https://doi.org/10.1145/3760250.3762230> |
| *GFS: A Preemption-aware Scheduling Framework for GPU Clusters with Predictive Spot Instance Management* | Jiaang Duan et al. | ASPLOS '26 |  | Fig. 6 |  | <https://doi.org/10.1145/3760250.3762231> |
| *AGS: Accelerating 3D Gaussian Splatting SLAM via CODEC-Assisted Frame Covisibility Detection* | Houshu He et al. | ASPLOS '26 | Fig. 2, 7, 8, 10, 13 | Fig. 1, 2, 7, 8, 11, 12 |  | <https://doi.org/10.1145/3760250.3762229> |
| *SuperOffload: Unleashing the Power of Large-Scale LLM Training on Superchips* | Xinyu Lian et al. | ASPLOS '26 | Fig. 5 |  |  | <https://doi.org/10.1145/3760250.3762217> |
| *XY-Serve: End-to-End Versatile Production Serving for Dynamic LLM Workloads* | Mingcong Song et al. | ASPLOS '26 |  | Fig. 1, 12 |  | <https://doi.org/10.1145/3760250.3762228> |
| *MoDM: Efficient Serving for Image Generation via Mixture-of-Diffusion Models* | Yuchen Xia et al. | ASPLOS '26 | Fig. 1, 4 | Fig. 4 |  | <https://doi.org/10.1145/3760250.3762220> |
| *DARTH-PUM: A Hybrid Processing-Using-Memory Architecture* | Ryan Wong, Ben Feinberg and Saugata Ghose | ASPLOS '26 | Fig. 1, 6, 8 | Fig. 1, 2, 4, 9 |  | <https://doi.org/10.1145/3779212.3790151> |
| *Taming the Long-Tail: Efficient Reasoning RL Training with Adaptive Drafter* | Qinghao Hu et al. | ASPLOS '26 | Fig. 4, 5, 9, 10 | Fig. 3, 5, 6, 9 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790231> |
| *GS-Scale: Unlocking Large-Scale 3D Gaussian Splatting Training via Host Offloading* | Donghyun Lee et al. | ASPLOS '26 | Fig. 2 | Fig. 2 |  | <https://doi.org/10.1145/3779212.3790167> |
| *M2XFP: A Metadata-Augmented Microscaling Data Format for Efficient Low-bit Quantization* | Weiming Hu et al. | ASPLOS '26 | Fig. 9 | Fig. 10, 12 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790185> |
| *AlphaSyndrome: Tackling the Syndrome Measurement Circuit Scheduling Problem for QEC Codes* | Yuhao Liu et al. | ASPLOS '26 | Fig. 9 | Fig. 3, 4, 6, 8, 9, 10, 11 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790123> |
| *A Programming Model for Disaggregated Memory over CXL* | Gal Assa et al. | ASPLOS '26 |  | Fig. 1, 5 |  | <https://doi.org/10.1145/3779212.3790121> |
| *Towards High-Goodput LLM Serving with Prefill-decode Multiplexing* | Yukang Chen et al. | ASPLOS '26 | Fig. 8 | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790236> |
| *FastTTS: Accelerating Test-Time Scaling for Edge LLM Reasoning* | Hao Mark Chen et al. | ASPLOS '26 |  | Fig. 9 | CC BY-NC-ND 4.0 | <https://doi.org/10.1145/3779212.3790161> |
| *STRAW: Stress-Aware WL-Based Read Disturbance Management for High-Density NAND Flash Memory* | Myoungjun Chun et al. | ASPLOS '26 | Fig. 7 | Fig. 7 |  | <https://doi.org/10.1145/3779212.3790228> |
| *COMPAS: A Distributed Multi-Party SWAP Test for Parallel Quantum Algorithms* | Brayden Goldstein-Gelb et al. | ASPLOS '26 | Fig. 2, 7 | Fig. 4, 6 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790143> |
| *Graphiti: Formally Verified Out-of-Order Execution in Dataflow Circuits* | Yann Herklotz et al. | ASPLOS '26 | Fig. 1 | Fig. 4, 5 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790166> |
| *TreeVQA: A Tree-Structured Execution Framework for Shot Reduction in Variational Quantum Algorithms* | Yuewen Hou, Dhanvi Bharadwaj and Gokul Subramanian Ravi | ASPLOS '26 | Fig. 5 | Fig. 5 |  | <https://doi.org/10.1145/3779212.3790239> |
| *PIPM: Partial and Incremental Page Migration for Multi-host CXL Disaggregated Shared Memory* | Gangqi Huang, Heiner Litz and Yuanchao Xu | ASPLOS '26 | Fig. 1, 9 | Fig. 9 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790203> |
| *A Cost-Effective Near-Storage Processing Solution for Offline Inference of Long-Context LLMs* | Hongsun Jang et al. | ASPLOS '26 | Fig. 7, 8 | Fig. 3, 8 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790119> |
| *Architecting Scalable Trapped Ion Quantum Computers using Surface Codes* | Scott Jones and Prakash Murali | ASPLOS '26 |  | Fig. 1 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790128> |
| *ICARUS: Criticality and Reuse based Instruction Caching for Datacenter Applications* | Vedant Kalbande et al. | ASPLOS '26 |  | Fig. 6, 9, 10 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790175> |
| *CREST: High-Performance Contention Resolution for Disaggregated Transactions* | Qihan Kang et al. | ASPLOS '26 | Fig. 8 | Fig. 7, 9 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790148> |
| *FuseFlow: A Fusion-Centric Compilation Framework for Sparse Deep Learning on Streaming Dataflow* | Rubens Lacouture et al. | ASPLOS '26 | Fig. 6 | Fig. 6, 7, 9 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790165> |
| *vCXLGen: Automated Synthesis and Verification of CXL Bridges for Heterogeneous Architectures* | Anatole Lefort et al. | ASPLOS '26 | Fig. 3, 5 | Fig. 1, 2, 5, 6, 10 |  | <https://doi.org/10.1145/3779212.3790245> |
| *CounterPoint: Using Hardware Event Counters to Refute and Refine Microarchitectural Assumptions* | Nick Lindsay et al. | ASPLOS '26 |  | Fig. 8, 10 |  | <https://doi.org/10.1145/3779212.3790145> |
| *Hardwired-Neuron Language Processing Units as General-Purpose Cognitive Substrates* | Yang Liu et al. | ASPLOS '26 | Fig. 4, 9 | Fig. 3, 4, 10 |  | <https://doi.org/10.1145/3779212.3790169> |
| *Ouroboros: Wafer-Scale SRAM CIM with Token-Grained Pipelining for Large Language Model Inference* | Yiqi Liu et al. | ASPLOS '26 | Fig. 2, 9 | Fig. 2, 7, 9, 10 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790197> |
| *LAER-MoE: Load-Adaptive Expert Re-layout for Efficient Mixture-of-Experts Training* | Xinyi Liu et al. | ASPLOS '26 |  | Fig. 3, 4 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790180> |
| *Performance Predictability in Heterogeneous Memory* | Jinshu Liu et al. | ASPLOS '26 | Fig. 3 | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790201> |
| *TetriServe: Efficiently Serving Mixed DiT Workloads* | Runyu Lu et al. | ASPLOS '26 | Fig. 5 |  | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790233> |
| *Neo: Real-Time On-Device 3D Gaussian Splatting with Reuse-and-Update Sorting Acceleration* | Changhun Oh et al. | ASPLOS '26 | Fig. 11, 12, 14 | Fig. 8, 12, 13, 14 |  | <https://doi.org/10.1145/3779212.3790192> |
| *SNIP: An Adaptive Mixed Precision Framework for Subbyte Large Language Model Training* | Yunjie Pan et al. | ASPLOS '26 | Fig. 2 | Fig. 6 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790223> |
| *Trinity: Three-Dimensional Tensor Program Optimization via Tile-level Equality Saturation* | Jaehyeong Park et al. | ASPLOS '26 |  | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790240> |
| *Rage Against the State Machine: Type-Stated Hardware Peripherals for Increased Driver Correctness* | Tyler Potyondy et al. | ASPLOS '26 | Fig. 2 | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790207> |
| *Lifetime-Aware Design for Item-Level Intelligence at the Extreme Edge* | Shvetank Prakash et al. | ASPLOS '26 | Fig. 3 |  | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790182> |
| *Mugi: Value Level Parallelism For Efficient LLMs* | Daniel Price et al. | ASPLOS '26 | Fig. 2, 3, 9 | Fig. 2, 3, 9, 10 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790189> |
| *Skyler: Static Analysis for Predicting API-Driven Costs in Serverless Applications* | Bernardo Ribeiro et al. | ASPLOS '26 | Fig. 4 | Fig. 1, 4 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790221> |
| *Co-Exploration of RISC-V Processor Microarchitectures and FreeRTOS Extensions for Lower Context-Switch Latency* | Markus Scheck, Tammo Mürmann and Andreas Koch | ASPLOS '26 | Fig. 3, 6 | Fig. 5 | CC BY-NC-ND 4.0 | <https://doi.org/10.1145/3779212.3790141> |
| *FlashMem: Supporting Modern DNN Workloads on Mobile with GPU Memory Hierarchy Optimizations* | Zhihao Shu et al. | ASPLOS '26 | Fig. 1, 3 | Fig. 3 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790164> |
| *Streaming Tensor Programs: A Streaming Abstraction for Dynamic Parallelism* | Gina Sohn et al. | ASPLOS '26 | Fig. 7 | Fig. 2, 3, 4, 6, 16 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790229> |
| *Borrowing Dirty Qubits in Quantum Programs* | Bonan Su et al. | ASPLOS '26 |  | Fig. 3 |  | <https://doi.org/10.1145/3779212.3790134> |
| *PropHunt: Automated Optimization of Quantum Syndrome Measurement Circuits* | Joshua Viszlai et al. | ASPLOS '26 | Fig. 8 | Fig. 4, 8, 9 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790205> |
| *Finding Reusable Instructions via E-Graph Anti-Unification* | Youwei Xiao et al. | ASPLOS '26 | Fig. 4 | Fig. 9, 13 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790162> |
| *CREATE: Cross-Layer Resilience Characterization and Optimization for Efficient yet Reliable Embodied AI Systems* | Tong Xie et al. | ASPLOS '26 | Fig. 11, 12 | Fig. 2, 3 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790147> |
| *SpeContext:  Enabling Efficient Long-context Reasoning with Speculative Context Sparsity in LLMs* | Jiaming Xu et al. | ASPLOS '26 | Fig. 2, 5 | Fig. 2, 3, 5 |  | <https://doi.org/10.1145/3779212.3790224> |
| *DIP: Efficient Large Multimodal Model Training with Dynamic Interleaved Pipeline* | Zhenliang Xue et al. | ASPLOS '26 | Fig. 2, 6, 7 | Fig. 2, 6, 7 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790154> |
| *Reconfigurable Quantum Instruction Set Computers for High Performance Attainable on Hardware* | Zhaohui Yang et al. | ASPLOS '26 |  | Fig. 1, 3, 7, 8, 10 |  | <https://doi.org/10.1145/3779212.3790208> |
| *Compass: Navigating the Design Space of Taint Schemes for RTL Security Verification* | Yuheng Yang et al. | ASPLOS '26 |  | Fig. 1, 2 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790144> |
| *Nemo: A Low-Write-Amplification Cache for Tiny Objects on Log-Structured Flash Devices* | Xufeng Yang et al. | ASPLOS '26 | Fig. 7, 11 | Fig. 3, 7, 9, 10, 11 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790191> |
| *PAT: Accelerating LLM Decoding via Prefix-Aware Attention with Resource Efficient Multi-Tile Kernel* | Jinjun Yi et al. | ASPLOS '26 |  | Fig. 2 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790200> |
| *iSwitch: QEC on Demand via In-Situ Encoding of Bare Qubits for Ion Trap Architectures* | Keyi Yin et al. | ASPLOS '26 | Fig. 4 | Fig. 2, 4 |  | <https://doi.org/10.1145/3779212.3790177> |
| *Anvil: A General-Purpose Timing-Safe Hardware Description Language* | Jason Zhijingcheng Yu et al. | ASPLOS '26 |  | Fig. 8 |  | <https://doi.org/10.1145/3779212.3790125> |
| *SwiftSpec: Disaggregated Speculative Decoding and Fused Kernels for Low-Latency LLM Inference* | Ziyi Zhang et al. | ASPLOS '26 |  | Fig. 3 |  | <https://doi.org/10.1145/3779212.3790246> |
| *BlendServe: Optimizing Offline Inference with Resource-Aware Batching* | Yilong Zhao et al. | ASPLOS '26 |  | Fig. 6 | CC BY 4.0 | <https://doi.org/10.1145/3779212.3790133> |
| *CLM: Removing the GPU Memory Barrier for 3D Gaussian Splatting* | Hexu Zhao et al. | ASPLOS '26 | Fig. 4 | Fig. 2, 4 |  | <https://doi.org/10.1145/3779212.3790140> |
| *Scaling Automated Database System Testing* | Suyang Zhong and Manuel Rigger | ASPLOS '26 | Fig. 5 | Fig. 5 |  | <https://doi.org/10.1145/3779212.3790215> |
| *RTeAAL Sim: Using Tensor Algebra to Represent and Accelerate RTL Simulation* | Yan Zhu et al. | ASPLOS '26 |  | Fig. 3 |  | <https://doi.org/10.1145/3779212.3790214> |
| *Nebula: Infinite-Scale 3D Gaussian Splatting in VR via Collaborative Rendering and Accelerated Stereo Rasterization* | He Zhu et al. | ASPLOS '26 | Fig. 9 | Fig. 11 |  | <https://doi.org/10.1145/3779212.3790190> |

## Named styles

A named style is the look of one paper's figures, which the skill reproduces when asked (`references/styles/`).
Its figures are kept as exemplars, rendered from the authors' figure files at their printed size.

| Style | Paper | Authors | Venue | Figures | Link |
|---|---|---|---|---|---|
| `charon` | *Charon: A Unified and Fine-Grained Simulator for Large-Scale LLM Training and Inference* | Mengtian Yang et al. | MLSys '26 | Fig. 1, 2, 3, 4, 5, 6, 12 | <https://arxiv.org/abs/2605.17164> |
