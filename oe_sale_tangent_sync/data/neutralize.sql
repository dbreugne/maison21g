-- neutralize tangent api configuration
UPDATE tangent_api_config
SET 
    endpoint_url = 'https://staging.mbs-posapi.synthesis.bz',
    username = '33000009',
    machine_id = '33000009',
    password = 'maisontest@123'
WHERE active = true;
