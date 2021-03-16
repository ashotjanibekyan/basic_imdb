"""tests for basic_imdb package"""
import pandas as pd
from basic_imdb import TitleGenerators
import matplotlib.pyplot as plt

df = pd.DataFrame(columns=['id', 'title', 'year', '#votes', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])

gen = TitleGenerators.generator(votes=1000, total=float('inf'))

i = 0

for t in gen:
    table = t.get_rating_table()
    print(t.get_title())
    df.loc[i] = [t.get_id(), t.get_title(), t.get_year(), t.get_votes(),
                table[1], table[2], table[3], table[4], table[5],
                table[6], table[7], table[8], table[9], table[10]]
    i+=1
    if i % 10 == 0:
        df.to_csv('./movies_1000p.csv', index=False)
        