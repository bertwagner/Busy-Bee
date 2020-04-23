import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
import boto3

ssm = boto3.client('ssm')
userpool_id = ssm.get_parameter(Name='user-pool-id', WithDecryption=True)['Parameter']['Value']
app_client_id = ssm.get_parameter(Name='app-client-id', WithDecryption=True)['Parameter']['Value']
region = "us-east-1"

keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def lambda_handler(event, context):
    token = event['queryStringParameters']['id_token']
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i 
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return {
            "statusCode":200,
            "body": claims
        }
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    return {
            "statusCode":200,
            "body": claims
        }
        
# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    event = {
        "queryStringParameters": { 
            "id_token": "eyJraWQiOiJldWVKV1JjeHhYSmVsSTNZV1Y2TnAwRWJkdVpqN2hqMEJWUmtUSEJhSFM4PSIsImFsZyI6IlJTMjU2In0.eyJhdF9oYXNoIjoiNjcxNWZKMVhyb2dwcUJoVEFNZnVQQSIsInN1YiI6ImM5MDcxYWU5LWZiNGUtNDRiZC1iZTg0LWMyZmYwZDI1ZWY0MSIsImF1ZCI6IjZubThpMzdrMmdzbmloaGFlaTI3MTFkNmhvIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNTg2NjA1MjkwLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9CQVdWekZaQVciLCJjb2duaXRvOnVzZXJuYW1lIjoiYzkwNzFhZTktZmI0ZS00NGJkLWJlODQtYzJmZjBkMjVlZjQxIiwiZXhwIjoxNTg2NjA4ODkwLCJpYXQiOjE1ODY2MDUyOTEsImVtYWlsIjoiYnVzeWJlZTFAYmVydHdhZ25lci5jb20ifQ.dtM7o7DwVvqZvgqmCHQYCDopAtZa-9s3DGNMEftYADz1D9IQG4vqJBDSnIQ-FsfTInzZ75GcvPorNw46V2oZx-rMFGGD7TcbPnti__AuAMwdJEDRLsH8ZKMfHp7eQCIhz35JIgIHP4m3lFsd1txvaKXSJ-FXmioMJWor4EF9pmXF_OJCjPSvyOr18KJNmHMa1sr0peZZMc1Jn2FiwomDiJsvsukd6gBuiOakmU4lp3t2AuQTIaRl6RPpFpi1lyU0bOoiidy_Gu4Lzad9Z3QYbe7umZuOEmQFnuA8SoxRbzi5kWRYbcNpREt6R_gmegwomqjcEC3GMbgc8IZURjVFHw", 
            "access_token": "eyJraWQiOiIwbmtIYTdTOXhmUDhEcThcLytubE91NFl6dXpYYlFValwvN0djWUczQUxZdU09IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJjOTA3MWFlOS1mYjRlLTQ0YmQtYmU4NC1jMmZmMGQyNWVmNDEiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6Im9wZW5pZCBlbWFpbCIsImF1dGhfdGltZSI6MTU4NjYwNTI5MCwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfQkFXVnpGWkFXIiwiZXhwIjoxNTg2NjA4ODkwLCJpYXQiOjE1ODY2MDUyOTEsInZlcnNpb24iOjIsImp0aSI6IjFhNzU3YWJmLTYyNzItNDVmYy1hNDdmLTQyNGI5MmYwOTMwMyIsImNsaWVudF9pZCI6IjZubThpMzdrMmdzbmloaGFlaTI3MTFkNmhvIiwidXNlcm5hbWUiOiJjOTA3MWFlOS1mYjRlLTQ0YmQtYmU4NC1jMmZmMGQyNWVmNDEifQ.OZvuaqkrrooUmE0v2UUBpLSRU4nLSvyEKwoMPkwvoSS42Kc8Xj-3ybmZrENQiL9kw7QsaYWDriPEqcEWKibZST0Zu0ZCFSJktDl2ZLeH13GMPhzsuqntbE09MCBBHsOXfloYLScns7tslH9yEmWAluCmPJLhplIXWCqE0hplUcMXpXj8rlsJ1hGhJS8SF58ka0H9fqanHrZsnUSkaC0LbGCGFkBd93dR5V8b4WS0-JhdvlZ-iSFroRG4EMAylstjGt3OeyWbTNeWwZwmhuk6qOx3yw2wYek2oxN_cLKtnxWIe5Et0mlUeM93OVL6oFohDuYE_jqnFWKq-KBDmYaQ1A",
            "expires_in":"3600",
            "token_type":"Bearer"
            }
        }
    
    lambda_handler(event, None)
