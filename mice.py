import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def implement_MICE(file, cols, max_iterator=25, rand_state=0):
    df_copy = file.copy()
    imputer = IterativeImputer(max_iter=max_iterator, random_state=rand_state)
    imputed_values = imputer.fit_transform(df_copy[cols])
    df_copy.loc[:, cols] = imputed_values
    return df_copy, imputed_values