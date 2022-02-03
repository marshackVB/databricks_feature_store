# Databricks notebook source
# MAGIC %md ## Model training

# COMMAND ----------

from databricks.feature_store import FeatureLookup
from databricks.feature_store import FeatureStoreClient
import mlflow

import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# Change this to your own experiment location
# Click on the Experiments icon in the side bar and select 'Create Blank Experiment' from the dropdown.
# Name the experiment and copy the directory listed on the upper left hand corner of the Experiment UI. 
mlflow.set_experiment('/Users/marshall.carter@databricks.com/demo/feature_store/experiment')

# COMMAND ----------

fs = FeatureStoreClient()

# COMMAND ----------

# MAGIC %md Specify the feature table names, columns, and join keys

# COMMAND ----------

feature_lookups = [
    FeatureLookup(
      table_name = 'default.ticket_features',
      feature_names = ['CabinChar', 'CabinMulti', 'Embarked', 'FareRounded', 'Parch', 'Pclass'],
      lookup_key = 'PassengerId'
    ),
    FeatureLookup(
      table_name = 'default.demographic_features',
      feature_names = ['Age', 'NameMultiple', 'NamePrefix', 'Sex', 'SibSp'],
      lookup_key = 'PassengerId'
    )
  ]

# COMMAND ----------

# MAGIC %md Join the features to form the training dataset

# COMMAND ----------

# Select passenger records of interest
passengers_and_target = spark.table('default.passenger_labels')

# Attach features to passengers
training_set = fs.create_training_set(df = passengers_and_target,
                                      feature_lookups = feature_lookups,
                                      label = 'Survived',
                                      exclude_columns = ['PassengerId'])

# Create training datast
training_df = training_set.load_df()

display(training_df)

# COMMAND ----------

# MAGIC %md Fit a scikit-learn pipeline model to the features. After fitting the model, local the model run in the Mlflow Tracking Server. Promote the model to the Model Registry. Local the model in the Registry and change its "Stage" to "Production"  
# MAGIC 
# MAGIC See https://www.mlflow.org/docs/latest/model-registry.html#registering-a-model for instructions.

# COMMAND ----------

# Convert to Pandas for scikit-learn training
data = training_df.toPandas()

# Split into training and test datasets
label = 'Survived'
features = [col for col in data.columns if col not in [label, 'PassengerId']]

X_train, X_test, y_train, y_test = train_test_split(data[features], data[label], test_size=0.25, random_state=123, shuffle=True)

# Categorize columns by data type
categorical_vars = ['NamePrefix', 'Sex', 'CabinChar', 'CabinMulti', 'Embarked', 'Parch', 'Pclass', 'SibSp']
numeric_vars = ['Age', 'FareRounded']
binary_vars = ['NameMultiple']

# Create the a pre-processing and modleing pipeline
binary_transform = make_pipeline(SimpleImputer(strategy = 'constant', fill_value = 'missing'))

numeric_transform = make_pipeline(SimpleImputer(strategy = 'most_frequent'))

categorical_transform = make_pipeline(SimpleImputer(missing_values = None, strategy = 'constant', fill_value = 'missing'), 
                                      OneHotEncoder(handle_unknown="ignore"))
  
transformer = ColumnTransformer([('categorial_vars', categorical_transform, categorical_vars),
                                 ('numeric_vars', numeric_transform, numeric_vars),
                                 ('binary_vars', binary_transform, binary_vars)],
                                  remainder = 'drop')

# Specify the model
# See Hyperopt for hyperparameter tuning: https://docs.databricks.com/applications/machine-learning/automl-hyperparam-tuning/index.html
model = xgb.XGBClassifier(n_estimators = 50, use_label_encoder=False)

classification_pipeline = Pipeline([("preprocess", transformer), ("classifier", model)])

# Fit the model, collect statistics, and log the model
with mlflow.start_run() as run:
  
  #mlflow.xgboost.autolog()
    
  # Fit model
  classification_pipeline.fit(X_train, y_train)
  
  train_pred = classification_pipeline.predict(X_train)
  test_pred = classification_pipeline.predict(X_test)
  
  # Calculate validation statistics
  precision_train, recall_train, f1_train, _ = precision_recall_fscore_support(y_train, train_pred, average='weighted')
  precision_test, recall_test, f1_test, _ = precision_recall_fscore_support(y_test, test_pred, average='weighted')
  
  decimals = 2
  validation_statistics = {"precision_training": round(precision_train, decimals),
                           "precision_testing": round(precision_test, decimals),
                           "recall_training": round(recall_train, decimals),
                           "recall_testing": round(recall_test, decimals),
                           "f1_training": round(f1_train, decimals),
                           "f1_testing": round(f1_test, decimals)}
  
  # Log the validation statistics
  mlflow.log_metrics(validation_statistics)
  
  # Fit final model
  final_model = classification_pipeline.fit(data[features], data[label])
  
  # Log the model and training data metadata
  fs.log_model(
    final_model,
    artifact_path="model_packaged",
    flavor = mlflow.sklearn, 
    training_set=training_set
  )
