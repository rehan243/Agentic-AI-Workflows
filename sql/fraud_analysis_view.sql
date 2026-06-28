CREATE OR REPLACE VIEW fraud_analysis AS
SELECT 
    t.transaction_id,
    t.user_id,
    t.amount,
    t.transaction_date,
    a.account_type,
    CASE 
        WHEN t.amount > 1000 THEN 'high_value'
        WHEN t.amount BETWEEN 500 AND 1000 THEN 'medium_value'
        ELSE 'low_value'
    END AS transaction_value_category,
    CASE 
        WHEN t.transaction_date < NOW() - INTERVAL '30 days' THEN 'old_transaction'
        ELSE 'recent_transaction'
    END AS transaction_age_category
FROM 
    transactions t
JOIN 
    accounts a ON t.user_id = a.user_id
WHERE 
    t.status = 'completed'
    AND a.account_status = 'active';

-- TODO: add more filters for specific fraud indicators in the future

-- this view will help in generating reports for potential fraud cases
-- consider adding indexes to the underlying tables for performance improvements