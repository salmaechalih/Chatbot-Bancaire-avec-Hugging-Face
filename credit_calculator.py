class CreditCalculator:
    def __init__(self, montant, duree_annees, taux_annuel):
        self.montant = montant
        self.duree_annees = duree_annees
        self.taux_annuel = taux_annuel

    def simulate_credit(self, capital=None, duration_years=None, credit_type=None, with_insurance=False):
        # Utilise les valeurs par défaut de l'objet si aucun paramètre n'est passé
        montant = capital if capital is not None else self.montant
        duree_annees = duration_years if duration_years is not None else self.duree_annees
        taux_annuel = self.taux_annuel  # tu peux adapter selon credit_type

        # Calcul
        taux_mensuel = taux_annuel / 12 / 100
        n = duree_annees * 12
        mensualite = montant * taux_mensuel / (1 - (1 + taux_mensuel) ** -n)
        total = mensualite * n
        interets = total - montant

        return {
            "mensualite": round(mensualite, 2),
            "total_rembourse": round(total, 2),
            "interets": round(interets, 2)
        }

    def format_simulation_result(self, simulation):
        return (
            f"💰 Mensualité : {simulation['mensualite']} €\n"
            f"💵 Total remboursé : {simulation['total_rembourse']} €\n"
            f"📊 Intérêts : {simulation['interets']} €"
        )
    def calculer_taeg(self, montant, duree_annees, taux_annuel, frais_dossier=0, assurance_mensuelle=0):
        taux_mensuel = taux_annuel / 12 / 100
        n = duree_annees * 12
        mensualite_hors_frais = montant * taux_mensuel / (1 - (1 + taux_mensuel) ** -n)
        mensualite_totale = mensualite_hors_frais + assurance_mensuelle
        total_paye = mensualite_totale * n + frais_dossier
    # Ici, formule simplifiée du TAEG
        taeg = ((total_paye / montant) ** (1 / duree_annees) - 1) * 100
        return round(taeg, 2)
    

