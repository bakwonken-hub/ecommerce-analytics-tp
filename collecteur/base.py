from abc import ABC, abstractmethod
import time
import random

class CollecteurBase(ABC):
    """Classe abstraite pour tous les collecteurs de sites e-commerce"""
    
    def __init__(self, nom_site):
        self.nom_site = nom_site
        self.donnees_collectees = []
    
    @abstractmethod
    def get_prix_produit(self, produit_info):
        """Retourne prix, disponibilité, promotion pour un produit donné"""
        pass
    
    def collecter_tous_produits(self, produits, max_retries=3):
        """Méthode robuste avec retry et fallback"""
        for produit in produits:
            for tentative in range(max_retries):
                try:
                    time.sleep(random.uniform(0.5, 1.5))
                    resultat = self.get_prix_produit(produit)
                    
                    resultat.update({
                        "site": self.nom_site,
                        "produit": produit["nom"],
                        "code_produit": produit["code"],
                        "timestamp": time.time()
                    })
                    
                    self.donnees_collectees.append(resultat)
                    break
                    
                except Exception as e:
                    if tentative == max_retries - 1:
                        self.donnees_collectees.append({
                            "site": self.nom_site,
                            "produit": produit["nom"],
                            "code_produit": produit["code"],
                            "prix": None,
                            "disponible": False,
                            "promotion": None,
                            "erreur": str(e),
                            "timestamp": time.time()
                        })
                    time.sleep(2 ** tentative)
        
        return self.donnees_collectees
