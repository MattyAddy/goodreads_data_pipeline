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


I then created the VM instance in the Console with the following configuration:
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

## Containerization

Docker is the tool to containerize the services needed to run this pipeline. Docker allows us to create an isolated, consistent, and reproducible environment for every pipeline run. When there are many services involved, such as when running Airflow, its helpful to have a service manage some of the complexity for the engineer. 

There are two files involved in this case, a Dockerfile and a Docker Compose YAML file. The Dockerfile will build the image which contain the instructions to build the container which the Airflow DAG will be running on. The Docker Compose file contains the rest of images for the Airflow services such as the web scheduler and web app. For this project, the Dockerfile will be called from within the Docker Compose file.

## Orchestration

Orchestration for this project will be handled by Airflow running on the Docker containers defined above. In simple terms, Airflow allows us to create and schedule the tasks in the pipeline via code. This is handled in the DAG (Directed Acyclic Graph) which defines the workflow's configuration and dependencies. The following screenshot outlines the 6 tasks in the DAG:

![image](https://github.com/user-attachments/assets/e0ebd828-afab-4152-bfc2-ec4930236100)

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

## Storage

The data lake in which to store the raw Parquet files from the scraper is Google Cloud Storage. As mentioned prior, the container was deployed via Terraform. the files are stored in the following folder hierarchy:

- Year
- 

## Data Warehouse 






## Transformation








## Visualization








## Conclusion
