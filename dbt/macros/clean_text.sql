{% macro clean_text(value) -%}

{% set value = dbt.safe_cast(value, api.Column.translate_type("string")) %}

replace(
    replace(
        replace({{ value }},"&apos;", "\'"),
            "&amp;", "&"),
        "&quot;", "\"")

{%- endmacro %}
