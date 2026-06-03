import requests
from bs4 import BeautifulSoup
import json
import re
from collections import defaultdict
from datetime import datetime

def generer_statistiques_pays():
    url = "https://live-tennis.eu/en/atp-live-ranking"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"
    }

    print("Téléchargement de la page...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur d'accès : {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    stats_pays = defaultdict(lambda: {"points": 0, "joueurs": 0})

    rows = soup.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 5:
            
            # 1. Trouver le pays
            pays = None
            for cell in cells:
                txt = cell.text.strip()
                if len(txt) == 3 and txt.isupper() and txt.isalpha():
                    pays = txt
                    break
                a_tag = cell.find('a')
                if a_tag and '/country/' in a_tag.get('href', ''):
                    pays = a_tag.text.strip()
                    break
            
            # 2. Trouver les points de manière ultra-robuste
            points = None
            if pays:
                # On cherche la cellule qui contient les points (souvent la 5ème ou 6ème cellule)
                # On nettoie tout sauf les chiffres pour analyser
                for cell in cells:
                    cell_txt = "".join(cell.text.split()).replace(',', '').replace('.', '')
                    
                    # Si la cellule contient des chiffres
                    if cell_txt.isdigit():
                        val = int(cell_txt)
                        # Les points du Top 1000 sont > 20 et excluent l'âge (souvent < 45)
                        if 20 <= val <= 20000:
                            # Double sécurité : on évite de confondre avec la cellule de l'âge
                            # L'âge est souvent juste avant le pays ou contient une petite valeur
                            if val != int(cells[0].text.strip().split('.')[0] if '.' in cells[0].text else 9999):
                                points = val
                
                # Extraction de secours par Regex si le texte est collé (ex: "20-1")
                if not points:
                    for cell in cells:
                        match = re.search(r'^(\d+)(?:[-+ ]|$)', cell.text.strip())
                        if match:
                            val = int(match.group(1))
                            if 20 <= val <= 20000:
                                points = val
                                break

            # 3. Accumulation
            if pays and points and len(pays) == 3:
                stats_pays[pays]["points"] += points
                stats_pays[pays]["joueurs"] += 1

    # Tri par points décroissants
    stats_triees = dict(sorted(stats_pays.items(), key=lambda item: item[1]['points'], reverse=True))

    resultat = {
        "derniere_mise_a_jour": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "donnees": stats_triees
    }

    with open('stats_tennis_pays.json', 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)
    
    print(f"Fichier écrit. Nombre de pays : {len(stats_triees)}. Exemple ITA : {stats_triees.get('ITA')}")

if __name__ == "__main__":
    generer_statistiques_pays()
