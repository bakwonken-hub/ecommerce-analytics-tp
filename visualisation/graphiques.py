import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

class VisualisateurEcommerce:
    def __init__(self, output_dir="outputs/graphiques"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def barplot_comparatif(self, df):
        pivot = df.pivot_table(index='produit', columns='site', values='prix', aggfunc='first')
        
        plt.figure(figsize=(12, 6))
        pivot.plot(kind='bar')
        plt.title("Comparaison des prix par produit et par site", fontsize=14, fontweight='bold')
        plt.xlabel("Produit", fontsize=12)
        plt.ylabel("Prix (€)", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title="Site")
        plt.tight_layout()
        plt.savefig(self.output_dir / "comparaison_prix.png", dpi=150)
        plt.close()
    
    def boxplot_distribution(self, df):
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x='site', y='prix')
        plt.title("Distribution des prix par site", fontsize=14, fontweight='bold')
        plt.xlabel("Site e-commerce", fontsize=12)
        plt.ylabel("Prix (€)", fontsize=12)
        plt.tight_layout()
        plt.savefig(self.output_dir / "distribution_prix_site.png", dpi=150)
        plt.close()
    
    def heatmap_disponibilite(self, df):
        dispo_matrix = df.groupby(['produit', 'site'])['disponible'].mean().unstack()
        
        plt.figure(figsize=(10, 6))
        sns.heatmap(dispo_matrix, annot=True, cmap='YlOrRd', fmt='.0%')
        plt.title("Taux de disponibilité par produit et site", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / "heatmap_disponibilite.png", dpi=150)
        plt.close()
