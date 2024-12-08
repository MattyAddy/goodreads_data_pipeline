{{
    config(
        materialized = 'table'
    )
}}

with cte_dedupe as (
select
    title,
    author,
    genre,
    numberofpages,
    case
        when publishdate <> "None" then parse_date('%B %d, %Y', publishdate)
        else NULL
    end as publishdate,
    ratingcount,
    averagerating,
    reviewcount,
    isbn,
    url as bookurl,
    row_number() over(partition by title,author) as row_num
from {{ source('dbt_staging','book_bronze_stg') }}
where title <> "None"

)

select
    {{ dbt_utils.generate_surrogate_key(['title','author']) }} as book_id,
    {{ clean_text("title") }} as title,
    {{ clean_text("author") }} as author,
    {{ dbt.safe_cast("isbn", api.Column.translate_type("string")) }} as isbn,
    {{ dbt.safe_cast("genre", api.Column.translate_type("string")) }} as genre,
    {{ dbt.safe_cast("publishdate", api.Column.translate_type("date")) }} as publishdate,
    {{ dbt.safe_cast("numberofpages", api.Column.translate_type("integer")) }} as numberofpages,
    {{ dbt.safe_cast("ratingcount", api.Column.translate_type("integer")) }} as ratingcount,
    {{ dbt.safe_cast("averagerating", api.Column.translate_type("decimal")) }} as averagerating,
    {{ dbt.safe_cast("reviewcount", api.Column.translate_type("integer")) }} as reviewcount,
    {{ dbt.safe_cast("bookurl", api.Column.translate_type("integer")) }} as bookurl,
from cte_dedupe
where row_num = 1