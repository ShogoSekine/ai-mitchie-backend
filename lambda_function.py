import os
import json
import urllib.request
import urllib.error

def lambda_handler(event, context):
    # 1. アプリからの入力を取得
    try:
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '今日もアプリを開いたよ！')
    except Exception:
        user_message = "今日もアプリを開いたよ！"

    # 2. 設定
    api_key = os.environ.get('GEMINI_API_KEY')
    # 安定版の latest を指定
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    system_instruction = "あなたは全肯定トレーナーのMitchieです。短く2文で褒めてください。"
    payload = {
        "contents": [{"parts": [{"text": f"{system_instruction}\nユーザー: {user_message}"}]}]
    }
    headers = {'Content-Type': 'application/json'}

    # 3. リクエスト実行
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req) as res:
            response_body = res.read().decode('utf-8')
            data = json.loads(response_body)
            mitchie_text = data['candidates'][0]['content']['parts'][0]['text']
            
            return create_response(200, mitchie_text.strip())

    except urllib.error.HTTPError as e:
        # --- ここで各エラーコードを拾います ---
        status_code = e.code
        error_info = e.read().decode('utf-8')
        
        if status_code == 429:
            msg = f"【Error 429】おっと、今はパワーが溢れすぎて制限がかかっちゃったみたいだ！少し時間を置いてからまた話そうぜ！"
        elif status_code == 404:
            msg = f"【Error 404】Mitchieの脳（モデル名）が見つからないみたいだ。設定を確認してくるから待っててくれ！"
        elif status_code == 403:
            msg = f"【Error 403】APIキーがうまく認識されないぞ。秘密の鍵をもう一度チェックだ！"
        elif status_code == 400:
            msg = f"【Error 400】送ったメッセージの形式が少し違うみたいだ。プロンプトを調整してみよう！"
        else:
            msg = f"【Error {status_code}】予想外のトラブルも進化のスパイスさ！詳細：{error_info[:50]}"
            
        return create_response(status_code, msg)

    except Exception as e:
        return create_response(500, f"【Fatal Error】何かが起きたけど、君の努力は消えないぜ！ {str(e)}")

def create_response(status, text):
    """レスポンス用の共通関数"""
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*" # iOSからのCORS対策
        },
        "body": json.dumps({"reply": text}, ensure_ascii=False)
    }
