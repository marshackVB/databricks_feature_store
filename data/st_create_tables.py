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
dbfs_file_locations = {'ticket':     '/dbfs/FileStore/marshall.carter/feature_store/passenger_ticket.csv',
                      'demographic': '/dbfs/FileStore/marshall.carter/feature_store/passenger_demographic.csv',
                      'labels':      '/dbfs/FileStore/marshall.carter/feature_store/passenger_labels.csv'}


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
  
  
  def create_schema(col_types):
    struct = StructType()
    for col_name, type in col_types:
      struct.add(col_name, type)
    return struct
  
  passenger_ticket_schema =      create_schema(passenger_ticket_types)
  passenger_dempgraphic_schema = create_schema(passenger_demographic_types)
  passenger_label_schema =       create_schema(passenger_label_types)
  
  
  def create_pd_dataframe(csv_file_path, schema):
    df = pd.read_csv(csv_file_path)
    return spark.createDataFrame(df, schema = schema)
  
  
  passenger_ticket_features =      create_pd_dataframe(dbfs_file_location['ticket'],      passenger_ticket_schema)
  passenger_demographic_features = create_pd_dataframe(dbfs_file_location['demographic'], passenger_dempgraphic_schema)
  passenger_labels =               create_pd_dataframe(dbfs_file_location['labels'],      passenger_label_schema)
  
  
  def write_to_delta(spark_df, delta_table_name):
    spark_df.write.mode('overwrite').format('delta').saveAsTable(delta_table_name)
    
  delta_tables = {"ticket":       "default.passenger_ticket_feautures",
                  "demographic":  "default.passenger_demographic_features",
                  "labels":       "default.passenger_labels"}
    
  write_to_delta(passenger_ticket_features,      delta_tables['ticket'])
  write_to_delta(passenger_demographic_features, delta_tables['demographic'])
  write_to_delta(passenger_labels,               delta_tables['labels'])
  
  
  out = f"""The following tables were created:
          - {delta_tables['ticket']}
          - {delta_tables['demographic']}
          - {delta_tables['labels']}
       """
  
  print(out)

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
