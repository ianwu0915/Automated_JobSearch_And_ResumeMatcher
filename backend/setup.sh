source myenv/bin/activate 
pip install -r requirements.txt
docker compose up -d
cd ..
uvicorn backend.main:app --reload