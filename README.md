# これはなに
- 進研ゼミ チャレンジタッチからメールが送られてきたら、即返信するbot
- 返信内容をLINEに送信
- ついでに、送られてきたメールの添付画像をLINEに送信（今どきメールなんて見ないですよね？

# overview
1. チャレンジユーザがメールを送る
1. imapにメールが入る
1. ここからプログラムの仕事
1. imapからメールを取る
1. LINEにメール内容を送信
1. seleniumを使ってメール内のリンクを開き、返信を自動でする
1. LINEに返信内容を送信
1. errorが起こったらそれをLINEに送信

# 使い方
1. 進研ゼミのメール `challenge-mail@mail.benesse.co.jp` を特定のフォルダに振り分けるよう、メーラー側でフィルタをしておく。
    1. メールボックス名は単語1つが吉。スペース入れて動くかは知らない。
1. LINE Notify TOKEN を取得
    1. https: // notify-bot.line.me/ja/
1. ChromeDriver - WebDriver for Chrome をdownload & PCのどっかに保存
    1. https: // sites.google.com/a/chromium.org/chromedriver/downloads
1. `.env` ファイルを作る
    1. 中身は `.env.sample` を参照
    1. ChromeDriverのパスはフルパスで
1. install
    1. ```
        pip install - r requirements.txt
        python3 - m venv venv
        . venv/bin/activate
        python main.py
        ```
1. cronで定期実行する


# 注意点
python debugできる人じゃないと難しいと思います。特にimap周りは闇が深いです

# Thanks
I edited and included several files of the repos below.

- https://github.com/10mohi6/line-notify-python/
- https://github.com/keitaoouchi/easyimap/
