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
from .cognitive_line_explainer import CognitiveLineExplainer
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
            reasoning_chains=[],
            decompositions=[],
            hypotheses=[],
            active_concepts={}
        )

        self.cognitive_load_evaluator = CognitiveLoadEvaluator()
        self.programming_strategy = ProgrammingStrategy()

        # 认知驱动的行级解释器
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
            strategy_used=implementation["strategy"],
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
        """Stage 1: Problem Comprehension"""
        self._transition_to_stage(ThinkingStage.PROBLEM_COMPREHENSION, request.requirement)

        # Analyze problem characteristics
        problem_chars = ProblemCharacteristics(
            domain="general",
            complexity="medium",
            data_structures=["list", "string"],
            algorithms=["iteration"],
            constraints=request.constraints or []
        )

        # Create problem decomposition
        decomposition_prompt = f"""
        Analyze this programming requirement and break it down into key components:

        Requirement: {request.requirement}
        Context: {request.context or 'None'}
        Constraints: {', '.join(request.constraints) if request.constraints else 'None'}

        Think like a human programmer. What are the main parts of this problem?
        What inputs, outputs, and processing steps are needed?
        """

        # Simulate cognitive processing
        understanding = {
            "main_goal": request.requirement,
            "key_components": ["input processing", "core logic", "output formatting"],
            "complexity_assessment": problem_chars.complexity,
            "initial_thoughts": [
                "Need to understand the exact requirements",
                "Identify input/output specifications",
                "Consider edge cases and constraints"
            ]
        }

        # Update working memory
        self.cognitive_model.current_state.working_memory.append(
            WorkingMemoryItem(
                content=f"Problem: {request.requirement}",
                importance=1.0,
                timestamp=datetime.now()
            )
        )

        self.cognitive_trace["reasoning"].append({
            "stage": "problem_comprehension",
            "understanding": understanding
        })

        return understanding

    def _plan_solution(self, problem_understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Solution Planning"""
        self._transition_to_stage(ThinkingStage.SOLUTION_PLANNING, "Planning solution approach")

        # Select programming strategy
        problem_chars = ProblemCharacteristics(
            domain="general",
            complexity="medium",
            data_structures=["list", "string"],
            algorithms=["iteration"],
            constraints=[]
        )

        strategy = self.programming_strategy.select_strategy(
            problem_chars,
            self.cognitive_model.current_state,
            self.thinking_process
        )

        # Create solution plan
        plan = {
            "strategy": strategy,
            "approach": "step-by-step implementation",
            "main_steps": [
                "Define function signature",
                "Implement core logic",
                "Handle edge cases",
                "Return result"
            ],
            "considerations": [
                "Input validation",
                "Performance optimization",
                "Code readability"
            ]
        }

        self.cognitive_trace["decisions"].append({
            "stage": "solution_planning",
            "strategy_selected": strategy.value,
            "reasoning": "Selected based on problem characteristics"
        })

        return plan

    def _design_algorithm(self, solution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 3: Algorithm Design"""
        self._transition_to_stage(ThinkingStage.ALGORITHM_DESIGN, "Designing algorithm structure")

        algorithm = {
            "pseudocode": [
                "1. Validate input parameters",
                "2. Initialize result variables",
                "3. Process input according to requirements",
                "4. Return processed result"
            ],
            "data_structures": ["variables", "loops"],
            "time_complexity": "O(n)",
            "space_complexity": "O(1)",
            "edge_cases": ["empty input", "invalid input"]
        }

        return algorithm

    def _implement_code(self, algorithm_design: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 4: Implementation"""
        self._transition_to_stage(ThinkingStage.IMPLEMENTATION, "Writing code")

        # For demo purposes, create a simple implementation
        # In real system, this would use LLM to generate code based on algorithm design

        code = """def solve_problem(input_data):
    \"\"\"
    Solves the given problem following cognitive-driven approach.

    Args:
        input_data: The input to process

    Returns:
        The processed result
    \"\"\"
    # Step 1: Validate input
    if not input_data:
        return None

    # Step 2: Process the input
    result = process_input(input_data)

    # Step 3: Return result
    return result

def process_input(data):
    \"\"\"Helper function to process input data\"\"\"
    # Implementation logic here
    return data
"""

        implementation = {
            "code": code,
            "explanation": "Implemented following step-by-step approach with clear structure",
            "confidence": 0.8,
            "strategy": algorithm_design.get("strategy", StrategyType.TOP_DOWN)
        }

        return implementation

    def _validate_solution(self, implementation: Dict[str, Any], request: CognitiveCodeGenRequest) -> Dict[str, Any]:
        """Stage 5: Validation"""
        self._transition_to_stage(ThinkingStage.VALIDATION, "Validating solution")

        # Simulate validation process
        validation = {
            "syntax_check": True,
            "logic_check": True,
            "test_cases_passed": True,
            "needs_optimization": False,
            "issues_found": []
        }

        return validation

    def _optimize_solution(self, implementation: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 6: Optimization (if needed)"""
        self._transition_to_stage(ThinkingStage.OPTIMIZATION, "Optimizing solution")

        # Return optimized implementation
        return implementation

    def _reflect_on_solution(self, implementation: Dict[str, Any], request: CognitiveCodeGenRequest) -> Dict[str, Any]:
        """Stage 7: Reflection"""
        self._transition_to_stage(ThinkingStage.REFLECTION, "Reflecting on solution quality")

        reflection = {
            "quality_assessment": "Good",
            "alternative_approaches": ["Could use different data structure"],
            "lessons_learned": ["Step-by-step approach worked well"],
            "improvements": ["Add more error handling"]
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