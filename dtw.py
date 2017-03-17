# coding=utf-8
import numpy as np


def get_dtw(arr_a, arr_b):
    len_a = len(arr_a)
    len_b = len(arr_b)
    dis = np.zeros((len_a, len_b))
    dtw = np.zeros((len_a + 1, len_b + 1))
    for i in np.arange(len_a) + 1:
        for j in np.arange(len_b) + 1:
            if i != 0 and j != 0:
                dis[i - 1][j - 1] = abs(arr_a[i - 1] - arr_b[j - 1])
                dtw[i][j] = min(dtw[i - 1][j], dtw[i][j - 1], dtw[i - 1][j - 1]) + dis[i - 1][j - 1]
    return dtw[-1, -1]


a = np.array([3, 5, 6, 7, 7, 1, 1])
b = np.array([3, 5, 6, 7, 7, 1])
c = np.array([5, 6, 7, 7, 1, 1])
print get_dtw(a, b)
print get_dtw(a, c)
