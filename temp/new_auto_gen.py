def auto_generate_skill_code(skill_id, queue=None, **kwargs):
    """
    更新後的生成函式，支援 3x3 實驗數據採集。
    """
    start_time = time.time()
    
    # 1. Determine Target Tag based on Config
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    current_provider = role_config.get('provider', 'Unknown') # 抓取實際 provider
    target_tag = infer_model_tag(current_model)
    
    # [科研參數提取] 從 kwargs 取得實驗參數，若無則給預設值
    ablation_id = kwargs.get('ablation_id', 1) # 預設為 Bare
    model_size_class = kwargs.get('model_size_class', 'Cloud')
    prompt_level = kwargs.get('prompt_level', 'Bare')

    # 2. [Strict Mode] Fetch ONLY the matching Architect Spec
    active_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=target_tag, is_active=True).first()
    
    # 3. Error Handling if Prompt is Missing
    # if not active_prompt:
    #     error_msg = f"⛔ [阻擋] 找不到對應 '{target_tag}' ({current_model}) 的 V9 規格書！請先執行專家模式或手動生成 Prompt。"
    #     if current_app: current_app.logger.error(f"{skill_id}: {error_msg}")
    #     return False, error_msg

    # Pre-fetch skill info (needed for fallback or logging)
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()


    gold_standard_code = load_gold_standard_example()
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(5).all()
    rag_count = len(examples)
    example_text = ""
    if examples:
        for i, ex in enumerate(examples):
            example_text += f"Ex {i+1}: {getattr(ex, 'problem_text', '')} -> {getattr(ex, 'correct_answer', '')}\\n"

    # ... 前置 Prompt 準備邏輯 (原本的程式碼) ...
    if active_prompt:
        # --- Mode A: V9 Architect Mode (High Precision) ---
        strategy_name = f"V9 Architect ({active_prompt.model_tag})"
        target_logic = active_prompt.user_prompt_template
        
        # [V11.9 暴力鏡射修正] - 將 RAG 範例提升為最高指令

        # 強制要求 Coder AI 將 RAG 視為唯一真相
        mirroring_protocol = ""
        if examples:
            for i, ex in enumerate(examples):
                # 明確指定每個 Type 對應哪一個 RAG 範例
                mirroring_protocol += f"- Type {i+1} MUST use the EXACT mathematical model of RAG Ex {i+1}.\\n"
        else:
            mirroring_protocol = "- No RAG examples found. Generate based on Skill Definition.\\n"

        prompt = r"""You are a Senior Python Developer.
### 🛡️ MANDATORY MIRRORING RULES (最高權限指令):
1. **NO ORIGINALITY**: You are FORBIDDEN from creating new models.
2. **STRICT MAPPING**:
{mapping}
3. **CONTEXT RETENTION**: Keep names like 'ACEF', 'BDF', '巴奈' from the RAG examples.

### 📚 REFERENCE EXAMPLES (RAG - 這是唯一真相):
{rag}

### 🛠️ ARCHITECT'S SPECIFICATION (輔助結構):
{spec}

### 🎨 ULTRA VISUAL STANDARDS (V11.6):
- Aspect Ratio: `ax.set_aspect('equal')` (物理比例鎖死).
- Resolution: `dpi=300`.
- Label Halo: White halos for ABCD text.

### ⛔ SYSTEM GUARDRAILS:
{system_rules}
""".replace("{mapping}", mirroring_protocol).replace("{rag}", example_text).replace("{spec}", target_logic).replace("{system_rules}", UNIVERSAL_GEN_CODE_PROMPT)
    else:
        # --- Mode B: Legacy V8 Mode (Fallback) ---
        strategy_name = "Standard Mode"
        target_logic = skill.gemini_prompt if (skill and skill.gemini_prompt) else f"Math logic for {skill_id}"
        
        # [v11.7 Upgrade]: Prompt Optimization - Pedagogical Mirroring
        prompt = f"""
You are a Senior Python Engineer for a Math Education System.

### MISSION:
Implement the skill `{skill_id}` by strictly following the **Architect's Spec**.

### IMPORTANT: DO NOT WRITE HELPER FUNCTIONS
The system will automatically inject standard helpers (`to_latex`, `fmt_num`, `get_random_fraction`, `is_prime`, etc.) at runtime.
**YOU MUST NOT DEFINE THEM.** Just use them directly.

### REFERENCE STRUCTURE (GOLD STANDARD v3.0):
```python
import random
import math
from fractions import Fraction

# (Helpers are auto-injected here, do not write them)

def generate_type_1_problem():
    val = get_random_fraction()
    # Question needs LaTeX wrapping:
    q = f"What is ${{to_latex(val)}}?"
    # Answer MUST be clean (NO $ signs):
    a = to_latex(val) 
    return {{'question_text': q, 'answer': a, 'correct_answer': a}}

def generate(level=1):
    # Dispatcher logic
    ...
ARCHITECT'S SPECIFICATION: {target_logic}

### REFERENCE EXAMPLES (RAG):
{example_text}

### 💡 INSTRUCTION:
Your task is to dynamize (Dynamize) the following examples into Python code, strictly adhering to their mathematical models.

### 🛡️ PEDAGOGICAL PRIORITY PROTOCOL (V11.7):
1. **Type 1 - Textbook Mirroring (Mirror Mode)**:
   - You MUST generate `generate_type_1` by strictly mirroring the first RAG example.
   - **NO ORIGINALITY**: Use the EXACT same mathematical model. ONLY Randomize the numbers.
   - **Context**: Keep keywords like "Aquarium", "Ticket". Do not change context.

2. **Data Linkage (Integer Guarantee)**:
   - For Reverse Calculation problems, generate the integer ANSWER first, then derive the question parameters.

CODING RULES:

1. **NO HELPERS**: Do NOT define `to_latex`, `fmt_num`, `check`, etc. They are auto-injected. Use them directly.

2. **Smart Dispatcher**: Implement `def generate(level=1):` to handle difficulty levels.
   - **[重要：函式命名規範]** 不論題目類型為何，主生成函式必須統一命名為 `generate()`。
   - 禁止使用 `generate_number_line()` 或 `generate_logic()` 等自定義名稱。
   - 如果有繪圖輔助函式（如 `draw_graph`），請在 `generate()` 函式內部呼叫它。
   - 必須確保檔案中存在 `def generate():` 和 `def check(user_answer, correct_answer):`。

3. **LaTeX Formatting (CRITICAL)**: 
   - All mathematical expressions (integers, fractions, equations) in `question_text` MUST be wrapped in single dollar signs `$`.
   - Example: `f"計算 ${fmt_num(a)} + {fmt_num(b)}$ 的值"` -> "計算 $3 + 5$ 的值".
   - **NO BACKTICKS**: Never use backticks (`) to wrap numbers or lists. BAD: `[1, 2]`. GOOD: $1, 2$.

4. **Answer Format Hint (CRITICAL)**:
   - You **MUST** append a clear format hint at the very end of `question_text`.
   - Format: `\\n(答案格式：...)`.
   - Example 1 (Values): `... \\n(答案格式：請填寫整數)` or `... \\n(答案格式：最簡分數)`.
   - Example 2 (Variables): `... \\n(答案格式：x=_, y=_)` (This ensures specific ordering).
   - Example 3 (Coordinates): `... \\n(答案格式：(x,y))`.

5. **Return Keys**: Return dict with keys: `'question_text'`, `'answer'`, `'correct_answer'`.
   - `correct_answer`: Must be a clean string for checking (e.g., "-5", "3/4", "x=2, y=3"). 
   - Do NOT use LaTeX (`$`) in `correct_answer` or `answer` keys, as this makes user input matching difficult. Keep it raw text.

6. **Language**: Traditional Chinese (Taiwan) ONLY (繁體中文). Use local terminology (e.g., 座標, 聯立方程式).

7. **Level Completeness**: Implement both Level 1 (Basic) and Level 2 (Advanced/Applied).

OUTPUT: Return ONLY the Python code. Start with `import random`.

[防呆輸出要求] 在 Python 檔案的最末尾，請務必包含以下代碼，確保進入點相容性：
```python
# 確保主進入點存在 (別名掛載)
if 'generate' not in globals() and any(k.startswith('generate_') for k in globals()):
    generate = next(v for k, v in globals().items() if k.startswith('generate_'))
``` """

    # 初始化計數器
    regex_fixes = 0
    logic_fixes = 0
    ast_repairs = 0
    prompt_tokens = 0
    completion_tokens = 0

    try:
        if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model}")
        
        client = get_ai_client(role='coder') 
        # 1. 取得 LLM 原始回覆 (攔截點)
        
        # 模擬 ai_wrapper 回傳 (內容, tokens) 的行為
        # 這裡假設你的 get_ai_client 回傳的 client 仍然是 google.generativeai 的物件
        response = client.generate_content(prompt)
        raw_response = response.text
        
        # [V9.8] 嘗試獲取 Token 用量
        try:
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
        except:
            pass

        raw_len = len(raw_response)
        
        # 2. 啟動自癒流水線與計時
        healing_start = time.time()
        
        processed_code = raw_response
        
        # 簡單清理 markdown
        match = re.search(r'```(?:python)?\s*(.*?)```', processed_code, re.DOTALL | re.IGNORECASE)
        if match: processed_code = match.group(1)
        elif "import random" in processed_code: processed_code = processed_code[processed_code.find("import random"):]
        
        # 根據實驗組別 (ablation_id) 決定修復強度
        # 1: Bare (不修復) | 2: Regex Only | 3: Full Healing (Regex + AST)
        
        final_code = processed_code
        
        if ablation_id >= 2:
            # Regex Armor
            final_code = inject_perfect_utils(final_code)
            
            # [V9.8.2 Defense] Hard Validation for 7B Models
            # validate_and_fix_code 包含了 regex 修復
            final_code, pre_fixes = validate_and_fix_code(final_code)
            regex_fixes += pre_fixes

            final_code, patch_fixes = universal_function_patcher(final_code)
            regex_fixes += patch_fixes
            
            final_code = fix_return_format(final_code)
            final_code = clean_global_scope_execution(final_code)
            final_code = inject_robust_dispatcher(final_code) 
            final_code = fix_missing_answer_key(final_code)
            
        
        if ablation_id == 3:
            # Full Healing (AST + Logic)
            # [V9.8] 驗證與修復
            is_valid, syntax_err = validate_python_code(final_code)
            if not is_valid:
                final_code, r_count = fix_code_syntax(final_code, syntax_err)
                regex_fixes += r_count # Count this as regex/syntax fix
                ast_repairs += 1 # Count as a repair event
                
            is_valid_log, logic_err = validate_logic_with_pyflakes(final_code)
            if not is_valid_log:
                final_code, l_count = fix_logic_errors(final_code, logic_err)
                logic_fixes += l_count
                ast_repairs += 1 # Count as a repair event

            # Final Logic Hardening
             # 1. String Deduplication
            if final_code.count("請輸入") > 1 or final_code.count("例如：") > 1:
                final_code = re.sub(r'(\(請輸入.*?\))(\s*\\n\1)+', r'\1', final_code)
            
             # 2. Quote Hardening
            font_pattern = r"(?:matplotlib\.|plt\.)?rcParams\[['\"]font\.sans-serif['\"]\]\s*=\s*(?:\[[^\]]*\]|['\"].*?['\"])"
            final_code = re.sub(font_pattern, "plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']", final_code)
            
             # 3. Physical Newline Hardening
            final_code = final_code.replace('\\\\n', '\\n')


        healing_duration = time.time() - healing_start

        # 3. 實驗評分：語法正確性校驗 (score_syntax)
        try:
            ast.parse(final_code)
            score_syntax = 100.0
        except SyntaxError:
            score_syntax = 0.0
            
        # 寫入檔案
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        header = f'''# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: {strategy_name}
# Duration: {time.time() - start_time:.2f}s | RAG: {rag_count} examples
# Created At: {created_at}
# Fix Status: Ablation={ablation_id}
#==============================================================================\n\n'''
        path = os.path.join(current_app.root_path, 'skills', f'{skill_id}.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(header + final_code)

        # 4. 呼叫更新後的 log_experiment (科研對接)
        log_experiment(
            skill_id=skill_id,
            start_time=start_time,
            prompt_len=len(prompt),
            code_len=len(final_code),
            is_valid=(score_syntax == 100.0),
            error_msg="None" if score_syntax == 100.0 else "Syntax Error",
            repaired=(ast_repairs > 0 or regex_fixes > 0 or logic_fixes > 0),
            model_name=current_model,
            actual_provider=current_provider,
            # --- 傳入科研專用 kwargs ---
            model_size_class=model_size_class,
            prompt_level=prompt_level,
            raw_response=raw_response,       # 存下 AI 的「原始幻覺」
            final_code=final_code,           # 存下你的「醫療成果」
            score_syntax=score_syntax,
            healing_duration=healing_duration,
            ablation_id=ablation_id,
            ast_repair_count=ast_repairs,
            regex_fix_count=regex_fixes,
            logic_fix_count=logic_fixes,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            resource_cleanup_flag=True # 標記資源釋放
        )

        return True, "Success"

    except Exception as e:
        # 即使崩潰也要紀錄，這對分析模型穩定性非常重要
        log_experiment(
            skill_id=skill_id,
            start_time=start_time,
            prompt_len=0,
            code_len=0,
            is_valid=False,
            error_msg=str(e),
            repaired=False,
            model_name=current_model if 'current_model' in locals() else "Unknown",
            raw_response=raw_response if 'raw_response' in locals() else "LLM API Failure",
            ablation_id=ablation_id,
            model_size_class=model_size_class,
            prompt_level=prompt_level
        )
        return False, str(e)
