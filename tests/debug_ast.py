# Debug AST structure
import ast

test_code = """
def generate(level=1, **kwargs):
    def helper(target):
        for i in range(100):
            if i == target:
                return i * 2
    
    result = helper(10)
    return {'answer': result}
"""

tree = ast.parse(test_code)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f"\n函数: {node.name}")
        print(f"  函数体长度: {len(node.body)}")
        for i, stmt in enumerate(node.body):
            print(f"  [{i}] {type(stmt).__name__}")
        
        if node.body:
            last = node.body[-1]
            print(f"  最后一个语句: {type(last).__name__}")
            
            # 检查是否有循环
            has_loop = False
            for stmt in ast.walk(node):
                if isinstance(stmt, (ast.For, ast.While)):
                    has_loop = True
                    break
            print(f"  包含循环: {has_loop}")
