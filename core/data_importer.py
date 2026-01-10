# -*- coding: utf-8 -*-
# ==============================================================================
# ID: core/data_importer.py
# Version: v9.0 (Science Fair Data-Driven Edition)
# Last Updated: 2026-01-10
# Author: Math-Master AI Dev Team
#
# Description:
#   Universal Data Import Module for the Math-Master AI Platform.
#   This module handles bulk data ingestion from Excel (.xlsx) files into the 
#   SQLite database using Pandas and SQLAlchemy.
#
#   [v9.0 Upgrade Highlights]:
#   1. Dynamic Model Discovery: Replaced hardcoded model mapping with SQLAlchemy
#      Registry scanning (Reflection). This allows the importer to automatically 
#      recognize new V9.0 tables (e.g., SkillGenCodePrompt) without code changes.
#   2. Fuzzy Matching: Implemented case-insensitive matching between Excel sheet
#      names and Database table names (e.g., Sheet 'Users' maps to Table 'users').
#   3. Smart Upsert: Uses `db.session.merge` to support both inserting new records
#      and updating existing ones based on Primary Keys.
#   4. Robustness: Added comprehensive error handling and detailed result logging
#      for better troubleshooting during the migration phase.
# ==============================================================================
import pandas as pd
import os
import logging
import traceback
from models import db

# 設定 Logger
logger = logging.getLogger(__name__)

def get_model_mapping():
    """
    動態獲取所有 SQLAlchemy Model 的對照表
    不再需要手動維護 {'table_name': ModelClass} 字典
    
    Returns: 
        dict: { 'table_name': ModelClass }
    """
    mapping = {}
    try:
        # 方法 A: 針對 SQLAlchemy 1.4+ / Flask-SQLAlchemy 3.x (較新版本)
        # db.Model.registry.mappers 會包含所有已註冊的模型
        if hasattr(db.Model, 'registry'):
            for mapper in db.Model.registry.mappers:
                cls = mapper.class_
                if hasattr(cls, '__tablename__'):
                    mapping[cls.__tablename__] = cls
        
        # 方法 B: 針對舊版 SQLAlchemy 或特殊情況 (Fallback)
        # 如果方法 A 抓不到，嘗試遞迴抓取 db.Model 的所有子類別
        if not mapping:
            def get_all_subclasses(cls):
                all_subclasses = []
                for subclass in cls.__subclasses__():
                    all_subclasses.append(subclass)
                    all_subclasses.extend(get_all_subclasses(subclass))
                return all_subclasses

            for cls in get_all_subclasses(db.Model):
                if hasattr(cls, '__tablename__'):
                    mapping[cls.__tablename__] = cls
        
        # Debug: 印出偵測到的模型，方便開發者確認
        # print(f"DEBUG: Detected Models: {list(mapping.keys())}")
                    
    except Exception as e:
        logger.error(f"Error generating model mapping: {e}")
        
    return mapping

def import_excel_to_db(filepath):
    """
    讀取 Excel 檔案，將每個 Sheet 的資料匯入對應的資料庫 Table (支援 Upsert)
    """
    if not os.path.exists(filepath):
        return False, "❌ 檔案不存在"

    try:
        # 1. 讀取 Excel 檔案 (取得所有 Sheet 的資料)
        xls = pd.read_excel(filepath, sheet_name=None, engine='openpyxl')
        
        # 動態取得對照表
        mapping = get_model_mapping()
        
        if not mapping:
            return False, "❌ 系統無法偵測到任何資料庫模型 (Model Mapping is empty)。"

        results = []
        results.append(f"ℹ️ 系統動態偵測到 {len(mapping)} 個資料庫模型。")
        
        # 2. 遍歷每一個 Sheet
        for sheet_name, df in xls.items():
            sheet_name_clean = sheet_name.strip()
            
            # 尋找對應的 Model
            model = None
            table_name = None

            # 2.1 精確比對
            if sheet_name_clean in mapping:
                model = mapping[sheet_name_clean]
                table_name = sheet_name_clean
            else:
                # 2.2 模糊比對 (忽略大小寫)
                # 例如 Excel Sheet 是 "Users"，但資料庫 Table 是 "users"
                for tbl_name, model_cls in mapping.items():
                    if tbl_name.lower() == sheet_name_clean.lower():
                        model = model_cls
                        table_name = tbl_name
                        break
            
            if not model:
                results.append(f"⚠️ 跳過 Sheet '{sheet_name}': 資料庫中無此 Table。")
                continue
            
            # 3. 資料處理 (Data Cleaning)
            # 將 pandas 的 NaN (空值) 轉為 Python 的 None
            df = df.where(pd.notnull(df), None)
            
            # 取得該 Model 的所有欄位名稱
            model_columns = model.__table__.columns.keys()
            
            imported_count = 0
            skipped_count = 0
            
            # 4. 逐列寫入資料庫
            for index, row in df.iterrows():
                try:
                    data = {}
                    # 只讀取 Model 裡有的欄位，忽略 Excel 裡多餘的欄位
                    for col in model_columns:
                        if col in row:
                            val = row[col]
                            
                            # 特殊處理：布林值字串轉換
                            if isinstance(val, str):
                                if val.lower() == 'true': val = True
                                elif val.lower() == 'false': val = False
                            
                            data[col] = val
                    
                    if not data:
                        skipped_count += 1
                        continue

                    # 使用 merge (UPSERT): 有 Primary Key 就更新，沒有就新增
                    instance = model(**data)
                    db.session.merge(instance)
                    imported_count += 1
                    
                except Exception as e:
                    print(f"❌ Error inserting row {index} in {sheet_name}: {e}")
                    continue
            
            results.append(f"✅ Table '{table_name}': 成功匯入/更新 {imported_count} 筆。")

        # 5. 提交變更
        db.session.commit()
        return True, "\n".join(results)

    except Exception as e:
        db.session.rollback()
        error_msg = f"❌ 匯入失敗: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return False, f"匯入發生錯誤: {str(e)}"