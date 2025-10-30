"""
认知驱动的代码生成代理

集成认知模块到主代码生成流程，让认知模型指导整个生成过程。
"""

from typing import Dict, List, Any, Optional
import json
from logger import logger

from llm.structured_llm import StructuredLLM
from tools.spec_tool import SpecTool
from tools.implement_tool import ImplementTool
from tools.validate_tool import ValidateTool
from tools.refine_tool import RefineTool
from tools.base import Tool

from cognitive.cognitive_agent import CognitiveCodeGenAgent, CognitiveCodeGenRequest
from cognitive.cognitive_model import CognitiveModel, CognitiveState, ThinkingStage
from cognitive.programming_strategy import ProgrammingStrategy, StrategyType
from cognitive.cognitive_decision_tracker import (
    CognitiveDecisionTracker, DecisionType, CognitiveDecisionManager
)
from cognitive.cognitive_load_aware_generator import CognitiveLoadAwareGenerator, CognitiveStrategy


class CognitiveDrivenCodeGenAgent:
    """认知驱动的代码生成代理

    整合认知科学模型到代码生成流程中，使生成过程更符合人类程序员的思维模式。
    """

    def __init__(
        self,
        llm: StructuredLLM,
        max_iterations: int = 10,
        max_refine_attempts: int = 3,
        enable_cognitive_guidance: bool = True
    ):
        """初始化认知驱动代理

        Args:
            llm: 结构化LLM实例
            max_iterations: 最大迭代次数
            max_refine_attempts: 最大代码优化尝试次数
            enable_cognitive_guidance: 是否启用认知指导
        """
        self.llm = llm
        self.max_iterations = max_iterations
        self.max_refine_attempts = max_refine_attempts
        self.enable_cognitive_guidance = enable_cognitive_guidance

        # 初始化工具
        self.tools = self._register_tools()

        # 初始化认知组件
        self.cognitive_agent = CognitiveCodeGenAgent(llm, max_thinking_depth=7)
        self.programming_strategy = ProgrammingStrategy()

        # 认知负荷感知生成器
        self.load_aware_generator = CognitiveLoadAwareGenerator(
            CognitiveStrategy(target_load=0.7, adaptation_threshold=0.8)
        )

        # 认知决策追踪
        self.decision_manager = CognitiveDecisionManager()
        self.current_tracker: Optional[CognitiveDecisionTracker] = None

        logger.info(f"CognitiveDrivenCodeGenAgent initialized with cognitive guidance: {enable_cognitive_guidance}")

    def _register_tools(self) -> Dict[str, Tool]:
        """注册可用的工具"""
        return {
            "generate_spec": SpecTool(self.llm),
            "implement_function": ImplementTool(self.llm),
            "validate_code": ValidateTool(),
            "refine_code": RefineTool(self.llm),
        }

    def generate(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """认知驱动的代码生成主入口

        Args:
            request: 用户需求
            context: 额外上下文信息

        Returns:
            包含代码、认知解释和过程跟踪的完整结果
        """
        logger.info(f"开始认知驱动代码生成，需求: {request}")

        # 创建认知追踪会话
        import uuid
        session_id = f"cognitive_{uuid.uuid4().hex[:8]}"
        self.current_tracker = self.decision_manager.start_session(session_id, request)

        try:
            if self.enable_cognitive_guidance:
                # 使用认知指导的工作流
                result = self._execute_cognitive_guided_workflow(request, context)
            else:
                # 回退到标准工作流
                result = self._execute_standard_workflow(request)

            return result

        except Exception as e:
            logger.error(f"认知驱动代码生成失败: {str(e)}")

            # 记录失败决策
            if self.current_tracker:
                self.current_tracker.record_decision(
                    stage="error_handling",
                    decision_type=DecisionType.ERROR_HANDLING,
                    decision="生成过程失败",
                    reasoning=f"发生异常: {str(e)}",
                    confidence=0.1,
                    expected_outcome="错误恢复"
                )

                # 结束会话
                self.decision_manager.end_session(
                    self.current_tracker.trace.session_id,
                    {"success": False, "error": str(e)}
                )

            return {
                "success": False,
                "error": str(e),
                "code": None,
                "cognitive_trace": self.current_tracker.get_decision_chain() if self.current_tracker else []
            }

    def _execute_cognitive_guided_workflow(self, request: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """执行认知指导的工作流

        结合认知模型的指导，动态调整生成策略和工具使用。
        """
        logger.info("执行认知指导的代码生成工作流")

        # 第一阶段：认知理解和策略选择
        cognitive_analysis = self._cognitive_problem_analysis(request, context)

        # 第二阶段：认知驱动的规范生成
        spec_result = self._cognitive_spec_generation(request, cognitive_analysis)
        if not spec_result["success"]:
            return spec_result

        spec = spec_result["spec"]

        # 第三阶段：认知驱动的实现
        impl_result = self._cognitive_implementation(spec, cognitive_analysis)
        if not impl_result["success"]:
            return impl_result

        current_code = impl_result["code"]
        current_explanation = impl_result["explanation"]

        # 第四阶段：认知驱动的验证和优化
        validation_result = self._cognitive_validation_and_refinement(
            current_code, current_explanation, spec, cognitive_analysis
        )

        # 整合最终结果
        final_result = {
            "success": validation_result["success"],
            "spec": spec.model_dump() if hasattr(spec, 'model_dump') else spec,
            "code": validation_result["code"],
            "explanation": validation_result["explanation"],
            "validation": validation_result.get("validation"),
            "cognitive_analysis": cognitive_analysis,
            "cognitive_decisions": self.current_tracker.get_decision_chain(),
            "cognitive_summary": self.current_tracker.get_decision_summary(),
            "strategy_adaptations": self.current_tracker.trace.strategy_adaptations,
            "refine_attempts": validation_result.get("refine_attempts", 0)
        }

        # 结束认知追踪会话
        self.decision_manager.end_session(
            self.current_tracker.trace.session_id,
            final_result
        )

        return final_result

    def _cognitive_problem_analysis(self, request: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """认知问题分析阶段

        使用认知代理进行深度问题理解和策略选择。
        """
        logger.info("阶段1: 认知问题分析")

        # 创建认知请求
        cognitive_request = CognitiveCodeGenRequest(
            requirement=request,
            context=json.dumps(context) if context else None,
            constraints=[],
            difficulty="medium"
        )

        # 执行认知分析（只到问题理解和策略规划阶段）
        cognitive_result = self.cognitive_agent.generate_code(cognitive_request)

        # 提取认知洞察
        analysis = {
            "problem_understanding": self._extract_problem_understanding(cognitive_result),
            "strategy_selection": cognitive_result.strategy_used,
            "cognitive_load_estimate": cognitive_result.cognitive_load,
            "thinking_stages": cognitive_result.thinking_stages,
            "confidence_level": cognitive_result.confidence
        }

        # 记录认知决策
        decision_id = self.current_tracker.record_decision(
            stage="problem_analysis",
            decision_type=DecisionType.STRATEGY_SELECTION,
            decision=f"选择策略: {cognitive_result.strategy_used.value}",
            reasoning="基于问题特征和认知模型分析",
            confidence=cognitive_result.confidence,
            expected_outcome="提高代码生成质量和可解释性"
        )

        logger.info(f"认知分析完成，选择策略: {cognitive_result.strategy_used.value}")
        return analysis

    def _cognitive_spec_generation(self, request: str, cognitive_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """认知驱动的规范生成

        根据认知分析调整规范生成策略。
        """
        logger.info("阶段2: 认知驱动规范生成")

        # 根据认知负荷调整规范详细程度
        cognitive_load = cognitive_analysis.get("cognitive_load_estimate")
        detail_level = self._determine_spec_detail_level(cognitive_load)

        spec_tool = self.tools["generate_spec"]

        # 使用认知指导的提示
        enhanced_request = self._enhance_request_with_cognitive_insights(request, cognitive_analysis)

        try:
            spec_result = spec_tool.execute(
                spec_tool.input_schema(requirement=enhanced_request)
            )

            if not spec_result.success:
                return {
                    "success": False,
                    "error": f"规范生成失败: {spec_result.message}"
                }

            # 记录认知决策
            self.current_tracker.record_decision(
                stage="spec_generation",
                decision_type=DecisionType.APPROACH_CHANGE,
                decision=f"生成详细级别: {detail_level}",
                reasoning=f"基于认知负荷评估: {cognitive_load}",
                confidence=0.8,
                expected_outcome="生成适当详细程度的规范"
            )

            return {
                "success": True,
                "spec": spec_result.data
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"规范生成异常: {str(e)}"
            }

    def _cognitive_implementation(self, spec, cognitive_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """认知驱动的代码实现

        根据认知策略调整实现风格和复杂度。
        """
        logger.info("阶段3: 认知驱动代码实现")

        # 根据认知策略选择实现风格
        strategy = cognitive_analysis.get("strategy_selection", StrategyType.TOP_DOWN)
        implementation_style = self._map_strategy_to_style(strategy)

        impl_tool = self.tools["implement_function"]

        try:
            impl_result = impl_tool.execute(
                impl_tool.input_schema(spec=spec, style=implementation_style)
            )

            if not impl_result.success:
                return {
                    "success": False,
                    "error": f"代码实现失败: {impl_result.message}"
                }

            # 认知负荷感知优化
            initial_code = impl_result.data.code
            adaptations, updated_config = self.load_aware_generator.assess_and_adapt(
                initial_code,
                cognitive_context={
                    "strategy": strategy,
                    "problem_complexity": cognitive_analysis.get("complexity_indicators", {})
                }
            )

            # 应用认知负荷适应策略
            if adaptations:
                optimized_code = self._apply_cognitive_adaptations(initial_code, adaptations, updated_config)
                self.current_tracker.record_decision(
                    stage="cognitive_adaptation",
                    decision_type=DecisionType.OPTIMIZATION_CHOICE,
                    decision=f"应用 {len(adaptations)} 个认知适应策略",
                    reasoning=f"认知负荷: {self.load_aware_generator.current_load.total_load:.2f}",
                    confidence=0.8,
                    alternatives=["不进行适应", "部分适应"],
                    expected_outcome="降低认知负荷，提高代码可理解性"
                )
            else:
                optimized_code = initial_code

            # 记录认知决策
            self.current_tracker.record_decision(
                stage="implementation",
                decision_type=DecisionType.APPROACH_CHANGE,
                decision=f"实现风格: {implementation_style}",
                reasoning=f"基于认知策略: {strategy.value}",
                confidence=0.85,
                expected_outcome="生成符合认知策略的代码"
            )

            return {
                "success": True,
                "code": optimized_code,
                "explanation": impl_result.data.explanation,
                "cognitive_adaptations": [adaptation.model_dump() for adaptation in adaptations]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"代码实现异常: {str(e)}"
            }

    def _cognitive_validation_and_refinement(self, code: str, explanation: str, spec,
                                           cognitive_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """认知驱动的验证和优化

        使用认知模型指导验证策略和优化方向。
        """
        logger.info("阶段4: 认知驱动验证和优化")

        validate_tool = self.tools["validate_code"]
        refine_tool = self.tools["refine_code"]

        current_code = code
        current_explanation = explanation

        for attempt in range(self.max_refine_attempts):
            # 验证
            validate_result = validate_tool.execute(
                validate_tool.input_schema(code=current_code, spec=spec)
            )

            validation = validate_result.data

            if validation.is_valid:
                logger.info(f"代码验证通过！({validation.passed_count}/{validation.total_tests} 测试)")

                # 记录成功的认知决策
                self.current_tracker.record_decision(
                    stage="validation_success",
                    decision_type=DecisionType.VALIDATION_STRATEGY,
                    decision="验证通过，生成完成",
                    reasoning=f"所有测试通过 ({validation.passed_count}/{validation.total_tests})",
                    confidence=0.95,
                    expected_outcome="交付高质量代码"
                )

                return {
                    "success": True,
                    "code": current_code,
                    "explanation": current_explanation,
                    "validation": validation.model_dump(),
                    "refine_attempts": attempt
                }

            # 验证失败，使用认知指导优化
            logger.warning(f"验证失败，使用认知指导优化 (第{attempt+1}次)")

            if attempt < self.max_refine_attempts - 1:
                # 认知驱动的优化策略选择
                optimization_strategy = self._select_optimization_strategy(validation, cognitive_analysis)

                refine_result = refine_tool.execute(
                    refine_tool.input_schema(
                        code=current_code,
                        spec=spec,
                        validation_result=validation
                    )
                )

                if not refine_result.success:
                    logger.error(f"优化失败: {refine_result.message}")
                    break

                refined = refine_result.data
                current_code = refined.code
                current_explanation = refined.explanation

                # 记录认知决策
                self.current_tracker.record_decision(
                    stage="refinement",
                    decision_type=DecisionType.OPTIMIZATION_CHOICE,
                    decision=f"优化策略: {optimization_strategy}",
                    reasoning=f"基于验证失败分析: {validation.passed_count}/{validation.total_tests} 通过",
                    confidence=0.7,
                    alternatives=[
                        "fundamental_redesign", "algorithmic_improvement", "incremental_fixes"
                    ],
                    expected_outcome="提高代码质量和测试通过率"
                )

        # 达到最大尝试次数
        return {
            "success": False,
            "code": current_code,
            "explanation": current_explanation,
            "validation": validation.model_dump(),
            "refine_attempts": self.max_refine_attempts,
            "message": "达到最大优化次数，但代码仍未完全通过验证"
        }

    def _execute_standard_workflow(self, request: str) -> Dict[str, Any]:
        """标准工作流（无认知指导）"""
        logger.info("执行标准代码生成工作流")

        # 简化的标准流程
        spec_tool = self.tools["generate_spec"]
        spec_result = spec_tool.execute(spec_tool.input_schema(requirement=request))

        if not spec_result.success:
            return {"success": False, "error": f"规范生成失败: {spec_result.message}"}

        impl_tool = self.tools["implement_function"]
        impl_result = impl_tool.execute(
            impl_tool.input_schema(spec=spec_result.data, style="concise")
        )

        if not impl_result.success:
            return {"success": False, "error": f"实现失败: {impl_result.message}"}

        return {
            "success": True,
            "code": impl_result.data.code,
            "explanation": impl_result.data.explanation,
            "spec": spec_result.data.model_dump()
        }

    # 辅助方法

    def _extract_problem_understanding(self, cognitive_result) -> Dict[str, Any]:
        """从认知结果中提取问题理解"""
        return {
            "main_concepts": cognitive_result.cognitive_trace.get("reasoning", [])[:3],
            "complexity_indicators": {
                "cognitive_load": cognitive_result.cognitive_load,
                "confidence": cognitive_result.confidence
            },
            "key_insights": cognitive_result.reasoning_chain[:5]
        }

    def _determine_spec_detail_level(self, cognitive_load) -> str:
        """根据认知负荷确定规范详细级别"""
        if hasattr(cognitive_load, 'intrinsic_load'):
            load_value = cognitive_load.intrinsic_load
        else:
            load_value = 0.5  # 默认值

        if load_value > 0.7:
            return "very_detailed"
        elif load_value > 0.4:
            return "detailed"
        else:
            return "concise"

    def _enhance_request_with_cognitive_insights(self, request: str, cognitive_analysis: Dict[str, Any]) -> str:
        """使用认知洞察增强请求"""
        strategy = cognitive_analysis.get("strategy_selection", StrategyType.TOP_DOWN)
        confidence = cognitive_analysis.get("confidence_level", 0.5)

        enhancement = f"\n\n[认知指导] 采用{strategy.value}策略，置信度: {confidence:.2f}"
        return request + enhancement

    def _map_strategy_to_style(self, strategy: StrategyType) -> str:
        """将认知策略映射到实现风格"""
        strategy_mapping = {
            StrategyType.TOP_DOWN: "structured",
            StrategyType.BOTTOM_UP: "incremental",
            StrategyType.DIVIDE_CONQUER: "modular",
            StrategyType.INCREMENTAL: "iterative",
            StrategyType.PROTOTYPE: "exploratory",
            StrategyType.PATTERN_BASED: "pattern_oriented",
            StrategyType.TEST_DRIVEN: "test_first",
            StrategyType.REFACTOR: "refactor_focused"
        }
        return strategy_mapping.get(strategy, "concise")

    def _select_optimization_strategy(self, validation, cognitive_analysis: Dict[str, Any]) -> str:
        """选择优化策略"""
        failed_tests = validation.total_tests - validation.passed_count
        failure_rate = failed_tests / validation.total_tests if validation.total_tests > 0 else 0

        if failure_rate > 0.5:
            return "fundamental_redesign"
        elif failure_rate > 0.3:
            return "algorithmic_improvement"
        else:
            return "incremental_fixes"

    def _apply_cognitive_adaptations(self, code: str, adaptations: List, updated_config: Dict[str, Any]) -> str:
        """应用认知适应策略到代码"""

        adapted_code = code

        for adaptation in adaptations:
            strategy = adaptation.strategy
            details = adaptation.implementation_details

            # 根据不同的适应策略修改代码
            if strategy.value == "reduce_complexity":
                adapted_code = self._reduce_code_complexity(adapted_code, details)
            elif strategy.value == "enhance_clarity":
                adapted_code = self._enhance_code_clarity(adapted_code, details)
            elif strategy.value == "increase_scaffolding":
                adapted_code = self._add_scaffolding(adapted_code, details)
            elif strategy.value == "optimize_chunking":
                adapted_code = self._optimize_code_chunking(adapted_code, details)

        return adapted_code

    def _reduce_code_complexity(self, code: str, details: Dict[str, Any]) -> str:
        """降低代码复杂度"""
        lines = code.split('\n')

        # 简化版本：添加解释性注释来降低认知负荷
        if details.get("add_explanatory_comments", True):
            enhanced_lines = []
            for line in lines:
                enhanced_lines.append(line)
                if 'if ' in line and line.strip().startswith('if'):
                    enhanced_lines.append(f"    # 检查条件: {line.strip()}")
                elif 'for ' in line and line.strip().startswith('for'):
                    enhanced_lines.append(f"    # 遍历操作: {line.strip()}")
            return '\n'.join(enhanced_lines)

        return code

    def _enhance_code_clarity(self, code: str, details: Dict[str, Any]) -> str:
        """增强代码清晰度"""

        # 简化版本：添加类型提示注释
        if details.get("add_type_hints", True):
            lines = code.split('\n')
            enhanced_lines = []

            for line in lines:
                if 'def ' in line and '(' in line and '->' not in line:
                    # 为函数添加返回类型注释
                    if ':' in line:
                        parts = line.split(':')
                        enhanced_line = parts[0] + ' -> Any:'
                        if len(parts) > 1:
                            enhanced_line += parts[1]
                        enhanced_lines.append(enhanced_line)
                    else:
                        enhanced_lines.append(line)
                else:
                    enhanced_lines.append(line)

            return '\n'.join(enhanced_lines)

        return code

    def _add_scaffolding(self, code: str, details: Dict[str, Any]) -> str:
        """添加脚手架支持"""

        if details.get("add_docstrings", True):
            lines = code.split('\n')
            enhanced_lines = []

            for i, line in enumerate(lines):
                if 'def ' in line and line.strip().startswith('def'):
                    enhanced_lines.append(line)
                    # 添加简单的文档字符串
                    function_name = line.split('(')[0].split('def ')[1]
                    enhanced_lines.append(f'    """')
                    enhanced_lines.append(f'    {function_name} 函数的实现')
                    enhanced_lines.append(f'    """')
                else:
                    enhanced_lines.append(line)

            return '\n'.join(enhanced_lines)

        return code

    def _optimize_code_chunking(self, code: str, details: Dict[str, Any]) -> str:
        """优化代码分块"""

        if details.get("add_section_comments", True):
            lines = code.split('\n')
            enhanced_lines = []

            current_section = ""
            for line in lines:
                if line.strip().startswith('def '):
                    enhanced_lines.append(f"# === 函数定义部分 ===")
                    enhanced_lines.append(line)
                elif '=' in line and not line.strip().startswith('#'):
                    if current_section != "variables":
                        enhanced_lines.append(f"# --- 变量处理 ---")
                        current_section = "variables"
                    enhanced_lines.append(line)
                elif line.strip().startswith('return'):
                    enhanced_lines.append(f"# --- 返回结果 ---")
                    enhanced_lines.append(line)
                else:
                    enhanced_lines.append(line)

            return '\n'.join(enhanced_lines)

        return code