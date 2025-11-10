# Distributed Jupyter Notebook System

分散型Jupyter Notebook実行環境 - リソース管理機能付き

クライアントPCの計算負荷を別のサーバーPCに分散させ、リソース制限を設けながら複数ユーザーで共有できるシステムです。

## 機能

- **メールホワイトリスト認証** - 許可されたユーザーのみアクセス可能
- **管理者ダッシュボード** - ユーザー管理、リソース制限設定、BAN機能
- **リソース管理** - CPU/メモリ/GPU/ストレージの使用量制限
- **リアルタイムNotebook実行** - WebSocket経由で即座に結果を表示
- **Python補完機能** - Monaco Editorによるコード補完

## 必要要件

- Python 3.8+
- Node.js 16+
- pip
- npm

## インストール

### 1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/distributed-jupyter.git
cd distributed-jupyter
```

### 2. 設定ファイルを作成

```bash
cp config/config.example.yaml config/config.yaml
```

### 3. config/config.yaml を編集

```yaml
server:
  secret_key: "ランダムな文字列に変更"  # 重要！

admin_emails:
  - "your-email@example.com"

whitelist_emails:
  - "your-email@example.com"
  - "user1@example.com"
```

**secret_key の生成:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. サーバー起動

**Windows:**
```bash
.\start_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

### 5. アクセス

ブラウザで **http://localhost:8000** を開く

## ストレージ構造

```
distributed-jupyter/
├── storage/          # ユーザーファイル（.gitignoreに含まれる）
├── notebooks/        # .ipynbファイル（.gitignoreに含まれる）
│   └── {user_id}/    # ユーザーごとのディレクトリ
│       └── *.ipynb
├── app.db           # SQLiteデータベース（.gitignoreに含まれる）
└── config/
    └── config.yaml  # 個人設定（.gitignoreに含まれる）
```

**ストレージの場所:**
- デフォルト: プロジェクトルートの `./storage` と `./notebooks`
- 変更可能: `config/config.yaml` の `storage` セクション

## ユーザー管理

### ホワイトリストに追加

`config/config.yaml` を編集：

```yaml
whitelist_emails:
  - "newuser@example.com"  # 追加
```

サーバーを再起動すると反映されます。

### 管理者権限を付与

```yaml
admin_emails:
  - "admin@example.com"  # 追加
```

管理者は以下が可能：
- 全ユーザーの管理
- リソース制限の設定
- ユーザーのBAN/承認

## ポート開放（外部アクセス）

### Windows
```powershell
New-NetFirewallRule -DisplayName "Distributed Jupyter" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Linux
```bash
sudo ufw allow 8000/tcp
```

## 開発

### クライアント開発モード

```bash
cd client
npm install
npm run dev
```

開発サーバー: http://localhost:3000

### サーバー開発モード

```bash
cd server
pip install -r requirements.txt
python main.py
```

## トラブルシューティング

詳細は [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) を参照

## ライセンス

MIT License

## 注意事項

- `config/config.yaml` は個人情報を含むため、Gitにコミットしないでください
- `secret_key` は必ず変更してください
- 本番環境ではHTTPS化を推奨します
