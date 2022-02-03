# Databricks Feature Store example project

This Databricks [Repo](https://docs.databricks.com/repos.html) provides an example [Feature Store](https://docs.databricks.com/applications/machine-learning/feature-store/index.html) workflow based on the titanic dataset. The dataset is split into two domain specific tables: features based on purchases and demographic information. Machine learning features are typically sourced from many underlying tables/sources, and this simple workflow is designed to mimic this characteristic.

Also, by create domain-specific feature sets, tables become more modular and can be leveraged across multiple projects and across teams. 

### Getting started

1. Clone this repository into a Databricks Repo


2. Run the **delta_table_setup** notebook to create the source tables used for feature generation.
    - This notebook uses [arbitrary file support](https://docs.databricks.com/repos.html#work-with-non-notebook-files-in-a-databricks-repo) by referencing a function stored in a .py file. Also, note the use of [ipython autoloading](https://ipython.org/ipython-doc/3/config/extensions/autoreload.html) for rapid development of functions and classes.  

  
3. Run the **passenger_demographic_features** and **passenter_ticket_features** notebooks to create and populate the two feature store tables. 
    - Navitate to the Feature Store icon on the left pane of the Databricks UI. There will be two entries, one for each feature table.


4. Open the **fit_model** notebook and create an MLflow Experiment as detailed in the first cell; adjust the mlflow.set_experiment() location to your own Experiment's location.

5. Run the **fit_model** notebook.  

6. Navigate to the MLflow Experiment and click on the run created by the notebook above. [Publish the model](https://docs.databricks.com/applications/machine-learning/manage-model-lifecycle/index.html#create-or-register-a-model-using-the-ui) to the Model Registry. Name the model and change the model's stage to 'Production'.

7. Open the **model_inference** notebook and replace the model's name referenced by get_run_id() to your model's name in the Model Registry. Run the notebook to perform inference.
