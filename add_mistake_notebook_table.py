from app import app, db
from models import MistakeNotebookEntry # 只需要導入 MistakeNotebookEntry

with app.app_context():
    # 檢查表格是否已經存在，如果不存在才建立
    inspector = db.inspect(db.engine)
    if not inspector.has_table(MistakeNotebookEntry.__tablename__):
        print(f"正在建立 {MistakeNotebookEntry.__tablename__} 表格...")
        MistakeNotebookEntry.__table__.create(db.engine)
        print(f"{MistakeNotebookEntry.__tablename__} 表格建立成功！")
    else:
        print(f"{MistakeNotebookEntry.__tablename__} 表格已存在，跳過建立。")

    print("資料庫更新完成，新的錯題本表格已加入。")
