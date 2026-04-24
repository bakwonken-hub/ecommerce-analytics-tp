# Configuration centralisée
PRODUITS = [
    {"nom": "iPhone 13", "code": "IP13", "prix_attendu": 700},
    {"nom": "Samsung Galaxy S23", "code": "SGS23", "prix_attendu": 800},
    {"nom": "AirPods Pro 2", "code": "APP2", "prix_attendu": 250},
    {"nom": "MacBook Air M2", "code": "MBA2", "prix_attendu": 1200},
    {"nom": "Smart TV 55\" 4K", "code": "TV55", "prix_attendu": 600},
]

SITES = ["Amazon", "Fnac", "Darty"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

REQUETE_TIMEOUT = 10
MAX_RETRIES = 3
DELAY_ENTRE_REQUETES = 1
