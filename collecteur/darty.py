# collecteur/darty.py
from .base import CollecteurBase
import random

class CollecteurDarty(CollecteurBase):
    def __init__(self):
        super().__init__("Darty")
    
    def get_prix_produit(self, produit_info):
        prix_base = {
            "iPhone 13": 689,
            "Samsung Galaxy S23": 759,
            "AirPods Pro 2": 235,
            "MacBook Air M2": 1179,
            "Smart TV 55\" 4K": 565
        }
        
        prix_actuel = prix_base.get(produit_info["nom"], 500)
        
        # 25% de chance de promotion Darty
        en_promo = random.random() < 0.25
        
        if en_promo:
            reduction = random.uniform(0.05, 0.2)
            prix_promo = round(prix_actuel * (1 - reduction), 2)
            promotion = f"-{int(reduction*100)}% + livraison offerte"
            prix_final = prix_promo
        else:
            promotion = None
            prix_final = prix_actuel
        
        disponible = random.random() < 0.92
        
        return {
            "prix": prix_final,
            "prix_original": prix_actuel,
            "promotion": promotion,
            "disponible": disponible,
            "garantie": "2 ans offerte" if disponible else None
        }