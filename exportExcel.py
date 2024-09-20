import pandas as pd
from collections import defaultdict


def excel_export(data_list: tuple) -> None:
    # print(list(data_list[0].keys()))
    # df_dict = merge_dictionaries(data_list)
    df_list = []

    for d in data_list:
        df_list.append(pd.DataFrame([d]))

    combined_df = pd.concat(df_list)

    # combined_df = combined_df.drop_duplicates(subset=['Наименование'])

    combined_df.to_excel('out_table_items.xlsx', index=False)


if __name__ == '__main__':
    excel_export(data)
