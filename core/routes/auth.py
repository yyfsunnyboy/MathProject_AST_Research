# -*- coding: utf-8 -*-
"""
=============================================================================
Module Name: auth.py
Description: 驗證與權限管理模組
             負責定義全域的登入檢查邏輯 (@before_request)
             確保未登入使用者無法存取核心功能
Version: V2.0 (Refactored)
Maintainer: Math AI Team
=============================================================================
"""
from flask import Blueprint

# 定義 Blueprints
# 注意：我們保留原本的 'core' 名稱，這樣你的 HTML template (url_for('core.xxx')) 都不用改，直接相容！
core_bp = Blueprint('core', __name__, template_folder='../../templates')
practice_bp = Blueprint('practice', __name__)

# 匯入各個模組以註冊路由
# 順序很重要：先定義好 Blueprint (上面)，再匯入使用它們的模組 (下面)
from . import auth, admin, practice, classroom, analysis