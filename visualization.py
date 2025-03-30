import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
import os

df = pd.read_csv('dataset.csv', sep='@', encoding='utf-8')

#universe_counts = df['universe'].value_counts()
#plt.pie(universe_counts[universe_counts>10], labels=universe_counts[universe_counts>10].index, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#ffccff'])
#plt.title('Родные вселенные персонажей')
#plt.axis('equal')
#plt.show()

def combine_strings(series):
    combined = ', '.join(set(serie.strip() for serie in series.dropna() if serie.strip()))
    return combined if combined else None

df_fil = df.groupby('character').agg({
    'occupation': combine_strings,  
    'height': 'mean',               
    'weight': 'mean'                
}).reset_index()
df_fil = df_fil.dropna(subset=['occupation', 'height', 'weight'])

def compare_characters(character1, character2):
    data1 = df_fil[df_fil['character'] == character1]
    data2 = df_fil[df_fil['character'] == character2]
    occupation1 = set(data1['occupation'].dropna().values[0].split(',')) if not data1['occupation'].isna().all() else set()
    occupation2 = set(data2['occupation'].dropna().values[0].split(',')) if not data2['occupation'].isna().all() else set()
    common_occupations = occupation1.union(occupation2)
    heights = [data1['height'].values[0], data2['height'].values[0]] if not data1['height'].isna().all() and not data2['height'].isna().all() else [None, None]
    weights = [data1['weight'].values[0], data2['weight'].values[0]] if not data1['weight'].isna().all() and not data2['weight'].isna().all() else [None, None]

    if not common_occupations and all(pd.isna(heights)) and all(pd.isna(weights)):
        print("Недостаточно данных для сравнения всех графиков.")
        return

    if not common_occupations:
        print("Недостаточно данных для графика профессий.")
        return

    if all(pd.isna(heights)):
        print("Недостаточно данных для сравнения роста.")
        return

    if all(pd.isna(weights)):
        print("Недостаточно данных для сравнения веса.")
        return

    fig = plt.figure(figsize=(10, 10))

    axes0 = fig.add_subplot(2, 1, 1)
    axes0.plot(list(common_occupations),
                 [1 if occ in occupation1 else 0 for occ in common_occupations],
                 marker='o', label=character1, color='blue')
    axes0.plot(list(common_occupations),
                 [1 if occ in occupation2 else 0 for occ in common_occupations],
                 marker='o', label=character2, color='orange')
    axes0.set_title('Профессии персонажей')
    axes0.set_ylabel('Принадлежность профессии')
    axes0.set_xticklabels(list(common_occupations), rotation=45)
    axes0.legend()
    axes0.grid()

    axes1 = fig.add_subplot(2, 2, 3)
    axes1.bar([character1, character2], heights, color=['blue', 'orange'])
    axes1.set_title('Сравнение роста персонажей')
    axes1.set_ylabel('Рост (см)')
    axes1.grid()

    axes2 = fig.add_subplot(2, 2, 4)
    axes2.bar([character1, character2], weights, color=['blue', 'orange'])
    axes2.set_title('Сравнение веса персонажей')
    axes2.set_ylabel('Вес (кг)')
    axes2.grid()

    plt.tight_layout()
    plt.show()

character1_widget = widgets.Dropdown(
    options=df_fil['character'].tolist(),
    description='character 1:',
    value=None
)

character2_widget = widgets.Dropdown(
    options=df_fil['character'].tolist(),
    description='character 2:',
    value=None
)

compare_button = widgets.Button(description='Compare')

def on_compare_button_clicked(b):
    clear_output(wait=True)
    display(character1_widget, character2_widget, compare_button)
    compare_characters(character1_widget.value, character2_widget.value)

compare_button.on_click(on_compare_button_clicked)

display(character1_widget, character2_widget, compare_button)