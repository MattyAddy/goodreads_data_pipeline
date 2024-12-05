{{
    config(
        materialized = "table"
    )
}}

{{ dbt_date.get_date_dimension("1500-01-01", "2049-12-31") }}