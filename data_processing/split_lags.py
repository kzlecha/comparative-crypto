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

    df = df.iloc[1:]
    dfPre = dfPre.iloc[1:]

    df["priceDirecetion"] = "neutral"

    pos_mask = df['priceUsd'] >= dfPre['priceUsd'] * 1.001
    neg_mask = df['priceUsd'] <= dfPre['priceUsd'] * 0.999
    df.loc[pos_mask, "priceDirection"] = "positive"
    df.loc[neg_mask, "priceDirection"] = "negative"

    return df


dir_path = "dataMar14/"
file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

for filename in file_list:

    filepath = dir_path + filename
    data = read_csv(filepath)

    data = reformat(data)
    
    data.to_csv("data/"+filename, index=False)
