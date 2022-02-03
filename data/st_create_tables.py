# Databricks notebook source
# MAGIC %md ## Data create notebook for single tenant customers

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, DoubleType, IntegerType, StringType
import pandas as pd

# COMMAND ----------

# MAGIC %md Create Delta tables from csv files

# COMMAND ----------

# Enter your dbfs locations for each data file
dbfs_file_locations = {'ticket':    '/dbfs/FileStore/marshall.carter/feature_store/passenger_ticket.csv',
                      'demographic': '/dbfs/FileStore/marshall.carter/feature_store/passenger_demographic.csv',
                      'labels':     '/dbfs/FileStore/marshall.carter/feature_store/passenger_labels.csv'}


def create_tables(dbfs_file_location=dbfs_file_locations):

  # Create Spark DataFrame schemas
  passenger_ticket_types = [('PassengerId',     StringType()),
                            ('Ticket',          StringType()),
                            ('Fare',            DoubleType()),
                            ('Cabin',           StringType()),
                            ('Embarked',        StringType()),
                            ('Pclass',          StringType()),
                            ('Parch',           StringType())]

  passenger_demographic_types = [('PassengerId',StringType()),
                                 ('Name',       StringType()),
                                 ('Sex',        StringType()),
                                 ('Age',        DoubleType()),
                                 ('SibSp',      StringType())]

  passenger_label_types = [('PassengerId',StringType()),
                           ('Survived',   IntegerType())]


  passenger_ticket_schema = StructType()
  for col_name, type in passenger_ticket_types:
    passenger_ticket_schema.add(col_name, type)

  passenger_dempgraphic_schema = StructType()
  for col_name, type in passenger_demographic_types:
    passenger_dempgraphic_schema.add(col_name, type)

  passenger_label_schema = StructType()
  for col_name, type in passenger_label_types:
    passenger_label_schema.add(col_name, type)

    
  # Read csv files  
  pd_ticket_features = pd.read_csv(dbfs_file_locations['ticket'])
  pd_demographic_features = pd.read_csv(dbfs_file_locations['demographic'])
  pd_labels = pd.read_csv(dbfs_file_location['labels'])


  # Convert to Spark DataFrames
  passenger_ticket_features = spark.createDataFrame(pd_ticket_features, schema = passenger_ticket_schema)
  passenger_demographic_features = spark.createDataFrame(pd_demographic_features, schema = passenger_dempgraphic_schema)
  passenger_labels = spark.createDataFrame(pd_labels, schema = passenger_label_schema)

  # Write to Delta
  table_mapping = {"ticket_features_source_table":      "default.passenger_ticket_feautures",
                   "demographic_features_source_table": "default.passenger_demographic_features",
                   "labels_source_table":               "default.passenger_labels"}
  
  passenger_ticket_features.write.mode('overwrite').format('delta').saveAsTable(table_mapping['ticket_features_source_table'])
  passenger_demographic_features.write.mode('overwrite').format('delta').saveAsTable(table_mapping['demographic_features_source_table'])
  passenger_labels.write.mode('overwrite').format('delta').saveAsTable(table_mapping['labels_source_table'])
  
  return table_mapping

# COMMAND ----------

create_tables()

# COMMAND ----------

# MAGIC %md To drop tables

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC -- DROP TABLE IF EXISTS default.passenger_ticket_feautures;
# MAGIC -- DROP TABLE IF EXISTS default.passenger_demographic_feautures;
# MAGIC -- DROP TABLE IF EXISTS default.passenger_labels;
