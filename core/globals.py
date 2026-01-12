# -*- coding: utf-8 -*-
"""
=============================================================================
Module Name: globals.py
Description: 全域變數定義檔
             用於存放跨模組共用的變數 (如 TASK_QUEUES)，以解決 Circular Import 問題
Version: V2.0 (Refactored)
Maintainer: Math AI Team
=============================================================================
"""
import queue

# 用於暫存正在執行的任務佇列 (簡易版 In-memory store)
# Key: task_id, Value: queue.Queue
TASK_QUEUES = {}