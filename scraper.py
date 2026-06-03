import requests
from bs4 import BeautifulSoup
import json
from collections import defaultdict
from datetime import datetime

def generer_statistiques_pays():
    url = "https://live-tennis.eu/en/atp-live-ranking"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("Téléchargement de la page Live-Tennis...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur d'accès au site : {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    stats_pays = defaultdict(lambda: {"points": 0, "joueurs": 0})

    # Cibler le tableau principal
    table = soup.find('table', id='atp_table')
    if not table:
        print("Erreur : Impossible de trouver le tableau '#atp_table'.")
        return

    rows = table.find_all('tr')
    for row in rows:
        # Recherche des cellules contenant le pays et les points
        # Sur live-tennis, elles ont souvent des classes spécifiques à inspecter, ou sont identifiables
        td_country = row.find('td', class_='cls_country') or row.find('span', class_='bdy_country')
        td_points = row.find('td', class_='cls_points')
        
        if td_country and td_points:
            # Récupère le code du pays (ex: FRA, ITA)
            pays = td_country.text.strip()
            
            # Nettoie la chaîne de caractères des points
            points_str = td_points.text.strip().replace('\xa0', '').replace(' ', '').replace(',', '')
            
            if points_str.isdigit():
                points = int(points_str)
                stats_pays[pays]["points"] += points
                stats_pays[pays]["joueurs"] += 1

    # Trier le dictionnaire par le nombre de points décroissant
    stats_triees = dict(sorted(stats_pays.items(), key=lambda item: item[1]['points'], reverse=True))

    # Structurer le résultat final
    resultat = {
        "derniere_mise_a_jour": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "donnees": stats_triees
    }

    # Sauvegarder localement dans le dossier de l'Action GitHub
    with open('stats_tennis_pays.json', 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)
    
    print(f"Calcul terminé. {len(stats_triees)} pays enregistrés.")

if __name__ == "__main__":
    generer_statistiques_pays()
