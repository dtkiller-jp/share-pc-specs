# OAuth認証情報の取得方法

## Google OAuth 2.0

### 1. Google Cloud Consoleにアクセス
https://console.cloud.google.com/

### 2. プロジェクトを作成
- 左上の「プロジェクトを選択」→「新しいプロジェクト」
- プロジェクト名: `Distributed Jupyter`（任意）
- 「作成」をクリック

### 3. OAuth同意画面を設定
- 左メニュー「APIとサービス」→「OAuth同意画面」
- User Type: 「外部」を選択（個人用）
- 「作成」をクリック
- アプリ情報を入力：
  - アプリ名: `Distributed Jupyter`
  - ユーザーサポートメール: あなたのメールアドレス
  - デベロッパーの連絡先情報: あなたのメールアドレス
- 「保存して次へ」を3回クリック

### 4. 認証情報を作成
- 左メニュー「認証情報」
- 「認証情報を作成」→「OAuthクライアントID」
- アプリケーションの種類: 「ウェブアプリケーション」
- 名前: `Distributed Jupyter Web Client`

### 5. リダイレクトURIを設定
「承認済みのリダイレクトURI」に以下を追加：

**ローカル開発用:**
```
http://localhost:8000/api/auth/google/callback
```

**本番環境用（サーバーのIPアドレスまたはドメイン）:**
```
http://YOUR_SERVER_IP:8000/api/auth/google/callback
http://yourdomain.com/api/auth/google/callback
```

### 6. 認証情報を取得
- 「作成」をクリック
- 表示される**クライアントID**と**クライアントシークレット**をコピー
- `config/config.yaml` の `oauth.google` セクションに貼り付け

---

## GitHub OAuth

### 1. GitHub Settingsにアクセス
https://github.com/settings/developers

### 2. OAuth Appを作成
- 「OAuth Apps」タブを選択
- 「New OAuth App」をクリック

### 3. アプリケーション情報を入力

**Application name:**
```
Distributed Jupyter
```

**Homepage URL:**
```
http://localhost:8000
```
（本番環境の場合は実際のURL）

**Application description:**（任意）
```
分散型Jupyter Notebook実行環境
```

**Authorization callback URL:**
```
http://localhost:8000/api/auth/github/callback
```

**本番環境の場合:**
```
http://YOUR_SERVER_IP:8000/api/auth/github/callback
```

### 4. アプリケーションを登録
- 「Register application」をクリック

### 5. 認証情報を取得
- **Client ID**が表示されるのでコピー
- 「Generate a new client secret」をクリック
- 表示される**Client Secret**をコピー（一度しか表示されないので注意！）
- `config/config.yaml` の `oauth.github` セクションに貼り付け

---

## config.yaml への設定例

```yaml
oauth:
  google:
    client_id: "123456789-abcdefghijklmnop.apps.googleusercontent.com"
    client_secret: "GOCSPX-abcdefghijklmnopqrstuvwxyz"
  github:
    client_id: "Iv1.1234567890abcdef"
    client_secret: "1234567890abcdef1234567890abcdef12345678"
```

---

## テスト方法

### 1. サーバーを起動
```bash
cd server
python main.py
```

### 2. ブラウザでアクセス
```
http://localhost:3000/login
```

### 3. OAuth認証をテスト
- 「Login with Google」または「Login with GitHub」をクリック
- 認証画面が表示されればOK
- 認証後、アプリケーションにリダイレクトされる

---

## トラブルシューティング

### エラー: redirect_uri_mismatch
- OAuth設定のリダイレクトURIが正しいか確認
- `http://` と `https://` の違いに注意
- ポート番号が含まれているか確認

### エラー: invalid_client
- クライアントIDとシークレットが正しいか確認
- YAMLファイルの形式が正しいか確認（インデント、引用符）

### 認証後にエラーが出る
- `admin_emails` に認証に使用したメールアドレスが含まれているか確認
- データベースが正しく初期化されているか確認（`python setup_db.py`）
