# CodeGen-X

A sophisticated code generation system with thinking graph architecture for automatic code generation and optimization.

## Features

- **Thinking Graph**: Intelligent planning and execution using graph-based thinking
- **Functional Code Generation**: Automated code generation with optimization
- **Multi-LLM Support**: Support for various LLM providers (DeepSeek, etc.)
- **Code Execution**: Safe code execution and validation
- **Modular Architecture**: Well-structured codebase with separate modules

## Project Structure

```
codegen-x/
├── codegen/                 # Core code generation modules
│   ├── code_executor.py     # Code execution and validation
│   ├── functional_code_generator.py  # Main code generation logic
│   ├── graph.py            # Graph operations
│   └── Logic2CFGParser.py  # Logic to control flow graph parser
├── config/                 # Configuration files
│   ├── config.py          # Configuration management
│   └── prompts.toml       # Prompt templates
├── controller/            # System controller
│   └── controller.py     # Main controller logic
├── llm/                   # LLM interface modules
│   ├── llm_interface.py  # Abstract LLM interface
│   ├── deepseek.py       # DeepSeek LLM implementation
│   ├── factory.py        # LLM factory pattern
│   └── message.py        # Message handling
├── tests/                 # Test modules
├── thinking_graph.py      # Core thinking graph implementation
├── logger.py             # Logging utilities
└── code/                 # Generated code output
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/codegen-x.git
cd codegen-x
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

[Add usage instructions here based on your specific implementation]

## Configuration

Configure the system by editing `config/prompts.toml` and setting up your LLM provider credentials.

## Testing

Run tests using:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

[Add your license here]
