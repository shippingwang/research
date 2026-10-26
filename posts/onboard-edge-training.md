---
title: On-board training & edge training
date: 2026-10-22
tags: [ml-systems, edge]
summary: 端侧训练
---

# On-board Training vs Edge Training

## 一、先把两个词分清

这两个词经常混着用，但约束层级不一样：

| | Edge Training（边缘训练） | On-board Training（板载/端侧训练） |
|---|---|---|
| 跑在哪 | 边缘服务器、网关、Jetson 盒子、车机域控 | 终端设备本身：手机、MCU、可穿戴、机器人本体 |
| 算力 | 接近小工作站，有 GPU/NPU | 百 mW～几 W，内存 KB～几 GB |
| 训什么 | 整模型微调、领域适配、本地数据闭环 | 只训 adapter / 小分类头 / 个性化层 |
| 代表场景 | 工厂本地微调、车端影子模式 | 手机个性化、MCU 上的关键词重新校准、相机自发更新 |

一句话：**edge training 是"把训练从云端搬到离数据近的机房"，on-board training 是"训练直接在芯片上发生，不出设备"**。后者才是硬骨头。

## 二、为什么训练难，推理容易

推理引擎（ExecuTorch、TFLite、QNN）在端侧已经很成熟，但训练一直跟不上，原因是训练比推理多背三重量：
1. **梯度**：每个参数一份；
2. **optimizer state**（Adam）：再两份，等于参数×3；
3. **activations**：反向传播要存中间激活，显存峰值比推理高数倍。

所以端侧训练的核心思路不是"把 PyTorch 搬小"，而是**绕开反向传播**。学界这几年基本是三条路线在卷：

- **PEFT/LoRA 系**：只训 0.01%～1% 参数，冻结主干。LoRA-Edge、TrainDeeploy 这类工作把 LoRA 再做张量分解、硬件加速，往 MCU 和极端边缘压。
- **零阶优化（Zeroth-Order）系**：不算梯度，靠多次 forward pass 扰动估计梯度，直接复用推理引擎，不用改 runtime。MobiZO 是这条路线在 LLM 上的代表，配 MP-LoRA 做并行扰动，已经能在 ExecuTorch 上跑端侧微调。
- **量化/低比特训练 + 256KB 级 MCU 训练**：MIT 2022 那篇《On-Device Training Under 256KB Memory》是里程碑，证明在几 KB RAM 的 MCU 上都能做小模型在线更新，后续 tinyML 社区一直在补工具链。

## 三、现状（2025–2026）

**已经落地的：**
- 手机端**推理**是标配（Apple Intelligence、骁龙 8 Gen 系列跑 7B～13B INT4）；
- 手机端**训练**目前主要是两种：Apple Foundation Models framework 给 app 开 on-device 模型访问，做轻量 personalization；Qualcomm 在 2025 演示了在推理模型上跑 on-device LoRA adapter、INT4 AdaScale 量化，配合 FastForward/GENIE SDK 做端侧推理+adapter 热插拔。
- MCU 端：Edge Impulse 这类平台已经把"传感器数据 → 端侧重训分类头"做成可视化流程，工业和可穿戴在用。

**还没落地的：**
- 在手机上对一个 7B 模型做全参数微调——不可能，内存墙过不去；
- 真正意义上的"用户数据持续在端上训练、越用越懂你"的闭环，目前是 federated learning 那套老故事，热度比 2019 年降了很多，工程上还卡在隐私、通信、非独立同分布数据上。

## 四、公司格局

- **Qualcomm**：端侧 GenAI 最激进的玩家，AI Hub + Snapdragon NPU，2025 把 IBM Granite 4.0 直接搬上端，做"云到边"的企业管线。
- **Apple**：闭源全栈，Foundation Models framework 是给开发者的端侧模型入口，个性化训练在系统层做，不开放。
- **Google**：TFLite 是端侧训练的老牌框架，Federated Learning 团队还在 Pixel 上做键盘/Gboard 的个性化；但 LLM 端侧训练这一波 Google 声音比 Qualcomm 小。
- **Meta**：ExecuTorch 是开源端侧推理 runtime，MobiZO 这类工作直接在它上面做 ZO 训练，等于把推理引擎反过来当训练引擎用。
- **NVIDIA**：Jetson 线吃的是 edge training 那一端——机器人、工控本地微调，不是 on-chip。
- **创业/工具层**：Edge Impulse（MCU 训练平台）、Tether/QVAC（跨异构 GPU 的 LoRA 微调框架，覆盖 Mali/Adreno/Apple GPU）。

## 五、学界在卷什么

1. **前向优化替代反向传播**：ZO、evolutionary、TD 式更新，目标是让训练复用推理图，这是我认为最有工程价值的方向——它直接解决了"推理引擎不支持训练"这个根问题。
2. **PEFT 的极端压缩**：LoRA→张量分解 LoRA→只训一个 output-side core，参数往千分之一压，同时要保精度。
3. **训练-推理同构硬件**：near-memory、SRAM-on-chip 训练，和 NPU 厂商的 ISA 一起 co-design。
4. **端侧持续学习/个性化**：在不重装 app 的前提下，模型在设备上随用户数据漂移，这部分学术界热，但产品化极少。

## 我的判断

- **edge training 已经是工程问题**，不是研究问题——车厂、工厂、机器人公司在 Jetson/Orin 上跑本地微调是常态。
- **on-board training 还卡在"训练的内存成本必须降一个量级"这个坎上**。未来 2–3 年能真正跑出来的形态，大概率不是"端侧训大模型"，而是：**冻结基座 + 端上只训一个几十 KB～几 MB 的 adapter**，由推理引擎用 ZO 或轻量 LoRA 完成。这也是 Qualcomm、Apple 现在实际在做的事。
- federated learning 作为"训练范式"叙事已经降温，但它的隐私计算外衣会一直被企业采购买单——别把它当技术突破看。
