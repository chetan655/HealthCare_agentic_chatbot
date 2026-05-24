install:
	pip install -r requirements.txt

run:
	uvicorn rag_workflow.app:app --reload

