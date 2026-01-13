import os
import json
import urllib.request

def lambda_handler(event, context):
  # 1. アプリからの入力を取得
  body = json.loads(event.get('body', '{}'))
  user_message = body.get('message', '今日も頑張ったよ！')

  # 2. Mitchieの性格（アルゴリズム）の注入 [cite: 7, 9]
  system_instruction = (
    "あなたはAIパーソナルトレーナーの『Mitchie』です。 "
    "以下のルールを厳守してください： "
    "1. 100%ポジティブに全肯定して褒めること [cite: 7, 9]。 "
    "2. トレーニングできなかった日も肯定的にフォローすること [cite: 13]。 "
    "3. 2〜3文で熱血かつ爽やかに回答すること。 "
  )

  # 3. Gemini APIへのリクエスト作成
  api_key = os.environ['GEMINI_API_KEY']
  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
  
  headers = {'Content-Type': 'application/json'}
  payload = {
    "contents": [{
      "parts": [{
        "text": f"{system_instruction}\n\nユーザーの報告: {user_message}"
      }]
    }]
  }

  # 4. API呼び出しの実行
  req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
  
  try:
    with urllib.request.urlopen(req) as res:
      response_body = res.read().decode('utf-8')
      data = json.loads(response_body)
      
      # Geminiからの回答テキストを抽出
      mitchie_text = data['candidates'][0]['content']['parts'][0]['text']
      
      return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"reply": mitchie_text.strip()}, ensure_ascii=False)
      }
  except Exception as e:
    print(f"Error: {e}")
    return {
      "statusCode": 500,
      "body": json.dumps({"reply": "通信トラブルも、次なる進化への休息さ！後でもう一度話そうぜ！"})
    }
