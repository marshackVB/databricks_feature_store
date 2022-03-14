# Databricks notebook source
# MAGIC %md ### Publishing a Delta feature store table to an online store  
# MAGIC Some use cases require Rest API model deployment required for inference. This is typically the case where an application outside of Databricks is recieving information and requires model predictions based on that information (imagine a user interface where a use can input information and receive a prediction). Im some cases, this external application may not have access to all the features the model requires. We can publish our features to an RDBMS that can be access by our MLflow model deployed via Rest API. In our scenario, the external application would only need to pass the PassengerId to the Rest endpoint to retrieve a prediction for a passenger.
# MAGIC 
# MAGIC 
# MAGIC In this example, we will copy a Delta Feature Store table to an AWS Aurora database. See the [online documentation here](https://docs.databricks.com/applications/machine-learning/feature-store/feature-tables.html#publish-features-to-an-online-feature-store).

# COMMAND ----------

from databricks.feature_store.online_store_spec.amazon_rds_mysql_online_store_spec import AmazonRdsMySqlSpec
from databricks.feature_store import FeatureStoreClient, FeatureLookup

fs = FeatureStoreClient()

# COMMAND ----------

# MAGIC %md #### Pre-join existing feature tables  
# MAGIC We currently have two Feature Store tables that are joined based on PassengerId to create the model training dataset. Since Feature Store tables are just Delta tables, and we want to avoid contantly joining tables in our online store each time our Rest API is called, lets create a third Feature Store table that joins the two source tables.
# MAGIC 
# MAGIC Note that the underlying feature tables will need to be updated before joining the tables.

# COMMAND ----------

demographic_features = (spark.table('default.demographic_features')
                             .select('PassengerId','Age', 'NameMultiple', 'NamePrefix', 'Sex', 'SibSp'))

ticket_features = (spark.table('default.ticket_features')
                             .select('PassengerId', 'CabinChar', 'CabinMulti', 'Embarked', 'FareRounded', 'Parch', 'Pclass'))

online_feature_table = demographic_features.join(ticket_features, ['PassengerId'], 'inner')

display(online_feature_table)

# COMMAND ----------

# MAGIC %md #### Create feature table

# COMMAND ----------

feature_table_name = 'default.online_feature_table'

# If the feature table has already been created, no need to recreate
try:
  fs.get_table(feature_table_name)
  print("Feature table entry already exists")
  pass
  
except Exception:
  fs.create_table(name =  feature_table_name,
                          primary_keys = 'PassengerId',
                          schema = online_feature_table.schema,
                          description = 'Online feature store table for Titanic passengers')

# COMMAND ----------

# MAGIC %md #### Write the Spark DataFrame to the Feature Table

# COMMAND ----------

fs.write_table(
  
  name=   feature_table_name,
  df =    online_feature_table,
  mode = 'merge'
  
  )

# COMMAND ----------

# MAGIC %md #### Configure the online store  
# MAGIC Publish a feature table to an online store, int this case an AWS Aurora RDBMS. We will pass the database and name of the Delta table, as well as an [**AmazonRdsMySqlSpec** ](https://docs.databricks.com/dev-tools/api/python/latest/feature-store/online_store_spec/databricks.feature_store.online_store_spec.amazon_rds_mysql_online_store_spec.html#module-databricks.feature_store.online_store_spec.amazon_rds_mysql_online_store_spec)instance that contains connection info associated with our Aurora RDBMS.

# COMMAND ----------

# Aurora cluster's Writer instance endpoint
host = 'feature-store.cluster-c7e3jyejr1kf.us-east-1.rds.amazonaws.com'
port = 3306

# Delta database and table name
database_name = 'feature_store'
table_name = 'online_feature_table'

user = dbutils.secrets.get(scope="aurora_writer", key="aurora-user")
password = dbutils.secrets.get(scope="aurora_writer", key="aurora-password")

read_secret_prefix = 'aurora_reader/aurora'
write_secret_prefix = 'aurora_writer/aurora'

fs = FeatureStoreClient()

# COMMAND ----------

# MAGIC %md **Option 1**: Pass username and password stored as Databricks Secrets

# COMMAND ----------

online_store = AmazonRdsMySqlSpec(
                    hostname=host, 
                    port=port, 
                    user=user,
                    password=password,
                    database_name=database_name, 
                    table_name=table_name
            )

# COMMAND ----------

# MAGIC %md **Option 2**: Pass the name of the Databricks Secret Scope that contains the username and password.  
# MAGIC  - The secret scope syntax is important. See [the examples here](https://docs.databricks.com/applications/machine-learning/feature-store/feature-tables.html#provide-online-store-credentials-using-databricks-secrets).

# COMMAND ----------

online_store = AmazonRdsMySqlSpec(
                    hostname=host, 
                    port=port,
                    read_secret_prefix=read_secret_prefix,
                    write_secret_prefix=write_secret_prefix, 
                    database_name=database_name, 
                    table_name=table_name
            )

# COMMAND ----------

# MAGIC %md View the feature table we will push to the online store

# COMMAND ----------

display(spark.table(f'default.{table_name}'))

# COMMAND ----------

# MAGIC %md Push the table to the Aurora database.  
# MAGIC  -  Available modes are 'merge' and 'overwrite'. 'Merge' will merge new records based on the primary key that was specified when the feature table was created.

# COMMAND ----------

fs.publish_table(name=f'default.{table_name}', 
                 online_store=online_store,
                 mode='merge')
