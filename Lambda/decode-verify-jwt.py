# Copyright 2017-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under the License.

import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
import secrets

region = secrets.region
userpool_id = secrets.userpool_id
app_client_id = secrets.app_client_id
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def lambda_handler(event, context):
    token = event['token']
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
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims
        
# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    event = {'token': 'eyJraWQiOiIxMEgxNFZBWDlGRnRUV29Fa3k5akQrNGZRM1lKOExjWkltMWI3REZrQ2lrPSIsImFsZyI6IlJTMjU2In0.eyJhdF9oYXNoIjoid0plemJWUVFpd0tlWEFiZ1EteDdWdyIsInN1YiI6IjVjNmMwODZiLTNhNDAtNGVhMy04ZjE4LWQxMmI2NmNhMjgxMSIsImF1ZCI6IjJkaDNrYmhpcmI2cWowbHFqN2Vkc250bzZkIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImV2ZW50X2lkIjoiMWQyZDdmYjAtMTJmOS00M2RmLTkyY2UtOGVjOGY2OTU5OWJiIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE1ODYyMTU5MjQsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX0E1cjBTcEpUNSIsImNvZ25pdG86dXNlcm5hbWUiOiI1YzZjMDg2Yi0zYTQwLTRlYTMtOGYxOC1kMTJiNjZjYTI4MTEiLCJleHAiOjE1ODYyMTk1MjQsImlhdCI6MTU4NjIxNTkyNCwiZW1haWwiOiJ0ZXN0ZG9lcjFAYmVydHdhZ25lci5jb20ifQ.ie70sp2MSDz_UoSacRvCNoQTolntQZuX26WXUh_UCzUYhQxROihH9SDcXxCEyCentNRbQFGP58AunArBDEXTX6tHb1LRv8M3DD-h9Q_5yq6IlLrq-RLTaHdlZodndw06-6Y6SGbgRMiJrNoFz5wdMyh9Fyc_TXsZdQEmSwEiCC1U-pcwN6i3YIXIHorFM4VuYGBITP9lrLv72gfKWHAqHQowOHMWFdgID-laFvGMKSrl05RgJIxyIy4ZI0zHH_-FLDxWdnpdSF-1zxA9YRg-op27d7PeCxYAV2-6eDVPaOZVI4mYM8hDfGux2RVmploXDMZClPD_WjooPWkp6VRibg'}
    lambda_handler(event, None)
