from typing import List
import warnings

import numpy as np
# from modin import pandas as pd  # import dask as dpd / import pandas as pd # which engine - pip install "modin[all]" is not space efficient and slow for enduser experience - we should specify the engine
import pandas as pd


# SCORING FUNCTIONS
def meanmax_harmonic(df: pd.DataFrame):
    mean_p = df.apply(lambda x: np.mean(x))
    max_p = df.apply(lambda x: max(x))
    df_out = ((mean_p.pow(-1) + max_p.pow(-1)) / 2) ** -1
    return df_out


def meanmax_geometric(df: pd.DataFrame):
    mean_p = df.apply(lambda x: np.mean(x))
    max_p = df.apply(lambda x: max(x))
    df_out = (mean_p * max_p) ** 1 / 2
    return df_out


def meanmax_arithmetic(df: pd.DataFrame):
    mean_p = df.apply(lambda x: np.mean(x))
    max_p = df.apply(lambda x: max(x))
    df_out = (mean_p + max_p) / 2
    return df_out


def hit_polynomial(df: pd.DataFrame, exponent: float = 2):
    df_out = df.apply(lambda x: x ** exponent).apply(lambda x: np.mean(x))
    return df_out


def hit_max(df: pd.DataFrame):
    df_out = df.apply(lambda x: max(x))
    return df_out


def hit_amean(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.mean(x))
    return df_out


def hit_hmean(df: pd.DataFrame):
    df_out = df.apply(lambda x: len(x) / np.sum(1.0 / x))
    return df_out


def hit_gmean(df: pd.DataFrame):
    df_out = df.apply(lambda x: x.prod() ** (1.0 / len(x)))
    return df_out


def hit_decile1(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.10))
    return df_out


def hit_decile2(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.20))
    return df_out


def hit_decile3(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.30))
    return df_out


def hit_decile4(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.40))
    return df_out


def hit_decile5(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.50))
    return df_out


def hit_decile6(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.60))
    return df_out


def hit_decile7(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.70))
    return df_out


def hit_decile8(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.80))
    return df_out


def hit_decile9(df: pd.DataFrame):
    df_out = df.apply(lambda x: np.quantile(x, 0.90))
    return df_out


def rank_median(df: pd.DataFrame):
    ranks = df.rank(ascending=False, axis=1)
    df_out = ranks.apply(lambda x: (len(x) - np.median(x)) / len(x))
    return df_out


def rank_mean(df: pd.DataFrame):
    ranks = df.rank(ascending=False, axis=1)
    df_out = ranks.apply(lambda x: (len(x) - np.mean(x)) / len(x))
    return df_out


def tomato_index(df: pd.DataFrame):
    max_vals = df.apply(lambda x: max(x), axis=1)
    filtered_fragments = df[df.max(axis=1) > np.median(max_vals)]
    ranks = filtered_fragments.rank(ascending=False, axis=1)
    df_out = ranks.apply(lambda x: (len(x) - np.mean(x)) / len(x))
    return df_out


def potato_index(df: pd.DataFrame):
    max_vals = df.apply(lambda x: max(x), axis=1)
    filtered_fragments = df[df.max(axis=1) < np.median(max_vals)]
    ranks = filtered_fragments.rank(ascending=False, axis=1)
    df_out = ranks.apply(lambda x: (len(x) - np.mean(x)) / len(x))
    return df_out


def potato_harmony(df: pd.DataFrame):
    max_vals = df.apply(lambda x: max(x), axis=1)
    filtered_fragments = df[df.max(axis=1) < np.median(max_vals)]
    df_out = filtered_fragments.apply(lambda x: len(x) / np.sum(1.0 / x))
    return df_out


def potato_mean(df: pd.DataFrame):
    max_vals = df.apply(lambda x: max(x), axis=1)
    filtered_fragments = df[df.max(axis=1) < np.median(max_vals)]
    df_out = filtered_fragments.apply(lambda x: np.mean(x))
    return df_out


def potato_geometry(df: pd.DataFrame):
    max_vals = df.apply(lambda x: max(x), axis=1)
    filtered_fragments = df[df.max(axis=1) < np.median(max_vals)]
    df_out = filtered_fragments.apply(lambda x: x.prod() ** (1.0 / len(x)))
    return df_out


def beet_harmony(df: pd.DataFrame):
    s = df.apply(lambda x: sum(x), axis=1)
    filtered_fragments = df[df.sum(axis=1) < np.median(s)]
    df_out = filtered_fragments.apply(lambda x: len(x) / np.sum(1.0 / x))
    return df_out


def beet_mean(df: pd.DataFrame):
    s = df.apply(lambda x: sum(x), axis=1)
    filtered_fragments = df[df.sum(axis=1) < np.median(s)]
    df_out = filtered_fragments.apply(lambda x: np.mean(x))
    return df_out


def beet_geometry(df: pd.DataFrame):
    s = df.apply(lambda x: sum(x), axis=1)
    filtered_fragments = df[df.sum(axis=1) < np.median(s)]
    df_out = filtered_fragments.apply(lambda x: x.prod() ** (1.0 / len(x)))
    return df_out


def hit_rank_adjusted_row(df: pd.DataFrame):
    rank_penalties = df.rank(ascending=False, axis=1) ** -1
    df_out = (df * rank_penalties).apply(lambda x: np.mean(x))
    return df_out


def hit_rank_adjusted_col(df: pd.DataFrame):
    rank_penalties = df.rank(ascending=False, axis=0) ** -1
    df_out = (df * rank_penalties).apply(lambda x: np.mean(x))
    return df_out


default_scoring_functions = (beet_geometry, beet_harmony, beet_mean,
                             hit_amean, hit_gmean, hit_hmean, tomato_index,
                             potato_geometry, potato_harmony, potato_index, potato_mean,
                             hit_decile1, hit_decile2, hit_decile3, hit_decile4, hit_decile5,
                             hit_decile6, hit_decile7, hit_decile8, hit_decile9,
                             hit_max, hit_polynomial, hit_rank_adjusted_col, hit_rank_adjusted_row,
                             meanmax_arithmetic, meanmax_geometric, meanmax_harmonic,
                             rank_mean, rank_median)


def score_and_rank(raw_result: pd.DataFrame,
                   scoring_functions: List[callable] = default_scoring_functions):
    with warnings.catch_warnings(record=True) as caught_warnings:
        scored_predictions = [(f.__name__, f(raw_result)) for f in scoring_functions]
        sorted_predictions, failed = {}, set()
        for f_name, prediction_frame in scored_predictions:
            prediction_frame: pd.DataFrame
            if prediction_frame.empty:
                failed.add(f_name)
            else:
                sorted_predictions[f_name] = [(h, s) for h, s in sorted(prediction_frame.to_dict().items(), key=lambda hs: hs[1], reverse=True)]
    return sorted_predictions, failed, [str(w.message) for w in caught_warnings]
