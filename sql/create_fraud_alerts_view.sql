-- this view will help us identify potential fraud alerts from transactions
-- we are looking for suspicious patterns in transaction amounts and frequencies

create or replace view fraud_alerts as
select 
    t.user_id,
    t.transaction_id,
    t.amount,
    t.transaction_date,
    count(t.transaction_id) over (partition by t.user_id order by t.transaction_date 
        rows between unbounded preceding and current row) as transaction_count,
    lag(t.amount) over (partition by t.user_id order by t.transaction_date) as previous_amount
from 
    transactions t
where 
    t.amount > 1000  -- threshold for high-value transactions
    or 
    (t.amount < 50 and t.transaction_date > current_date - interval '30 days')  -- potential low-value fraud

-- we can add more filters or join with other tables to enrich our data later
-- TODO: consider adding geo-location data to enhance fraud detection capabilities

-- now let's get the alerts based on the defined criteria
select 
    user_id,
    transaction_id,
    amount,
    transaction_date,
    transaction_count,
    previous_amount
from 
    fraud_alerts
where 
    transaction_count > 5  -- flagging users with too many transactions
    or 
    (previous_amount is not null and amount > previous_amount * 2);  -- flagging sudden spikes in transaction amounts