---
title: On-board training & edge training
date: 2026-10-22
tags: [ml-systems, edge]
summary: 端侧 / 机载训练与云端训练差在约束，不只差在算力数字。
---

## 区分

- **Edge inference**：模型已训好，设备上只跑前向。
- **Edge / on-board training**：在设备或邻近节点上更新参数（或适配器）。

二者的瓶颈集中不同：前者多是延迟与能耗；后者还要面对数据驻留、通信轮次、优化器状态体积与热设计。

## 常见折中

- 只训 LoRA / 偏置等小参数，主干冻结
- 本地多步累积，稀疏上传
- 教师在云、学生在边的蒸馏或互蒸馏

## 仍想弄清的

- 在固定焦耳预算下，何时该训、何时只该检
- 与「连续学习 / 遗忘」文献怎么对齐实验协议

> Placeholder note — fill in papers and numbers later.
