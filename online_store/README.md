# Setting up an online feature store

## Create an [AWS Aurora database cluster](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html)  

 You can use the example Terraform scripts to provision an Aurora cluster in the default VPC of your AWS account. You will need to [install and configure the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html). As part of this process, you will need to enter your AWS access key id and secret access key. The Terraform scripts provision the below resources; your AWS User must have permission to create these resources. 
  - A Security Group that provides internet access to the Aurora cluster
  - An Aurora cluster
  - A single Aurora cluster instance, which is added to the cluster, that handles both reads and writes  
  

Applying the terraform template will output a master username, password, and cluster endpoint address. These must be saved and will be used to authenticate to the Aurora cluster. To view the non-redacted password, issue the command, 'terraform output -json' from the terminal after terraform provisions the resources.  

To provision the resources, navigate to the terraform folder in your terminal and issue the below commands, [assuming you have installed Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli).
```
terraform init
terraform plan
terraform apply
terraform output -json

# When you are ready to tear down the infrastructure
teffaform destroy
```

Note that the Aurora cluster provisioned by these scripts is designed for demonstration purposes. Further configuration would be required for a production deployment.


## Connect to the Aurora cluster using a SQL editor
 - [DBeaver](https://dbeaver.io/) is an easy to use and free SQL editor that can easily connect to your Aurora cluster throught a MySQL connection.
 - Create the MySQL connection using the master username, password, cluster endpoint address, and the database, 'feature_store', that was created by the Terraform.  

<img src="../img/dbeaver_mysql.png"
     width=700
     style="float: center;"/>


## Create a user with write access and a user with read-only access to the feature store database.  
 - The crendtials for these users (user name and password) will be saved as Databricks Secrets referenceable by the Databricks Feature Store.
```
CREATE USER 'writer'@'%' IDENTIFIED BY '<writer-password>';
CREATE USER 'reader'@'%' IDENTIFIED BY '<reader-only-password';

GRANT ALL PRIVILEGES ON feature_store.* TO 'writer';
GRANT SELECT ON feature_store.* TO 'reader';

SELECT User FROM mysql.user;

SHOW GRANTS for writer;
SHOW GRANTS for reader;
```

## Create two Databricks Secret Scopes; one for the write user's credentials and another for the read-only user's credentials.
 - Install and configure the [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) to authenticate to your Databricks workspace.
 - Use the CLI to create the secret scopes; each scope contains two secrets that share the same prefix (in the example below, 'aurora-'). One of the secrets should contain the postfix, 'user' and the other 'password'. It is important [that you follow this syntax](https://docs.databricks.com/applications/machine-learning/feature-store/feature-tables.html#provide-online-store-credentials-using-databricks-secrets).
 ```
databricks secrets put --scope aurora_writer --key aurora-user --profile e2-demo-east
databricks secrets put --scope aurora_writer --key aurora-password --profile e2-demo-east

databricks secrets put --scope aurora_reader --key aurora-user --profile e2-demo-east
databricks secrets put --scope aurora_reader --key aurora-password --profile e2-demo-east
 ```

 - See the [Databricks Secrets documentation](https://docs.databricks.com/security/secrets/secrets.html) 
 - In general, to access Databricks Secrets within a workspace, [see the documentation](https://docs.databricks.com/dev-tools/databricks-utils.html#secrets-utility-dbutilssecrets)

When publishing Delta Feature Store tables to Aurora, the Feature Store will leverage the above items to establish a connection using the follow syntax.
 - Note that Feature Store tables are Delta tables; we are simply copying the Delta table to Aurora and esuring the tables are in synce by merging changes from the Delta Feature Store table to the Aurora table.
```
host = 'feature-store.cluster-############.us-east-1.rds.amazonaws.com'
port = 3306
database_name = 'feature_store'
table_name = 'online_feature_table'
read_secret_prefix = 'aurora_reader/aurora'
write_secret_prefix = 'aurora_writer/aurora'

online_store = AmazonRdsMySqlSpec(
                    hostname=host, 
                    port=port,
                    read_secret_prefix=read_secret_prefix,
                    write_secret_prefix=write_secret_prefix, 
                    database_name=database_name, 
                    table_name=table_name
            )

fs.publish_table(name=f'default.{table_name}', # Delta table reference
                 online_store=online_store,
                 mode='merge')
```
See the [AmazonRdsMySqlSpec documentation](https://docs.databricks.com/dev-tools/api/python/latest/feature-store/online_store_spec/databricks.feature_store.online_store_spec.amazon_rds_mysql_online_store_spec.html#module-databricks.feature_store.online_store_spec.amazon_rds_mysql_online_store_spec)  

## After running the Databricks Notebook to publish the Feature Store table, query the table using the SQL editor.
```
SELECT * FROM feature_store.online_feature_table;
``` 