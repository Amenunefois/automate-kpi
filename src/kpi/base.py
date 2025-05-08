import pandas as pd

def agregat_par_temps(df, date_col, value_col, niveau='mois'):
    """
    Agrège les valeurs numériques par période de temps.
    :param df: DataFrame contenant les données
    :param date_col: nom de la colonne contenant les dates
    :param value_col: nom de la colonne à agréger
    :param niveau: 'jour', 'semaine', 'mois', 'trimestre', 'annee'
    :return: DataFrame agrégé
    """
    if niveau == 'jour':
        df['Jour'] = df[date_col].dt.date
        group_col = 'Jour'
    elif niveau == 'semaine':
        df['Semaine'] = df[date_col].dt.to_period('W').astype(str)
        group_col = 'Semaine'
    elif niveau == 'mois':
        df['Mois'] = df[date_col].dt.to_period('M').astype(str)
        group_col = 'Mois'
    elif niveau == 'trimestre':
        df['Trimestre'] = df[date_col].dt.to_period('Q').astype(str)
        group_col = 'Trimestre'
    elif niveau == 'annee':
        df['Année'] = df[date_col].dt.year
        group_col = 'Année'
    else:
        raise ValueError("Niveau non supporté")

    return df.groupby(group_col)[value_col].sum().reset_index()
