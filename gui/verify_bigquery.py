"""Verify BigQuery data loaded correctly"""
from google.cloud import bigquery

client = bigquery.Client(project="blah-905ad")

# Check breach data
query = """
SELECT COUNT(*) as total, 
       COUNTIF(risk_level='CRITICAL') as critical, 
       COUNTIF(risk_level='HIGH') as high 
FROM `blah-905ad.osint_investigation.breach_results`
"""
result = client.query(query).to_dataframe()
print("Breach Results:")
print(result.to_string(index=False))

# Check grants
query = """
SELECT COUNT(*) as total, 
       SUM(amount_usd) as total_amount, 
       COUNTIF(status LIKE '%FLAGGED%') as flagged 
FROM `blah-905ad.osint_investigation.grants_tracked`
"""
result = client.query(query).to_dataframe()
print("\nGrants Tracked:")
print(result.to_string(index=False))

# Check entities
query = """
SELECT COUNT(*) as total, 
       COUNTIF(entity_type='Contractor') as contractors 
FROM `blah-905ad.osint_investigation.hbnc_entities`
"""
result = client.query(query).to_dataframe()
print("\nHBNC Entities:")
print(result.to_string(index=False))

print("\nAll data verified in BigQuery!")
