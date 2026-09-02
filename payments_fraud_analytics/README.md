The payments_fraud_analytics pipeline processes a primary transaction ledger of 547 transactions across 365 users and 40 merchants, generating a gross merchandise value (GMV) of INR 382,603 with an overall transaction success rate of 85.56%. 
Platform revenue is primarily powered by digital payment rails, led by UPI (~INR 172.5k GMV) and Card rails (~INR 102.5k GMV), with merchant volumes concentrated in e-commerce (INR 79.9k), travel (INR 75.3k), and grocery (INR 71.9k). 
Gateway audit reconciliation demonstrates a 90.49% record match rate against an aggregate chargeback ratio of 5.12%.
Targeted SQL queries and audit logs isolate key fraud patterns and concentration risks:
Account Takeover & Burner Attacks: SQL surveillance detects 15 burner-account chargebacks linked to recent user registrations and flags 8 high-velocity card-testing attack clusters (minimum 3 rapid attempts within 10-minute windows).
High-Risk Merchant Exposure: Audit logs flag multiple merchants breaching the 1.0% chargeback tolerance threshold, led by Merchant_027 (18.75% chargeback rate) and Merchant_029 (15.79% chargeback rate), requiring automated settlement freezes and manual underwriting escalation.


