# -*- coding: utf-8 -*-
"""
性能測試腳本 - Code Generator 優化驗證
用於測試優化後的 code_generator.py 性能提升

測試方法：
1. 選擇一個 skill_id
2. 運行 10 次代碼生成
3. 記錄平均時間、最小時間、最大時間
4. 對比優化前後的數據

預期結果：
- 平均執行時間從 300 秒降至 105-170 秒
- Regex 操作時間減少 20-30%
- 函數清洗時間減少 15-20%
"""

import time
import sys
import os
from statistics import mean, stdev

# 添加專案根目錄到 path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from models import db
from config import Config
from core.code_generator import auto_generate_skill_code

def create_test_app():
    """創建測試用的 Flask app"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def test_performance(skill_id, iterations=5):
    """
    測試指定 skill 的代碼生成性能
    
    Args:
        skill_id: 技能 ID
        iterations: 測試次數（默認 5 次，避免過長時間）
    
    Returns:
        dict: 包含平均時間、標準差等統計信息
    """
    app = create_test_app()
    
    print(f"{'='*80}")
    print(f"開始性能測試：Skill ID = {skill_id}")
    print(f"測試次數：{iterations}")
    print(f"{'='*80}\n")
    
    times = []
    
    with app.app_context():
        for i in range(iterations):
            print(f"\n[測試 {i+1}/{iterations}] 開始生成代碼...")
            start_time = time.time()
            
            try:
                success, message, stats = auto_generate_skill_code(skill_id)
                duration = time.time() - start_time
                times.append(duration)
                
                print(f"  ✅ 完成：{duration:.2f} 秒")
                print(f"     成功：{success}")
                print(f"     Tokens：{stats.get('tokens', 'N/A')}")
                print(f"     修復次數：{stats.get('fixes', 'N/A')}")
                
            except Exception as e:
                duration = time.time() - start_time
                print(f"  ❌ 錯誤：{duration:.2f} 秒")
                print(f"     例外：{str(e)}")
                # 即使失敗也記錄時間
                times.append(duration)
    
    # 統計分析
    if times:
        avg_time = mean(times)
        min_time = min(times)
        max_time = max(times)
        std_time = stdev(times) if len(times) > 1 else 0
        
        print(f"\n{'='*80}")
        print(f"性能測試結果")
        print(f"{'='*80}")
        print(f"  平均時間：{avg_time:.2f} 秒")
        print(f"  最小時間：{min_time:.2f} 秒")
        print(f"  最大時間：{max_time:.2f} 秒")
        print(f"  標準差：  {std_time:.2f} 秒")
        print(f"{'='*80}\n")
        
        # 對比分析（假設優化前為 300 秒）
        baseline = 300.0
        improvement = ((baseline - avg_time) / baseline) * 100
        
        print(f"對比優化前（假設 {baseline:.0f} 秒）：")
        if avg_time < baseline:
            print(f"  🎉 性能提升：{improvement:.1f}%")
            print(f"  ⏱️  節省時間：{baseline - avg_time:.1f} 秒")
        else:
            print(f"  ⚠️  性能下降：{abs(improvement):.1f}%")
        
        return {
            'avg': avg_time,
            'min': min_time,
            'max': max_time,
            'std': std_time,
            'improvement': improvement if avg_time < baseline else -abs(improvement)
        }
    else:
        print("\n❌ 沒有有效的測試數據")
        return None

def quick_test():
    """快速測試（僅 1 次）"""
    print("快速測試模式：僅運行 1 次生成\n")
    
    # 這裡替換為您的測試 skill_id
    test_skill_id = "jh_數學1上_MixedIntegerAdditionAndSubtraction"
    
    app = create_test_app()
    with app.app_context():
        from models import SkillInfo
        skill = SkillInfo.query.filter_by(skill_id=test_skill_id).first()
        
        if not skill:
            print(f"❌ 找不到 Skill ID: {test_skill_id}")
            print("請修改腳本中的 test_skill_id 為您的有效技能ID")
            return
        
        print(f"測試技能：{skill.skill_ch_name} ({test_skill_id})\n")
        
        start = time.time()
        success, msg, stats = auto_generate_skill_code(test_skill_id)
        duration = time.time() - start
        
        print(f"\n{'='*80}")
        print(f"快速測試結果")
        print(f"{'='*80}")
        print(f"  執行時間：{duration:.2f} 秒")
        print(f"  成功：    {success}")
        print(f"  訊息：    {msg}")
        print(f"  Tokens：  {stats.get('tokens', 'N/A')}")
        print(f"  修復次數：{stats.get('fixes', 'N/A')}")
        print(f"{'='*80}\n")
        
        if duration < 300:
            improvement = ((300 - duration) / 300) * 100
            print(f"🎉 相比優化前（300秒），性能提升 {improvement:.1f}%")
        else:
            print(f"⚠️  執行時間超過預期")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Code Generator 性能測試工具')
    parser.add_argument('--skill-id', type=str, help='要測試的技能 ID')
    parser.add_argument('--iterations', type=int, default=5, help='測試次數（默認5次）')
    parser.add_argument('--quick', action='store_true', help='快速測試模式（僅1次）')
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test()
    elif args.skill_id:
        test_performance(args.skill_id, args.iterations)
    else:
        print("使用方法：")
        print("  1. 快速測試：    python test_performance.py --quick")
        print("  2. 完整測試：    python test_performance.py --skill-id <ID> --iterations 5")
        print("\n範例：")
        print("  python test_performance.py --quick")
        print("  python test_performance.py --skill-id jh_數學1上_IntegerAddition --iterations 3")
