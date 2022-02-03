# Databricks notebook source
# MAGIC %md ### Feature engineering logic for demographic features

# COMMAND ----------

from pyspark.sql.functions import col
import pyspark.sql.functions as func
from databricks.feature_store import FeatureStoreClient
from databricks.feature_store import feature_table

# COMMAND ----------

# MAGIC %md Instatiate feature store client

# COMMAND ----------

fs = FeatureStoreClient()

# COMMAND ----------

# MAGIC %md Define feature transformation logic

# COMMAND ----------

def compute_passenger_demographic_features(df):
  
             # Extract prefic from name, such as Mr. Mrs., etc.
  return (df.withColumn('NamePrefix', func.regexp_extract(col('Name'), '([A-Za-z]+)\.', 1))
             # Extract a secondary name in the Name column if one exists
            .withColumn('NameSecondary_extract', func.regexp_extract(col('Name'), '\(([A-Za-z ]+)\)', 1))
             # Create a feature indicating if a secondary name is present in the Name column
            .selectExpr("*", "case when length(NameSecondary_extract) > 0 then NameSecondary_extract else NULL end as NameSecondary")
            .drop('NameSecondary_extract')
            .selectExpr("*", "case when NameSecondary is not NULL then '1' else '0' end as NameMultiple"))

# COMMAND ----------

# MAGIC %md Apply transformation logic to source table

# COMMAND ----------

df = spark.table('default.passenger_demographic_features')
passenger_demographic_features = compute_passenger_demographic_features(df)

# COMMAND ----------

# MAGIC %md Create an entry in the feature store if one does not exist

# COMMAND ----------

feature_table_name = 'default.demographic_features'

# If the feature table has already been created, no need to recreate
try:
  fs.get_table(feature_table_name)
  print("Feature table entry already exists")
  pass
  
except Exception:
  fs.create_table(name = feature_table_name,
                          primary_keys = 'PassengerId',
                          schema = passenger_demographic_features.schema,
                          description = 'Demographic-related features for Titanic passengers')

# COMMAND ----------

# MAGIC %md Populate the feature table

# COMMAND ----------

fs.write_table(
  
  name= feature_table_name,
  df = passenger_demographic_features,
  mode = 'merge'
  
  )

# COMMAND ----------

# MAGIC %md To drop the feature table; this table must also be delted in the feature store UI

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC -- DROP TABLE IF EXISTS default.demographic_features;
