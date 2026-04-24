# collecteur/fnac.py
from .base import CollecteurBase
import random

class CollecteurFnac(CollecteurBase):
    def __init__(self):
        super().__init__("Fnac")
    
    def get_prix_produit(self, produit_info):
        # Prix différents pour chaque site (réalisme concurrentiel)
        prix_base = {
            "iPhone 13": 699,
            "Samsung Galaxy S23": 769,
            "AirPods Pro 2": 239,
            "MacBook Air M2": 1199,
            "Smart TV 55\" 4K": 579
        }
        
        prix_actuel = prix_base.get(produit_info["nom"], 500)
        
        # 15% de chance de promotion Fnac
        en_promo = random.random() < 0.15
        
        if en_promo:
            reduction = random.uniform(0.1, 0.3)  # Promos plus fortes à la Fnac
            prix_promo = round(prix_actuel * (1 - reduction), 2)
            promotion = f"-{int(reduction*100)}% + fidélité"
            prix_final = prix_promo
        else:
            promotion = None
            prix_final = prix_actuel
        
        disponible = random.random() < 0.9  # Un peu moins dispo qu'Amazon
        
        return {
            "prix": prix_final,
            "prix_original": prix_actuel,
            "promotion": promotion,
            "disponible": disponible,
            "stock": random.randint(0, 50) if disponible else 0
        }