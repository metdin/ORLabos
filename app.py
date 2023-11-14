from flask import Flask, render_template, send_file, jsonify, request
from pymongo import MongoClient
import json
import csv

app = Flask(__name__)

#MongoDB connection settings
MONGO_URI = "mongodb://mojaBazaSpremnik:27017/"
DATABASE_NAME = "sportski_klubovi"
COLLECTION_NAME = "klubovi"
filtered_data =[]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/datatable')
def datatable():
    return render_template('datatable.html')

@app.route('/download_csv')
def download_csv():
    csv_filename = "klubovi.csv"
    return send_file(csv_filename, as_attachment=True)

@app.route('/download_json')
def download_json():
    json_filename = "klubovi.json"
    return send_file(json_filename, as_attachment=True)

@app.route('/data')
def get_data():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    data = list(collection.find({}))
    return jsonify(data)


@app.route('/filter_data', methods=['POST'])
def filter_data():
    global filtered_data
    query = request.form.get('query')
    attribute = request.form.get('attribute', '')

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    filter = {}
    if attribute and query:
        filter[attribute] = {"$regex": query, "$options": "i"}  # Case-insensitive regex search
        filtered_data = list(collection.find(filter))
    if attribute == "":
        filtered_data = list(collection.find({ "$text": { "$search": query } }))
    if attribute == "RangNatjecanja":
        int_query = int(query)
        filtered_data = list(collection.find({"RangNatjecanja": int_query}))
    if attribute == "GodinaOsnutka":
        int_query = int(query)
        filtered_data = list(collection.find({"GodinaOsnutka": int_query}))


    #print("Received query:", query, "and attribute:", attribute)
    return jsonify(filtered_data)

@app.route('/export_json', methods=['GET'])
def export_json():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    global filtered_data
    data = filtered_data
    filtered_data = list(collection.find({}))
    with open('filtered_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    return send_file('filtered_data.json', as_attachment=True)

@app.route('/export_csv', methods=['GET'])
def export_csv():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    global filtered_data
    data = filtered_data
    filtered_data = list(collection.find({}))
    with open('filtered_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    with open('filtered_data.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # Create a CSV file and write the data with UTF-8 encoding
    with open('filtered_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write the header
        csv_writer.writerow(
            ['ImeKluba', 'Sport', 'Mjesto', 'Liga', 'RangNatjecanja', 'GodinaOsnutka', 'Predsjednik.Ime',
             'Predsjednik.Prezime', 'Kontakt_Email', 'Kontakt_Telefon', 'Igrač.Ime', 'Igrač.Prezime'])

        # Iterate through each document and write data to CSV
        for document in data:
            players = document.get('Igrači', [])
            for player in players:
                csv_writer.writerow([
                    document.get('ImeKluba', ''),
                    document.get('Sport', ''),
                    document.get('Mjesto', ''),
                    document.get('Liga', ''),
                    document.get('RangNatjecanja', ''),
                    document.get('GodinaOsnutka', ''),
                    document.get('Predsjednik', {}).get('Ime', ''),
                    document.get('Predsjednik', {}).get('Prezime', ''),
                    document.get('Kontakt', {}).get('Email', ''),
                    document.get('Kontakt', {}).get('Telefon', ''),
                    player.get('Ime', ''),
                    player.get('Prezime', '')
                ])
    return send_file('filtered_data.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

