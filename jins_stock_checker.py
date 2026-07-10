"""
JINS商品ページの在庫監視スクリプト
再入荷（SOLD OUT表示が消えた）を検知したらメールで通知します。

■ 使い方の概要
1. 下の CONFIG 部分を自分の情報に書き換える
2. GitHub Actions で15〜30分おきに自動実行する（無料）
   → セットアップ手順は README_setup.md を参照

■ 必要なもの
- 監視したい商品のURL
- 通知を送りたいメールアドレス
- 送信元として使うGmailアカウント + アプリパスワード
  (Googleアカウント → セキュリティ → 2段階認証を有効化 → アプリパスワードを発行)
"""

import smtplib
import ssl
import sys
from email.mime.text import MIMEText
import urllib.request

# ============ CONFIG（ここを書き換える） ============
PRODUCT_URL = "https://www.jins.com/jp/item/MTF-23S-184_95.html"  # 監視したい商品ページのURL
SOLD_OUT_TEXT = "SOLD OUT"  # 品切れ時にページに表示される文言（必要に応じて変更）

GMAIL_ADDRESS = "khikaru0719@gmail.com"      # 送信元Gmailアドレス
GMAIL_APP_PASSWORD = "xolg tyuy muad ykhi"          # Googleアプリパスワード（16桁）
NOTIFY_TO = "khikaru0719@gmail.com"       # 通知を受け取りたいメールアドレス
# =====================================================


def is_in_stock(url: str, sold_out_text: str) -> bool:
    """商品ページを取得し、在庫があるかどうかを判定する"""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; StockChecker/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        html = res.read().decode("utf-8", errors="ignore")
    return sold_out_text not in html


def send_email(subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = NOTIFY_TO

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, [NOTIFY_TO], msg.as_string())


def main():
    try:
        in_stock = is_in_stock(PRODUCT_URL, SOLD_OUT_TEXT)
    except Exception as e:
        print(f"チェック中にエラーが発生しました: {e}", file=sys.stderr)
        # エラー時は通知しない（誤報を避けるため）。必要ならここでもメール送信可能。
        return

    if in_stock:
        print("在庫あり！ 通知メールを送信します。")
        send_email(
            subject="【再入荷】JINSの商品が再入荷しました！",
            body=f"以下の商品が再入荷した可能性があります。すぐに確認してください。\n\n{PRODUCT_URL}",
        )
    else:
        print("まだ品切れです。")


if __name__ == "__main__":
    main()
