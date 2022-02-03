from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, DoubleType, IntegerType, StringType
import pandas as pd

spark = SparkSession.builder.getOrCreate()

def create_tables():

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
  pd_ticket_features = pd.read_csv('data/passenger_ticket.csv')
  pd_demographic_features = pd.read_csv('data/passenger_demographic.csv')
  pd_labels = pd.read_csv('data/passenger_labels.csv')


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
  
  
  