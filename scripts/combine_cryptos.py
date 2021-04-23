from os import listdir
from os.path import isfile, join

from pandas import concat, read_csv, DataFrame


def shift_sentiments(df, look_back=11):
    """
    """
    sentiments = {}
    for column in [column for column in df.columns if column != "priceUsd"]:
        for i in range(1, look_back):
            sentiments[column+"_t-"+str(i)] = df[column].shift(-1)

    return DataFrame(sentiments)


def get_price_data(df, look_back=10):
    price_list = {}
    for i in range(1, look_back):
        price_list["t-"+str(i)] = df.priceUsd.shift(-1)

    price_list = DataFrame(price_list)

    mean = price_list.mean(axis=1)
    std = price_list.std(axis=1)
    return mean, std


def assign_price_dir(df, dfPre):
    """
    Assign postive/negative/neutral direction to the price
    """
    df["priceDirection"] = "neutral"

    pos_mask = df['priceUsd'] > dfPre['priceUsd']
    neg_mask = df['priceUsd'] <= dfPre['priceUsd']
    df.loc[pos_mask, "priceDirection"] = "positive"
    df.loc[neg_mask, "priceDirection"] = "negative"


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
    df["datetime"] = dates

    return df.dropna(axis=0)



dir_path = "dataApr15/training/2h/"
file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

list_data = []

for filename in [name for name in file_list]:

    filepath = dir_path + filename
    df = read_csv(filepath)
    
    df = reformat(df)
    df["cryptocurrency"] = filename.replace("2h.csv", "")
    
    list_data.append(df)

df = concat(list_data)
df = df.sample(frac=1).sort_values(by="datetime",ascending=True)
df.to_csv("data/training_2h.csv", index=False)
