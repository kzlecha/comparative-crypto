from os import listdir
from os.path import isfile, join

from pandas import concat, read_csv


dir_path = "data/"
file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

file_endings = ["5m.csv", "hourly.csv", "daily.csv"]

for file_ending in file_endings:
    list_data = []

    for filename in [name for name in file_list if file_ending in name]:
        print(filename)

        filepath = dir_path + filename
        df = read_csv(filepath)
        
        df["cryptocurrency"] = filename.replace(file_ending, "")
        
        list_data.append(df)

    df = concat(list_data)
    df.to_csv("data/combined/"+file_ending, index=False)
