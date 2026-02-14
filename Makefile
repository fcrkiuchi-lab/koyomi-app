.PHONY: help test test-unit test-integration coverage clean install format lint

help:
	@echo "暦 KOYOMI - 開発コマンド"
	@echo ""
	@echo "make install        - 依存パッケージのインストール"
	@echo "make test           - 全テスト実行"
	@echo "make test-unit      - 単体テストのみ実行"
	@echo "make test-integration - 統合テストのみ実行"
	@echo "make coverage       - カバレッジレポート生成"
	@echo "make format         - コードフォーマット（black）"
	@echo "make lint           - コード品質チェック（flake8）"
	@echo "make clean          - キャッシュ・一時ファイル削除"
	@echo "make run            - Streamlit アプリ起動"

install:
	pip install -r requirements.txt --break-system-packages

test:
	pytest -v

test-unit:
	pytest tests/unit -v -m unit

test-integration:
	pytest tests/integration -v -m integration

coverage:
	pytest --cov=src/koyomi --cov-report=html --cov-report=term-missing
	@echo "カバレッジレポート: htmlcov/index.html"

format:
	black src/ tests/ app.py

lint:
	flake8 src/ tests/ app.py --max-line-length=100

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf src/koyomi/__pycache__
	rm -rf tests/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	streamlit run app.py
