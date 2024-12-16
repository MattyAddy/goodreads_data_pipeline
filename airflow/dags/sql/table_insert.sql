CREATE TABLE IF NOT EXISTS {{ params.dataset_name }}.{{ params.table_name }} (
        Title STRING, 
        Author STRING,
        Genre STRING,
        NumberOfPages STRING,
        PublishDate STRING,
        RatingCount STRING,
        AverageRating STRING,
        ReviewCount STRING,
        ISBN STRING,
        URL STRING
);
 
TRUNCATE TABLE {{ params.dataset_name }}.{{ params.table_name }};

MERGE {{ params.dataset_name }}.{{ params.table_name }} t
USING {{ params.dataset_name }}.{{ params.external_table_name }} s
ON t.Title = s.Title
WHEN NOT MATCHED THEN INSERT ROW;