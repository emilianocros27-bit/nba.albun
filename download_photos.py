#!/usr/bin/env python3
"""
Descarga las fotos de los 150 jugadores desde Wikipedia.
Uso: python3 download_photos.py
Las fotos se guardan en img/players/ y se referencian desde index.html.
"""
import os, json, urllib.request, urllib.parse, time, re

PLAYERS = {
  "Atlanta Hawks":          ["Trae Young","Dejounte Murray","Bogdan Bogdanovic","De'Andre Hunter","Clint Capela"],
  "Boston Celtics":         ["Jayson Tatum","Jaylen Brown","Jrue Holiday","Al Horford","Kristaps Porzingis"],
  "Brooklyn Nets":          ["Mikal Bridges","Cam Thomas","Dennis Schroder","Ben Simmons","Nic Claxton"],
  "Charlotte Hornets":      ["LaMelo Ball","Brandon Miller","Terry Rozier","Miles Bridges","Mark Williams"],
  "Chicago Bulls":          ["Zach LaVine","DeMar DeRozan","Nikola Vucevic","Alex Caruso","Coby White"],
  "Cleveland Cavaliers":    ["Donovan Mitchell","Darius Garland","Evan Mobley","Jarrett Allen","Max Strus"],
  "Detroit Pistons":        ["Cade Cunningham","Jaden Ivey","Bojan Bogdanovic","Isaiah Stewart","James Wiseman"],
  "Indiana Pacers":         ["Tyrese Haliburton","Buddy Hield","Myles Turner","Pascal Siakam","Bennedict Mathurin"],
  "Miami Heat":             ["Jimmy Butler","Bam Adebayo","Tyler Herro","Kyle Lowry","Duncan Robinson"],
  "Milwaukee Bucks":        ["Giannis Antetokounmpo","Damian Lillard","Khris Middleton","Brook Lopez","Bobby Portis"],
  "New York Knicks":        ["Jalen Brunson","Julius Randle","RJ Barrett","Mitchell Robinson","Immanuel Quickley"],
  "Orlando Magic":          ["Paolo Banchero","Franz Wagner","Jalen Suggs","Wendell Carter Jr.","Gary Harris"],
  "Philadelphia 76ers":     ["Joel Embiid","Tyrese Maxey","Kelly Oubre Jr.","Tobias Harris","De'Anthony Melton"],
  "Toronto Raptors":        ["Scottie Barnes","RJ Barrett","Immanuel Quickley","Jakob Poeltl","Gradey Dick"],
  "Washington Wizards":     ["Kyle Kuzma","Bradley Beal","Jordan Poole","Kristaps Porzingis","Daniel Gafford"],
  "Dallas Mavericks":       ["Luka Doncic","Kyrie Irving","Tim Hardaway Jr.","P.J. Washington","Dwight Powell"],
  "Denver Nuggets":         ["Nikola Jokic","Jamal Murray","Michael Porter Jr.","Aaron Gordon","Kentavious Caldwell-Pope"],
  "Golden State Warriors":  ["Stephen Curry","Klay Thompson","Andrew Wiggins","Draymond Green","Jonathan Kuminga"],
  "Houston Rockets":        ["Alperen Sengun","Jalen Green","Fred VanVleet","Dillon Brooks","Jabari Smith Jr."],
  "Los Angeles Clippers":   ["Kawhi Leonard","Paul George","James Harden","Russell Westbrook","Ivica Zubac"],
  "Los Angeles Lakers":     ["LeBron James","Anthony Davis","Austin Reaves","D'Angelo Russell","Rui Hachimura"],
  "Memphis Grizzlies":      ["Ja Morant","Desmond Bane","Jaren Jackson Jr.","Marcus Smart","Vince Williams Jr."],
  "Minnesota Timberwolves": ["Anthony Edwards","Karl-Anthony Towns","Rudy Gobert","Mike Conley","Jaden McDaniels"],
  "New Orleans Pelicans":   ["Zion Williamson","CJ McCollum","Brandon Ingram","Jonas Valanciunas","Herbert Jones"],
  "Oklahoma City Thunder":  ["Shai Gilgeous-Alexander","Jalen Williams","Luguentz Dort","Josh Giddey","Chet Holmgren"],
  "Phoenix Suns":           ["Kevin Durant","Devin Booker","Bradley Beal","Jusuf Nurkic","Eric Gordon"],
  "Portland Trail Blazers": ["Damian Lillard","Scoot Henderson","Jerami Grant","Anfernee Simons","Deandre Ayton"],
  "Sacramento Kings":       ["De'Aaron Fox","Domantas Sabonis","Malik Monk","Kevin Huerter","Harrison Barnes"],
  "San Antonio Spurs":      ["Victor Wembanyama","Devin Vassell","Keldon Johnson","Tre Jones","Jeremy Sochan"],
  "Utah Jazz":              ["Lauri Markkanen","Collin Sexton","Jordan Clarkson","Walker Kessler","John Collins"],
}

WIKI_SEARCH = {
  "Cam Thomas":          "Cam Thomas (basketball)",
  "Brandon Miller":      "Brandon Miller (basketball)",
  "Isaiah Stewart":      "Isaiah Stewart (basketball)",
  "Myles Turner":        "Myles Turner (basketball)",
  "Duncan Robinson":     "Duncan Robinson (basketball)",
  "Jalen Brunson":       "Jalen Brunson (basketball)",
  "Mitchell Robinson":   "Mitchell Robinson (basketball)",
  "Franz Wagner":        "Franz Wagner (basketball)",
  "Gary Harris":         "Gary Harris (basketball)",
  "Paul George":         "Paul George (basketball)",
  "Anthony Davis":       "Anthony Davis (basketball)",
  "Jalen Williams":      "Jalen Williams (basketball)",
  "Eric Gordon":         "Eric Gordon (basketball)",
  "Herbert Jones":       "Herbert Jones (basketball)",
  "Mark Williams":       "Mark Williams (basketball)",
  "Tre Jones":           "Tre Jones (basketball)",
  "John Collins":        "John Collins (basketball)",
}

os.makedirs("img/players", exist_ok=True)

def safe_filename(name):
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name) + ".jpg"

def get_wiki_thumb(player_name):
    search_name = WIKI_SEARCH.get(player_name, player_name)
    title = urllib.parse.quote(search_name.replace(" ", "_"))
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json&pithumbsize=400"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NBAAlbumBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        pages = data["query"]["pages"]
        page = list(pages.values())[0]
        return page.get("thumbnail", {}).get("source", "")
    except Exception as e:
        print(f"  ERROR buscando {player_name}: {e}")
        return ""

def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NBAAlbumBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            with open(filepath, "wb") as f:
                f.write(r.read())
        return True
    except Exception as e:
        print(f"  ERROR descargando: {e}")
        return False

photo_map = {}
all_players = []
for team, players in PLAYERS.items():
    for p in players:
        if p not in all_players:
            all_players.append(p)

print(f"Descargando fotos de {len(all_players)} jugadores...\n")

for i, player in enumerate(all_players):
    fname = safe_filename(player)
    fpath = f"img/players/{fname}"
    if os.path.exists(fpath):
        print(f"[{i+1}/{len(all_players)}] {player} - ya existe")
        photo_map[player] = f"img/players/{fname}"
        continue

    print(f"[{i+1}/{len(all_players)}] {player}...", end=" ", flush=True)
    thumb_url = get_wiki_thumb(player)
    if thumb_url:
        ok = download_image(thumb_url, fpath)
        if ok:
            print(f"OK")
            photo_map[player] = f"img/players/{fname}"
        else:
            print(f"FALLO descarga")
    else:
        print(f"sin foto en Wikipedia")
    time.sleep(0.3)

# Inject LOCAL_PHOTOS into index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

entries = ",\n  ".join(f'"{k}": "{v}"' for k, v in photo_map.items())
new_obj = f"const LOCAL_PHOTOS = {{\n  {entries}\n}};"
html = re.sub(r"const LOCAL_PHOTOS = \{[^}]*\};", new_obj, html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"\nListo! {len(photo_map)}/{len(all_players)} fotos descargadas.")
print("index.html actualizado con las rutas locales.")
print("Abre index.html en el navegador.")
