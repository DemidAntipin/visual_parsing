from bs4 import BeautifulSoup # библиотека для парсинга - поиск информации по структуре тегов
from bs4.element import Tag
import requests # получение данных по ссылке
import pandas as pd
import re

html = requests.get('https://intothespiderverse.fandom.com/wiki/Category:Characters').text
soup = BeautifulSoup(html, 'html')

items = []
for item in soup.find_all('li', {'class':'category-page__member'}):
  href=item.find('a')
  link='https://intothespiderverse.fandom.com'+href['href']
  title=href['title']
  if title[:8]=="Category": # нет смысла отдельно обрабатывать категории, иначе страницы их них будут спарсены дважды (они уже присутствуют в списке)
    continue
  elif title[:8]=="Template": # страница без персонажей
    continue
  else:
    subhtml = requests.get(link).text
    subsoup = BeautifulSoup(subhtml, 'html')
    data=subsoup.find('aside', {'role': 'region'})
    if isinstance(data, Tag):
      name = data.find('h2', {'data-source': 'name'}).text
      alias = (data.find('div', {'data-source': 'alias'}).find('div', {'class': 'pi-data-value'}) if data.find('div', {'data-source': 'alias'}) else None)
      if alias:
        for sup in alias.find_all('sup'):
          sup.decompose()
        for sup in alias.find_all('small'):
          sup.decompose()
        alias = [line.strip() for line in alias.stripped_strings if line.strip() and line not in ['Codenames', 'Derivatives', 'Nicknames', 'In-Universe Media', 'Organizational Names', 'Editorial Names']]
      else:
        alias = None
      counterpart_div = data.find('div', {'data-source': 'counterpart'})
      if counterpart_div:
        li_items = counterpart_div.find_all('li')
        if li_items:
          alters = [item.find('a').get_text() for item in li_items if item.find('a')]
        else:
          single_li = counterpart_div.find('li')
          alters = single_li.get_text() if single_li else counterpart_div.find('a').get_text() if counterpart_div.find('a') else None
      else:
        alters = None
      universe=(data.find('div', {'data-source': 'universe'}).find('div', {'class': 'pi-data-value'}).get_text() if data.find('div', {'data-source': 'universe'}) else None)
      occupation = (data.find('div', {'data-source': 'occupation'}).find('div', {'class': 'pi-data-value'}) if data.find('div', {'data-source': 'occupation'}) else None)
      if occupation:
        for sup in occupation.find_all('sup'):
          sup.decompose()
        for sup in occupation.find_all('small'):
          sup.decompose()
        occupation = occupation.get_text(separator="||")
        occupation = re.sub(r'\s\|\|\s', '||', occupation).replace('||||', '||').replace(' ', '_').replace('_||', '_').split('||')
      else:
        occupation = None
      identity=(data.find('div', {'data-source': 'identity'}).find('div', {'class': 'pi-data-value'}).get_text() if data.find('div', {'data-source': 'identity'}) else None)
      status=(data.find('div', {'data-source': 'status'}).find('div', {'class': 'pi-data-value'}).get_text() if data.find('div', {'data-source': 'status'}) else None)
      birth=(data.find('div', {'data-source': 'born'}).find('div', {'class': 'pi-data-value'}).get_text() if data.find('div', {'data-source': 'born'}) else None)
      species=(data.find('div', {'data-source': 'species'}).find('div', {'class': 'pi-data-value'}).text if data.find('div', {'data-source': 'species'}) else None)
      gender=(data.find('div', {'data-source': 'gender'}).find('div', {'class': 'pi-data-value'}).text if data.find('div', {'data-source': 'gender'}) else None)
      height=(data.find('div', {'data-source': 'height'}).find('div', {'class': 'pi-data-value'}).text.split()[0] if data.find('div', {'data-source': 'height'}) else None)
      weight=(data.find('div', {'data-source': 'weight'}).find('div', {'class': 'pi-data-value'}).text if data.find('div', {'data-source': 'weight'}) else None)

      alias_list = alias if isinstance(alias, list) else [alias] if alias is not None else []
      occupation_list = occupation if isinstance(occupation, list) else [occupation] if occupation is not None else []
      alters_list = alters if isinstance(alters, list) else [alters] if alters is not None else []
      for a in alias_list or [None]:
        for occ in occupation_list or [None]:
          for alter in alters_list or [None]:
            items.append({
                'name': name,
                'alias': a,
                'alteregos': alter,
                'universe': universe,
                'occupation': occ,
                'identity': identity,
                'status': status,
                'birth': birth,
                'species': species,
                'gender': gender,
                'height': height,
                'weight': weight
            })

    else: # нет данных для парсинга
      continue
df = pd.DataFrame(items)

# Приведение полей к единому формату

def convert_height(height):
    if not height:
      return None
    if isinstance(height, float):
      return height
    if 'cm' in height:
        return float(height.replace('cm', ''))
    elif '-' in height:  # Если указан диапазон
        low, high = height.split('-')
        low = low.strip()
        high = high.strip()
        if "'" in low or "'" in high:
            low_feet, low_inches = map(float, low.replace('"', '').split("'"))
            high_feet, high_inches = map(float, high.replace('"', '').split("'"))
            low_cm = round(low_feet * 30.48 + low_inches * 2.54)
            high_cm = round(high_feet * 30.48 + high_inches * 2.54)
            return round((low_cm + high_cm) / 2)  # Берем среднее значение
        else:
            return round((float(low) + float(high)) / 2)  # Берем среднее значение
    elif "'" in height:  # Если указано в футах и дюймах
        if height[-1]=="'":
          height+='0'
        feet, inches = map(float, height.replace('"', '').split("'"))
        return round(feet * 30.48 + inches * 2.54)
    else:
        if float(height)<3:
          return float(height)*100 # метры в см
        else:
          return float(height)  # уже в см

def convert_weight(weight):
    if isinstance(weight, float):
      return weight
    if weight is None:
        return None
    elif 'kg' in weight:
        weight=weight.split()[0]
        weight_value = ''.join(filter(lambda x: x.isdigit() or x == '.', weight))
        return float(weight_value) if weight_value else None
    elif 'lbs' in weight:
        # Переводим фунты в килограммы (1 lb = 0.453592 kg)
        weight_value = ''.join(filter(lambda x: x.isdigit() or x == '.', weight))
        return round(float(weight_value) * 0.453592, 2) if weight_value else None
    elif 'ton' in weight:
        weight_value = ''.join(filter(lambda x: x.isdigit() or x == '.', weight.replace(' ', '')))
        return round(float(weight_value) * 1000, 2) if weight_value else None
    else:
        return None

def extract_year(date):
    if isinstance(date, float):
      return date
    if date is None:
        return None
    if "Before 21st Century" in date:
        return 1953

    for i in range(len(date)-3):
      try:
        year=int(date[i:i+4])
        if len(str(year))==4:
          return year
        else:
          continue
      except Exception:
        continue
    return None

df['character'] = df['name'] + " (" + df['universe'] + ")"
df['height'] = df['height'].apply(convert_height)
df['weight'] = df['weight'].apply(convert_weight)
df['birth'] = df['birth'].apply(extract_year)

df.to_csv('dataset.csv', index=False, header=True, sep='@', encoding='utf-8')