import click
import os
import pandas
import warnings

warnings.filterwarnings('ignore')


if __name__ == '__main__':
    df = pandas.read_csv('data.csv', sep=';')
    amount = []
    unit = []
    for a in df.amount:
        a = a.split(' ')
        if len(a) == 1:
            amount.append(a[0])
            unit.append(None)
        else:
            amount.append(a[0])
            unit.append(a[1])
    new_amount = []
    for x in amount:
        try:
            new_amount.append(int(x))
        except ValueError:
            new_amount.append(float(x))
    df['amount'] = new_amount
    df['unit'] = unit
    recipes = df['recipe'].unique().tolist()

    print('Here are your recipes:')
    print('')
    for i, r in enumerate(recipes):
        print(f'({i + 1}) {r}')
    print('')
    print('Please specify which recipe(s) you\'d like. ', end='')
    print('For example "1x2 3x1" for two times the first recipe and one times the third.')
    chosen = input(':- ')
    pattern = '([0-9]+)x([0-9]+)'
    recipe_no = []
    quantity = []
    for x in chosen.strip().split(' '):
        n, q = x.split('x')
        recipe_no.append(int(n))
        quantity.append(int(q))
    chosen_recipes = [recipes[i - 1] for i in recipe_no]

    print('You chose these recipes:')
    print('')
    print('\n'.join(chosen_recipes))
    print('')
    sub = df[df.recipe.isin(chosen_recipes)]
    for i, r in enumerate(chosen_recipes):
        sub['amount'][sub['recipe'] == r] *= quantity[i]

    to_shop = sub.groupby('ingredient').agg({'amount': 'sum', 'store': 'max', 'type': 'max', 'unit': 'max'})
    to_shop = to_shop.reset_index()

    print('Here\'s your shopping list...')
    print('')
    lines = []
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

        lines.append('')

    with open('shoppinglist.txt', 'w') as f:
        f.write('\n'.join(['  ' + x for x in lines]))
    print('\n'.join(lines))
    if click.confirm('print the list?'):
        os.popen('lp shoppinglist.txt')