import json
import csv

# Load the original JSON data
with open('pom.json', 'r', encoding='utf-8') as json_file:
    data = [json.loads(line) for line in json_file]

# Create an array with a comma delimiter
with open('exported_data_array.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4)

with open('exported_data_array.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Create a CSV file and write the data with UTF-8 encoding
with open('novi_csv.csv', 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write the header
    csv_writer.writerow(['ImeKluba', 'Sport', 'Mjesto', 'Liga', 'RangNatjecanja', 'GodinaOsnutka', 'Predsjednik.Ime', 'Predsjednik.Prezime', 'Kontakt_Email', 'Kontakt_Telefon', 'Igrač.Ime', 'Igrač.Prezime'])

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