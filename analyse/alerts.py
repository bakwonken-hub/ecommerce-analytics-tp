class SystemeAlertes:
    """Système d'alerte pour les opportunités d'achat"""
    
    @staticmethod
    def check_bonnes_affaires(df, seuil_economie=50):
        """Identifie les produits avec promotion intéressante"""
        df_temp = df[df['promotion'].notna()].copy()
        df_temp['economie'] = df_temp['prix_original'] - df_temp['prix']
        bonnes_affaires = df_temp[df_temp['economie'] >= seuil_economie]
        
        alertes = []
        for _, row in bonnes_affaires.iterrows():
            alertes.append({
                "produit": row['produit'],
                "site": row['site'],
                "prix_actuel": row['prix'],
                "prix_original": row['prix_original'],
                "economie": row['economie'],
                "promotion": row['promotion']
            })
        
        return alertes
    
    @staticmethod
    def check_rupture(df):
        """Alerte sur produits indisponibles importants"""
        ruptures = df[~df['disponible']][['produit', 'site', 'prix_original']]
        return ruptures if not ruptures.empty else None