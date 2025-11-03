"""
代码行解释器

提供逐行代码解释，包括认知推理、语义目的和程序员意图。
支持多种解释类型，包括语法分析、逻辑推理和认知建模。
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from llm.structured_llm import StructuredLLM


class CognitiveType(Enum):
    """认知类型"""
    SYNTAX = "syntax"              # 语法分析
    LOGIC = "logic"                # 逻辑推理
    INTENTION = "intention"        # 意图理解
    PATTERN = "pattern"            # 模式识别
    ABSTRACTION = "abstraction"    # 抽象思维
    DECOMPOSITION = "decomposition"  # 分解思维


class LineExplanation(BaseModel):
    """单行代码解释"""
    line_number: int = Field(description="行号")
    code_content: str = Field(description="代码内容")
    cognitive_type: CognitiveType = Field(description="认知类型")
    semantic_purpose: str = Field(description="语义目的")
    cognitive_reasoning: str = Field(description="认知推理过程")
    programmer_intent: str = Field(description="程序员意图")
    context_relevance: str = Field(description="上下文相关性")
    complexity_level: float = Field(description="复杂度等级", ge=0, le=1)

    class Config:
        extra = "forbid"


class CodeExplanationResult(BaseModel):
    """代码解释结果"""
    line_explanations: Dict[int, LineExplanation] = Field(description="逐行解释")
    overall_structure: str = Field(description="整体结构分析")
    cognitive_patterns: List[str] = Field(description="认知模式")
    complexity_analysis: Dict[str, Any] = Field(description="复杂度分析")
    learning_insights: List[str] = Field(description="学习洞察")

    class Config:
        extra = "forbid"


class CognitiveLineExplainer:
    """
    认知驱动的代码行解释器

    提供详细的逐行代码解释，模拟程序员的认知过程。
    """

    def __init__(self, llm: Optional[StructuredLLM] = None):
        """初始化解释器"""
        self.llm = llm
        self.explanation_cache = {}

    def explain_code_lines(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        解释代码的每一行

        Args:
            code: 要解释的代码
            context: 额外的上下文信息

        Returns:
            包含逐行解释的字典
        """
        if not code.strip():
            return {
                "line_explanations": {},
                "overall_structure": "空代码",
                "cognitive_patterns": [],
                "complexity_analysis": {"overall": 0.0},
                "learning_insights": []
            }

        if self.llm:
            return self._explain_with_llm(code, context)
        else:
            return self._explain_basic(code, context)

    def _explain_with_llm(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """使用 LLM 进行详细解释"""

        context_info = ""
        if context:
            requirement = context.get("requirement", "")
            strategy = context.get("strategy", "")
            context_info = f"""
            原始需求: {requirement}
            使用策略: {strategy}
            """

        explanation_prompt = f"""
        请对以下代码进行逐行的认知解释，模拟一个经验丰富的程序员阅读代码时的思维过程：

        代码:
        ```python
        {code}
        ```

        上下文信息:
        {context_info}

        请为每一行非空、非注释的代码提供详细解释，包括：
        1. 确定认知类型（语法、逻辑、意图、模式、抽象、分解）
        2. 解释这行代码的语义目的
        3. 描述理解这行代码的认知推理过程
        4. 阐述程序员写这行代码的意图
        5. 分析与上下文的相关性
        6. 评估这行代码的复杂度等级 (0-1)

        同时提供：
        - 整体结构分析
        - 识别的认知模式
        - 复杂度分析
        - 学习洞察

        请以结构化的方式回答。
        """

        try:
            # 由于我们没有为这个特定场景定义 Pydantic 模型，
            # 我们将使用基础的文本生成然后解析
            # 在实际项目中应该定义专门的 schema

            # 暂时使用基础解释作为降级
            return self._explain_basic(code, context)

        except Exception as e:
            # LLM 调用失败，使用基础解释
            return self._explain_basic(code, context)

    def _explain_basic(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """基础代码解释（不使用 LLM）"""

        lines = code.split('\n')
        line_explanations = {}

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('#'):
                continue

            # 基础分析
            cognitive_type, semantic_purpose, reasoning, intent = self._analyze_line_basic(stripped)

            explanation = LineExplanation(
                line_number=i,
                code_content=line,
                cognitive_type=cognitive_type,
                semantic_purpose=semantic_purpose,
                cognitive_reasoning=reasoning,
                programmer_intent=intent,
                context_relevance=self._assess_context_relevance(stripped, context),
                complexity_level=self._assess_complexity(stripped)
            )

            line_explanations[i] = explanation

        # 整体分析
        overall_structure = self._analyze_overall_structure(lines)
        cognitive_patterns = self._identify_cognitive_patterns(lines)
        complexity_analysis = self._analyze_complexity(lines)
        learning_insights = self._generate_learning_insights(lines, context)

        return {
            "line_explanations": line_explanations,
            "overall_structure": overall_structure,
            "cognitive_patterns": cognitive_patterns,
            "complexity_analysis": complexity_analysis,
            "learning_insights": learning_insights
        }

    def _analyze_line_basic(self, line: str) -> tuple:
        """基础的单行分析"""

        if line.startswith('def '):
            return (
                CognitiveType.SYNTAX,
                "定义函数",
                "识别函数定义语法，理解函数名和参数",
                "创建一个可重用的代码块来实现特定功能"
            )

        elif line.startswith('class '):
            return (
                CognitiveType.ABSTRACTION,
                "定义类",
                "理解面向对象的抽象概念",
                "创建一个数据和方法的封装单元"
            )

        elif '=' in line and 'def' not in line and 'class' not in line:
            return (
                CognitiveType.LOGIC,
                "变量赋值",
                "理解赋值操作，跟踪变量状态变化",
                "存储计算结果或设置初始值"
            )

        elif line.startswith('if ') or line.startswith('elif '):
            return (
                CognitiveType.LOGIC,
                "条件判断",
                "评估条件表达式，理解分支逻辑",
                "根据不同条件执行不同的代码路径"
            )

        elif line.startswith('for ') or line.startswith('while '):
            return (
                CognitiveType.PATTERN,
                "循环控制",
                "理解迭代模式，预期重复执行",
                "对集合中的元素或满足条件时重复执行操作"
            )

        elif line.startswith('return '):
            return (
                CognitiveType.INTENTION,
                "返回结果",
                "理解函数输出，连接输入与输出的关系",
                "将计算结果传递给函数调用者"
            )

        elif line.startswith('try:') or line.startswith('except'):
            return (
                CognitiveType.PATTERN,
                "异常处理",
                "理解错误处理模式，预期可能的失败情况",
                "优雅地处理程序执行中可能出现的错误"
            )

        else:
            return (
                CognitiveType.LOGIC,
                "执行操作",
                "理解语句的执行效果",
                "执行特定的计算或操作"
            )

    def _assess_context_relevance(self, line: str, context: Optional[Dict[str, Any]]) -> str:
        """评估代码行与上下文的相关性"""
        if not context:
            return "与代码整体结构相关"

        requirement = context.get("requirement", "")
        if requirement:
            # 简单的关键词匹配
            if any(word in line.lower() for word in requirement.lower().split() if len(word) > 3):
                return f"直接实现需求：{requirement}"

        return "支持代码结构和逻辑流程"

    def _assess_complexity(self, line: str) -> float:
        """评估代码行的复杂度"""
        complexity = 0.1  # 基础复杂度

        # 基于不同模式增加复杂度
        if 'lambda' in line:
            complexity += 0.3
        if 'list(' in line or 'dict(' in line or 'set(' in line:
            complexity += 0.2
        if 'and' in line or 'or' in line:
            complexity += 0.1
        if '[' in line and ']' in line:  # 列表/字典访问
            complexity += 0.1
        if '.' in line:  # 方法调用
            complexity += 0.1

        return min(complexity, 1.0)

    def _analyze_overall_structure(self, lines: List[str]) -> str:
        """分析代码的整体结构"""
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

        if not non_empty_lines:
            return "空代码结构"

        has_function = any('def ' in line for line in non_empty_lines)
        has_class = any('class ' in line for line in non_empty_lines)
        has_loops = any(line.strip().startswith(('for ', 'while ')) for line in non_empty_lines)
        has_conditions = any(line.strip().startswith(('if ', 'elif ')) for line in non_empty_lines)

        structure_parts = []
        if has_function:
            structure_parts.append("函数定义")
        if has_class:
            structure_parts.append("类定义")
        if has_loops:
            structure_parts.append("循环结构")
        if has_conditions:
            structure_parts.append("条件判断")

        if structure_parts:
            return f"包含{', '.join(structure_parts)}的结构化代码"
        else:
            return "线性执行的简单代码结构"

    def _identify_cognitive_patterns(self, lines: List[str]) -> List[str]:
        """识别认知模式"""
        patterns = []

        # 检查各种模式
        if any('def ' in line for line in lines):
            patterns.append("函数抽象模式")

        if any(line.strip().startswith('for ') or line.strip().startswith('while ') for line in lines):
            patterns.append("迭代处理模式")

        if any(line.strip().startswith('if ') for line in lines):
            patterns.append("条件分支模式")

        if any('try:' in line or 'except' in line for line in lines):
            patterns.append("错误处理模式")

        assignment_count = sum(1 for line in lines if '=' in line and 'def' not in line and 'class' not in line)
        if assignment_count > 2:
            patterns.append("状态管理模式")

        return patterns

    def _analyze_complexity(self, lines: List[str]) -> Dict[str, Any]:
        """分析代码复杂度"""
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

        if not non_empty_lines:
            return {"overall": 0.0, "cognitive_load": "低"}

        total_complexity = sum(self._assess_complexity(line) for line in non_empty_lines)
        avg_complexity = total_complexity / len(non_empty_lines)

        if avg_complexity < 0.3:
            cognitive_load = "低"
        elif avg_complexity < 0.6:
            cognitive_load = "中"
        else:
            cognitive_load = "高"

        return {
            "overall": round(avg_complexity, 2),
            "cognitive_load": cognitive_load,
            "total_lines": len(non_empty_lines),
            "complexity_distribution": "基础分析"
        }

    def _generate_learning_insights(self, lines: List[str], context: Optional[Dict[str, Any]]) -> List[str]:
        """生成学习洞察"""
        insights = []

        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

        if any('def ' in line for line in lines):
            insights.append("代码使用函数封装，体现了模块化编程思想")

        if any('if ' in line for line in lines):
            insights.append("使用条件语句实现逻辑分支，体现了算法的决策过程")

        if len(non_empty_lines) > 10:
            insights.append("代码较长，可考虑进一步分解为更小的函数")

        if context and context.get("strategy"):
            strategy = context["strategy"]
            insights.append(f"代码实现采用了{strategy}策略，体现了问题解决的系统性方法")

        return insights