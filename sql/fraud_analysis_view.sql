create or replace view fraud_analysis as
select 
    transaction_id,
    user_id,
    transaction_amount,
    transaction_date,
    case 
        when transaction_amount > 1000 then 'high_value'
        when transaction_amount between 500 and 1000 then 'medium_value'
        else 'low_value'
    end as value_category,
    case 
        when transaction_date >= current_date - interval '30 days' then 'recent'
        else 'older'
    end as transaction_age
from 
    transactions
where 
    transaction_status = 'completed'
    and user_id is not null
    and transaction_amount > 0;

-- this is to help analyze patterns in high-value transactions over time
-- TODO: consider adding additional filters for specific user segments

create index idx_user_id on transactions(user_id);
create index idx_transaction_date on transactions(transaction_date);

-- make sure to update this view if transaction logic changes
-- we might need to join with user data for more insights later