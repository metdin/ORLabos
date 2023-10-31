@echo off

docker exec -d mojaBazaSpremnik mongoexport --db sportski_klubovi --collection klubovi --out pom.json 

docker cp mojaBazaSpremnik:/data/pom.json .

python3 json_to_csv.py

del pom.json

del exported_data_array.json