# Databricks notebook source
# MAGIC %md ### Generate Delta tables from csv files
# MAGIC These tables will be transformed into feature tables

# COMMAND ----------

from data.create_tables import create_tables

# COMMAND ----------

# See https://ipython.org/ipython-doc/3/config/extensions/autoreload.html
%load_ext autoreload
%autoreload 2

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
