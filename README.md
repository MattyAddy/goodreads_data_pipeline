# Goodreads Data Pipeline

## Introduction
Reading is one my favorite activies. Whether I'm learning about art history or binging a fantasy series, I've always enjoyed the educational and entertainment benefits of reading each day. Though I enjoy the act, I've always struggled in finding that "next" book to read. I currently track my reading activity through Goodreads, which is part social media and part book database. This is also the place where I sift through reviews on unread books to decide which book to buy next. This is a time consuming process however so I wanted to create a more concise solution with a better signal to noise ratio. 

The following project is a data pipeline which ingests, loads, and transforms book data on a daily cadence. A dashboard then consumes this data and provides actionable insights so that users can spend less time researching and more time reading.

This project leverages I've learned in the Data Engineering Zoomcamp. Thank you to Alexey and team for the content!

## Architecture
The architecture for this pipeline follows an ELT approach which is short for Extract, Load, and Transform. At a high level, the pipeline conducts the following:
1. Extract data via web scraping
2. Load to data lake
3. Load to data warehouse
4. Transform warehouse data
5. Visualize


![Goodreads Data Pipeline](https://github.com/user-attachments/assets/4c38c82c-8b21-4ae9-9bc2-8b7f7bca286f)

**Cloud Vendor**: Google Cloud Plaform <br />
**Infrastructure Deployment**: Terraform <br />
**Compute**: GCP VM Instance and BigQuery Compute <br />
**Containerization**: Docker Compose <br />
**Orchestration**: Airflow <br />
**Ingestion**: Beautiful Soup Web Scraper <br />
**Storage**: GCP Cloud Storage <br />
**Transformation**: dbt Cloud <br />
**Reporting**: Looker Studio <br />


## Prerequisites

- Google Cloud account
- dbt Cloud account
- Github account
- Python 3
- Google Cloud CLI
- Git Bash
- Visual Studio Code

## Web Scraping

Before diving into the pipeline, I needed to get a working script to ingest data from Goodreads and drop to a file. Ideally I could use their API, but the company recently stopped issuing API keys. With that in mind, I started learning about webscraping. Though its not nearly as efficient, we can still extract meaningful data in a reasonble amount of time since the volume is so low. I decided to focus specifically on the "Most Read This Week" books per genre. I started with the genre page and extraced just the urls for each of the 40 genres.

If I navigate to one to a genre, we can see 100 books on the page. When selecting an individual book, we can now see some meaningful data such as Publishing Date, Author, Number of Page, and Review data. Each book will ultimately be the grain of the dataset. To illustrate, this is how one example will appear if I save as a CSV:





At a high level, this is what the scraper is doing:

Extract list of genre URL's from the HTML and add to a list
Loop through the list and extract the book URLS from each and add to another list
Perform the scraping via the BLANK function and drop to a json file
Add each json to a list and generate one pandas dataframe
Conver the pandas dataframe to a parquet file



## Infrastructure

All of the core resources for this project are provided by Google Cloud: <br />
- VM Instance  <br />
- Cloud Storage <br />
- BigQuery  <br />

### VM Instance

The nucleus of this project is a virtual machine created via the Console. Before spinning up the resource, I generated an SSH key which allows me to remotely access the VM via Git Bash and VS Code:

- Navigate to the hidden directory .ssh/ from the root directory  <br />
- Run the following to generate the keypair: `ssh-keygen -t rsa -f ~/.ssh/gcp_key -C madams`  <br />

![image](https://github.com/user-attachments/assets/943d24b6-927e-43e6-9617-7bc64551c3f8)

- Copy the public key and paste in Google Cloud under Metadata/SSH Keys:

<img src="https://github.com/user-attachments/assets/54e40b9d-60e7-45cd-8c5e-fb2f2afce237" width="700" />


The VM instance is now created in the Console with the following configuration:

- Machine type: e2-standard-4
- Boot disk
    - Operating system: Ubuntu<br />
    - Version: Ubuntu 20.04 LTS <br />
    - Size: 32 GB <br />

<img src="https://github.com/user-attachments/assets/8ea21127-9118-4533-937d-74e330126241" width="700" />

To access the machine via SSH:

- Create a config file in the same .ssh/ directory using: `touch config`
- Open VS Code with the .ssh directory:` code .`
- Populate the file as follows:
```
Host instance-madams-1
    HostName 34.74.218.92
    User madams
    IdentityFile c:/Users/matta/.ssh/gcp_key
```
The HostName IP is found under the VM Instance for External IP:  <br />

<img src="https://github.com/user-attachments/assets/3a8f8329-26b7-489d-8b00-8259bbaa24a8" width="300" />

- Run the following in root directory: `ssh instance-madams-1`

![image](https://github.com/user-attachments/assets/b10fd753-f77e-4ec7-913d-2496262f200f)

The VM can also be connected to via VS Code in order to access the pipeline scripts 

![image](https://github.com/user-attachments/assets/c50a5045-ce2c-4479-bbf7-923c669eaa25)

I then installed the following on the VM:
- Anaconda
- Docker
- Docker Compose
- Terraform
- Airflow

### Terraform Deployment

The remaining resources to deploy are GCP Cloud Storage and BigQuery. These resources will be deployed via Terraform from the VM. Terraform is an Infrastructure as Code tool (IaC) which allows for code-based deployment without neeeding to access the Console. One can consistently deploy resources with the exact configuration each time with the ability to store those files in source control. The two files `main.tf` and `variables.tf` are found under this project's `terraform` directory.

The process to setup Terraform and deploy:

- Create Service Account in the Console:
![image](https://github.com/user-attachments/assets/9cf6caff-1637-4589-95e8-5dcf0c55abf7)


- Assign the following roles to the account:
    - Compute Admin
    - Storage Admin
    - BigQuery Admin
  
- Under Service Acconts/Keys, Add Key as a JSON file

![image](https://github.com/user-attachments/assets/b1c6e462-df2a-4709-90e6-65f356114a75)

- Create new hidden directory in the VM from the root directory: `mkdir .google`
- Create subdirectory: `mdkir credentials`
- Create empty file: `google_credentials.json`
- Edit the file: `nano google_credentials.json`
- Copy the JSON file from local downloads into the empty file on the VM:
- 
<img width="500" alt="Screenshot 2024-12-15 145358" src="https://github.com/user-attachments/assets/2f742b23-2cff-494f-a046-ff35d78b1ccc" />

- Export environment variable: `export GOOGLE_APPLICATION_CREDENTIALS=~/.google/credentials/google_credentials.json`
- Authenticate service account: `gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS`
- Add credential file path to the variables Terraform file
- Run the following inside of terraform directory to initialze and deploy resources:

```
terraform init
terraform plan
terraform apply
```
*Note: The initialization step only needs run once

## Containerization

Docker is the tool to containerize the services needed to run this pipeline. Docker allows us to create an isolated, consistent, and reproducible environment for every pipeline run. When there are many services involved, such as when running Airflow, its helpful to have a service manage some of the complexity for the engineer. 

There are two files involved in this case, a Dockerfile and a Docker Compose YAML file. The Dockerfile will build the image which contain the instructions to build the container which the Airflow DAG will be running on. The Docker Compose file contains the rest of images for the Airflow services such as the web scheduler and web app. This file is pulled from Airflow's site and then modified with my own directories and environment variables. The Dockerfile will be called from within the Docker Compose file so that everything can be built with one command.

To run thse containers, navigate to the `airflow` directory and run the following in order:

```
docker-compose build
docker-compose up airflow-init
docker-compose up
```
*Note: The build step only needs to be run once unless the Dockerfile needs to be changed in the future

We can now see the active containers by running: `docker-compose ps`

## Orchestration

Orchestration for this project will be handled by Airflow running on the Docker containers defined above. In simple terms, Airflow allows us to create and schedule the tasks in the pipeline via code. This is handled in the DAG (Directed Acyclic Graph) which defines the workflow's configuration and dependencies. The following screenshot outlines the 6 tasks in the DAG:

![image](https://github.com/user-attachments/assets/b6ca3a4d-f410-4c98-829e-3b58074185e9)

This screenshot comes from the Airflow UI which is running on one of the containers defined above. It can be accessed by:
- Forward port 8080 in VS Code
![image](https://github.com/user-attachments/assets/ba5dcfde-95ca-4df7-97b2-16f529d7bd41)

- Navigate to http://localhost:8080/home on the local machine

![image](https://github.com/user-attachments/assets/71e62614-dd6b-4954-b22c-c6d4e3d7e57d)

As mentioned previously there are 6 tasks in this DAG:
- Extract data: Run BASH command to kick off the python webscraping script which drops parquet file to `/data` directory
- Load data: Upload parquet file from `/data` to Google Cloud Storage
- Remove local file: Run BASH command to remove from `/data`
- Delete external table: Drop external table in BigQuery using SQL script
- Create and insert external table: Create new external table in BigQuery and insert the contents of the daily parquet file
- Internal table insert: Load data from external table to internal staging table in BigQuery

The DAG runs on a daily schedule at 12:00 UTC time. The last 12 runs can be seen here. The final 4 runs represent the full dataset being pulled at the scheduled time:

![image](https://github.com/user-attachments/assets/7dddd566-7a10-4829-9e1e-6bda0f08745b)

## Storage

The data lake in which to store the raw Parquet files is Google Cloud Storage. As mentioned prior, the container was deployed via Terraform. The files are stored using the following folder hierarchy:

![image](https://github.com/user-attachments/assets/7c7c0e52-a3b0-4825-ae53-fbd70884113c)

## Data Warehouse 

BigQuery is used for the data warehouse. This is where we will perform the data modeling and additional transformations to curate a more impactful dataset. The Terraform script defined two different datasets: goodreads_db_raw and goodreads_db. BQ "datasets" are the equivalent to schemas in other databases such as SQL Server. Heres a quick query to show the raw data after it initially lands:

![image](https://github.com/user-attachments/assets/c88fcc3a-ed80-4582-baf2-2875caad2770)

![image](https://github.com/user-attachments/assets/d061ed02-399f-4b07-b9ab-4f123851782a)

BigQuery is also partially responsible for the compute in this pipeline. When the dbt models run, dbt will be sending querires to BigQuery to actually run the transformations. 

## Transformation and Data Modeling

After the data arrives in BigQuery, dbt Cloud is used to both transform and model the data. The data itself follows a medallion architecture with three layers: bronze, silver, and gold. 

- Bronze: Initial state coming from data lake
- Silver: Dataset that undergoes deduplication, cleaning, data type casting, and creating a unique primary key
- Gold: Incremntal data coming from silver layer

Once the data is ready in the gold layer, we can do some lightweight dimensional modeling following the Kimball approach. This involves separating out numerical data into a fact table and descriptive characterisics about those facts into dimension tables. The Kimball method follows this four-step design process:

- Choose the business problem
    - How can we provide actionable data to help readers select their next book?
- Define the grain of the data
    - 1 book per record
- Select the dimensions
    - Author
    - Genre
    - Date
- Select the facts
    - Number of pages
    - Rating Count
    - Average Rating
    - Review Count
    - Top Shelf Indicator

This process will be relatively straightforward since there is only 1 dataset, but these principles are able to scale to much larger projects. The end product for the data model is represented as such:









From start to finish, here is the data lineage from dbt.






We can see that date is missing since it is generated through macro provided by the calogica/dbt_date package







The code to perform each of these steps are found under `dbt/models/` of this repo.


## Visualization

The finalized output is a two page Looker Studio dashboard.





## Conclusion
