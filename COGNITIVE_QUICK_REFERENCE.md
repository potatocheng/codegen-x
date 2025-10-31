# Cognitive 工作流快速参考卡

## 选择决策树

```
你想做什么？
│
├─→ 日常代码生成 (快速、简单)
│   └─→ 使用: CodeGenAgent
│       code = CodeGenAgent(llm).generate(request)
│
├─→ 学术研究/论文 (详细分析)
│   └─→ 使用: CognitiveDrivenCodeGenAgent
│       code = CognitiveDrivenCodeGenAgent(
│           llm, enable_cognitive_guidance=True
│       ).generate(request, context)
│
└─→ 定制工作流 (完全控制)
    └─→ 直接使用认知工具
        from cognitive.* import ...
        # 自己组织流程
```

---

## 快速代码模板

### 模板1️⃣：标准模式（推荐日常使用）

```python
from llm.structured_llm import StructuredLLM
from agent.code_agent import CodeGenAgent

llm = StructuredLLM(model="gpt-4o-2024-08-06")
agent = CodeGenAgent(llm)

result = agent.generate(
    "写一个二分查找函数"
)

# 检查结果
if result["success"]:
    print(result["code"])
```

**输出**：代码 + 功能验证结果 + 行有效性评分

---

### 模板2️⃣：认知模式（推荐研究/论文）

```python
from llm.structured_llm import StructuredLLM
from agent.cognitive_code_agent import CognitiveDrivenCodeGenAgent

llm = StructuredLLM(model="gpt-4o-2024-08-06")
agent = CognitiveDrivenCodeGenAgent(
    llm=llm,
    enable_cognitive_guidance=True
)

result = agent.generate(
    request="写一个二分查找函数",
    context={"domain": "算法", "level": "中等"}
)

# 完整的分析
if result["success"]:
    print(f"代码:\n{result['code']}")
    print(f"\n认知分析:\n{result['cognitive_analysis']}")
    print(f"\n决策链:\n{result['cognitive_decisions']}")
    print(f"\n认知摘要:\n{result['cognitive_summary']}")
```

**输出**：代码 + 认知分析 + 决策链 + 摘要

---

## 认知工作流的4个阶段

```
阶段1: 认知问题分析
├─ 理解问题
├─ 选择策略 (8种编程策略)
└─ 估算认知负荷 (0-1)
  ↓
阶段2: 认知驱动规范生成
├─ 根据负荷调整详细程度
├─ 增强需求说明
└─ 生成 FunctionSpec
  ↓
阶段3: 认知驱动代码实现
├─ 根据策略调整实现风格
├─ 评估认知复杂度
└─ 应用负荷适应
  ↓
阶段4: 认知驱动验证与优化
├─ 验证 (功能 + 行有效性)
├─ 分析认知负荷
├─ 应用适应策略
└─ 循环优化 (最多3次)
```

---

## 认知负荷估计参考

```python
# 认知负荷值范围: 0.0 - 1.0

if load < 0.3:
    difficulty = "简单"
    strategy = "简洁规范，直接实现"

elif load < 0.7:
    difficulty = "中等"
    strategy = "标准规范，结构化实现"

else:
    difficulty = "复杂"
    strategy = "详细规范，分步实现，多次优化"
```

---

## 8种编程策略一览

| 策略 | 适用场景 | 特点 |
|------|--------|------|
| **STRATEGIC** | 高层规划 | 整体规划，大局观 |
| **STRUCTURED** | 清晰结构 | 逻辑清晰，层次分明 |
| **DATA_FLOW** | 数据变换 | 关注数据流向 |
| **OOP** | 对象建模 | 对象和方法 |
| **DECLARATIVE** | 描述"是什么" | 声明式定义 |
| **BOTTOM_UP** | 从细节构建 | 先实现细节，再组合 |
| **TOP_DOWN** | 从整体分解 | 先规划整体，再细化 |
| **HYBRID** | 复杂问题 | 结合多种方法 |

---

## 6种认知负荷适应策略

| 策略 | 作用 | 使用场景 |
|------|------|---------|
| **REDUCE_COMPLEXITY** | 降低复杂度 | 圈复杂度过高 |
| **INCREASE_SCAFFOLDING** | 增加脚手架 | 代码可读性差 |
| **OPTIMIZE_CHUNKING** | 优化分块 | 认知负荷过高 |
| **ENHANCE_CLARITY** | 增强清晰度 | 逻辑不清楚 |
| **PROVIDE_GUIDANCE** | 提供指导 | 需要更多说明 |
| **ADAPTIVE_PACING** | 自适应节奏 | 逐步学习 |

---

## 输出对比表

### 标准模式的输出字段
```
result = {
    "success": bool,
    "spec": dict,
    "code": str,
    "explanation": str,
    "validation": dict,
    "refine_attempts": int
}
```

### 认知模式的输出字段
```
result = {
    "success": bool,
    "spec": dict,
    "code": str,
    "explanation": str,
    "validation": dict,

    # 【认知模式额外输出】
    "cognitive_analysis": dict,
    "cognitive_decisions": list,
    "cognitive_summary": dict,
    "strategy_adaptations": list,
    "refine_attempts": int
}
```

---

## 关键概念速查

### 认知负荷的三个组成部分
```
总负荷 = 内在负荷 + 外在负荷 + 有效负荷
        (问题难)  (干扰)   (学习)
```

### 决策类型（7种）
```
1. STRATEGY_SELECTION      - 选择策略
2. TOOL_SELECTION          - 选择工具
3. APPROACH_CHANGE         - 改变方法
4. OPTIMIZATION_CHOICE     - 优化选择
5. VALIDATION_STRATEGY     - 验证策略
6. ERROR_HANDLING          - 错误处理
7. REFINEMENT_DIRECTION    - 优化方向
```

### 思考阶段（6个）
```
1. problem_comprehension   - 问题理解
2. strategy_selection      - 策略选择
3. design_planning         - 设计规划
4. implementation          - 实现
5. verification            - 验证
6. optimization            - 优化
```

---

## 常用配置参数

### CognitiveStrategy（认知策略）
```python
CognitiveStrategy(
    target_load=0.7,              # 目标认知负荷
    load_tolerance=0.1,           # 容忍范围 ±0.1
    adaptation_threshold=0.8,     # 触发适应的阈值
    scaffolding_level=0.5,        # 脚手架水平 (0-1)
    chunking_size=7,              # 一次处理的单位数
    guidance_verbosity=0.6        # 指导详细程度
)
```

### 代理配置
```python
# 标准代理
CodeGenAgent(
    llm=llm,
    max_iterations=10,
    max_refine_attempts=3
)

# 认知驱动代理
CognitiveDrivenCodeGenAgent(
    llm=llm,
    max_iterations=10,
    max_refine_attempts=3,
    enable_cognitive_guidance=True  # 关键参数
)
```

---

## 性能特征对比

| 指标 | 标准模式 | 认知模式 |
|------|--------|--------|
| **生成速度** | 快 | 慢 (3-5倍) |
| **输出大小** | 小 | 大 (4-5倍) |
| **内存使用** | 低 | 中等 |
| **适合场景** | 日常 | 研究 |
| **可解释性** | 低 | 高 |

---

## 何时用哪个？

### ✅ 用标准模式的情况
```
□ 需要快速生成代码
□ 日常开发工作
□ 简单问题
□ 性能是首要考虑
□ 只关心最终代码
□ 实验性开发
```

### ✅ 用认知模式的情况
```
□ 学术研究
□ 论文撰写
□ 需要深入分析
□ 复杂算法
□ 需要决策追踪
□ 需要可解释性
□ 学习代码生成过程
```

---

## 调试技巧

### 检查认知分析
```python
result = agent.generate(request, context)

# 查看策略选择
print(result['cognitive_analysis']['strategy_selection'])

# 查看认知负荷
print(result['cognitive_analysis']['cognitive_load_estimate'])

# 查看置信度
print(result['cognitive_analysis']['confidence_level'])
```

### 检查决策链
```python
# 查看所有决策
for i, decision in enumerate(result['cognitive_decisions']):
    print(f"{i+1}. [{decision['stage']}] {decision['decision']}")
    print(f"   → {decision['reasoning']}")
    print(f"   confidence: {decision['confidence']}")
```

### 检查适应策略
```python
# 查看应用的策略
for adaptation in result['strategy_adaptations']:
    print(f"{adaptation['strategy']}: {adaptation['action']}")
    print(f"Expected reduction: {adaptation['expected_load_reduction']}")
```

---

## 常见问题

**Q: 认知模式比标准模式慢多少？**
A: 通常 3-5 倍，因为要做更多分析

**Q: 认知负荷 0.7 是多少？**
A: 中等难度，需要标准详细程度的规范

**Q: 决策链有什么用？**
A: 解释代码生成过程，用于论文分析

**Q: 能自定义认知策略吗？**
A: 可以，修改 CognitiveStrategy 参数

**Q: 行有效性检查在两种模式都有吗？**
A: 是的，都有，这是 ValidateTool 的核心功能

---

## 快速参考命令

```python
# 标准模式 - 一行生成代码
from agent.code_agent import CodeGenAgent
code = CodeGenAgent(llm).generate("...").get("code")

# 认知模式 - 完整分析
from agent.cognitive_code_agent import CognitiveDrivenCodeGenAgent
result = CognitiveDrivenCodeGenAgent(llm, enable_cognitive_guidance=True).generate("...", context={})

# 查看所有模块
from cognitive import *

# 运行演示
python examples/cognitive_demo.py
```

---

**记住**：
- 日常用 → **标准模式**
- 研究用 → **认知模式**
- 学习用 → **两个都试试**

