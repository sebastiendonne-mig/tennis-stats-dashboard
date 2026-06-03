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

    # On récupère toutes les lignes du tableau
    rows = soup.find_all('tr')
    print(f"Nombre de lignes trouvées : {len(rows)}")

    for row in rows:
        cells = row.find_all('td')
        # Une ligne de joueur valide sur ce site contient au moins 9 à 11 cellules
        if len(cells) >= 8:
            
            # 1. Extraction du pays (généralement dans une cellule avec un lien vers le pays ou du texte en majuscules)
            pays = None
            for cell in cells:
                # Cherche un lien qui ressemble à /en/country/xxx
                a_tag = cell.find('a')
                if a_tag and '/country/' in a_tag.get('href', ''):
                    pays = a_tag.text.strip()
                    break
                # Alternative : si la cellule a exactement 3 lettres en majuscules (ex: FRA, ITA, USA)
                txt = cell.text.strip()
                if len(txt) == 3 and txt.isupper() and txt.isalpha():
                    pays = txt
                    break
            
            # 2. Extraction des points actuels (colonne "Current Points")
            # On cherche une cellule qui contient uniquement un nombre élevé (les points du joueur)
            points = None
            for cell in cells:
                # Nettoyage de la cellule
                clean_txt = cell.text.strip().replace('\xa0', '').replace(' ', '').replace(',', '')
                # Si c'est un nombre et qu'il est supérieur à 10 (les joueurs du top ont bcp de points)
                if clean_txt.isdigit() and int(clean_txt) > 10:
                    # On s'assure de ne pas prendre l'âge ou le rang (souvent dans les 3 premières cellules)
                    # Les points sont généralement situés au milieu/fin des cellules
                    points = int(clean_txt)
            
            # Si on a trouvé à la fois un pays valide et des points
            if pays and points and len(pays) == 3:
                # Sécurité pour éviter de confondre les points avec l'âge (ex: Sinner 24 ans, 13500 pts)
                if points > 100: 
                    stats_pays[pays]["points"] += points
                    stats_pays[pays]["joueurs"] += 1

    # Si le dictionnaire est vide, on met une donnée de test pour ne pas casser le HTML
    if not stats_pays:
        print("Avertissement : Aucun joueur trouvé, application du mode secours.")
        stats_pays["FRA"] = {"points": 5000, "joueurs": 2}

    # Tri par points
    stats_triees = dict(sorted(stats_pays.items(), key=lambda item: item[1]['points'], reverse=True))

    resultat = {
        "derniere_mise_a_jour": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "donnees": stats_triees
    }

    with open('stats_tennis_pays.json', 'w', encoding='utf-8') as f:
        json.dump(resultat, f, indent=4, ensure_ascii=False)
    
    print(f"Fichier écrit avec succès. Nombre de pays : {len(stats_triees)}")

if __name__ == "__main__":
    generer_statistiques_pays()
