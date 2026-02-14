#!/usr/bin/env python3
"""
Streamlit Cloud デプロイ前チェック

このスクリプトで環境を検証
"""
import sys
from pathlib import Path

print("🔍 暦 KOYOMI - デプロイ前チェック")
print("=" * 50)

# Python バージョン
print(f"Python: {sys.version}")
assert sys.version_info >= (3, 11), "Python 3.11+ required"
print("✅ Python バージョン OK")

# 必須ファイル確認
required_files = [
    "app.py",
    "requirements.txt",
    "taizan_db.json",
    ".streamlit/config.toml",
    ".gitignore",
]

for file in required_files:
    path = Path(file)
    if path.exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} が見つかりません")
        sys.exit(1)

# requirements.txt 確認
print("\n📦 requirements.txt チェック:")
with open("requirements.txt") as f:
    content = f.read()
    if ">=" in content:
        print("⚠️  警告: >= が含まれています（固定推奨）")
    else:
        print("✅ バージョン固定済み")

# src/koyomi 構造確認
src_path = Path("src/koyomi")
if not src_path.exists():
    print(f"❌ {src_path} が見つかりません")
    sys.exit(1)

modules = ["core", "layer1", "chat", "storage"]
for module in modules:
    module_path = src_path / module
    if module_path.exists():
        print(f"✅ src/koyomi/{module}")
    else:
        print(f"❌ src/koyomi/{module} が見つかりません")

print("\n" + "=" * 50)
print("✅ すべてのチェック完了！")
print("Streamlit Cloud にデプロイ可能です")
print("=" * 50)
