import requests
from bs4 import BeautifulSoup
import json
from collections import defaultdict
from datetime import datetime

def generer_statistiques_pays():
    url = "https://live-tennis.eu/en/atp-live-ranking"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9"
    }

    print("Téléchargement de la page Live-Tennis...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur d'accès au site : {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    stats_pays = defaultdict(lambda: {"points": 0, "joueurs": 0})

    # Liste officielle des codes pays ATP à 3 lettres pour filtrer les tr
    codes_atp = {'ITA', 'USA', 'ESP', 'FRA', 'ARG', 'GER', 'AUS', 'CZE', 'RUS', 'GBR', 
                 'CAN', 'SRB', 'BEL', 'KAZ', 'JPN', 'BRA', 'NED', 'CRO', 'NOR', 'CHI', 
                 'SUI', 'POR', 'AUT', 'MON', 'CHN', 'HUN', 'POL', 'PER', 'DEN', 'SVK', 
                 'GRE', 'BIH', 'TWN', 'BOL', 'EST', 'PAR', 'LTU', 'ROU', 'RSA', 'BUL', 
                 'HKG', 'UKR', 'COL', 'FIN', 'SWE', 'GEO', 'ECU', 'TUN', 'TUR', 'KOR', 
                 'LUX', 'IND', 'MEX', 'URU', 'THA', 'JAM', 'CIV', 'UZB', 'JOR', 'LAT', 
                 'MKD', 'DOM', 'SLO', 'MDA', 'LBN', 'IRL', 'NZL', 'MAR', 'ZIM', 'BLR', 'NMI', 'CYP', 'CRC', 'SEN', 'IRI'}

    # On récupère toutes les lignes de tableau (tr) de la page
    rows = soup.find_all('tr')
    
    for row in rows:
        # On récupère les classes de la ligne (ex: ['ITA', 'of1'] ou ['FRA', 'of2', 'dn'])
        row_classes = row.get('class', [])
        
        if row_classes:
            # La première classe correspond TOUJOURS au code pays du joueur sur ce site
            potentiel_pays = row_classes[0].upper()
            
            if potentiel_pays in codes_atp:
                cells = row.find_all('td')
                # Une ligne de joueur valide contient de nombreuses cellules (au moins 7)
                if len(cells) >= 7:
                    try:
                        # Le nom du joueur est dans la cellule avec la classe 'pn'
                        player_name = row.find('td', class_='pn')
                        
                        # La cellule des points est la 7ème cellule de la ligne (index 6)
                        # On extrait uniquement les chiffres pour éviter les bugs de formatage
                        raw_points = "".join(char for char in cells[6].text if char.isdigit())
                        
                        if player_name and raw_points:
                            points = int(raw_points)
                            
                            # Validation finale de sécurité sur la cohérence des points
                            if 15 <= points <= 25000:
                                stats_pays[potentiel_pays]["points"] += points
                                stats_pays[potentiel_pays]["joueurs"] += 1
                    except (IndexError, ValueError):
                        continue

    # Tri des pays par points décroissants
    stats_triees = dict(sorted(stats_pays.items(), key=lambda item: item[1]['points'], reverse=True))

    resultat = {
        "derniere_mise_a_jour": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "donnees": stats_triees
    }

    # Sauvegarde du fichier JSON
    with open('stats_tennis_pays.json', 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)
    
    print(f"Scraping réussi ! Italie : {stats_triees.get('ITA')}")

if __name__ == "__main__":
    generer_statistiques_pays()
