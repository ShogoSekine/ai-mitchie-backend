import os
import json
import urllib.request
import urllib.error
import traceback

def lambda_handler(event, context):
    try:
        # 1. 受信データの解析
        # HTTP API の場合、body が None の場合があるため対策
        body_str = event.get('body', '{}')
        if not body_str: body_str = '{}'
        body = json.loads(body_str)
        user_message = body.get('message', 'テスト送信')

        # 2. Gemini API 設定
        api_key = os.environ.get('GEMINI_API_KEY')
        # あなたのリストで確認できた 2.5-flash を使用
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": f"君は全肯定トレーナーのMitchieだ。短く褒めて。 ユーザーの報告: {user_message}"}]}]
        }
        
        # 3. リクエスト実行
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}, 
            method='POST'
        )

        with urllib.request.urlopen(req) as res:
            response_body = res.read().decode('utf-8')
            data = json.loads(response_body)
            # Gemini の回答を抽出
            mitchie_text = data['candidates'][0]['content']['parts'][0]['text']
            return create_response(200, mitchie_text.strip())

    except urllib.error.HTTPError as e:
        # Google API からのエラー (400, 429, 404など)
        err_msg = e.read().decode('utf-8')
        return create_response(e.code, f"Google API Error: {err_msg}")
    except Exception as e:
        # Python 自体のエラー (KeyError, JSONDecodeErrorなど)
        stack_trace = traceback.format_exc()
        return create_response(500, f"Lambda Internal Error: {str(e)}\n{stack_trace}")

def create_response(status, text):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"reply": text}, ensure_ascii=False)
    }
