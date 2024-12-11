{%- macro top_shelf_logic(averagerating,ratingcount,reviewcount) -%}

    case 
        when averagerating >= 4.5
            and ratingcount >= 100000
            and reviewcount >= 10000
        then TRUE
        else FALSE
    end

{%- endmacro %}