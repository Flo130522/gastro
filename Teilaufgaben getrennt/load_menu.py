import pandas as pd

def load_menu(menu_file, encoding="utf-8", index_col="id"):
    menu = pd.read_csv(menu_file, encoding=encoding)
    return menu

menu_file = r"speisekarte.csv"
restaurant_menu = load_menu(menu_file)
print(restaurant_menu)