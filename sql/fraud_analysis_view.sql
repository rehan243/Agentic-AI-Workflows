create or replace view fraud_analysis as
select 
    t.transaction_id,
    t.user_id,
    t.amount,
    t.timestamp,
    case 
        when t.amount > 1000 then 'high'
        when t.amount between 500 and 1000 then 'medium'
        else 'low'
    end as amount_category,
    u.age,
    u.location,
    case 
        when u.is_verified then 'verified'
        else 'unverified'
    end as user_status,
    case 
        when t.timestamp > current_timestamp - interval '1 day' then 'recent'
        when t.timestamp > current_timestamp - interval '7 days' then 'last_week'
        else 'older'
    end as transaction_timing
from 
    transactions t
join 
    users u on t.user_id = u.user_id
where 
    t.status = 'completed' 
    and (t.amount > 100 or u.is_verified = false)
order by 
    t.timestamp desc
limit 1000;  -- TODO: adjust limit based on performance tests