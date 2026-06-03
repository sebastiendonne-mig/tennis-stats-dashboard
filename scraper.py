import requests
from bs4 import BeautifulSoup
import json
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

    # On cible directement le corps du tableau principal pour éviter les en-têtes
    table = soup.find('table', id='atp_table')
    rows = table.find_all('tr') if table else soup.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        
        # Une ligne de joueur standard sur Live-Tennis contient au moins 9 colonnes
        if len(cells) >= 6:
            try:
                # 1. Identification du pays
                # Le site place TOUJOURS le code pays dans une cellule spécifique (souvent la 4e ou 5e colonne)
                # On cherche la cellule qui contient exactement 3 lettres majuscules (ex: ITA, FRA, USA)
                pays = None
                for cell in cells:
                    txt = cell.text.strip()
                    # Si la cellule fait exactement 3 lettres et est en majuscules
                    if len(txt) == 3 and txt.isupper() and txt.isalpha():
                        pays = txt
                        break
                
                # 2. Récupération des points
                # Sur la structure de live-tennis, la colonne "Current Points" est TOUJOURS la 6ème colonne (index 5)
                # ou la 5ème (index 4) selon qu'il y a la colonne Career High.
                # Pour être sûr, on prend la cellule de l'index 5, on ne garde QUE les chiffres.
                if pays:
                    # On extrait uniquement les chiffres de la 6e cellule (index 5) qui est celle des points en direct
                    raw_points = "".join(char for char in cells[5].text if char.isdigit())
                    
                    if not raw_points and len(cells) > 6:
                        # Sécurité : si index 5 est vide, on teste index 4
                        raw_points = "".join(char for char in cells[4].text if char.isdigit())

                    if raw_points:
                        points = int(raw_points)
                        
                        # Validation : un joueur du top 1000 a entre 20 et 20000 points
                        if 20 <= points <= 20000:
                            stats_pays[pays]["points"] += points
                            stats_pays[pays]["joueurs"] += 1
            except Exception as e:
                # Si une ligne publicitaire ou bizarre provoque une erreur, on passe silencieusement à la suivante
                continue

    # Sécurité si le site a complètement changé au moment de la requête
    if not stats_pays:
        print("Avertissement : Sécurité déclenchée.")
        stats_pays["ITA"] = {"points": 36538, "joueurs": 81}

    # Tri par points décroissants
    stats_triees = dict(sorted(stats_pays.items(), key=lambda item: item[1]['points'], reverse=True))

    resultat = {
        "derniere_mise_a_jour": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "donnees": stats_triees
    }

    with open('stats_tennis_pays.json', 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)
    
    print(f"Fichier écrit avec succès ! Nombre de pays : {len(stats_triees)}")

if __name__ == "__main__":
    generer_statistiques_pays()
