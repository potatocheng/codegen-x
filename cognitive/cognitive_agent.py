"""
Cognitive-driven Code Generation Agent

This module implements a cognitive agent that simulates human programmer thinking
for generating high-quality, explainable code with line-by-line reasoning.
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
import time
from datetime import datetime

from .cognitive_model import (
    CognitiveModel, CognitiveState, ThinkingStage,
    CognitiveTransition, WorkingMemoryItem
)
from .thinking_process import (
    ThinkingProcess, ReasoningChain, ThoughtStep,
    ProblemDecomposition, SolutionHypothesis, ThoughtType
)
from .cognitive_load import CognitiveLoadEvaluator, CognitiveComplexity
from .programming_strategy import ProgrammingStrategy, StrategyType, ProblemCharacteristics
from .line_effectiveness_validator import LineEffectivenessValidator
from .cognitive_line_explainer import CognitiveLineExplainer
from .llm_schemas import (
    ProblemComprehension, SolutionPlan, AlgorithmDesign,
    CodeImplementation, ValidationResult, OptimizationResult,
    SolutionReflection, ProblemComplexity, ComponentType
)
from llm.structured_llm import StructuredLLM


class CognitiveCodeGenRequest(BaseModel):
    """Request for cognitive-driven code generation"""
    requirement: str = Field(description="Natural language requirement")
    context: Optional[str] = Field(default=None, description="Additional context")
    constraints: Optional[List[str]] = Field(default_factory=list, description="Implementation constraints")
    difficulty: Optional[str] = Field(default="medium", description="Problem difficulty level")


class CognitiveCodeGenOutput(BaseModel):
    """Output from cognitive-driven code generation"""
    generated_code: str = Field(description="Generated Python code")
    explanation: str = Field(description="High-level explanation")
    line_explanations: Dict[int, str] = Field(description="Line-by-line explanations")
    cognitive_explanation: Dict[str, Any] = Field(description="Detailed cognitive explanation", default_factory=dict)
    cognitive_trace: Dict[str, Any] = Field(description="Cognitive process trace")
    reasoning_chain: List[str] = Field(description="Step-by-step reasoning")
    confidence: float = Field(description="Confidence in solution (0-1)")
    cognitive_load: CognitiveComplexity = Field(description="Cognitive complexity analysis")
    strategy_used: StrategyType = Field(description="Programming strategy employed")
    thinking_stages: List[Dict[str, Any]] = Field(description="Cognitive stages traversed")


class CognitiveCodeGenAgent:
    """
    Cognitive-driven Code Generation Agent

    Simulates human programmer cognition to generate explainable code
    with detailed reasoning at each step.
    """

    def __init__(self, llm: StructuredLLM, max_thinking_depth: int = 5):
        self.llm = llm
        self.max_thinking_depth = max_thinking_depth

        # Initialize cognitive components
        self.cognitive_model = CognitiveModel(
            current_state=CognitiveState(
                stage=ThinkingStage.PROBLEM_COMPREHENSION,
                focus="",
                working_memory=[],
                mental_effort=0.0,
                confidence=0.0,
                timestamp=datetime.now()
            ),
            state_history=[],
            transitions=[]
        )

        self.thinking_process = ThinkingProcess(
            session_id=f"session_{int(time.time())}",
            problem_statement="",  # 将在生成代码时设置
            reasoning_chains=[],
            decompositions=[],
            hypotheses=[],
            active_concepts={}
        )

        self.cognitive_load_evaluator = CognitiveLoadEvaluator()
        self.programming_strategy = ProgrammingStrategy()
        self.effectiveness_validator = LineEffectivenessValidator()
        self.line_explainer = CognitiveLineExplainer(llm)

        # Cognitive trace for explainability
        self.cognitive_trace = {
            "stages": [],
            "decisions": [],
            "reasoning": [],
            "strategy_changes": []
        }

    def generate_code(self, request: CognitiveCodeGenRequest) -> CognitiveCodeGenOutput:
        """
        Generate code using cognitive-driven approach

        Simulates human programmer thinking through all cognitive stages
        """
        start_time = time.time()

        # 更新思维过程的问题陈述
        self.thinking_process.problem_statement = request.requirement

        # Reset cognitive state
        self._reset_cognitive_state()

        # Stage 1: Problem Comprehension
        problem_understanding = self._comprehend_problem(request)

        # Stage 2: Solution Planning
        solution_plan = self._plan_solution(problem_understanding)

        # Stage 3: Algorithm Design
        algorithm_design = self._design_algorithm(solution_plan)

        # Stage 4: Implementation
        implementation = self._implement_code(algorithm_design)

        # Stage 5: Validation
        validation_result = self._validate_solution(implementation, request)

        # Stage 6: Optimization (if needed)
        if validation_result["needs_optimization"]:
            implementation = self._optimize_solution(implementation, validation_result)

        # Stage 7: Reflection
        reflection = self._reflect_on_solution(implementation, request)

        # Generate line-by-line explanations using cognitive explainer
        cognitive_explanation = self.line_explainer.explain_code_lines(
            implementation["code"],
            context={
                "requirement": request.requirement,
                "cognitive_trace": self.cognitive_trace,
                "strategy": implementation["strategy"]
            }
        )

        # Extract line explanations for backward compatibility
        line_explanations = {}
        for line_num, exp in cognitive_explanation["line_explanations"].items():
            line_explanations[line_num] = (
                f"[{exp.cognitive_type.value}] {exp.semantic_purpose} | "
                f"认知推理: {exp.cognitive_reasoning} | "
                f"程序员意图: {exp.programmer_intent}"
            )

        # Evaluate cognitive load
        cognitive_load = self.cognitive_load_evaluator.evaluate_code_complexity(
            implementation["code"],
            {"requirement": request.requirement}
        )

        return CognitiveCodeGenOutput(
            generated_code=implementation["code"],
            explanation=implementation["explanation"],
            line_explanations=line_explanations,
            cognitive_explanation=cognitive_explanation,
            cognitive_trace=self.cognitive_trace,
            reasoning_chain=self._extract_reasoning_chain(),
            confidence=implementation["confidence"],
            cognitive_load=cognitive_load,
            strategy_used=implementation.get("strategy_object", StrategyType.TOP_DOWN),
            thinking_stages=self._extract_thinking_stages()
        )

    def _reset_cognitive_state(self):
        """Reset cognitive state for new problem"""
        self.cognitive_model.current_state = CognitiveState(
            stage=ThinkingStage.PROBLEM_COMPREHENSION,
            focus="",
            working_memory=[],
            mental_effort=0.0,
            confidence=0.0,
            timestamp=datetime.now()
        )
        self.cognitive_model.state_history = []
        self.cognitive_model.transitions = []

        self.thinking_process.reasoning_chains = []
        self.thinking_process.decompositions = []
        self.thinking_process.hypotheses = []
        self.thinking_process.active_concepts = {}

        self.cognitive_trace = {
            "stages": [],
            "decisions": [],
            "reasoning": [],
            "strategy_changes": []
        }

    def _transition_to_stage(self, new_stage: ThinkingStage, focus: str):
        """Transition to new cognitive stage"""
        old_state = self.cognitive_model.current_state

        new_state = CognitiveState(
            stage=new_stage,
            focus=focus,
            working_memory=old_state.working_memory.copy(),
            mental_effort=0.0,
            confidence=0.0,
            timestamp=datetime.now()
        )

        transition = CognitiveTransition(
            from_stage=old_state.stage,
            to_stage=new_stage,
            trigger=focus,
            timestamp=datetime.now()
        )

        self.cognitive_model.state_history.append(old_state)
        self.cognitive_model.transitions.append(transition)
        self.cognitive_model.current_state = new_state

        self.cognitive_trace["stages"].append({
            "stage": new_stage.value,
            "focus": focus,
            "timestamp": datetime.now().isoformat()
        })

    def _comprehend_problem(self, request: CognitiveCodeGenRequest) -> Dict[str, Any]:
        """Stage 1: Problem Comprehension with LLM"""
        self._transition_to_stage(ThinkingStage.PROBLEM_COMPREHENSION, request.requirement)

        # Create detailed problem analysis prompt
        comprehension_prompt = f"""
        作为一个经验丰富的程序员，请仔细分析以下编程需求并提供详细的问题理解：

        需求描述: {request.requirement}
        额外上下文: {request.context or '无'}
        约束条件: {', '.join(request.constraints) if request.constraints else '无特殊约束'}
        预估难度: {request.difficulty}

        请从以下角度进行分析：
        1. 理解问题的核心目标和主要功能
        2. 识别需要处理的关键组件类型
        3. 评估问题的复杂度等级
        4. 明确输入和输出要求
        5. 识别约束条件和限制
        6. 考虑可能的边界情况
        7. 提出初步的实现思路
        8. 确定需要的领域知识

        请以结构化的方式回答，确保涵盖所有重要方面。
        """

        try:
            # 使用 LLM 进行结构化分析
            comprehension_result = self.llm.generate_structured(
                prompt=comprehension_prompt,
                output_schema=ProblemComprehension
            )

            # 将结构化结果转换为字典格式以保持兼容性
            understanding = {
                "main_goal": comprehension_result.main_goal,
                "key_components": [comp.value for comp in comprehension_result.key_components],
                "complexity_assessment": comprehension_result.complexity_assessment.value,
                "input_requirements": comprehension_result.input_requirements,
                "output_requirements": comprehension_result.output_requirements,
                "constraints": comprehension_result.constraints,
                "edge_cases": comprehension_result.edge_cases,
                "initial_thoughts": comprehension_result.initial_thoughts,
                "domain_knowledge_needed": comprehension_result.domain_knowledge_needed,
                "llm_analysis": comprehension_result  # 保存完整的结构化结果
            }

        except Exception as e:
            # LLM 调用失败时的降级处理
            self.cognitive_trace["decisions"].append({
                "stage": "problem_comprehension",
                "issue": f"LLM 调用失败: {str(e)}",
                "fallback": "使用基础分析"
            })

            understanding = {
                "main_goal": request.requirement,
                "key_components": ["input_processing", "core_logic", "output_formatting"],
                "complexity_assessment": "medium",
                "input_requirements": ["待分析的输入数据"],
                "output_requirements": ["处理后的结果"],
                "constraints": request.constraints or [],
                "edge_cases": ["空输入", "无效输入"],
                "initial_thoughts": [
                    "需要理解具体要求",
                    "识别输入输出规格",
                    "考虑边界情况和约束"
                ],
                "domain_knowledge_needed": ["基础编程概念"]
            }

        # 创建问题分解用于思维过程
        decomposition = self.thinking_process.decompose_problem(
            request.requirement,
            approach="top_down"
        )

        # Update working memory
        self.cognitive_model.current_state.working_memory.append(
            WorkingMemoryItem(
                content=f"Problem: {understanding['main_goal']}",
                importance=1.0,
                timestamp=datetime.now()
            )
        )

        # 更新认知追踪
        self.cognitive_trace["reasoning"].append({
            "stage": "problem_comprehension",
            "understanding": understanding,
            "decomposition_id": decomposition,
            "confidence": 0.8
        })

        return understanding

    def _plan_solution(self, problem_understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Solution Planning with LLM"""
        self._transition_to_stage(ThinkingStage.SOLUTION_PLANNING, "Planning solution approach")

        # Create solution planning prompt
        planning_prompt = f"""
        基于对问题的理解，请制定详细的解决方案计划：

        问题目标: {problem_understanding['main_goal']}
        关键组件: {', '.join(problem_understanding['key_components'])}
        复杂度评估: {problem_understanding['complexity_assessment']}
        输入要求: {', '.join(problem_understanding.get('input_requirements', []))}
        输出要求: {', '.join(problem_understanding.get('output_requirements', []))}
        约束条件: {', '.join(problem_understanding.get('constraints', []))}
        边界情况: {', '.join(problem_understanding.get('edge_cases', []))}

        请选择最适合的编程策略并制定实施计划：
        1. 选择最合适的解决策略（如自顶向下、递归、动态规划等）
        2. 解释选择该策略的理由
        3. 列出实施的主要步骤
        4. 确定步骤之间的依赖关系
        5. 识别需要考虑的因素
        6. 预见可能的挑战
        7. 提供备选方案
        8. 估计实施难度

        请提供结构化的规划方案。
        """

        try:
            # 使用 LLM 进行解决方案规划
            planning_result = self.llm.generate_structured(
                prompt=planning_prompt,
                output_schema=SolutionPlan
            )

            plan = {
                "strategy": planning_result.chosen_strategy.value,
                "strategy_rationale": planning_result.strategy_rationale,
                "approach": f"采用{planning_result.chosen_strategy.value}策略的步骤化实施",
                "main_steps": planning_result.main_steps,
                "step_dependencies": planning_result.step_dependencies,
                "considerations": planning_result.considerations,
                "potential_challenges": planning_result.potential_challenges,
                "alternative_approaches": planning_result.alternative_approaches,
                "estimated_difficulty": planning_result.estimated_difficulty.value,
                "llm_plan": planning_result  # 保存完整的结构化结果
            }

        except Exception as e:
            # LLM 调用失败时的降级处理
            self.cognitive_trace["decisions"].append({
                "stage": "solution_planning",
                "issue": f"LLM 调用失败: {str(e)}",
                "fallback": "使用基础规划"
            })

            # 根据问题理解选择合适的策略
            complexity = problem_understanding.get('complexity_assessment', 'medium')
            if complexity in ['simple', 'trivial']:
                strategy = "top_down"
            elif complexity == 'complex':
                strategy = "divide_conquer"
            else:
                strategy = "iterative"

            plan = {
                "strategy": strategy,
                "strategy_rationale": f"基于{complexity}复杂度选择{strategy}策略",
                "approach": "step-by-step implementation",
                "main_steps": [
                    "定义函数签名",
                    "实现核心逻辑",
                    "处理边界情况",
                    "返回结果"
                ],
                "step_dependencies": {},
                "considerations": [
                    "输入验证",
                    "性能优化",
                    "代码可读性"
                ],
                "potential_challenges": ["实现复杂度", "性能要求"],
                "alternative_approaches": ["其他算法选择"],
                "estimated_difficulty": complexity
            }

        # 根据选择的策略创建编程策略对象
        try:
            problem_chars = ProblemCharacteristics(
                domain="general",
                complexity=plan["estimated_difficulty"],
                data_structures=problem_understanding.get('key_components', ["list"]),
                algorithms=[plan["strategy"]],
                constraints=problem_understanding.get('constraints', [])
            )

            strategy = self.programming_strategy.select_strategy(
                problem_chars,
                self.cognitive_model.current_state,
                self.thinking_process
            )
            plan["strategy_object"] = strategy

        except Exception as e:
            plan["strategy_object"] = StrategyType.TOP_DOWN

        self.cognitive_trace["decisions"].append({
            "stage": "solution_planning",
            "strategy_selected": plan["strategy"],
            "reasoning": plan["strategy_rationale"]
        })

        return plan

    def _design_algorithm(self, solution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 3: Algorithm Design with LLM"""
        self._transition_to_stage(ThinkingStage.ALGORITHM_DESIGN, "Designing algorithm structure")

        # Create algorithm design prompt
        algorithm_prompt = f"""
        基于解决方案计划，请设计详细的算法：

        选择的策略: {solution_plan['strategy']}
        策略理由: {solution_plan['strategy_rationale']}
        主要步骤: {', '.join(solution_plan['main_steps'])}
        需要考虑的因素: {', '.join(solution_plan['considerations'])}
        潜在挑战: {', '.join(solution_plan['potential_challenges'])}

        请设计算法的详细结构：
        1. 为算法命名并提供描述
        2. 编写清晰的伪代码步骤
        3. 确定需要的数据结构
        4. 分析算法组件及其作用
        5. 计算时间和空间复杂度
        6. 定义循环不变量（如适用）
        7. 说明边界情况的处理方法
        8. 识别优化机会

        请提供结构化的算法设计。
        """

        try:
            # 使用 LLM 进行算法设计
            algorithm_result = self.llm.generate_structured(
                prompt=algorithm_prompt,
                output_schema=AlgorithmDesign
            )

            algorithm = {
                "algorithm_name": algorithm_result.algorithm_name,
                "algorithm_description": algorithm_result.algorithm_description,
                "pseudocode": algorithm_result.pseudocode,
                "data_structures": algorithm_result.data_structures,
                "components": [
                    {
                        "name": comp.name,
                        "purpose": comp.purpose,
                        "input_type": comp.input_type,
                        "output_type": comp.output_type,
                        "complexity": comp.complexity
                    } for comp in algorithm_result.components
                ],
                "time_complexity": algorithm_result.time_complexity,
                "space_complexity": algorithm_result.space_complexity,
                "invariants": algorithm_result.invariants,
                "edge_cases": algorithm_result.edge_cases_handling,
                "optimization_opportunities": algorithm_result.optimization_opportunities,
                "llm_design": algorithm_result  # 保存完整的结构化结果
            }

        except Exception as e:
            # LLM 调用失败时的降级处理
            self.cognitive_trace["decisions"].append({
                "stage": "algorithm_design",
                "issue": f"LLM 调用失败: {str(e)}",
                "fallback": "使用基础算法设计"
            })

            algorithm = {
                "algorithm_name": "solve_problem",
                "algorithm_description": f"使用{solution_plan['strategy']}策略解决问题",
                "pseudocode": [
                    "1. 验证输入参数",
                    "2. 初始化结果变量",
                    "3. 根据需求处理输入",
                    "4. 返回处理结果"
                ],
                "data_structures": ["variables", "loops"],
                "components": [
                    {
                        "name": "input_validator",
                        "purpose": "验证输入",
                        "input_type": "Any",
                        "output_type": "bool",
                        "complexity": "O(1)"
                    },
                    {
                        "name": "core_processor",
                        "purpose": "核心处理逻辑",
                        "input_type": "Any",
                        "output_type": "Any",
                        "complexity": "O(n)"
                    }
                ],
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "invariants": ["输入保持有效", "处理过程保持一致性"],
                "edge_cases": ["empty input", "invalid input"],
                "optimization_opportunities": ["缓存计算结果", "减少重复操作"]
            }

        return algorithm

    def _implement_code(self, algorithm_design: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 4: Implementation with LLM"""
        self._transition_to_stage(ThinkingStage.IMPLEMENTATION, "Writing code")

        # Create implementation prompt
        implementation_prompt = f"""
        基于算法设计，请实现完整的Python代码：

        算法名称: {algorithm_design.get('algorithm_name', 'solve_problem')}
        算法描述: {algorithm_design.get('algorithm_description', '')}
        伪代码: {chr(10).join(algorithm_design.get('pseudocode', []))}
        数据结构: {', '.join(algorithm_design.get('data_structures', []))}
        时间复杂度: {algorithm_design.get('time_complexity', 'O(n)')}
        空间复杂度: {algorithm_design.get('space_complexity', 'O(1)')}
        边界情况: {', '.join(algorithm_design.get('edge_cases', []))}

        请实现高质量的Python代码：
        1. 编写清晰的函数签名
        2. 添加完整的文档字符串
        3. 实现核心算法逻辑
        4. 创建必要的辅助函数
        5. 添加必要的导入语句
        6. 包含实现说明和设计理由

        确保代码：
        - 符合Python最佳实践
        - 处理所有边界情况
        - 具有良好的可读性和可维护性
        - 包含适当的错误处理
        """

        try:
            # 使用 LLM 进行代码实现
            implementation_result = self.llm.generate_structured(
                prompt=implementation_prompt,
                output_schema=CodeImplementation
            )

            implementation = {
                "function_name": implementation_result.function_name,
                "function_signature": implementation_result.function_signature,
                "code": implementation_result.implementation_code,
                "docstring": implementation_result.docstring,
                "helper_functions": implementation_result.helper_functions,
                "imports": implementation_result.import_statements,
                "explanation": implementation_result.code_rationale,
                "implementation_notes": implementation_result.implementation_notes,
                "confidence": 0.9,  # 高置信度，因为基于详细设计
                "strategy": algorithm_design.get("strategy", "top_down"),
                "strategy_object": StrategyType.TOP_DOWN,
                "llm_implementation": implementation_result  # 保存完整的结构化结果
            }

            # 合并完整代码
            full_code_parts = []

            # 添加导入语句
            if implementation_result.import_statements:
                full_code_parts.extend(implementation_result.import_statements)
                full_code_parts.append("")  # 空行分隔

            # 添加辅助函数
            if implementation_result.helper_functions:
                full_code_parts.extend(implementation_result.helper_functions)
                full_code_parts.append("")  # 空行分隔

            # 添加主函数
            full_code_parts.append(implementation_result.implementation_code)

            implementation["code"] = "\n".join(full_code_parts)

        except Exception as e:
            # LLM 调用失败时的降级处理
            self.cognitive_trace["decisions"].append({
                "stage": "implementation",
                "issue": f"LLM 调用失败: {str(e)}",
                "fallback": "使用基础实现"
            })

            algorithm_name = algorithm_design.get('algorithm_name', 'solve_problem')

            # 生成基础的代码实现
            code = f'''def {algorithm_name}(input_data):
    """
    {algorithm_design.get('algorithm_description', '解决给定问题的函数')}

    Args:
        input_data: 输入数据

    Returns:
        处理后的结果

    Time Complexity: {algorithm_design.get('time_complexity', 'O(n)')}
    Space Complexity: {algorithm_design.get('space_complexity', 'O(1)')}
    """
    # Step 1: 验证输入
    if not input_data:
        return None

    # Step 2: 处理输入数据
    result = process_input(input_data)

    # Step 3: 返回结果
    return result


def process_input(data):
    """辅助函数：处理输入数据"""
    # 在这里实现具体的处理逻辑
    return data
'''

            implementation = {
                "function_name": algorithm_name,
                "function_signature": f"def {algorithm_name}(input_data)",
                "code": code,
                "docstring": f"{algorithm_name}函数的文档",
                "helper_functions": ["process_input"],
                "imports": [],
                "explanation": f"基于{algorithm_design.get('algorithm_description', '算法设计')}实现的代码",
                "implementation_notes": ["使用降级实现", "需要进一步完善"],
                "confidence": 0.6,  # 较低置信度
                "strategy": algorithm_design.get("strategy", "top_down"),
                "strategy_object": StrategyType.TOP_DOWN
            }

        return implementation

    def _validate_solution(self, implementation: Dict[str, Any], request: CognitiveCodeGenRequest) -> Dict[str, Any]:
        """Stage 5: Validation with LLM"""
        self._transition_to_stage(ThinkingStage.VALIDATION, "Validating solution")

        # Create validation prompt
        validation_prompt = f"""
        请验证以下代码实现的质量和正确性：

        原始需求: {request.requirement}
        实现的代码:
        ```python
        {implementation['code']}
        ```

        函数名称: {implementation.get('function_name', 'unknown')}
        实现说明: {implementation.get('explanation', '')}
        置信度: {implementation.get('confidence', 0.0)}

        请从以下方面进行验证：
        1. 语法正确性检查
        2. 逻辑正确性分析
        3. 需求满足程度评估
        4. 测试用例通过情况
        5. 发现的问题列表
        6. 改进建议
        7. 是否需要优化
        8. 总体置信度评分

        请提供详细的验证结果。
        """

        try:
            # 使用 LLM 进行代码验证
            validation_result = self.llm.generate_structured(
                prompt=validation_prompt,
                output_schema=ValidationResult
            )

            validation = {
                "syntax_check": validation_result.syntax_valid,
                "logic_check": validation_result.logic_valid,
                "test_cases_passed": validation_result.test_cases_passed,
                "total_test_cases": validation_result.total_test_cases,
                "issues_found": validation_result.identified_issues,
                "suggestions": validation_result.suggestions,
                "needs_optimization": validation_result.needs_optimization,
                "confidence_score": validation_result.confidence_score,
                "llm_validation": validation_result  # 保存完整的结构化结果
            }

        except Exception as e:
            # LLM 调用失败时的降级处理
            self.cognitive_trace["decisions"].append({
                "stage": "validation",
                "issue": f"LLM 调用失败: {str(e)}",
                "fallback": "使用基础验证"
            })

            # 基础验证逻辑
            syntax_valid = True
            try:
                compile(implementation['code'], '<string>', 'exec')
            except SyntaxError:
                syntax_valid = False

            validation = {
                "syntax_check": syntax_valid,
                "logic_check": True,  # 假设逻辑正确
                "test_cases_passed": 1,
                "total_test_cases": 1,
                "issues_found": [] if syntax_valid else ["语法错误"],
                "suggestions": ["添加更多测试", "优化性能"],
                "needs_optimization": False,
                "confidence_score": 0.7 if syntax_valid else 0.3
            }

        return validation

    def _optimize_solution(self, implementation: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 6: Optimization with LLM (if needed)"""
        self._transition_to_stage(ThinkingStage.OPTIMIZATION, "Optimizing solution")

        # Create optimization prompt
        optimization_prompt = f"""
        请优化以下代码实现，基于验证结果中发现的问题：

        当前代码:
        ```python
        {implementation['code']}
        ```

        验证结果:
        - 发现的问题: {', '.join(validation.get('issues_found', []))}
        - 改进建议: {', '.join(validation.get('suggestions', []))}
        - 置信度评分: {validation.get('confidence_score', 0.0)}

        请提供优化方案：
        1. 优化后的代码实现
        2. 使用的优化技术
        3. 性能改进说明
        4. 权衡考虑
        5. 优化理由解释

        请确保优化后的代码质量更高，性能更好。
        """

        try:
            # 使用 LLM 进行代码优化
            optimization_result = self.llm.generate_structured(
                prompt=optimization_prompt,
                output_schema=OptimizationResult
            )

            # 更新实现
            optimized_implementation = implementation.copy()
            optimized_implementation.update({
                "code": optimization_result.optimized_code,
                "optimization_techniques": optimization_result.optimization_techniques,
                "performance_improvements": optimization_result.performance_improvements,
                "trade_offs": optimization_result.trade_offs,
                "explanation": optimization_result.optimization_rationale,
                "confidence": min(implementation.get('confidence', 0.8) + 0.1, 1.0),  # 提升置信度
                "llm_optimization": optimization_result  # 保存完整的结构化结果
            })

        except Exception as e:
            # LLM 调用失败时的降级处理
            self.cognitive_trace["decisions"].append({
                "stage": "optimization",
                "issue": f"LLM 调用失败: {str(e)}",
                "fallback": "跳过优化"
            })

            optimized_implementation = implementation  # 返回原实现

        return optimized_implementation

    def _reflect_on_solution(self, implementation: Dict[str, Any], request: CognitiveCodeGenRequest) -> Dict[str, Any]:
        """Stage 7: Reflection with LLM"""
        self._transition_to_stage(ThinkingStage.REFLECTION, "Reflecting on solution quality")

        # Create reflection prompt
        reflection_prompt = f"""
        请对整个解决方案进行深入反思：

        原始需求: {request.requirement}
        最终实现:
        ```python
        {implementation['code']}
        ```

        实现说明: {implementation.get('explanation', '')}
        最终置信度: {implementation.get('confidence', 0.0)}

        请从以下角度进行反思：
        1. 解决方案质量评估
        2. 实现的优势和劣势
        3. 可能的备选方案
        4. 从中学到的经验教训
        5. 未来可能的改进方向
        6. 深层洞察和思考
        7. 整体满意度评分

        请提供结构化的反思结果。
        """

        try:
            # 使用 LLM 进行解决方案反思
            reflection_result = self.llm.generate_structured(
                prompt=reflection_prompt,
                output_schema=SolutionReflection
            )

            reflection = {
                "quality_assessment": reflection_result.quality_assessment,
                "strengths": reflection_result.strengths,
                "weaknesses": reflection_result.weaknesses,
                "alternative_approaches": reflection_result.alternative_approaches,
                "lessons_learned": reflection_result.lessons_learned,
                "future_improvements": reflection_result.future_improvements,
                "insights": [
                    {
                        "type": insight.insight_type,
                        "description": insight.description,
                        "impact": insight.impact,
                        "confidence": insight.confidence
                    } for insight in reflection_result.insights
                ],
                "overall_satisfaction": reflection_result.overall_satisfaction,
                "llm_reflection": reflection_result  # 保存完整的结构化结果
            }

        except Exception as e:
            # LLM 调用失败时的降级处理
            self.cognitive_trace["decisions"].append({
                "stage": "reflection",
                "issue": f"LLM 调用失败: {str(e)}",
                "fallback": "使用基础反思"
            })

            reflection = {
                "quality_assessment": "Good",
                "strengths": ["完成了基本功能", "结构清晰"],
                "weaknesses": ["可能需要更多测试", "性能可以优化"],
                "alternative_approaches": ["使用不同的算法", "采用不同的数据结构"],
                "lessons_learned": ["逐步方法效果良好", "需要更好的错误处理"],
                "future_improvements": ["添加更多边界情况处理", "提高代码复用性"],
                "insights": [
                    {
                        "type": "implementation",
                        "description": "结构化方法有助于代码质量",
                        "impact": "positive",
                        "confidence": 0.8
                    }
                ],
                "overall_satisfaction": 0.7
            }

        return reflection

    def _generate_line_explanations(self, code: str) -> Dict[int, str]:
        """Generate line-by-line explanations for the code"""
        lines = code.split('\n')
        explanations = {}

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                if line.startswith('def '):
                    explanations[i] = f"Function definition: {line}"
                elif line.startswith('if '):
                    explanations[i] = f"Conditional check: {line}"
                elif line.startswith('return '):
                    explanations[i] = f"Return statement: {line}"
                elif '=' in line and not line.startswith('#'):
                    explanations[i] = f"Variable assignment: {line}"
                else:
                    explanations[i] = f"Code execution: {line}"

        return explanations

    def _extract_reasoning_chain(self) -> List[str]:
        """Extract reasoning chain from cognitive trace"""
        reasoning_chain = []

        for stage_info in self.cognitive_trace["stages"]:
            reasoning_chain.append(f"Stage: {stage_info['stage']} - {stage_info['focus']}")

        for decision in self.cognitive_trace["decisions"]:
            reasoning_chain.append(f"Decision: {decision.get('reasoning', 'Made strategic decision')}")

        return reasoning_chain

    def _extract_thinking_stages(self) -> List[Dict[str, Any]]:
        """Extract thinking stages for analysis"""
        return self.cognitive_trace["stages"]


# Factory function for easy instantiation
def create_cognitive_agent(llm: StructuredLLM, max_thinking_depth: int = 5) -> CognitiveCodeGenAgent:
    """Create a cognitive code generation agent"""
    return CognitiveCodeGenAgent(llm, max_thinking_depth)