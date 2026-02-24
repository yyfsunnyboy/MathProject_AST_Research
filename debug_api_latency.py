import os
import time
import google.generativeai as genai

# --- Configuration ---
# 使用者提供的 API Key
API_KEY = "AIzaSyCLQakaMXGD-pYFHEcHG_6vK9e2g8TiWNw"

# 要測試的技能和 prompt 檔案
SKILL_NAME = "jh_數學1上_FourArithmeticOperationsOfIntegers"
PROMPT_FILE = "ab1_bare_prompt.md"

# 要使用的模型
MODEL_NAME = "gemini-pro" # 使用 1.5 flash 來確保與使用者在網頁上比較的體驗更接近

def main():
    """
    主執行函式，用於測量單一 Gemini API 呼叫的延遲。
    """
    print("="*60)
    print("Gemini API Latency Test for Ab1 Bare Prompt")
    print("="*60)

    # 1. 設定 API Key
    try:
        genai.configure(api_key=API_KEY)
        print("[OK] Google AI SDK configured.")
    except Exception as e:
        print(f"[Error] Failed to configure SDK: {e}")
        return

    # 2. 讀取 Prompt 內容
    try:
        # 假設此腳本在專案根目錄執行，或路徑相對於根目錄
        prompt_path = os.path.join("agent_skills", SKILL_NAME, "experiments", PROMPT_FILE)
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
        print(f"[OK] Successfully read prompt from: {prompt_path}")
    except FileNotFoundError:
        print(f"[Error] Prompt file not found at: {prompt_path}")
        print("Please ensure you are running this script from the project root directory.")
        return
    except Exception as e:
        print(f"[Error] Failed to read prompt file: {e}")
        return

    # 3. 初始化模型
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        print(f"[OK] Initialized model: {MODEL_NAME}")
    except Exception as e:
        print(f"[Error] Failed to initialize model: {e}")
        return

    # 4. 執行 API 呼叫並計時
    print("\n[IN PROGRESS] Calling the Gemini API... (This may take several minutes)")
    
    start_time = time.perf_counter()
    
    try:
        response = model.generate_content(prompt_content)
        
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print("Test Complete!")
        print("="*60)
        print("[OK] API call was successful.")
        print(f"[Result] Total time spent on the API call: {duration:.2f} seconds")
        
    except Exception as e:
        end_time = time.perf_counter()
        duration = end_time - start_time
        print("\n" + "="*60)
        print("Test Failed!")
        print("="*60)
        print(f"[Error] An error occurred during the API call after {duration:.2f} seconds.")
        print(f"Error details: {e}")


if __name__ == "__main__":
    main()
