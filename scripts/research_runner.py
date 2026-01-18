# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): scripts/research_runner.py
功能說明 (Description): 執行大規模題目採樣，數據存入 execution_samples 後自動
                       匯出 Excel 報表至 reports/ 目錄。
執行語法 (Usage): 

版本資訊 (Version): V1.4 (Auto-Export Research Edition)
=============================================================================
"""
import os
import sys
import time
import sqlite3
import importlib.util
import glob
import pandas as pd
from tqdm import tqdm

# ==========================================
# 1. 環境初始化 (Environment Setup)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(current_dir)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SKILLS_DIR = os.path.join(PROJECT_ROOT, 'skills')
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'kumon_math.db')
PROTECTED_FILES = {"Example_Program.py", "__init__.py", "base_skill.py", "Example_Program_Research.py"}

# 確保目錄存在
os.makedirs(REPORTS_DIR, exist_ok=True)

def get_skill_menu():
    """ 掃描 skills 目錄並產出選單 """
    files = glob.glob(os.path.join(SKILLS_DIR, "*.py"))
    skill_list = [os.path.basename(f).replace('.py', '') for f in files 
                  if os.path.basename(f) not in PROTECTED_FILES]
    return sorted(skill_list)

# ==========================================
# 2. Excel 匯出邏輯 (Export Logic)
# ==========================================
def export_to_excel(skill_id, ablation_id=3, model_size="14B"):
    """ 從資料庫抓取最新採樣數據並匯出「含嵌入圖片」的 Excel """
    import io, base64 # 確保引入必要工具
    conn = sqlite3.connect(DB_PATH)
    
    query = f"""
        SELECT mode, sample_index, question_text, correct_answer, image_base64,
               is_crash, is_logic_correct, score_complexity, duration_seconds, timestamp
        FROM execution_samples 
        WHERE skill_id = '{skill_id}' AND ablation_id = {ablation_id}
        ORDER BY id DESC LIMIT 20
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    tag_timestamp = time.strftime('%Y%m%d_%H%M')
    # 修正檔名：移除重複的 Ab，加入 model_size
    base_id = skill_id.replace(f"_Ab{ablation_id}", "") 
    file_name = f"{base_id}_Ab{ablation_id}_{model_size}_{tag_timestamp}.xlsx"
    file_path = os.path.join(REPORTS_DIR, file_name)

    # 使用 xlsxwriter 引擎進行圖片處理
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    # 移除 Base64 文字欄位後匯出其餘數據，避免 Excel 內容過長
    df.drop(columns=['image_base64']).to_excel(writer, sheet_name='ResearchData', index=False)
    
    workbook  = writer.book
    worksheet = writer.sheets['ResearchData']
    
    # 在第 K 欄 (索引 10) 插入圖片標題與調整寬度
    worksheet.write(0, 10, "題目圖片 (Visual)")
    worksheet.set_column('K:K', 40) 

    for idx, b64_str in enumerate(df['image_base64']):
        if b64_str and len(b64_str) > 100: # 確保有圖片數據
            try:
                img_data = base64.b64decode(b64_str)
                img_file = io.BytesIO(img_data)
                
                # 設定列高以容納圖片
                worksheet.set_row(idx + 1, 120) 
                # 插入圖片並縮放至適合儲存格大小
                worksheet.insert_image(idx + 1, 10, f'img_{idx}.png', 
                                       {'image_data': img_file, 'x_scale': 0.35, 'y_scale': 0.35})
            except Exception as e:
                worksheet.write(idx + 1, 10, f"圖片損毀: {e}")

    writer.close()
    return file_path

# ==========================================
# 3. 核心採樣流程
# ==========================================
def run_research_samples(skill_id, n_samples=20, ablation_id=3):
    """
    [科研目標]: 採集 20 道題目數據，分析 14B 模型的出題品質。
    """
    skill_file = os.path.join(SKILLS_DIR, f"{skill_id}.py")
    
    # 動態加載技能模組
    spec = importlib.util.spec_from_file_location(skill_id, skill_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"\n🧪 啟動科研採樣: {skill_id} (Ablation: {ablation_id})")
    
    for i in tqdm(range(n_samples), desc="採樣進度"):
        start_time = time.time()
        # 初始狀態標記
        is_crash = 0
        is_logic_correct = 0
        res = {}
        
        try:
            # 讓程式產出一道題目
            res = module.generate()

            # 增加檢查：如果不是字典，報警但不要崩潰
            if not isinstance(res, dict):
                print(f"⚠️ 警告: 模式 [{skill_id}] 回傳了非字典格式: {type(res)}")
                continue
            
            # [自檢邏輯]: 將正確答案餵回 check()，檢查內部一致性
            check_res = module.check(res['correct_answer'], res['correct_answer'])
            is_logic_correct = 1 if check_res.get('correct') else 0
            
        except Exception as e:
            # 紀錄崩潰狀態
            is_crash = 1
            print(f"\n❌ 第 {i+1} 題生成失敗: {str(e)}")

        duration = time.time() - start_time
        
        # 計算難度分數 (簡易演算法: 題目字數越多通常越複雜)
        q_text = res.get('question_text', '')
        score = min(10, len(q_text) // 10) if q_text else 0

        # ------------------------------------------------------------------
        # 3. 數據寫入 (對應 Phase 4 欄位)
        # ------------------------------------------------------------------
        cursor.execute("""
            INSERT INTO execution_samples (
                skill_id, mode, sample_index, question_text, correct_answer, 
                image_base64, is_crash, is_logic_correct, score_complexity, 
                duration_seconds, ablation_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            skill_id, 
            res.get('mode', 0),    # 擷取產出的模式 (1-6)
            i + 1, 
            q_text, 
            str(res.get('correct_answer', '')),
            res.get('image_base64', ''),
            is_crash, 
            is_logic_correct, 
            score, 
            duration, 
            ablation_id
        ))
        conn.commit()

    conn.close()
    print(f"\n✅ 採樣完成！20 道題目已存入 execution_samples 表格。")

    # (執行完成後呼叫匯出)
    print(f"\n📦 正在產生科研報表...")
    report_path = export_to_excel(skill_id, ablation_id)
    if report_path:
        print(f"✅ 報表已匯出: {report_path}")

if __name__ == "__main__":
    print("="*60)
    print("🔬 Math AI Research Runner (V1.4 - Auto Export)")
    print("="*60)
    
    skills = get_skill_menu()
    if not skills:
        print("❌ skills/ 目錄內沒有可測試的檔案。")
        sys.exit(0)
        
    for i, name in enumerate(skills, 1):
        print(f"   [{i}] {name}")
        
    try:
        choice = int(input(f"\n👉 請選擇要採樣的技能 (1-{len(skills)}): "))
        if 1 <= choice <= len(skills):
            run_research_samples(skills[choice-1])
        else:
            print("❌ 超出範圍。")
    except ValueError:
        print("❌ 請輸入數字。")