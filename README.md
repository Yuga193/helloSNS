# helloSNS

# helloSNS

使用したフレームワーク
- Flask
- tailwindCSS

## ファイル構造
├── README.md  
├── app  
│   ├── __pycache__  
│   │   ├── DB.cpython-311.pyc  
│   │   ├── __init__.cpython-311.pyc  
│   │   ├── app.cpython-311.pyc  
│   │   ├── main.cpython-311.pyc  
│   │   └── view.cpython-311.pyc  
│   ├── main.py (バックエンド管理)  
│   ├── static  
│   │   └── src  
│   │       └── style.css (tailwindCSSで使用)  
│   └── templates (画面構成の管理)  
│       ├── DM.html (個人チャットの画面)  
│       ├── completion.html (会員登録完了時の画面)  
│       ├── login.html (ログインフォーラムの画面)  
│       ├── message.html (送受信したメッセージを一覧表示する画面)  
│       ├── mypage.html (マイページの画面)  
│       ├── search.html (メッセージを送るユーザーを検索する画面)  
│       ├── style.css (tailwindCSSで使用)  
│       ├── test.html (メイン画面)  
│       └── user.html (会員登録のデータ入力フォーラムの画面)  
├── node_modules  
├── database.db (データベース)  
├── docker-compose.yaml  
├── dockerfile  
├── package-lock.json  
├── package.json  
├── requirements.txt (dockerで使用)  
└── tailwind.config.js  


## DB構成
### 『users』(ユーザーデータを管理)  
ID(登録時に自動的に割り当てられる管理用のID)  
name(そのユーザーの名前)  
password(そのユーザーがログイン時に使用するパスワード)  
userID(そのユーザーのID)  

### 『Message』(送られたテキストが持つデータを管理)  
id (そのテキストメッセージが持つID)  
sender_id(テキストメッセージを送った人のuserID)※usersテーブルから取得  
receiver_id(テキストメッセージを受け取った人のuserID)※usersテーブルから取得  
send_name(テキストメッセージを送った人のname)※usersテーブルから取得  
receiver_name (テキストメッセージを受け取った人のname)※usersテーブルから取得  
chat_session_id(このテキストメッセージが存在する位置をIDとして管理)  
content(テキストメッセージの内容)  
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP(テキストメッセージの送信日時)  


## DB構成
### 『users』(ユーザーデータを管理)
- ID: 登録時に自動的に割り当てられる管理用のID
- name: そのユーザーの名前
- password: そのユーザーがログイン時に使用するパスワード
- userID: そのユーザーのID

### 『Message』(送られたテキストが持つデータを管理)
- id: そのテキストメッセージが持つID
- sender_id: テキストメッセージを送った人のuserID (※usersテーブルから取得)
- receiver_id: テキストメッセージを受け取った人のuserID (※usersテーブルから取得)
- send_name: テキストメッセージを送った人のname (※usersテーブルから取得)
- receiver_name: テキストメッセージを受け取った人のname (※usersテーブルから取得)
- chat_session_id: このテキストメッセージが存在する位置をIDとして管理
- content: テキストメッセージの内容
- timestamp: DATETIME DEFAULT CURRENT_TIMESTAMP (テキストメッセージの送信日時)

