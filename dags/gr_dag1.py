import os
import pendulum
from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator, BigQueryCreateExternalTableOperator
from google.cloud import storage

start = pendulum.datetime(2024, 11, 9, tz="UTC")
airflow_file_path = os.environ.get("AIRFLOW_HOME","/opt/airflow/")

# Directory variables
execution_date_string = "{{ data_interval_start.strftime('%Y%m%d') }}"
year_folder = "{{ data_interval_start.strftime('%Y') }}"
month_folder = "{{ data_interval_start.strftime('%m') }}"
parquet_file = f"goodreads_{execution_date_string}.parquet"

# File names
source_file_name = f"{airflow_file_path}/data/{parquet_file}"
destination_blob_name = f"raw_data/{year_folder}/{month_folder}/{parquet_file}"

# Google environment variables
GCP_PROJECT = os.environ.get("GCP_PROJECT_ID")
GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")
GCP_DATASET = os.environ.get("GCP_DATASET")
#GCP_CONNECTION = os.environ.get("AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT")

external_table = "full_external_stg"
blob_name = f"madams-terraform-book-data-lake/raw_data/{year_folder}/{month_folder}"

# Taskflow DAG
@dag(
    schedule_interval = None,
    start_date = start,
    catchup = False,
    tags=['example'],
)
def goodreads_etl_taskflow():
    @task.bash
    def goodreads_extract_data():
        # return f"python {airflow_file_path}/python_scripts/test_scrape.py > {source_file_name}"
        return f"python {airflow_file_path}/python_scripts/test_scrape.py"
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

    # create_insert_external_table = BigQueryCreateExternalTableOperator(
    #     task_id = "create_external_table",
    #     destination_project_dataset_table = f"{GCP_DATASET}.{external_table}",
    #     bucket = GCS_BUCKET,
    #     #source_objects = [f"{blob_name}/goodreads*.parquet"],
    #     source_objects = [f"{blob_name}/goodreads_20241118"],
    #     )

    create_insert_external_table = BigQueryCreateExternalTableOperator(
        task_id="create_external_table",
        table_resource = {
            "tableReference": {
                "projectId": GCP_PROJECT,
                "datasetId": GCP_DATASET,
                "tableId": external_table,
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{blob_name}/goodreads*.parquet"],
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
        }   
        )

    # Establish dependencies
    goodreads_extract = goodreads_extract_data()
    goodreads_load = goodreads_load_data(GCS_BUCKET,source_file_name,destination_blob_name)
    remove_local_file = remove_local_file_data()

    goodreads_extract >> goodreads_load >> remove_local_file  >> delete_external_table >> create_insert_external_table

    # Establish dependencies
    # chain(
    #     goodreads_extract_data(),
    #     goodreads_load_data(GCS_BUCKET,source_file_name,destination_blob_name),
    #     remove_local_file_data()
    #     )

goodreads_etl_taskflow()
