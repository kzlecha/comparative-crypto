from os import listdir
from os.path import isfile, join

from pandas import concat, read_csv


def reformat(dfPre):
    """
    reformat the dataframe
    FIXME: explain in more detial
    @param dfPre: dataframe before preprocessing
    """
    dfPre['priceUsd'] = dfPre['priceUsd'].fillna(method='pad')
    df = dfPre.copy(True)


    df['priceUsd'] = df.priceUsd.shift(-1)
    df['priceBtc'] = df.priceBtc.shift(-1)

    df["priceDirection"] = "neutral"

    pos_mask = df['priceUsd'] > dfPre['priceUsd']
    neg_mask = df['priceUsd'] <= dfPre['priceUsd']
    df.loc[pos_mask, "priceDirection"] = "positive"
    df.loc[neg_mask, "priceDirection"] = "negative"

    df['priceT+1'] = df.priceUsd
    df['priceUsd'] = df.priceUsd.shift(1)
    df['priceBtc'] = df.priceBtc.shift(1)

    exclude_cols = [0,1,2,4,5,6,7,9,11,12,13,14,16,18,19,20,21,23,25]
    df = df.iloc[:, ~df.columns.isin(df.columns[exclude_cols])]

    df = df.iloc[1:-1]
    df = df.iloc[:7321]

    return df


dir_path = "dataHourly/"
file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

for filename in file_list:

    filepath = dir_path + filename
    data = read_csv(filepath)

    data = reformat(data)
    
    data.to_csv("datatest/"+filename, index=False)
