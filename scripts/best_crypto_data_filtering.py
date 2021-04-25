from os import listdir
from os.path import isfile, join

from pandas import concat, read_csv, DataFrame


def shift_sentiments(df, look_back=12):
    """
    add the previous look_back sentiments to the dataframe
    """
    sentiments = {}
    for column in [column for column in df.columns if column != "priceUsd"]:
        for i in range(1, look_back+1, 1):
            sentiments[column+"_t-"+str(i)] = df[column].shift(i)

    return DataFrame(sentiments)


def get_price_data(df, look_back=12):
    """
    get the mean and standard deviation of the price over the look back time
    """
    price_list = {}
    for i in range(1, look_back+1, 1):
        price_list["t-"+str(i)] = df.priceUsd.shift(i)

    price_list = DataFrame(price_list)

    mean = price_list.mean(axis=1)
    std = price_list.std(axis=1)
    return mean, std


def assign_best_price(df):
    """
    Assign postive/negative/neutral direction to the price
    """
    diff_cols = [column for column in df.columns if "price_diff" in column]

    # assign best price to best price
    df["best_diff"] = df[diff_cols].max(axis=1)

    # assign crypto name to best price
    df["best_crypto"] = None
    for col in diff_cols:
        crypto_name = col.replace("price_diff_", "")

        mask = df["best_diff"] == df[col]
        df["best_crypto"].loc[mask] = crypto_name

    df = df.drop(diff_cols, axis=1)
    return df


def reformat(dfPre):
    """
    reformat the dataframe to contain sentiment from t-1 to t-10 and the mean
    and standard deviation of prices from t-1 to t-10
    ---
    new columns:
        - price_t: price at time t (what forecasting)
        - mean_price_before: mean price in 10 times before t (history)
        - std_price_before: std price in 10 times before t (history)
        - sentiment_t-1, ..., sentiment_t-10: sentiment in t-1 to t-10
        - volume_t-1, ..., volume_t-10: volume in t-1 to t-10
    Note that sentiment is seperated for positive and negative
    ---
    @param dfPre: dataframe before preprocessing
    """
    prices = dfPre['priceUsd'].fillna(method='pad')
    dates = dfPre["datetime"]

    exclude_cols = [0,1,2,4,5,6,7,9,11,12,13,14,16,18,19,20,21,23,25]
    dfPre = dfPre.iloc[:, ~dfPre.columns.isin(dfPre.columns[exclude_cols])]

    # shift the sentiments
    df = shift_sentiments(dfPre)

    # get the new prices
    df["mean_price_before"], df["std_price_before"] = get_price_data(dfPre)
    df["priceUsd"] = prices
    df.index = dates

    df["price_diff"] = df['priceUsd'] - df['mean_price_before']

    return df.dropna(axis=0)



dir_path = "dataApr15/training/2h/"
file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

list_dfs = []
for filename in [name for name in file_list]:
    crypto_name = filename.replace("2h.csv", "")

    filepath = dir_path + filename
    df = reformat(read_csv(filepath))

    new_cols = [column + "_" + crypto_name for column in df.columns]
    df.columns = new_cols

    list_dfs.append(df)

new_df = concat(list_dfs, axis=1, join="inner")
new_df = assign_best_price(new_df)

new_df = new_df.loc[new_df["best_crypto"] != ""]

new_df.to_csv("data/all_2h.csv", index=False)
