from abc import ABC, abstractmethod
import time
import random
import logging
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollecteurBase(ABC):
    """Classe abstraite pour tous les collecteurs de sites e-commerce"""
    
    def __init__(self, nom_site):
        self.nom_site = nom_site
        self.ua = UserAgent()
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
                    logger.info(f"[{self.nom_site}] Collecte {produit['nom']}...")
                    
                    # Simulation de latence réseau
                    time.sleep(random.uniform(1, 3))
                    
                    # Appel spécifique au site
                    resultat = self.get_prix_produit(produit)
                    
                    # Ajout des métadonnées
                    resultat.update({
                        "site": self.nom_site,
                        "produit": produit["nom"],
                        "code_produit": produit["code"],
                        "timestamp": time.time()
                    })
                    
                    self.donnees_collectees.append(resultat)
                    logger.info(f"✓ {produit['nom']} : {resultat.get('prix', 'N/A')} €")
                    break
                    
                except Exception as e:
                    logger.error(f"❌ Tentative {tentative+1}/{max_retries} échouée: {e}")
                    if tentative == max_retries - 1:
                        # Valeur par défaut en cas d'échec total
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
                    time.sleep(2 ** tentative)  # Backoff exponentiel
        
        return self.donnees_collectees