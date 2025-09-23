from codegen.functional_code_generator import FunctionalCodeGenerator
from codegen.graph import Graph
from codegen.code_executor import CodeExecutor, ExecutionResult

from pathlib import Path
 
class Controller:
    def __init__(self, request: str = ""):
        self.graph = Graph()
        self.codegener = FunctionalCodeGenerator(request)
        self.code_executor = CodeExecutor()

    def run(self):
        project_root = Path(__file__).parent.parent

        # 将生成的合约写入到文件中
        self.codegener.generate_contract()
        contract_file = project_root / "code" / "contract.json"
        contract_file.parent.mkdir(parents=True, exist_ok=True)
        with open(contract_file, "w", encoding="utf-8") as f:
            f.write(self.codegener.contract_raw)
        
        # 将合约转换为logic
        self.codegener.generate_logic()
        logic_file = project_root / "code" / "logic.py"
        logic_file.parent.mkdir(parents=True, exist_ok=True)
        with open(logic_file, "w", encoding="utf-8") as f:
            f.write(self.codegener.logic)

        # 将逻辑转换为实现
        self.codegener.generate_implementation()
        code_file = project_root / "code" / "generated_code.py"
        code_file.parent.mkdir(parents=True, exist_ok=True)
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(self.codegener.implementation)

        result = self.code_executor.run(self.codegener.implementation)


