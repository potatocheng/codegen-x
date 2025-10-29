# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeGen-X is an AI-driven code generation system that uses an **Agent + Tools** architecture with structured LLM outputs. The system transforms natural language requests into production-ready Python code through an intelligent workflow: **Spec → Implement → Validate → Refine** (with automatic iteration until tests pass).

## Core Architecture

### Agent + Tools Architecture

The new architecture uses an autonomous agent that orchestrates specialized tools:

1. **SpecTool** ([tools/spec_tool.py](tools/spec_tool.py))
   - Generates detailed function specifications from user requirements
   - Uses structured LLM output (Pydantic models) - no JSON parsing needed
   - Returns `FunctionSpec` with parameters, examples, edge cases, exceptions

2. **ImplementTool** ([tools/implement_tool.py](tools/implement_tool.py))
   - Implements code based on the specification
   - Generates complete function code and test cases
   - Returns `Implementation` object with code, explanation, and tests

3. **ValidateTool** ([tools/validate_tool.py](tools/validate_tool.py))
   - Executes code against spec examples using [CodeExecutor](codegen/code_executor.py)
   - Returns detailed `ValidationResult` with pass/fail for each test
   - Provides actionable suggestions for failures

4. **RefineTool** ([tools/refine_tool.py](tools/refine_tool.py))
   - Fixes code based on validation failures
   - Uses LLM to analyze failed tests and generate improved code
   - Iterates until tests pass (max attempts configurable)

### Key Components

- **CodeGenAgent** ([agent/code_agent.py](agent/code_agent.py)): Main orchestrator that executes the workflow (Spec → Implement → Validate → Refine loop). Automatically retries implementation until all tests pass or max attempts reached.

- **StructuredLLM** ([llm/structured_llm.py](llm/structured_llm.py)): Wrapper for OpenAI API with Pydantic structured outputs. Guarantees type-safe responses, eliminates JSON parsing errors. Supports any OpenAI-compatible API (including DeepSeek).

- **Tool Base Classes** ([tools/base.py](tools/base.py)): Abstract `Tool`, `ToolInput`, `ToolOutput` classes using Pydantic for full type safety.

### Workflow

```
User Request
    ↓
[SpecTool] → FunctionSpec (with examples)
    ↓
[ImplementTool] → Implementation (code + tests)
    ↓
[ValidateTool] → ValidationResult
    ↓
  Pass? → Done ✓
    ↓ Fail
[RefineTool] → Improved Implementation
    ↓
[ValidateTool] → ... (repeat up to N times)
```

## Development Commands

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your-api-key"
# Or for DeepSeek/other compatible APIs:
export OPENAI_BASE_URL="https://api.deepseek.com"
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run new agent tests
python -m pytest tests/test_agent.py

# Run with coverage
python -m pytest --cov=tools --cov=agent --cov=llm tests/

# Run specific test
python -m pytest tests/test_agent.py::TestCodeGenAgent::test_spec_tool -v
```

### Using the System

**Command Line Usage:**

```bash
# Generate code from command line
python main.py "Write a function to remove duplicates from a sorted array"

# Specify custom model
python main.py "Calculate factorial" --model gpt-4o-2024-08-06

# Custom output directory
python main.py "Binary search" --output my_output

# Interactive mode (no arguments)
python main.py
```

**Python API:**

```python
from llm.structured_llm import StructuredLLM
from agent.code_agent import CodeGenAgent

# Initialize
llm = StructuredLLM(model="gpt-4o-2024-08-06")
agent = CodeGenAgent(llm, max_refine_attempts=3)

# Generate code
result = agent.generate("Write a function to reverse a linked list")

if result["success"]:
    print(f"Function: {result['spec']['name']}")
    print(f"Code:\n{result['code']}")
    print(f"Tests passed: {result['validation']['passed_count']}/{result['validation']['total_tests']}")
else:
    print(f"Failed: {result.get('message')}")
```

**Output Structure:**

Generated artifacts saved to `code/generated/`:
- `spec.json`: Function specification with all requirements
- `implementation.py`: Final working code
- `validation.json`: Test results and validation details

## Important Implementation Details

### Structured Output Benefits

**No more JSON parsing errors!** The new architecture uses Pydantic models with OpenAI's structured output API:

```python
# Old way (fragile)
response = llm.call(messages)
json_start = response.find('{')
json_end = response.rfind('}') + 1
data = json.loads(response[json_start:json_end])  # Can fail!

# New way (guaranteed)
spec = llm.generate_structured(
    prompt=prompt,
    output_schema=FunctionSpec  # Pydantic model
)
# spec is already a validated FunctionSpec object!
```

### Adding New Tools

To add a new tool to the system:

1. **Create tool class** in `tools/your_tool.py`:

```python
from pydantic import BaseModel, Field
from tools.base import Tool, ToolInput, ToolOutput

class YourInput(ToolInput):
    param: str = Field(description="Parameter description")

class YourResult(BaseModel):
    result: str

class YourOutput(ToolOutput):
    data: YourResult

class YourTool(Tool):
    name = "your_tool"
    description = "What this tool does"
    input_schema = YourInput

    def execute(self, input: YourInput) -> YourOutput:
        # Implementation
        return YourOutput(success=True, data=YourResult(...))
```

2. **Register in agent** ([agent/code_agent.py](agent/code_agent.py)):

```python
def _register_tools(self):
    return {
        # ... existing tools
        "your_tool": YourTool(self.llm),
    }
```

### Validation and Testing

The `ValidateTool` automatically runs examples from the spec:

```python
# In FunctionSpec
examples=[
    Example(
        inputs={"nums": [1, 1, 2]},
        expected_output=2,
        description="Remove duplicates"
    )
]

# ValidateTool generates and runs:
# result = remove_duplicates(nums=[1, 1, 2])
# assert result == 2
```

### Error Handling

Tools return `ToolOutput` with success flag:

```python
result = tool.execute(input)
if not result.success:
    # Handle failure
    print(result.message)
    # result.data may be None
```

Agent automatically handles tool failures and can retry or adjust strategy.

## Testing Guidelines

**Mock LLM for Testing:**

Use `MockStructuredLLM` pattern from [tests/test_agent.py](tests/test_agent.py):

```python
class MockStructuredLLM:
    def generate_structured(self, prompt, output_schema, **kwargs):
        if output_schema == FunctionSpec:
            return FunctionSpec(name="test_func", ...)
        elif output_schema == Implementation:
            return Implementation(code="def test(): pass", ...)
```

**Test individual tools:**

```python
def test_spec_tool():
    mock_llm = MockStructuredLLM()
    tool = SpecTool(mock_llm)
    result = tool.execute(tool.input_schema(requirement="..."))
    assert result.success
    assert isinstance(result.data, FunctionSpec)
```

**Test full agent workflow:**

```python
def test_agent_generate():
    mock_llm = MockStructuredLLM()
    agent = CodeGenAgent(mock_llm, max_refine_attempts=2)
    result = agent.generate("Write a test function")
    assert result["success"]
```

## Architecture Benefits

### Why This is Better

1. **Type Safety**: Pydantic models eliminate runtime type errors
2. **No JSON Parsing**: LLM outputs are automatically validated
3. **Composable Tools**: Easy to add/remove/modify tools independently
4. **Self-Healing**: Agent automatically retries failed implementations
5. **Testable**: Each tool can be tested in isolation
6. **Extensible**: New tools don't require changing existing code

### Migration from Old Architecture

The old architecture (ThinkingGraph, StepGraph, multi-stage pipeline) is **deprecated**. Key differences:

| Old | New |
|-----|-----|
| Hard-coded 4-stage pipeline | Dynamic tool-based workflow |
| Manual JSON parsing + retry loops | Structured outputs (guaranteed valid) |
| String-based prompt templates in TOML | Prompts embedded in tool classes |
| No automatic testing/validation | Built-in validation with auto-refinement |
| Complex dependencies (Spec → StepGraph → Logic → Impl) | Simple linear flow with feedback loops |

Old code in `codegen/functional_code_generator.py`, `thinking_graph.py`, `codegen/step_graph.py` is kept for reference but should not be used for new features.

## Legacy Code (Do Not Use)

The following modules are **deprecated** and retained only for reference:

- `controller/controller.py` - Old controller
- `codegen/functional_code_generator.py` - Old pipeline
- `codegen/step_graph.py` - Old step graph system
- `thinking_graph.py` - Graph architecture (no longer needed)
- `config/prompts.toml` - Old prompt templates

**Always use the new Agent + Tools architecture for new development.**
