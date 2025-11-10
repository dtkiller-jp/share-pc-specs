# Distributed Jupyter Notebook System

分散型Jupyter Notebook実行環境 - リソース管理機能付き

## 機能

- OAuth 2.0認証（Google/GitHub）
- ホワイトリスト制アクセス管理
- 管理者ダッシュボード
- ユーザーごとのリソース制限（CPU/メモリ/GPU/ストレージ）
- リアルタイムNotebook実行

## セットアップ

詳細な設定方法は [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) を参照してください。

### クイックスタート

1. **OAuth認証情報を取得**
   - Google: https://console.cloud.google.com/
   - GitHub: https://github.com/settings/developers

2. **config/config.yaml を編集**
   ```bash
   # secret_keyを生成
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # config/config.yaml に以下を設定：
   # - secret_key（上で生成した値）
   # - OAuth認証情報（client_id, client_secret）
   # - admin_emails（管理者のメールアドレス）
   ```

3. **サーバー起動**
   ```bash
   cd server
   pip install -r requirements.txt
   python setup_db.py
   python main.py
   ```

4. **クライアント起動**
   ```bash
   cd client
   npm install
   npm run dev
   ```

5. **アクセス**
   - ブラウザで http://localhost:3000 を開く

## ポート開放（外部アクセス用）

### Windows
```powershell
New-NetFirewallRule -DisplayName "Distributed Jupyter" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Linux
```bash
sudo ufw allow 8000/tcp
```
