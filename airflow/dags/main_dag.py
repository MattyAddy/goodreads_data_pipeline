import os
import pendulum
from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator, BigQueryCreateExternalTableOperator
from google.cloud import storage

# DAG variables
start = pendulum.datetime(2024, 12, 12, tz="UTC")
airflow_file_path = os.environ.get("AIRFLOW_HOME","/opt/airflow/")

execution_date_string = "{{ data_interval_end.strftime('%Y%m%d') }}"
year_folder = "{{ data_interval_end.strftime('%Y') }}"
month_folder = "{{ data_interval_end.strftime('%m') }}"
parquet_file = f"goodreads_{execution_date_string}.parquet"
blob_name = f"madams-terraform-book-data-lake/raw_data/{year_folder}/{month_folder}"
schema = "goodreads_db_raw" 
external_table = "ext_book_bronze_stg"
table = "book_bronze_stg"

source_file_name = f"{airflow_file_path}/data/{parquet_file}"
destination_blob_name = f"raw_data/{year_folder}/{month_folder}/{parquet_file}"

GCP_PROJECT = os.environ.get("GCP_PROJECT_ID")
GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")
GCP_DATASET = os.environ.get("GCP_DATASET")

# Taskflow DAG
@dag(
    dag_id = "goodreads_main_dag",
    schedule = '0 12 * * *',
    max_active_runs = 1,
    start_date = start,
    catchup = True,
    default_args = {
        "retries": 1,
        "retry_delay": pendulum.duration(seconds = 100)
    },
)
def goodreads_etl_taskflow():
    @task.bash
    def goodreads_extract_data():
        return f"python {airflow_file_path}/python_scripts/goodreads_scrape.py"
    @task
    def goodreads_load_data(bucket,source_file,destination_blob):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket)
        blob = bucket.blob(destination_blob)

        blob.upload_from_filename(source_file)
    @task.bash
    def remove_local_file_data():
        return f"rm {source_file_name}"

    delete_external_table = BigQueryInsertJobOperator(
    task_id="delete_external_job",
    configuration = {
        "query": {
            "query": "{% include 'sql/drop_external.sql' %}",
            "useLegacySql": False,
        }
    },
    params = {
        "project_id": GCP_PROJECT,
        "dataset_name": GCP_DATASET,
        "external_table_name": external_table,
    }   
    )

    create_insert_external_table = BigQueryCreateExternalTableOperator(
        task_id="create_external_job",
        table_resource = {
            "tableReference": {
                "projectId": GCP_PROJECT,
                "datasetId": GCP_DATASET,
                "tableId": external_table,
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{blob_name}/{parquet_file}"]
            },
        },
    )

    internal_table_insert = BigQueryInsertJobOperator(
        task_id="internal_table_insert_job",
        configuration = {
            "query": {
                "query": "{% include 'sql/table_insert.sql' %}",
                "useLegacySql": False,
            }
        },
        params = {
            "project_id": GCP_PROJECT,
            "dataset_name": GCP_DATASET,
            "external_table_name": external_table,
            "table_name": table,
        }   
        )

    # Map taskflow to legacy
    goodreads_extract = goodreads_extract_data()
    goodreads_load = goodreads_load_data(GCS_BUCKET,source_file_name,destination_blob_name)
    remove_local_file = remove_local_file_data()

    # Establish dependencies
    goodreads_extract >> goodreads_load >> remove_local_file  >> delete_external_table >> create_insert_external_table >> internal_table_insert

goodreads_etl_taskflow()