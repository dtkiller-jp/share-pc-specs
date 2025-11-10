# セットアップガイド

## 1. OAuth認証情報の取得

### Google OAuth

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. 「APIとサービス」→「認証情報」に移動
4. 「認証情報を作成」→「OAuthクライアントID」を選択
5. アプリケーションの種類：「ウェブアプリケーション」
6. 承認済みのリダイレクトURIを追加：
   - `http://localhost:8000/api/auth/google/callback`
   - `http://YOUR_SERVER_IP:8000/api/auth/google/callback`
7. 作成後、**クライアントID**と**クライアントシークレット**をコピー

### GitHub OAuth

1. [GitHub Settings](https://github.com/settings/developers) にアクセス
2. 「OAuth Apps」→「New OAuth App」をクリック
3. 以下を入力：
   - Application name: `Distributed Jupyter`
   - Homepage URL: `http://localhost:8000`
   - Authorization callback URL: `http://localhost:8000/api/auth/github/callback`
4. 「Register application」をクリック
5. **Client ID**をコピー
6. 「Generate a new client secret」をクリックして**Client Secret**をコピー

## 2. config/config.yaml の設定

```yaml
server:
  host: "0.0.0.0"  # 外部アクセスを許可する場合は 0.0.0.0
  port: 8000
  secret_key: "1KHBEtRBaSRmsBYgEGvAV9pMkalph2rnMeg8gf-9yxc"  # 重要！

oauth:
  google:
    client_id: "YOUR_GOOGLE_CLIENT_ID"  # Google Consoleから取得
    client_secret: "YOUR_GOOGLE_CLIENT_SECRET"  # Google Consoleから取得
  github:
    client_id: "YOUR_GITHUB_CLIENT_ID"  # GitHubから取得
    client_secret: "YOUR_GITHUB_CLIENT_SECRET"  # GitHubから取得

admin_emails:
  - "your-email@example.com"  # 管理者のメールアドレス（複数可）
  - "admin2@example.com"

database:
  url: "sqlite:///./app.db"  # SQLite（開発用）
  # url: "postgresql://user:password@localhost/dbname"  # PostgreSQL（本番用）

storage:
  base_path: "./storage"
  notebooks_path: "./notebooks"

default_limits:
  cpu_percent: 50        # デフォルトCPU使用率上限（%）
  memory_mb: 2048        # デフォルトメモリ上限（MB）= 2GB
  gpu_memory_mb: 4096    # デフォルトGPUメモリ上限（MB）= 4GB
  storage_mb: 5120       # デフォルトストレージ上限（MB）= 5GB
```

## 3. secret_key の生成方法

Pythonで安全なシークレットキーを生成：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

出力された文字列を `secret_key` に設定してください。

## 4. ポート開放（外部アクセスを許可する場合）

### Windowsファイアウォール

```powershell
# PowerShellを管理者として実行
New-NetFirewallRule -DisplayName "Distributed Jupyter" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Linuxファイアウォール（ufw）

```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

### ルーター設定

1. ルーターの管理画面にアクセス
2. ポートフォワーディング設定
3. 外部ポート: 8000 → 内部IP: サーバーのローカルIP、内部ポート: 8000

## 5. 初回セットアップ

```bash
# サーバーディレクトリに移動
cd server

# 依存パッケージをインストール
pip install -r requirements.txt

# データベースを初期化（管理者ユーザーを作成）
python setup_db.py

# サーバーを起動
python main.py
```

## 6. クライアントセットアップ

```bash
# クライアントディレクトリに移動
cd client

# 依存パッケージをインストール
npm install

# 開発サーバーを起動
npm run dev
```

## 7. アクセス方法

- **ローカル**: http://localhost:3000
- **同一ネットワーク**: http://サーバーのローカルIP:3000
- **外部**: http://サーバーのグローバルIP:3000

## 8. トラブルシューティング

### OAuth認証が失敗する

- `config.yaml` のクライアントIDとシークレットが正しいか確認
- リダイレクトURIが正しく設定されているか確認
- サーバーのURLが正しいか確認

### ポートが使用中

```bash
# Windowsでポート8000を使用しているプロセスを確認
netstat -ano | findstr :8000

# Linuxでポート8000を使用しているプロセスを確認
lsof -i :8000
```

### データベースエラー

```bash
# データベースを削除して再作成
rm app.db
python setup_db.py
```

## 9. 本番環境での推奨設定

1. **HTTPS化**: Let's EncryptなどでSSL証明書を取得
2. **データベース**: SQLiteからPostgreSQLに変更
3. **リバースプロキシ**: NginxやApacheを使用
4. **環境変数**: 機密情報は環境変数で管理

```bash
# 環境変数の例
export SECRET_KEY="your-secret-key"
export GOOGLE_CLIENT_ID="your-google-client-id"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
```
