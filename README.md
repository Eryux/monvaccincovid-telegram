# MonVaccinCovid

Rester informé des créneaux de vaccination disponibles sur Doctolib directement sur Telegram.


### Pré-requis

* Python 3.7


### Installation

* Cloner le répertoire GitHub sur votre machine

* Installer les dépendances python requises `pip install -r requirements.txt` ou `pip3 install -r requirements.txt`

* Créer une base de donnée MySQL ou MariaDB au format InnoDB et exécuter le fichier `database.sql`

* Créer et éditer le fichier `settings.py` (voir exemple)

* Lancer le bot `python app.py` ou `python3 app.py`


### settings.py

Le fichier settings.py est requis pour que le bot fonctionne. Ce fichier n'est pas présent dans le répertoire github, il doit être créé à la racine du projet.

```python
# settings.py

# Database configuration
DATABASE = {
    'host': 'localhost',
    'port': 3306,
    'db': 'vaccincovid',
    'user': 'vaccincovid',
    'password': 'vaccincovid'
}

# Telegram bot token
TELEGRAM_TOKEN = "TELEGRAM BOT TOKEN"

# Day start hour
# default: 7
DAY_HOUR = 7

# Night start hour
# default: 21
NIGHT_HOUR = 22

# Delay between two doctolib fetch in ms
# default: 5000
API_REQUEST_DELAY = 2000

# Delay between two fetch for a same center in seconds for day
# default: 300
CENTER_REQUEST_DELAY_DAY = 5

# Delay between two fetch for a same center in seconds for night
# default: 600
CENTER_REQUEST_DELAY_NIGHT = 5

# Center cache expire in seconds
# default: 1800
CENTER_FETCH_CACHE_EXPIRE = 1800

# Doctolib motive refs
# default: [6970, 7005]
DOCTOLIB_REFS = [6970, 7005]

# Max check per chat
# default: 50
WATCH_LIMIT = 50
```

### Les commandes

`check` Ajouter des centres de vaccination à surveiller

`liste` Lister les centres de vaccination que le bot surveille

`stop` Arrêter la surveillance d'un centre de vaccination

`stopall` Arrêter la surveillance de tous les centres de vaccination