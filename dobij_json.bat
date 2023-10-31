@echo off

docker exec -d mojaBazaSpremnik mongoexport --db sportski_klubovi --collection klubovi --out novi_json.json --pretty

docker cp mojaBazaSpremnik:/data/novi_json.json .