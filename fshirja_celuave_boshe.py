import pandas as pd

data = pd.read_csv('Cybersecurity_attacks.csv')
df = pd.DataFrame(data)

print('Para eleminimit rreshtave boshe')
print(df)

df_pastruar = data.dropna()


print('Pas pastrimit te rreshtave qe kane celula boshe')
print(df_pastruar)