import jwt
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from google.auth.transport import requests
from google.oauth2 import id_token

# Cloud Schedulerの `対象` を設定
# 指定しなかった場合、Cloud Scheduler はデフォルトで、リクエスト パラメータを含む URL 全体をオーディエンスとして使用
# CLIENT_ID = 'https://***.jp.ngrok.io/api/command-with-auth'
CLIENT_ID = 'https://***.jp.ngrok.io/api/command'


class HealthCheckView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'ham': 'spam'
        })


class CommandView(View):
    def get(self, request, *args, **kwargs):
        print(request)

        authz_header = request.headers.get('Authorization')  # => Bearer ***
        received_id_token = authz_header.replace('Bearer', '').lstrip()  # => IDトークンだけになる
        print(received_id_token)

        # JWTのヘッダを検証なしでdecode
        print(jwt.get_unverified_header(received_id_token))
        # => {'alg': 'RS256', 'kid': '***', 'typ': 'JWT'}

        # JWTのペイロードを検証なしでdecode
        print(jwt.decode(received_id_token, options={"verify_signature": False}))
        # =>
        # {
        #   'aud': 'https://***.jp.ngrok.io/api/command',
        #   'azp': '***',
        #   'email': '***@ringo-tabetter-devops.iam.gserviceaccount.com',
        #   'email_verified': True,
        #   'exp': 1664324413,
        #   'iat': 1664320813,
        #   'iss': 'https://accounts.google.com',
        #   'sub': '***'
        # }

        # google-authによる検証
        id_info = id_token.verify_oauth2_token(received_id_token, requests.Request(), CLIENT_ID)
        print(id_info)
        # =>
        # 検証に成功した場合、jwt.decode と同じ結果が得られる
        # 検証に失敗した場合
        # ValueError: Could not verify token signature.
        # Token has wrong audience https://***.jp.ngrok.io/api/command-with-auth, expected one of ['https:***']

        return JsonResponse({
            'foo': 'bar'
        })


class CommandWithAuthView(View):
    def get(self, request, *args, **kwargs):
        authz_header = request.headers.get('Authorization')
        received_id_token = authz_header.replace('Bearer', '').lstrip()

        try:
            id_info = id_token.verify_oauth2_token(received_id_token, requests.Request(), CLIENT_ID)
            print(id_info)

            return JsonResponse({
                'status': 'success'
            })
        except ValueError as e:
            print(e)
            return JsonResponse({
                'status': 'unauthorized'
            })
