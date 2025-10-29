"""
Cognitive-driven Code Generation Workflow

This module provides the main workflow for cognitive-driven code generation
that integrates with the existing CodeGen-X system while adding cognitive capabilities.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from llm.structured_llm import StructuredLLM
from cognitive.cognitive_agent import CognitiveCodeGenAgent, CognitiveCodeGenRequest, CognitiveCodeGenOutput


class CognitiveWorkflow:
    """
    Main workflow for cognitive-driven code generation

    Integrates cognitive agent with existing system infrastructure
    """

    def __init__(self, model: str = "gpt-4o-2024-08-06", output_dir: str = "code/cognitive_generated"):
        """
        Initialize cognitive workflow

        Args:
            model: LLM model to use
            output_dir: Directory to save generated artifacts
        """
        self.llm = StructuredLLM(model=model)
        self.cognitive_agent = CognitiveCodeGenAgent(self.llm)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_cognitive_code(
        self,
        requirement: str,
        context: Optional[str] = None,
        constraints: Optional[list] = None,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate code using cognitive-driven approach

        Args:
            requirement: Natural language requirement
            context: Additional context
            constraints: Implementation constraints
            difficulty: Problem difficulty level

        Returns:
            Dictionary containing generation results and cognitive analysis
        """
        print(f"\n🧠 Starting cognitive-driven code generation...")
        print(f"Requirement: {requirement}")

        # Create cognitive request
        request = CognitiveCodeGenRequest(
            requirement=requirement,
            context=context,
            constraints=constraints or [],
            difficulty=difficulty
        )

        try:
            # Generate code using cognitive agent
            result = self.cognitive_agent.generate_code(request)

            # Save generated artifacts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_dir = self.output_dir / f"session_{timestamp}"
            session_dir.mkdir(exist_ok=True)

            # Save code
            code_file = session_dir / "generated_code.py"
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(result.generated_code)

            # Save cognitive analysis
            analysis_file = session_dir / "cognitive_analysis.json"
            cognitive_data = {
                "requirement": requirement,
                "explanation": result.explanation,
                "line_explanations": result.line_explanations,
                "reasoning_chain": result.reasoning_chain,
                "confidence": result.confidence,
                "strategy_used": result.strategy_used.value,
                "thinking_stages": result.thinking_stages,
                "cognitive_load": {
                    "intrinsic_load": result.cognitive_load.intrinsic_load,
                    "extraneous_load": result.cognitive_load.extraneous_load,
                    "germane_load": result.cognitive_load.germane_load,
                    "total_load": result.cognitive_load.total_load,
                    "working_memory_usage": result.cognitive_load.working_memory_usage
                },
                "cognitive_trace": result.cognitive_trace,
                "timestamp": timestamp
            }

            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(cognitive_data, f, indent=2, ensure_ascii=False)

            # Generate explainability report
            report_file = session_dir / "explainability_report.md"
            self._generate_explainability_report(result, report_file)

            print(f"✅ Code generation completed successfully!")
            print(f"📁 Output saved to: {session_dir}")
            print(f"🎯 Strategy used: {result.strategy_used.value}")
            print(f"📊 Confidence: {result.confidence:.2f}")
            print(f"🧮 Cognitive Load: {result.cognitive_load.total_load:.2f}")

            return {
                "success": True,
                "code": result.generated_code,
                "explanation": result.explanation,
                "line_explanations": result.line_explanations,
                "cognitive_analysis": cognitive_data,
                "output_dir": str(session_dir),
                "confidence": result.confidence,
                "strategy": result.strategy_used.value
            }

        except Exception as e:
            print(f"❌ Error during cognitive code generation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "code": None,
                "explanation": None
            }

    def _generate_explainability_report(self, result: CognitiveCodeGenOutput, report_file: Path):
        """Generate detailed explainability report"""
        report_content = f"""# Cognitive Code Generation Report

## Generated Code
```python
{result.generated_code}
```

## Overall Explanation
{result.explanation}

## Line-by-Line Explanations
"""
        for line_num, explanation in result.line_explanations.items():
            report_content += f"**Line {line_num}:** {explanation}\n\n"

        report_content += f"""
## Cognitive Process Analysis

### Strategy Used
**{result.strategy_used.value}** - Selected based on problem characteristics and cognitive load assessment.

### Reasoning Chain
"""
        for i, step in enumerate(result.reasoning_chain, 1):
            report_content += f"{i}. {step}\n"

        report_content += f"""
### Thinking Stages
"""
        for stage in result.thinking_stages:
            report_content += f"- **{stage['stage']}**: {stage['focus']}\n"

        report_content += f"""
### Cognitive Load Analysis
- **Intrinsic Load**: {result.cognitive_load.intrinsic_load:.2f} (problem complexity)
- **Extraneous Load**: {result.cognitive_load.extraneous_load:.2f} (implementation complexity)
- **Germane Load**: {result.cognitive_load.germane_load:.2f} (learning and schema construction)
- **Total Load**: {result.cognitive_load.total_load:.2f}
- **Working Memory Usage**: {result.cognitive_load.working_memory_usage:.2f}

### Confidence Assessment
**{result.confidence:.2f}** - Based on solution completeness, strategy alignment, and validation results.

## Cognitive Trace Details
"""

        if result.cognitive_trace.get("decisions"):
            report_content += "### Key Decisions\n"
            for decision in result.cognitive_trace["decisions"]:
                report_content += f"- {decision.get('reasoning', 'Strategic decision made')}\n"

        report_content += f"""
## Academic Relevance

This cognitive-driven approach provides several advantages for research publication:

1. **Explainability**: Every line of code has a cognitive justification
2. **Human-like Processing**: Mimics actual programmer cognitive processes
3. **Load Management**: Optimizes cognitive burden during generation
4. **Strategy Adaptation**: Selects appropriate programming strategies
5. **Process Transparency**: Complete trace of decision-making process

## Future Research Directions

1. **Cognitive Load Optimization**: Further research on minimizing extraneous load
2. **Strategy Learning**: Machine learning approaches to improve strategy selection
3. **Collaborative Cognition**: Multiple agent cognitive processes
4. **Domain-Specific Cognition**: Specialized cognitive models for different programming domains
"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

    def analyze_cognitive_session(self, session_dir: str) -> Dict[str, Any]:
        """Analyze a completed cognitive generation session"""
        session_path = Path(session_dir)

        if not session_path.exists():
            return {"error": "Session directory not found"}

        # Load cognitive analysis
        analysis_file = session_path / "cognitive_analysis.json"
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)

            return {
                "success": True,
                "analysis": analysis,
                "cognitive_stages": len(analysis.get("thinking_stages", [])),
                "reasoning_steps": len(analysis.get("reasoning_chain", [])),
                "cognitive_load": analysis.get("cognitive_load", {}),
                "strategy": analysis.get("strategy_used", "unknown")
            }

        return {"error": "Analysis file not found"}


def demonstrate_cognitive_generation():
    """Demonstrate the cognitive-driven code generation system"""
    print("🧠 Cognitive-Driven Code Generation Demo")
    print("=" * 50)

    workflow = CognitiveWorkflow()

    # Example requirements for demonstration
    examples = [
        {
            "requirement": "Write a function to remove duplicates from a sorted array in-place",
            "difficulty": "medium",
            "constraints": ["O(1) extra space", "modify array in-place"]
        },
        {
            "requirement": "Implement a binary search algorithm with detailed error handling",
            "difficulty": "easy",
            "context": "Should work with any sorted list of comparable elements"
        },
        {
            "requirement": "Create a function that validates a binary search tree",
            "difficulty": "hard",
            "constraints": ["recursive approach preferred", "handle edge cases"]
        }
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n--- Example {i} ---")
        result = workflow.generate_cognitive_code(**example)

        if result["success"]:
            print(f"✅ Generated successfully with {result['confidence']:.0%} confidence")
            print(f"📁 Saved to: {result['output_dir']}")
        else:
            print(f"❌ Failed: {result['error']}")

        print("-" * 30)


if __name__ == "__main__":
    demonstrate_cognitive_generation()