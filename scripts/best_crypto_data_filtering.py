from os import listdir
from os.path import isfile, join

from pandas import concat, read_csv, DataFrame
from sklearn.preprocessing import StandardScaler


def shift_sentiments(df, look_back=12):
    """
    add the previous look_back sentiments to the dataframe
    """
    sentiments = {}
    for column in ["sentiment_positive_total", "sentiment_negative_total", "social_volume_total"]:
        for i in range(1, look_back+1, 1):
            sentiments[column+"_t-"+str(i)] = df[column].shift(i)
    # print(sentiments.keys())

    return DataFrame(sentiments, index=df.index)


def shift_price(df, look_back=12):
    """
    add the previous look_back sentiments to the dataframe
    """
    price_data = get_price_data(df)
    # print(price_data.head())

    historical_price = {}
    for column in price_data.columns:
        for i in range(1, look_back+1, 1):
            historical_price[column+"_t-"+str(i)] = price_data[column].shift(i)

    # print( len(DataFrame(historical_price)))

    return DataFrame(historical_price, index=df.index)


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

    price_data = DataFrame()
    price_data["mean_price"], price_data["std_price"] = mean, std

    return price_data


def assign_best_price(df):
    """
    Assign postive/negative/neutral direction to the price
    """
    diff_cols = [column for column in df.columns if "price_diff" in column]

    # df[diff_cols] = StandardScaler().fit_transform(df[diff_cols])

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
    dates = dfPre["datetime"]
    dfPre.index = dates

    prices = dfPre['priceUsd'].fillna(method='pad')

    exclude_cols = [0,1,2,4,5,6,7,9,11,12,13,14,16,18,19,20,21,23,25]
    # dfPre = dfPre.iloc[:, ~dfPre.columns.isin(dfPre.columns[exclude_cols])]

    # shift the sentiments
    # df_sentiments = shift_sentiments(dfPre)
    df_sentiments = dfPre[["sentiment_positive_total", "sentiment_negative_total", "social_volume_total"]]
    # df_sentiments = DataFrame(index=dfPre.index)

    # get the new prices
    df_prices = shift_price(dfPre)


    # return
    df = concat([df_sentiments, df_prices], axis=1)
    df["priceUsd"] = prices

    df["price_diff"] = df['priceUsd'] - df['mean_price_t-1']

    return df.dropna(axis=0)



dir_path = "dataApr15/2h/"
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

new_df.to_csv("dataLSTM/combined_cryptos/price_2h.csv", index=False)

# print(new_df.groupby("best_crypto")["best_crypto"].count())
# print(new_df.columns)
