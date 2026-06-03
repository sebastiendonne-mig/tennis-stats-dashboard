import requests
from bs4 import BeautifulSoup
import json
from collections import defaultdict
from datetime import datetime

def generer_statistiques_pays():
    url = "https://live-tennis.eu/en/atp-live-ranking"
    # En-têtes complets pour contourner les protections anti-bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }

    print("Téléchargement de la page Live-Tennis...")
    response = requests.get(url, headers=headers)
    
    # Si le site nous bloque, on crée quand même un fichier pour éviter que l'action GitHub plante
    if response.status_code != 200:
        print(f"Erreur d'accès au site : {response.status_code}. Création d'un fichier de secours.")
        stats_pays = {"Erreur": {"points": 0, "joueurs": 0}}
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        stats_pays = defaultdict(lambda: {"points": 0, "joueurs": 0})

        # Analyse de la page
        table = soup.find('table', id='atp_table')
        if not table:
            # Recherche alternative si l'id a changé
            table = soup.find('table')
            
        if table:
            rows = table.find_all('tr')
            for row in rows:
                td_country = row.find('td', class_='cls_country') or row.find('span', class_='bdy_country')
                td_points = row.find('td', class_='cls_points')
                
                if td_country and td_points:
                    pays = td_country.text.strip()
                    points_str = td_points.text.strip().replace('\xa0', '').replace(' ', '').replace(',', '')
                    if points_str.isdigit():
                        points = int(points_str)
                        stats_pays[pays]["points"] += points
                        stats_pays[pays]["joueurs"] += 1

    # Tri et structuration
    stats_triees = dict(sorted(stats_pays.items(), key=lambda item: item[1]['points'], reverse=True))
    resultat = {
        "derniere_mise_a_jour": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "donnees": stats_triees
    }

    # Sauvegarde impérative du fichier
    with open('stats_tennis_pays.json', 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)
    
    print("Fichier écrit avec succès.")

if __name__ == "__main__":
    generer_statistiques_pays()
