from .base import CollecteurBase
import random

class CollecteurAmazon(CollecteurBase):
    def __init__(self):
        super().__init__("Amazon")
    
    def get_prix_produit(self, produit_info):
        prix_base = {
            "iPhone 13": 679,
            "Samsung Galaxy S23": 749,
            "AirPods Pro 2": 229,
            "MacBook Air M2": 1149,
            "Smart TV 55\" 4K": 549
        }
        
        prix_actuel = prix_base.get(produit_info["nom"], 500)
        en_promo = random.random() < 0.2
        
        if en_promo:
            reduction = random.uniform(0.05, 0.25)
            prix_promo = round(prix_actuel * (1 - reduction), 2)
            promotion = f"-{int(reduction*100)}%"
            prix_final = prix_promo
        else:
            promotion = None
            prix_final = prix_actuel
        
        disponible = random.random() < 0.95
        
        return {
            "prix": prix_final,
            "prix_original": prix_actuel,
            "promotion": promotion,
            "disponible": disponible,
            "livraison": "Prime 24h" if disponible else None
        }
