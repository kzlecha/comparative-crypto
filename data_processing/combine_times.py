from os import listdir
from os.path import isfile, join

from pandas import concat, read_csv


dir_path = "dataMar14/"
file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

file_endings = ["5m.csv", "hourly.csv", "daily.csv"]

for file_ending in file_endings:
    list_data = []

    for filename in [name for name in file_list if file_ending in name]:
        print(filename)

        filepath = dir_path + filename
        df = read_csv(filepath)
        df["diff_pos_neg"] = df["sentiment_positive_total"] - df["sentiment_negative_total"]

        # set to neutral by default
        df["category"] = 0
        df.loc[df["diff_pos_neg"] > 0.05, ["category"]] = 1
        df.loc[df["diff_pos_neg"] < 0.05, ["category"]] = -1
        
        list_data.append(df)

    df = concat(list_data)
    df.to_csv("data/unfiltered/"+file_ending, index=False)
