{{
    config(
        materialized = 'table'
    )
}}

{% set now = modules.datetime.datetime.now() %}

select distinct
    {{ dbt_utils.generate_surrogate_key(['genre']) }} as genre_dim_id,
    genre,
    cast('{{ now }}' as datetime) as insertdatetime
from {{ ref('book_gold') }}