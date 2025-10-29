"""
认知驱动的行级代码解释器

使用LLM生成基于认知科学的深层语义解释，而不是简单的语法分类。
模拟人类程序员在阅读代码时的认知过程和思维模式。
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from enum import Enum

from llm.structured_llm import StructuredLLM
from .cognitive_model import CognitiveModel, CognitiveState, ThinkingStage


class CognitiveLineType(Enum):
    """认知层面的代码行类型"""
    PROBLEM_SETUP = "problem_setup"           # 问题设置（函数定义、参数）
    MENTAL_MODEL = "mental_model"             # 心理模型构建（变量初始化、数据结构）
    LOGICAL_REASONING = "logical_reasoning"    # 逻辑推理（条件判断、循环）
    DATA_TRANSFORMATION = "data_transformation" # 数据转换（计算、处理）
    GOAL_ACHIEVEMENT = "goal_achievement"      # 目标达成（返回结果、输出）
    ERROR_HANDLING = "error_handling"          # 错误处理（异常、边界条件）
    COGNITIVE_OFFLOAD = "cognitive_offload"    # 认知卸载（辅助函数、注释）


class LineExplanation(BaseModel):
    """单行代码的认知解释"""
    line_number: int = Field(description="行号")
    code_line: str = Field(description="代码内容")
    cognitive_type: CognitiveLineType = Field(description="认知类型")
    semantic_purpose: str = Field(description="语义目的")
    cognitive_reasoning: str = Field(description="认知推理过程")
    programmer_intent: str = Field(description="程序员意图")
    mental_model_impact: str = Field(description="对心理模型的影响")
    cognitive_load: float = Field(description="认知负荷 (0-1)", ge=0, le=1)
    dependencies: List[int] = Field(description="依赖的其他行号", default_factory=list)
    contributes_to: List[int] = Field(description="贡献给其他行号", default_factory=list)


class CodeBlockExplanation(BaseModel):
    """代码块的整体认知解释"""
    overall_strategy: str = Field(description="整体策略")
    cognitive_flow: str = Field(description="认知流程")
    mental_model_evolution: List[str] = Field(description="心理模型演化过程")
    decision_points: List[Dict[str, Any]] = Field(description="关键决策点")
    complexity_analysis: Dict[str, Any] = Field(description="复杂度分析")


class CognitiveLineExplainer:
    """认知驱动的行级代码解释器"""

    def __init__(self, llm: StructuredLLM):
        self.llm = llm

    def explain_code_lines(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成代码的认知驱动行级解释

        Args:
            code: 要解释的代码
            context: 额外上下文信息

        Returns:
            包含行级解释和整体分析的字典
        """
        lines = code.strip().split('\n')

        # 第一阶段：生成每行的认知解释
        line_explanations = []
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                explanation = self._generate_line_explanation(
                    line_number=i,
                    code_line=line,
                    full_code=code,
                    context=context
                )
                line_explanations.append(explanation)

        # 第二阶段：生成整体认知流程分析
        block_explanation = self._generate_block_explanation(code, line_explanations, context)

        # 第三阶段：构建认知依赖图
        dependency_graph = self._build_cognitive_dependency_graph(line_explanations)

        return {
            "line_explanations": {exp.line_number: exp for exp in line_explanations},
            "block_explanation": block_explanation,
            "dependency_graph": dependency_graph,
            "cognitive_summary": self._generate_cognitive_summary(line_explanations, block_explanation)
        }

    def _generate_line_explanation(self, line_number: int, code_line: str,
                                 full_code: str, context: Optional[Dict[str, Any]]) -> LineExplanation:
        """生成单行的认知解释"""

        prompt = f"""
作为一个认知科学专家和程序员，请分析这行代码在程序员思维过程中的作用。

完整代码：
```python
{full_code}
```

当前分析行（第{line_number}行）：
{code_line}

请从以下认知角度分析这行代码：

1. **认知类型**：这行代码在程序员的思维过程中扮演什么角色？
   - 问题设置：定义问题空间和参数
   - 心理模型：构建或修改数据的心理模型
   - 逻辑推理：执行条件判断或循环逻辑
   - 数据转换：处理和转换数据
   - 目标达成：实现最终目标
   - 错误处理：处理异常情况
   - 认知卸载：减少认知负担的辅助代码

2. **语义目的**：这行代码的真正目的是什么？（不只是语法层面）

3. **认知推理**：程序员写这行代码时的思维过程是什么？

4. **程序员意图**：程序员希望通过这行代码实现什么？

5. **心理模型影响**：这行代码如何改变程序员对问题的心理模型？

6. **认知负荷**：理解这行代码需要多大的认知努力？(0-1)

请提供深入的认知层面分析，不是简单的语法描述。
"""

        # 使用结构化输出生成解释
        try:
            explanation_data = self.llm.generate_structured(
                prompt=prompt,
                output_schema=LineExplanation,
                model="gpt-4o-2024-08-06"
            )

            # 设置基本信息
            explanation_data.line_number = line_number
            explanation_data.code_line = code_line.strip()

            return explanation_data

        except Exception as e:
            # 如果LLM调用失败，返回基础解释
            return self._generate_fallback_explanation(line_number, code_line)

    def _generate_block_explanation(self, code: str, line_explanations: List[LineExplanation],
                                  context: Optional[Dict[str, Any]]) -> CodeBlockExplanation:
        """生成代码块的整体认知解释"""

        prompt = f"""
作为认知科学专家，请分析这段代码的整体认知结构。

代码：
```python
{code}
```

行级分析摘要：
{self._summarize_line_explanations(line_explanations)}

请提供以下认知层面的整体分析：

1. **整体策略**：程序员采用了什么样的问题解决策略？

2. **认知流程**：程序员的思维是如何从问题理解流向解决方案的？

3. **心理模型演化**：程序员的心理模型是如何逐步构建和演化的？

4. **关键决策点**：代码中有哪些关键的认知决策点？

5. **复杂度分析**：从认知角度看，这段代码的复杂度如何？

请提供深入的认知科学分析。
"""

        try:
            return self.llm.generate_structured(
                prompt=prompt,
                output_schema=CodeBlockExplanation,
                model="gpt-4o-2024-08-06"
            )
        except Exception as e:
            # 返回基础分析
            return CodeBlockExplanation(
                overall_strategy="逐步解决问题",
                cognitive_flow="问题理解 -> 解决方案设计 -> 实现",
                mental_model_evolution=["构建问题模型", "设计解决方案", "实现代码"],
                decision_points=[],
                complexity_analysis={"cognitive_load": "medium", "complexity_type": "linear"}
            )

    def _build_cognitive_dependency_graph(self, line_explanations: List[LineExplanation]) -> Dict[str, Any]:
        """构建认知依赖图"""

        # 分析变量和概念的依赖关系
        dependencies = {}
        contributions = {}

        for explanation in line_explanations:
            line_num = explanation.line_number

            # 简单的依赖分析（可以进一步增强）
            for other_exp in line_explanations:
                if other_exp.line_number < line_num:
                    # 检查是否有认知依赖
                    if self._has_cognitive_dependency(explanation, other_exp):
                        if line_num not in dependencies:
                            dependencies[line_num] = []
                        dependencies[line_num].append(other_exp.line_number)

                        if other_exp.line_number not in contributions:
                            contributions[other_exp.line_number] = []
                        contributions[other_exp.line_number].append(line_num)

        return {
            "dependencies": dependencies,
            "contributions": contributions,
            "cognitive_clusters": self._identify_cognitive_clusters(line_explanations)
        }

    def _has_cognitive_dependency(self, current: LineExplanation, previous: LineExplanation) -> bool:
        """判断两行代码是否有认知依赖关系"""

        # 基于认知类型的依赖规则
        dependency_rules = {
            CognitiveLineType.MENTAL_MODEL: [CognitiveLineType.PROBLEM_SETUP],
            CognitiveLineType.LOGICAL_REASONING: [CognitiveLineType.MENTAL_MODEL, CognitiveLineType.PROBLEM_SETUP],
            CognitiveLineType.DATA_TRANSFORMATION: [CognitiveLineType.MENTAL_MODEL, CognitiveLineType.LOGICAL_REASONING],
            CognitiveLineType.GOAL_ACHIEVEMENT: [CognitiveLineType.DATA_TRANSFORMATION, CognitiveLineType.LOGICAL_REASONING],
        }

        current_type = current.cognitive_type
        previous_type = previous.cognitive_type

        return previous_type in dependency_rules.get(current_type, [])

    def _identify_cognitive_clusters(self, line_explanations: List[LineExplanation]) -> List[Dict[str, Any]]:
        """识别认知功能簇"""

        clusters = []
        current_cluster = []
        current_type = None

        for explanation in line_explanations:
            if current_type is None or explanation.cognitive_type == current_type:
                current_cluster.append(explanation.line_number)
                current_type = explanation.cognitive_type
            else:
                if current_cluster:
                    clusters.append({
                        "type": current_type.value,
                        "lines": current_cluster,
                        "description": f"认知功能簇: {current_type.value}"
                    })
                current_cluster = [explanation.line_number]
                current_type = explanation.cognitive_type

        # 添加最后一个簇
        if current_cluster:
            clusters.append({
                "type": current_type.value,
                "lines": current_cluster,
                "description": f"认知功能簇: {current_type.value}"
            })

        return clusters

    def _generate_cognitive_summary(self, line_explanations: List[LineExplanation],
                                  block_explanation: CodeBlockExplanation) -> Dict[str, Any]:
        """生成认知摘要"""

        total_cognitive_load = sum(exp.cognitive_load for exp in line_explanations)
        avg_cognitive_load = total_cognitive_load / len(line_explanations) if line_explanations else 0

        type_distribution = {}
        for exp in line_explanations:
            type_name = exp.cognitive_type.value
            type_distribution[type_name] = type_distribution.get(type_name, 0) + 1

        return {
            "total_lines_analyzed": len(line_explanations),
            "average_cognitive_load": avg_cognitive_load,
            "cognitive_type_distribution": type_distribution,
            "complexity_level": "high" if avg_cognitive_load > 0.7 else "medium" if avg_cognitive_load > 0.4 else "low",
            "dominant_cognitive_types": sorted(type_distribution.items(), key=lambda x: x[1], reverse=True)[:3],
            "overall_strategy": block_explanation.overall_strategy
        }

    def _summarize_line_explanations(self, line_explanations: List[LineExplanation]) -> str:
        """总结行级解释"""

        summary_lines = []
        for exp in line_explanations:
            summary_lines.append(f"第{exp.line_number}行: {exp.cognitive_type.value} - {exp.semantic_purpose}")

        return "\n".join(summary_lines)

    def _generate_fallback_explanation(self, line_number: int, code_line: str) -> LineExplanation:
        """生成备用解释（当LLM不可用时）"""

        line = code_line.strip()

        # 基础认知类型推断
        if line.startswith('def '):
            cognitive_type = CognitiveLineType.PROBLEM_SETUP
            purpose = "定义函数，设置问题求解的框架"
        elif line.startswith('if ') or line.startswith('elif ') or line.startswith('else'):
            cognitive_type = CognitiveLineType.LOGICAL_REASONING
            purpose = "执行条件判断，进行逻辑推理"
        elif line.startswith('return '):
            cognitive_type = CognitiveLineType.GOAL_ACHIEVEMENT
            purpose = "返回结果，达成问题求解目标"
        elif '=' in line and not line.startswith('#'):
            cognitive_type = CognitiveLineType.MENTAL_MODEL
            purpose = "构建或修改数据的心理模型"
        else:
            cognitive_type = CognitiveLineType.DATA_TRANSFORMATION
            purpose = "执行数据处理或转换操作"

        return LineExplanation(
            line_number=line_number,
            code_line=line,
            cognitive_type=cognitive_type,
            semantic_purpose=purpose,
            cognitive_reasoning="基于语法模式的基础推理",
            programmer_intent="实现特定的编程逻辑",
            mental_model_impact="对整体问题求解模型的贡献",
            cognitive_load=0.5,
            dependencies=[],
            contributes_to=[]
        )


def create_cognitive_line_explainer(llm: StructuredLLM) -> CognitiveLineExplainer:
    """创建认知行级解释器"""
    return CognitiveLineExplainer(llm)