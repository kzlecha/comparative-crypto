from os import listdir
from os.path import isfile, join

from pandas import concat, read_csv, DataFrame


def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    # n_vars = 1 if type(data) is list else data.shape[1]
    # df = DataFrame(data)
    cols = list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
    # put it all together
    agg = concat(cols, axis=1)
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg

dir_path = "dataMar14/"
file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]


for filename in file_list:

    filepath = dir_path + filename
    df = read_csv(filepath)

    df = series_to_supervised(df, 6, 2)
    
    df.to_csv("data/"+filename, index=False)
