# UTF-8移行ガイド

## 概要
PatiPati システムを従来の複数エンコーディング（EUC-JP / Shift_JIS）から **UTF-8** に統一的に移行しました。

## 変更内容

### 1. 文字エンコーディングの統一
- すべてのPerlスクリプト（.cgi, .pl）を UTF-8 に変更
- すべてのHTMLテンプレート（.html）を UTF-8 に変更
- HTTPヘッダーの `Content-Type` を `charset=UTF-8` に統一

### 2. 文字コード変換ライブラリの変更
**変更前：**
```perl
require $jcode;  # jacode.pl を使用
&jcode'convert(*value,'euc');
```

**変更後：**
```perl
use utf8;
use Encode qw/decode encode/;
use Encode::Guess qw/shift_jis euc-jp utf8/;
```

### 3. 既存ログファイルとの互換性

既存の Shift_JIS / EUC-JP で保存されたログファイルとの互換性を保つため、**エンコーディング自動検出機能**を実装しました。

#### 自動検出関数（sub.pl）
```perl
sub read_file_auto_encoding {
    my ($filename) = @_;
    # ファイルをバイナリで読み込み
    # Encode::Guess でエンコーディングを推測
    # 自動的に UTF-8 に変換して返す
}
```

この関数により、以下のエンコーディングのファイルを自動的に読み込めます：
- UTF-8（新規ファイル）
- Shift_JIS（既存ファイル）
- EUC-JP（既存ファイル）

### 4. 新規ファイルの保存形式

**新規作成されるファイルはすべて UTF-8 で保存されます：**
- ログファイル（`logs/*.cgi`）
- ブラックリストファイル（`logs/blist.txt`）

## 動作確認項目

### 基本機能
- [ ] 拍手フォームの表示
- [ ] 日本語メッセージの送信
- [ ] サンクスページの表示
- [ ] 文字数制限の動作

### ログ機能
- [ ] 新規ログの記録（UTF-8で保存）
- [ ] 既存ログの読み込み（自動エンコーディング検出）
- [ ] 管理画面（view.cgi / view2.cgi）での表示

### ブラックリスト機能
- [ ] IP登録・解除
- [ ] ブラックリスト一覧表示

### メール機能（有効な場合）
- [ ] メール送信（ISO-2022-JPエンコーディング）

## トラブルシューティング

### 問題1: 文字化けが発生する
**原因：** エディタでファイルを保存する際にUTF-8以外のエンコーディングで保存された

**対処法：**
1. エディタでファイルを開く
2. **UTF-8（BOMなし）** で保存し直す

### 問題2: 既存ログが正しく表示されない
**原因：** Encode::Guess モジュールがインストールされていない

**対処法：**
```bash
cpan Encode::Guess
```

または、システム管理者に相談してPerlモジュールをインストールしてもらう

### 問題3: "Wide character in print" 警告が出る
**原因：** 出力時のbinmode設定が正しくない

**対処法：**
各CGIファイルで、print前に以下が実行されていることを確認：
```perl
binmode(STDOUT, ":utf8");
```

## 既存データの移行（オプション）

既存のログファイルやブラックリストファイルを完全にUTF-8に変換したい場合：

### Linuxの場合
```bash
cd patipati/logs
for file in *.cgi *.log *.txt; do
  if [ -f "$file" ]; then
    iconv -f SHIFT_JIS -t UTF-8 "$file" > "$file.utf8"
    mv "$file.utf8" "$file"
  fi
done
```

### Windowsの場合
PowerShellを使用：
```powershell
Get-ChildItem -Path "patipati\logs" -Include *.cgi,*.log,*.txt | ForEach-Object {
    $content = Get-Content $_.FullName -Encoding Default
    $content | Out-File $_.FullName -Encoding UTF8
}
```

**注意：** 自動検出機能があるため、この移行作業は必須ではありません。

## 技術的な詳細

### ファイル一覧

#### Perlスクリプト（5ファイル）
- `preset.cgi` - 設定ファイル
- `sub.pl` - 共通サブルーチン
- `index.cgi` - メインCGI
- `view.cgi` - ログビューア
- `view2.cgi` - ログビューア（別バージョン）

#### HTMLテンプレート（7ファイル）
- `error.html` - エラーページ
- `last.html` - 連続投稿制限ページ
- `thanks.html` - サンクスページ1
- `thanks2.html` - サンクスページ2
- `thanks3.html` - サンクスページ3
- `thanks4.html` - サンクスページ4
- `thanks5.html` - サンクスページ5

### メール送信について

メール送信機能では、日本語メールの標準である **ISO-2022-JP** を使用します：

```perl
sub mail {
    my $subject_jis = encode('iso-2022-jp', $subject);
    my $msg_jis = encode('iso-2022-jp', $msg);
    # メール送信処理
}
```

これにより、すべてのメールクライアントで正しく日本語が表示されます。

## まとめ

✅ **メリット**
- すべてのファイルが UTF-8 で統一
- 最新のPerlバージョンで動作保証
- モダンなエディタで快適に編集可能
- Gitでの差分管理が容易
- 既存ログファイルとの互換性も維持

✅ **後方互換性**
- 既存の Shift_JIS / EUC-JP ログファイルも自動的に読み込み可能
- 新規ファイルは UTF-8 で保存
- 段階的な移行が可能

---

**最終更新：** 2025年（移行実施日）
**バージョン：** PatiPati 4.3 + UTF-8対応版
