"""
行代码有效性验证器

验证生成代码中的每一行都是有用的、必要的，不存在冗余或无关的代码。
基于代码依赖分析、逻辑流追踪和目标相关性评估。
"""

from typing import Dict, List, Tuple, Optional, Any, Set
from pydantic import BaseModel, Field
from enum import Enum
import re


class LineUtility(Enum):
    """代码行的有用性等级"""
    ESSENTIAL = "essential"           # 必需（逻辑无法进行）
    IMPORTANT = "important"           # 重要（提高代码质量、可读性）
    OPTIONAL = "optional"             # 可选（有益但不必需）
    REDUNDANT = "redundant"           # 冗余（可以删除）
    UNUSED = "unused"                 # 未使用（从未被引用）


class LineAnalysis(BaseModel):
    """单行代码的有效性分析"""
    line_number: int = Field(description="行号")
    code_line: str = Field(description="代码内容")
    utility: LineUtility = Field(description="有用性等级")
    reason: str = Field(description="判断原因")
    dependencies: Set[int] = Field(description="依赖的行号集合", default_factory=set)
    dependents: Set[int] = Field(description="被依赖的行号集合", default_factory=set)
    contributes_to_goal: bool = Field(description="是否对最终目标有贡献")
    suggestion: Optional[str] = Field(description="优化建议", default=None)


class CodeEffectivenessReport(BaseModel):
    """代码有效性报告"""
    total_lines: int = Field(description="总行数")
    essential_lines: int = Field(description="必需行数")
    important_lines: int = Field(description="重要行数")
    optional_lines: int = Field(description="可选行数")
    redundant_lines: int = Field(description="冗余行数")
    unused_lines: int = Field(description="未使用行数")

    effectiveness_score: float = Field(
        description="有效性评分 (0-1, 1为完美)",
        ge=0,
        le=1
    )

    analysis: List[LineAnalysis] = Field(description="各行的详细分析")
    recommendations: List[str] = Field(description="优化建议")
    optimized_code: Optional[str] = Field(description="优化后的代码", default=None)


class LineEffectivenessValidator:
    """
    验证代码行有效性的工具类

    分析每一行代码是否：
    1. 有明确的用途
    2. 对逻辑流有贡献
    3. 不存在冗余
    4. 被正确使用
    """

    def __init__(self):
        """初始化验证器"""
        self.variable_pattern = re.compile(r'\b([a-zA-Z_]\w*)\b')
        self.assignment_pattern = re.compile(r'(\w+)\s*=')
        self.usage_pattern = re.compile(r'(?:return|print|assert|raise|if|elif|while|for).*')

    def analyze_code(self, code: str, function_goal: Optional[str] = None) -> CodeEffectivenessReport:
        """
        分析代码的行有效性

        Args:
            code: 完整代码字符串
            function_goal: 函数的目标描述

        Returns:
            代码有效性报告
        """
        lines = code.split('\n')

        # 第1步：建立变量和行的映射关系
        var_definitions = self._find_variable_definitions(lines)
        var_usages = self._find_variable_usages(lines)

        # 第2步：分析每行的有效性
        analyses = []
        for line_num, line in enumerate(lines, 1):
            analysis = self._analyze_single_line(
                line_num, line, lines, var_definitions, var_usages
            )
            analyses.append(analysis)

        # 第3步：计算依赖关系
        self._compute_dependencies(analyses)

        # 第4步：评估有效性等级
        self._evaluate_utility(analyses, function_goal)

        # 第5步：生成报告
        report = self._generate_report(analyses, lines)

        return report

    def _find_variable_definitions(self, lines: List[str]) -> Dict[str, List[int]]:
        """
        找到所有变量定义及其行号

        Returns:
            {变量名: [行号列表]}
        """
        definitions = {}
        for line_num, line in enumerate(lines, 1):
            # 跳过注释和空行
            if line.strip().startswith('#') or not line.strip():
                continue

            # 找赋值语句
            matches = self.assignment_pattern.findall(line)
            for var_name in matches:
                if var_name not in definitions:
                    definitions[var_name] = []
                definitions[var_name].append(line_num)

        return definitions

    def _find_variable_usages(self, lines: List[str]) -> Dict[str, List[int]]:
        """
        找到所有变量使用及其行号

        Returns:
            {变量名: [行号列表]}
        """
        usages = {}

        for line_num, line in enumerate(lines, 1):
            # 跳过定义行本身的变量声明部分
            line_content = line.split('=', 1)[-1] if '=' in line else line

            # 找所有变量引用
            matches = self.variable_pattern.findall(line_content)
            for var_name in matches:
                # 排除关键字
                if var_name in ('if', 'else', 'elif', 'for', 'while', 'def', 'return',
                               'class', 'import', 'from', 'as', 'None', 'True', 'False'):
                    continue

                if var_name not in usages:
                    usages[var_name] = []
                if line_num not in usages[var_name]:
                    usages[var_name].append(line_num)

        return usages

    def _analyze_single_line(
        self,
        line_num: int,
        line: str,
        all_lines: List[str],
        var_definitions: Dict[str, List[int]],
        var_usages: Dict[str, List[int]]
    ) -> LineAnalysis:
        """分析单行代码的有效性"""

        stripped = line.strip()

        # 空行和注释
        if not stripped:
            return LineAnalysis(
                line_number=line_num,
                code_line=line,
                utility=LineUtility.OPTIONAL,
                reason="空行（可选），用于代码可读性",
                contributes_to_goal=False
            )

        if stripped.startswith('#'):
            return LineAnalysis(
                line_number=line_num,
                code_line=line,
                utility=LineUtility.OPTIONAL,
                reason="注释行（可选），用于代码理解",
                contributes_to_goal=False
            )

        # 分析代码行
        utility = LineUtility.IMPORTANT
        reason = "代码行"
        contributes = True
        suggestion = None

        # 检查是否是必需行
        if 'def ' in stripped or 'class ' in stripped:
            utility = LineUtility.ESSENTIAL
            reason = "函数/类定义，必需"

        elif 'return' in stripped:
            utility = LineUtility.ESSENTIAL
            reason = "返回语句，必需"

        elif '=' in stripped and 'def ' not in stripped:
            # 赋值语句 - 检查是否被使用
            var_name = self.assignment_pattern.search(stripped)
            if var_name:
                var_name = var_name.group(1)
                if var_name in var_usages:
                    future_usages = [n for n in var_usages[var_name] if n > line_num]
                    if future_usages:
                        utility = LineUtility.ESSENTIAL
                        reason = f"定义了被使用的变量 '{var_name}'"
                    else:
                        utility = LineUtility.UNUSED
                        reason = f"定义的变量 '{var_name}' 在此之后未被使用"
                        suggestion = f"删除此行"
                        contributes = False
                else:
                    utility = LineUtility.UNUSED
                    reason = f"定义的变量 '{var_name}' 从未被使用"
                    suggestion = "删除此行"
                    contributes = False

        elif any(kw in stripped for kw in ['if ', 'elif ', 'for ', 'while ', 'try:', 'except ']):
            utility = LineUtility.ESSENTIAL
            reason = "控制流语句，必需"

        elif re.match(r'^\s*(else|finally):', stripped):
            utility = LineUtility.ESSENTIAL
            reason = "控制流语句，必需"

        # 检查是否重复
        if utility != LineUtility.UNUSED:
            duplicate_count = sum(1 for l in all_lines if l.strip() == stripped)
            if duplicate_count > 1:
                utility = LineUtility.REDUNDANT
                reason = "重复的代码行"
                suggestion = "删除重复行"
                contributes = False

        return LineAnalysis(
            line_number=line_num,
            code_line=line,
            utility=utility,
            reason=reason,
            contributes_to_goal=contributes,
            suggestion=suggestion
        )

    def _compute_dependencies(self, analyses: List[LineAnalysis]):
        """计算行之间的依赖关系"""

        for i, analysis in enumerate(analyses):
            line = analysis.code_line.strip()

            # 找这行使用的变量
            used_vars = self.variable_pattern.findall(line)

            for var in used_vars:
                # 找该变量的定义行
                for j in range(i - 1, -1, -1):
                    prev_line = analyses[j].code_line.strip()
                    if re.search(rf'\b{var}\s*=', prev_line):
                        analysis.dependencies.add(analyses[j].line_number)
                        analyses[j].dependents.add(analysis.line_number)
                        break

    def _evaluate_utility(self, analyses: List[LineAnalysis], goal: Optional[str] = None):
        """评估每行的有用性等级（考虑依赖关系）"""

        # 标记所有有依赖的行为重要或必需
        for analysis in analyses:
            if analysis.dependents and analysis.utility not in (LineUtility.ESSENTIAL, LineUtility.UNUSED):
                analysis.utility = LineUtility.IMPORTANT
                analysis.reason += " (被其他行依赖)"

    def _generate_report(self, analyses: List[LineAnalysis], lines: List[str]) -> CodeEffectivenessReport:
        """生成有效性报告"""

        essential_count = sum(1 for a in analyses if a.utility == LineUtility.ESSENTIAL)
        important_count = sum(1 for a in analyses if a.utility == LineUtility.IMPORTANT)
        optional_count = sum(1 for a in analyses if a.utility == LineUtility.OPTIONAL)
        redundant_count = sum(1 for a in analyses if a.utility == LineUtility.REDUNDANT)
        unused_count = sum(1 for a in analyses if a.utility == LineUtility.UNUSED)

        # 计算有效性评分
        total = len(analyses)
        if total > 0:
            # 评分 = (必需 + 重要 + 可选*0.5 - 冗余 - 未使用) / 总数
            effectiveness = (essential_count + important_count + optional_count*0.5) / total
            effectiveness = max(0, min(1, effectiveness))  # 限制在 0-1
        else:
            effectiveness = 1.0

        # 生成优化建议
        recommendations = []

        if redundant_count > 0:
            recommendations.append(f"发现 {redundant_count} 行重复代码，建议删除")

        if unused_count > 0:
            recommendations.append(f"发现 {unused_count} 行未使用的变量，建议删除")

        if optional_count > total * 0.3:
            recommendations.append("可选代码行较多，考虑精简代码")

        # 生成优化后的代码（删除冗余和未使用的行）
        optimized_lines = []
        for i, line in enumerate(lines, 1):
            # 找对应的分析
            analysis = next((a for a in analyses if a.line_number == i), None)
            if analysis and analysis.utility not in (LineUtility.REDUNDANT, LineUtility.UNUSED):
                optimized_lines.append(line)

        optimized_code = '\n'.join(optimized_lines) if optimized_lines else None

        return CodeEffectivenessReport(
            total_lines=total,
            essential_lines=essential_count,
            important_lines=important_count,
            optional_lines=optional_count,
            redundant_lines=redundant_count,
            unused_lines=unused_count,
            effectiveness_score=effectiveness,
            analysis=analyses,
            recommendations=recommendations,
            optimized_code=optimized_code
        )

    def suggest_optimizations(self, report: CodeEffectivenessReport) -> List[str]:
        """
        基于报告生成优化建议

        Returns:
            优化建议列表
        """
        suggestions = []

        # 找需要删除的行
        removable_lines = [
            a for a in report.analysis
            if a.utility in (LineUtility.REDUNDANT, LineUtility.UNUSED)
        ]

        if removable_lines:
            suggestions.append(f"[REMOVE] Can be deleted: {[a.line_number for a in removable_lines]}")
            for line_analysis in removable_lines:
                if line_analysis.suggestion:
                    suggestions.append(f"   Line {line_analysis.line_number}: {line_analysis.suggestion}")

        # 建议合并或简化的地方
        for analysis in report.analysis:
            if analysis.utility == LineUtility.OPTIONAL and not analysis.code_line.strip().startswith('#'):
                suggestions.append(f"[SIMPLIFY] Line {analysis.line_number} can be simplified or merged")

        return suggestions
