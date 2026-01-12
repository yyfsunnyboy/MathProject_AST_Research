"""
=============================================================================
Module Name: __init__.py (Routes Package)
Description: 路由模組初始化
             負責定義 Flask Blueprints (core_bp, practice_bp) 並匯入所有子路由模組
             確保 app.py 能夠一次性註冊所有拆分後的路由
Version: V2.0 (Refactored)
Maintainer: Math AI Team
=============================================================================
"""
from flask import Blueprint
core_bp = Blueprint('core', __name__, template_folder='../../templates')
practice_bp = Blueprint('practice', __name__)

# 這一行會去讀取你的 admin.py
from . import auth, admin, practice, classroom, analysis, exam