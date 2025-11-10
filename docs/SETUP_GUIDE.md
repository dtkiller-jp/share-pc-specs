# セットアップガイド

## クイックスタート

### 1. サーバー起動

**Windows:**
```bash
.\start_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

### 2. アクセス

ブラウザで http://localhost:8000 を開く

---

## 設定

### config/config.yaml

```yaml
# サーバー設定
server:
  host: "0.0.0.0"  # 外部アクセス許可
  port: 8000
  secret_key: "ランダムな文字列"  # 必ず変更！

# 管理者メールアドレス
admin_emails:
  - "admin@example.com"

# ホワイトリスト（アクセス許可）
whitelist_emails:
  - "admin@example.com"
  - "user1@example.com"
  - "user2@example.com"

# デフォルトリソース制限
default_limits:
  cpu_percent: 50        # CPU使用率上限（%）
  memory_mb: 2048        # メモリ上限（MB）
  gpu_memory_mb: 4096    # GPUメモリ上限（MB）
  storage_mb: 5120       # ストレージ上限（MB）
```

### secret_key の生成

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ユーザー管理

### ホワイトリストに追加

`config/config.yaml` の `whitelist_emails` にメールアドレスを追加：

```yaml
whitelist_emails:
  - "newuser@example.com"
```

サーバーを再起動すると反映されます。

### 管理者権限を付与

`admin_emails` にメールアドレスを追加：

```yaml
admin_emails:
  - "admin@example.com"
```

管理者は以下が可能：
- 全ユーザーの管理
- リソース制限の設定
- ユーザーのBAN/承認

---

## ポート開放（外部アクセス）

### Windows

```powershell
New-NetFirewallRule -DisplayName "Distributed Jupyter" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Linux

```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

---

## トラブルシューティング

### ログインできない

- `whitelist_emails` にメールアドレスが登録されているか確認
- サーバーを再起動

### コードが実行されない

- Pythonがインストールされているか確認
- `ipykernel` がインストールされているか確認：
  ```bash
  pip install ipykernel
  ```

### ポートが使用中

```bash
# Windows
netstat -ano | findstr :8000

# Linux
lsof -i :8000
```

---

## 本番環境

### 推奨設定

1. **secret_key を変更**
2. **HTTPS化**（Let's Encrypt等）
3. **リバースプロキシ**（Nginx/Apache）
4. **PostgreSQL使用**（SQLiteは開発用）

### PostgreSQL設定例

```yaml
database:
  url: "postgresql://user:password@localhost/distributed_jupyter"
```
