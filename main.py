import click
import numpy
import os
import pandas
import warnings


warnings.filterwarnings('ignore')


if __name__ == '__main__':
    df = pandas.read_csv('data.csv', sep=';')
    df_ing = pandas.read_csv('ingredients.csv', sep=';')
    df = df.merge(df_ing, on='ingredient')
    recipes = df['recipe'].unique().tolist()

    print('Here are your recipes:')
    print('')
    for i, r in enumerate(recipes):
        print(f'({i + 1}) {r}')
    print('')
    print('Please specify which recipe(s) you\'d like. ', end='')
    print('For example "1 3" for the first and 3rd')
    chosen = input(':- ')
    chosen_recipes = [recipes[int(x) - 1] for x in chosen.split()]

    lines = []
    lines.append('You chose these recipes:')
    lines.append('')
    lines.extend(chosen_recipes)
    lines.append('')
    sub = df[df.recipe.isin(chosen_recipes) & numpy.logical_not(df.supply)][['amount', 'ingredient']]
    sub = sub.groupby('ingredient').agg({'amount': 'sum'})
    sub.reset_index()
    to_shop = sub.merge(df_ing, on='ingredient')
    to_shop = to_shop[['ingredient', 'store', 'type', 'unit', 'amount', 'url']]
    to_shop = to_shop.reset_index()
    supplies = df_ing[df_ing.supply]
    supplies['amount'] = supplies['minimum']
    supplies = supplies[['ingredient', 'store', 'type', 'unit', 'amount', 'url']]
    to_shop = pandas.concat([to_shop, supplies])
    to_shop['store'][numpy.logical_not(to_shop.url.isna())] = 'online'

    lines.append('Here\'s your shopping list...')
    lines.append('')
    stores = to_shop.groupby('store')
    for s in stores:
        lines.append('-' * 20)
        lines.append(f'At the {s[0]} store')
        lines.append('-' * 20)
        lines.append('')
        store_shopping = s[1].groupby('type')
        for g in store_shopping:
            lines.append('  ' + g[0].upper())
            for i in range(g[1].shape[0]):
                row = g[1].iloc[i]
                if not isinstance(row["unit"], str):
                    lines.append(f'    {row["amount"]} {row["ingredient"]}')
                else:
                    lines.append(f'    {row["amount"]} {row["unit"]} {row["ingredient"]}')
                if s[0] == 'online':
                    lines[-1] = lines[-1].ljust(50) + row['url']

        lines.append('')

    with open('shoppinglist.txt', 'w') as f:
        f.write('\n'.join(['  ' + x for x in lines]))
    print('\n'.join(lines))
    if click.confirm('print the list?'):
        os.popen('lp shoppinglist.txt')
