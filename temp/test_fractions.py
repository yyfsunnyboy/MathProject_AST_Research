import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.code_generator import auto_generate_skill_code

is_ok, msg, metrics = auto_generate_skill_code(
    'jh_數學1上_FourArithmeticOperationsOfNumbers', 
    'qwen2.5-coder:14b', 
    force_regenerate=True, 
    ablation_id=3, 
    model_size_class='14B'
)

print(f'結果: {is_ok}')
print(f'訊息: {msg}')
print(f'時間: {metrics.get("total_time_sec", 0):.2f}秒')
print(f'Regex 修復: {metrics.get("regex_fixes", 0)}')
print(f'AST 修復: {metrics.get("ast_fixes", 0)}')
