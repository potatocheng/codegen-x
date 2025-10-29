from typing import Dict, List, Any, Optional
import json
from logger import logger

from llm.structured_llm import StructuredLLM
from tools.spec_tool import SpecTool
from tools.implement_tool import ImplementTool
from tools.validate_tool import ValidateTool
from tools.refine_tool import RefineTool
from tools.base import Tool


class CodeGenAgent:
    """代码生成Agent

    使用工具和LLM协作完成代码生成任务。
    Agent可以自主规划执行步骤，调用合适的工具。
    """

    def __init__(
        self,
        llm: StructuredLLM,
        max_iterations: int = 10,
        max_refine_attempts: int = 3
    ):
        """初始化Agent

        Args:
            llm: 结构化LLM实例
            max_iterations: 最大迭代次数（防止无限循环）
            max_refine_attempts: 最大代码优化尝试次数
        """
        self.llm = llm
        self.max_iterations = max_iterations
        self.max_refine_attempts = max_refine_attempts
        self.tools = self._register_tools()
        self.memory: List[Dict[str, Any]] = []

        logger.info(f"CodeGenAgent initialized with {len(self.tools)} tools")

    def _register_tools(self) -> Dict[str, Tool]:
        """注册可用的工具"""
        return {
            "generate_spec": SpecTool(self.llm),
            "implement_function": ImplementTool(self.llm),
            "validate_code": ValidateTool(),
            "refine_code": RefineTool(self.llm),
        }

    def generate(self, request: str) -> Dict[str, Any]:
        """主入口：生成代码

        Args:
            request: 用户需求

        Returns:
            包含最终代码和过程信息的字典
        """
        logger.info(f"开始生成代码，需求: {request}")

        # 重置记忆
        self.memory = []

        try:
            # 使用简化的工作流（不使用工具调用API，直接控制流程）
            result = self._execute_workflow(request)
            return result
        except Exception as e:
            logger.error(f"代码生成失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "code": None
            }

    def _execute_workflow(self, request: str) -> Dict[str, Any]:
        """执行标准工作流

        工作流：
        1. 生成规范
        2. 实现代码
        3. 验证代码
        4. 如果验证失败，优化代码并重新验证（最多N次）
        """
        # 步骤1: 生成规范
        logger.info("步骤1: 生成函数规范")
        spec_tool = self.tools["generate_spec"]
        spec_result = spec_tool.execute(spec_tool.input_schema(requirement=request))

        if not spec_result.success:
            raise RuntimeError(f"生成规范失败: {spec_result.message}")

        spec = spec_result.data
        logger.info(f"规范生成成功: {spec.name}")

        # 步骤2: 实现代码
        logger.info("步骤2: 实现函数")
        impl_tool = self.tools["implement_function"]
        impl_result = impl_tool.execute(
            impl_tool.input_schema(spec=spec, style="concise")
        )

        if not impl_result.success:
            raise RuntimeError(f"实现代码失败: {impl_result.message}")

        implementation = impl_result.data
        logger.info("代码实现成功")

        # 步骤3-4: 验证和优化循环
        logger.info("步骤3: 验证代码")
        validate_tool = self.tools["validate_code"]
        refine_tool = self.tools["refine_code"]

        current_code = implementation.code
        current_explanation = implementation.explanation

        for attempt in range(self.max_refine_attempts):
            # 验证
            validate_result = validate_tool.execute(
                validate_tool.input_schema(code=current_code, spec=spec)
            )

            validation = validate_result.data

            if validation.is_valid:
                logger.info(f"代码验证通过！({validation.passed_count}/{validation.total_tests} 测试)")
                return {
                    "success": True,
                    "spec": spec.model_dump(),
                    "code": current_code,
                    "explanation": current_explanation,
                    "validation": validation.model_dump(),
                    "refine_attempts": attempt
                }

            # 验证失败，尝试优化
            logger.warning(
                f"代码验证失败 ({validation.passed_count}/{validation.total_tests} 测试通过)，"
                f"尝试优化 (第{attempt+1}次)"
            )

            if attempt < self.max_refine_attempts - 1:
                refine_result = refine_tool.execute(
                    refine_tool.input_schema(
                        code=current_code,
                        spec=spec,
                        validation_result=validation
                    )
                )

                if not refine_result.success:
                    logger.error(f"优化代码失败: {refine_result.message}")
                    break

                refined = refine_result.data
                current_code = refined.code
                current_explanation = refined.explanation
                logger.info("代码已优化，重新验证")

        # 达到最大尝试次数仍未通过
        logger.warning(f"达到最大优化次数({self.max_refine_attempts})，返回当前最佳代码")
        return {
            "success": False,
            "spec": spec.model_dump(),
            "code": current_code,
            "explanation": current_explanation,
            "validation": validation.model_dump(),
            "refine_attempts": self.max_refine_attempts,
            "message": "代码未通过所有测试，但已达到最大优化次数"
        }

    def generate_with_tools_api(self, request: str) -> Dict[str, Any]:
        """使用OpenAI工具调用API的高级版本（可选）

        这个方法让LLM自主决定调用哪些工具，更灵活但也更复杂。
        当前使用的是简化版的固定工作流。
        """
        # TODO: 实现基于工具调用API的版本
        raise NotImplementedError("工具调用API版本待实现")

    def _format_tool_descriptions(self) -> str:
        """格式化工具描述供LLM参考"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool.description}")
        return "\n".join(descriptions)

    def _get_tool_schemas(self) -> List[Dict]:
        """获取所有工具的OpenAI schema"""
        return [tool.to_openai_tool_schema() for tool in self.tools.values()]
