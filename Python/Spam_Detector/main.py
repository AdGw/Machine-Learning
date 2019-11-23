import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score

dataframe = pd.read_csv('spam2.csv', delimiter='\t',header=None)

X_train_dataset, X_test_dataset, y_train_dataset, y_test_dataset = train_test_split(dataframe[1],dataframe[0])

vectorizer = TfidfVectorizer()
X_train_dataset = vectorizer.fit_transform(X_train_dataset)
classifier_log = LogisticRegression()
classifier_log.fit(X_train_dataset, y_train_dataset)

X_test_dataset = vectorizer.transform( ['000 Prize Jackpot!', 'Hey honey, whats up?'] )

predictions_logistic = classifier_log.predict(X_test_dataset)
print(predictions_logistic)
