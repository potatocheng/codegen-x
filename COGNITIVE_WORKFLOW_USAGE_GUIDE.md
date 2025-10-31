# Cognitive 工具使用指南与工作流详解

## 快速开始

### 选择1️⃣：使用标准代理（推荐日常使用）

```python
from llm.structured_llm import StructuredLLM
from agent.code_agent import CodeGenAgent

# 初始化标准代理
llm = StructuredLLM(model="gpt-4o-2024-08-06")
agent = CodeGenAgent(llm)

# 生成代码
result = agent.generate("写一个二分查找函数")

# 输出
print(f"代码: {result['code']}")
print(f"通过测试: {result['validation']['passed_count']}/{result['validation']['total_tests']}")
```

**优点**：
- 简单易用
- 已集成行有效性检查
- 适合日常工作

### 选择2️⃣：使用认知驱动代理（研究/论文用途）

```python
from llm.structured_llm import StructuredLLM
from agent.cognitive_code_agent import CognitiveDrivenCodeGenAgent

# 初始化认知驱动代理
llm = StructuredLLM(model="gpt-4o-2024-08-06")
agent = CognitiveDrivenCodeGenAgent(
    llm=llm,
    enable_cognitive_guidance=True  # 启用认知指导
)

# 生成代码（带认知分析）
result = agent.generate(
    request="写一个二分查找函数",
    context={"domain": "算法", "level": "中等"}
)

# 输出包含更多信息
print(f"代码: {result['code']}")
print(f"认知分析: {result['cognitive_analysis']}")
print(f"决策链: {result['cognitive_decisions']}")
print(f"认知总结: {result['cognitive_summary']}")
```

**优点**：
- 完整的认知分析
- 决策追踪和解释
- 适合研究和论文

---

## 🧠 Cognitive 工作流详解

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                  Cognitive-Driven Code Generation                │
│                                                                  │
│          CognitiveDrivenCodeGenAgent                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  阶段1: 认知问题分析                │
        │  (Cognitive Problem Analysis)      │
        │                                     │
        │  输入: 用户需求 + 上下文            │
        │  过程:                              │
        │  ├─ CognitiveCodeGenAgent分析      │
        │  ├─ 提取问题理解                   │
        │  ├─ 选择编程策略                   │
        │  └─ 估算认知负荷                   │
        │                                     │
        │  输出: cognitive_analysis           │
        │  {                                 │
        │    "problem_understanding": "...", │
        │    "strategy_selection": "...",    │
        │    "cognitive_load_estimate": 0.6, │
        │    "thinking_stages": [...],       │
        │    "confidence_level": 0.8         │
        │  }                                 │
        │                                     │
        │  决策追踪: 记录策略选择决策          │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  阶段2: 认知驱动规范生成            │
        │  (Cognitive Spec Generation)       │
        │                                     │
        │  输入: cognitive_analysis           │
        │  过程:                              │
        │  ├─ 根据认知负荷调整规范详细程度   │
        │  ├─ 增强请求（加入认知洞察）      │
        │  ├─ SpecTool生成规范               │
        │  └─ 评估规范的认知友好性           │
        │                                     │
        │  输出: FunctionSpec                │
        │  + 规范生成决策                    │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  阶段3: 认知驱动代码实现            │
        │  (Cognitive Implementation)        │
        │                                     │
        │  输入: FunctionSpec + 策略          │
        │  过程:                              │
        │  ├─ 根据选定策略调整实现风格       │
        │  ├─ ImplementTool生成代码          │
        │  │  + 行有效性要求                 │
        │  ├─ 评估生成代码的认知复杂度       │
        │  └─ 必要时应用负荷适应策略         │
        │                                     │
        │  输出: Implementation              │
        │  + 实现决策                        │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  阶段4: 认知驱动验证与优化          │
        │  (Cognitive Validation & Refinement)│
        │                                     │
        │  输入: Implementation + FunctionSpec │
        │  过程:                              │
        │  ├─ ValidateTool测试               │
        │  │  + 功能正确性                   │
        │  │  + 行有效性检查                 │
        │  ├─ 认知复杂度分析                 │
        │  ├─ 识别认知瓶颈                   │
        │  ├─ 应用负荷适应策略               │
        │  │  - 降低复杂度                   │
        │  │  - 增加脚手架                   │
        │  │  - 优化分块                     │
        │  │  - 增强清晰度                   │
        │  ├─ 如果失败，RefineTool优化       │
        │  │  + 包含行有效性反馈             │
        │  │  + 包含认知分析建议             │
        │  └─ 循环验证（最多3次）            │
        │                                     │
        │  输出: 最终代码 + 详细分析          │
        │  + 完整的决策链                    │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │  完成：生成完整报告                 │
        │  - 最终代码                        │
        │  - 认知分析详情                    │
        │  - 完整决策链                      │
        │  - 认知摘要                        │
        │  - 策略适应记录                    │
        └─────────────────────────────────────┘
```

---

## 📊 详细的4个阶段

### 阶段1️⃣：认知问题分析

**作用**：理解问题特征，选择最合适的编程策略

**过程**：
```python
def _cognitive_problem_analysis(self, request, context):
    # 1. 创建认知请求
    cognitive_request = CognitiveCodeGenRequest(
        requirement=request,           # "写一个二分查找函数"
        context=json.dumps(context),   # 额外上下文
        constraints=[],                # 约束条件
        difficulty="medium"            # 难度估计
    )

    # 2. 执行认知分析（使用CognitiveCodeGenAgent）
    cognitive_result = self.cognitive_agent.generate_code(cognitive_request)

    # 3. 提取分析结果
    analysis = {
        "problem_understanding": "...",  # 对问题的理解
        "strategy_selection": DIVIDE_AND_CONQUER,  # 选择的策略
        "cognitive_load_estimate": 0.6,  # 认知负荷估计
        "thinking_stages": [...],        # 思考阶段序列
        "confidence_level": 0.8          # 置信度
    }

    # 4. 记录决策
    self.current_tracker.record_decision(
        stage="problem_analysis",
        decision_type=DecisionType.STRATEGY_SELECTION,
        decision=f"选择策略: {strategy.value}",
        reasoning="基于问题特征和认知模型分析",
        confidence=0.8,
        expected_outcome="提高代码生成质量"
    )

    return analysis
```

**输出示例**：
```python
{
    "problem_understanding": "需要在排序数组中二分查找",
    "strategy_selection": "DIVIDE_AND_CONQUER",
    "cognitive_load_estimate": 0.6,  # 中等难度
    "thinking_stages": [
        "problem_comprehension",
        "strategy_selection",
        "algorithm_design"
    ],
    "confidence_level": 0.85
}
```

### 阶段2️⃣：认知驱动规范生成

**作用**：根据认知分析调整规范的详细程度

**关键决策**：
```python
def _determine_spec_detail_level(self, cognitive_load):
    """根据认知负荷决定规范详细程度"""
    if cognitive_load.intrinsic_load < 0.3:
        return "concise"      # 简洁：简单问题
    elif cognitive_load.intrinsic_load < 0.7:
        return "standard"     # 标准：中等问题
    else:
        return "detailed"     # 详细：复杂问题
```

**规范生成流程**：
```
认知负荷估计
    ↓
决定详细程度 (simple/standard/detailed)
    ↓
增强用户请求 (加入认知洞察)
    ↓
SpecTool 生成规范
    ↓
评估规范的认知友好性
    ↓
输出 FunctionSpec
```

**输出**：增强的 FunctionSpec，带有认知友好的结构

### 阶段3️⃣：认知驱动代码实现

**作用**：根据选定策略调整代码实现方式

**策略选择**：
```python
# 8种编程策略
STRATEGIC_APPROACH          # 策略性方法
STRUCTURED_APPROACH         # 结构化方法
DATA_FLOW_APPROACH         # 数据流方法
OBJECT_ORIENTED_APPROACH   # 面向对象方法
DECLARATIVE_APPROACH       # 声明式方法
BOTTOM_UP_APPROACH         # 自底向上方法
TOP_DOWN_APPROACH          # 自顶向下方法
HYBRID_APPROACH            # 混合方法
```

**实现流程**：
```
选定的编程策略
    ↓
根据策略调整 ImplementTool 提示
    ├─ 增加策略指导
    └─ 加入行有效性要求 ✓
    ↓
ImplementTool 生成代码
    ↓
评估代码的认知复杂度
    ↓
如果复杂度过高，应用负荷适应策略：
    ├─ 降低复杂度
    ├─ 增加脚手架
    ├─ 优化分块
    ├─ 增强清晰度
    ├─ 提供指导
    └─ 自适应节奏
    ↓
输出 Implementation
```

### 阶段4️⃣：认知驱动验证与优化

**最复杂的阶段**，包含循环验证

**验证步骤**：
```
┌─ ValidateTool 验证
│  ├─ 功能测试（测试用例）
│  ├─ 行有效性检查 ✓
│  └─ 输出 ValidationResult
│
├─ 认知复杂度分析
│  ├─ 评估代码认知负荷
│  ├─ 识别认知瓶颈
│  └─ 记录分析结果
│
├─ 判断是否通过
│  ├─ 功能正确 AND
│  └─ 认知负荷可接受 AND
│      代码质量好
│
├─ 如果失败，应用 CognitiveLoadAwareGenerator
│  └─ 生成适应策略
│     ├─ 策略1: 降低复杂度
│     ├─ 策略2: 增加脚手架
│     ├─ 策略3: 优化分块
│     └─ ...
│
├─ RefineTool 优化代码
│  ├─ 修复功能错误
│  ├─ 应用认知适应策略
│  ├─ 改进行有效性 ✓
│  └─ 生成改进代码
│
└─ 循环验证（最多3次）
   └─ 回到 ValidateTool
```

**适应策略详解**：
```python
adaptations = [
    AdaptationAction(
        strategy=REDUCE_COMPLEXITY,
        action="减少嵌套层级，简化条件判断",
        reasoning="检测到圈复杂度过高",
        expected_load_reduction=0.2
    ),
    AdaptationAction(
        strategy=INCREASE_SCAFFOLDING,
        action="添加更多中间变量和步骤说明",
        reasoning="提高代码可读性",
        expected_load_reduction=0.15
    ),
    AdaptationAction(
        strategy=OPTIMIZE_CHUNKING,
        action="分解为更小的函数",
        reasoning="降低认知负荷",
        expected_load_reduction=0.25
    )
]
```

---

## 🎯 Cognitive 工作流 vs 标准工作流

### 标准工作流（CodeGenAgent）
```
需求
  ↓
SpecTool
  ↓
ImplementTool (有行有效性要求)
  ↓
ValidateTool (功能 + 行有效性)
  ↓
完成？ ← NO ─┐
  ↓ YES     │
返回代码   RefineTool (有行有效性反馈)
          │
          └─ 循环验证
```

**特点**：
- 快速、简洁
- 4个主要工具
- 适合日常使用

### 认知工作流（CognitiveDrivenCodeGenAgent）
```
需求 + 上下文
  ↓
【认知分析】
├─ 理解问题
├─ 选择策略
├─ 估算负荷
└─ 记录决策1
  ↓
【认知规范生成】
├─ 根据负荷调整详细程度
├─ 增强请求
├─ 生成规范
└─ 记录决策2
  ↓
【认知实现】
├─ 根据策略调整风格
├─ 评估复杂度
├─ 应用负荷适应
└─ 记录决策3
  ↓
【认知验证与优化】
├─ 验证（功能+质量）
├─ 分析认知负荷
├─ 应用策略适应
├─ 循环优化
└─ 记录决策4-N
  ↓
返回代码 + 完整认知分析
```

**特点**：
- 完整的认知分析
- 7个模块协同
- 决策追踪
- 适合研究/论文

---

## 📈 输出对比

### 标准工作流的输出
```python
{
    "success": True,
    "spec": {...},
    "code": "def binary_search(arr, target): ...",
    "explanation": "使用两个指针...",
    "validation": {
        "is_valid": True,
        "passed_count": 3,
        "total_tests": 3,
        "line_effectiveness_score": 0.93,
        "line_effectiveness_analysis": {...}
    },
    "refine_attempts": 0
}
```

### 认知工作流的输出
```python
{
    "success": True,
    "spec": {...},
    "code": "def binary_search(arr, target): ...",
    "explanation": "...",
    "validation": {...},

    # 【新增】认知分析
    "cognitive_analysis": {
        "problem_understanding": "...",
        "strategy_selection": "DIVIDE_AND_CONQUER",
        "cognitive_load_estimate": 0.6,
        "thinking_stages": [...],
        "confidence_level": 0.85
    },

    # 【新增】完整决策链
    "cognitive_decisions": [
        {
            "stage": "problem_analysis",
            "decision": "选择分治策略",
            "reasoning": "问题特征适合分治",
            "confidence": 0.85,
            "timestamp": "2024-10-31T12:34:56"
        },
        {
            "stage": "spec_generation",
            "decision": "使用标准详细程度",
            "reasoning": "中等认知负荷",
            "confidence": 0.80
        },
        ...
    ],

    # 【新增】认知摘要
    "cognitive_summary": {
        "total_decisions": 5,
        "average_confidence": 0.84,
        "session_duration": 15.3,
        "dominant_strategy": "DIVIDE_AND_CONQUER",
        "adaptations_applied": 2
    },

    # 【新增】策略适应记录
    "strategy_adaptations": [
        {
            "stage": "validation",
            "strategy": "REDUCE_COMPLEXITY",
            "action": "简化嵌套条件",
            "expected_reduction": 0.2
        }
    ],

    "refine_attempts": 1
}
```

---

## 🚀 使用场景指南

### 何时使用标准工作流 ✓

```python
# 日常代码生成
agent = CodeGenAgent(llm)
result = agent.generate("写一个快速排序函数")
```

**适用场景**：
- ✅ 日常开发任务
- ✅ 快速原型开发
- ✅ 性能要求高
- ✅ 简单问题
- ✅ 只关心最终代码

### 何时使用认知工作流 ✓

```python
# 研究或详细分析
agent = CognitiveDrivenCodeGenAgent(llm, enable_cognitive_guidance=True)
result = agent.generate(
    request="写一个快速排序函数",
    context={"domain": "算法", "level": "高级"}
)
```

**适用场景**：
- ✅ 学术研究
- ✅ 论文撰写
- ✅ 深度分析需求
- ✅ 复杂算法
- ✅ 需要决策追踪
- ✅ 需要认知分析
- ✅ 想要完整的可解释性

---

## 💻 实际代码示例

### 示例1️⃣：标准模式
```python
from llm.structured_llm import StructuredLLM
from agent.code_agent import CodeGenAgent

# 初始化
llm = StructuredLLM(model="gpt-4o-2024-08-06")
agent = CodeGenAgent(llm, max_refine_attempts=3)

# 生成代码
result = agent.generate(
    "实现一个快速排序算法，要求时间复杂度O(n log n)"
)

# 检查结果
if result["success"]:
    print(f"✓ 代码生成成功")
    print(f"  代码长度: {len(result['code'])} 字符")
    print(f"  测试通过: {result['validation']['passed_count']}/{result['validation']['total_tests']}")
    print(f"  行有效性: {result['validation']['line_effectiveness_score']:.2f}/1.0")
    print(f"  优化次数: {result['refine_attempts']}")
    print("\n代码:")
    print(result['code'])
else:
    print(f"✗ 生成失败: {result.get('error')}")
```

### 示例2️⃣：认知模式
```python
from llm.structured_llm import StructuredLLM
from agent.cognitive_code_agent import CognitiveDrivenCodeGenAgent

# 初始化
llm = StructuredLLM(model="gpt-4o-2024-08-06")
agent = CognitiveDrivenCodeGenAgent(
    llm=llm,
    max_refine_attempts=3,
    enable_cognitive_guidance=True
)

# 带上下文的生成
result = agent.generate(
    request="实现一个二分查找树的插入和查询操作",
    context={
        "domain": "数据结构",
        "level": "进阶",
        "constraints": ["必须保持平衡", "插入时间O(log n)"]
    }
)

# 检查结果
if result["success"]:
    print(f"✓ 认知驱动代码生成成功")

    # 基本信息
    print(f"代码:")
    print(result['code'])

    # 认知分析
    print(f"\n【认知分析】")
    analysis = result['cognitive_analysis']
    print(f"  问题理解: {analysis['problem_understanding']}")
    print(f"  选择策略: {analysis['strategy_selection']}")
    print(f"  认知负荷: {analysis['cognitive_load_estimate']:.1f}")
    print(f"  置信度: {analysis['confidence_level']:.2f}")

    # 决策摘要
    print(f"\n【决策摘要】")
    summary = result['cognitive_summary']
    print(f"  总决策数: {summary['total_decisions']}")
    print(f"  平均置信度: {summary['average_confidence']:.2f}")
    print(f"  耗时: {summary['session_duration']:.2f}秒")
    print(f"  主要策略: {summary['dominant_strategy']}")

    # 决策链
    print(f"\n【完整决策链】")
    for i, decision in enumerate(result['cognitive_decisions'], 1):
        print(f"  决策{i}: [{decision['stage']}] {decision['decision']}")
        print(f"    理由: {decision['reasoning']}")
        print(f"    置信度: {decision['confidence']:.2f}")

    # 策略适应
    if result['strategy_adaptations']:
        print(f"\n【应用的适应策略】")
        for adaptation in result['strategy_adaptations']:
            print(f"  {adaptation['strategy']}: {adaptation['action']}")

else:
    print(f"✗ 生成失败: {result.get('error')}")
```

---

## 🔧 配置选项

### 标准代理配置
```python
agent = CodeGenAgent(
    llm=llm,
    max_iterations=10,        # 最大迭代次数
    max_refine_attempts=3     # 最大优化尝试次数
)
```

### 认知代理配置
```python
agent = CognitiveDrivenCodeGenAgent(
    llm=llm,
    max_iterations=10,
    max_refine_attempts=3,
    enable_cognitive_guidance=True  # 启用/禁用认知指导
)

# 自定义认知策略
from cognitive.cognitive_load_aware_generator import CognitiveStrategy

strategy = CognitiveStrategy(
    target_load=0.7,              # 目标认知负荷
    load_tolerance=0.1,           # 负荷容忍度
    adaptation_threshold=0.8,     # 适应阈值
    scaffolding_level=0.5,        # 脚手架水平
    chunking_size=7,              # 分块大小
    guidance_verbosity=0.6        # 指导详细程度
)
```

---

## 📚 完整工作流总结表

| 方面 | 标准工作流 | 认知工作流 |
|------|----------|----------|
| **主要类** | CodeGenAgent | CognitiveDrivenCodeGenAgent |
| **阶段数** | 4 | 4 |
| **子过程数** | 4 | 12+ |
| **包含模块** | 4个工具 | 7个认知模块 + 4个工具 |
| **决策追踪** | ❌ | ✅ |
| **认知分析** | ❌ | ✅ |
| **行有效性** | ✅ | ✅ |
| **输出字段数** | 6 | 12+ |
| **使用难度** | 简单 | 中等 |
| **执行时间** | 快 | 较慢 |
| **推荐用途** | 日常 | 研究/论文 |

---

## ✨ 关键概念

### 认知负荷 (Cognitive Load)
```python
# 三种类型的认知负荷
intrinsic_load: 问题本身的复杂度
extraneous_load: 不必要的复杂度（应该最小化）
germane_load: 与学习和理解相关的有效负荷

# 总负荷 = intrinsic_load + extraneous_load + germane_load
```

### 适应策略 (Adaptation Strategies)
```python
REDUCE_COMPLEXITY      # 降低问题复杂度
INCREASE_SCAFFOLDING   # 增加脚手架（更多说明）
OPTIMIZE_CHUNKING      # 优化分块（分解问题）
ENHANCE_CLARITY        # 增强清晰度
PROVIDE_GUIDANCE       # 提供指导
ADAPTIVE_PACING        # 自适应节奏
```

### 编程策略 (Programming Strategies)
```python
STRATEGIC_APPROACH          # 策略性：整体规划
STRUCTURED_APPROACH         # 结构化：清晰的结构
DATA_FLOW_APPROACH         # 数据流：关注数据变换
OBJECT_ORIENTED_APPROACH   # 面向对象：对象和方法
DECLARATIVE_APPROACH       # 声明式：描述"是什么"
BOTTOM_UP_APPROACH         # 自底向上：从细节到整体
TOP_DOWN_APPROACH          # 自顶向下：从整体到细节
HYBRID_APPROACH            # 混合：结合多种方法
```

---

## 🎓 总结

**选择建议**：

1. **日常工作** → 用标准工作流
   ```python
   agent = CodeGenAgent(llm)
   result = agent.generate("...")
   ```

2. **研究论文** → 用认知工作流
   ```python
   agent = CognitiveDrivenCodeGenAgent(llm, enable_cognitive_guidance=True)
   result = agent.generate(request="...", context={...})
   ```

3. **需要最详细分析** → 直接使用认知工具
   ```python
   from cognitive.cognitive_load_aware_generator import CognitiveLoadAwareGenerator
   # 自己组织工作流...
   ```

---

希望这份指南能帮助你理解和选择合适的工作流！有任何问题吗？
