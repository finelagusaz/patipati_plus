# patipatiVer4.3 ＋Towa （phase5） UTF-8対応版

Perl のアップデートで動かなくなった patipati をモダンな環境で動作するように改造したものです。

**最新版では完全にUTF-8に移行し、既存のShift_JIS/EUC-JPファイルとの互換性も維持しています。**

## 主な変更点

### Phase 1-5: 基本的な動作修正

- `jcode.pl` から `jacode.pl` に変更
- モジュールの呼び出し方を変更

### Phase 6: UTF-8完全移行（最新版）

- **文字エンコーディングをUTF-8に統一**
  - すべてのPerlスクリプト（.cgi, .pl）をUTF-8化
  - すべてのHTMLテンプレート（.html）をUTF-8化
  - HTTPヘッダーを`charset=UTF-8`に統一

- **モダンなPerlモジュールを使用**
  - `jacode.pl`（古いライブラリ）を廃止
  - 標準の`Encode`モジュールを使用
  - `Encode::Guess`による自動エンコーディング検出

- **既存ログファイルとの互換性を維持**
  - 既存のShift_JIS/EUC-JPログファイルを自動検出して読み込み
  - 新規ファイルはすべてUTF-8で保存
  - 段階的な移行が可能

- **外部入力の柔軟な処理**
  - フォーム入力のエンコーディング自動検出
  - Shift_JIS/EUC-JP/UTF-8のいずれにも対応
  - 外部システムからの呼び出しにも対応

## 必要な環境

- Perl 5.8以降（`Encode`モジュール標準搭載）
- `Encode::Guess`モジュール（自動エンコーディング検出用）

### Encode::Guessのインストール

```bash
cpan Encode::Guess
```

または、システム管理者に依頼してインストールしてください。

## ファイル構成

### Perlスクリプト（5ファイル）

- [preset.cgi](patipati/preset.cgi) - 設定ファイル（UTF-8化、Encodeモジュール使用）
- [sub.pl](patipati/sub.pl) - 共通サブルーチン（エンコーディング自動検出機能追加）
- [index.cgi](patipati/index.cgi) - メインCGI（UTF-8化、入力自動検出対応）
- [view.cgi](patipati/view.cgi) - ログビューア（UTF-8化）
- [view2.cgi](patipati/view2.cgi) - ログビューア別バージョン（UTF-8化）

### HTMLテンプレート（7ファイル）

- [error.html](patipati/error.html) - エラーページ（UTF-8化）
- [last.html](patipati/last.html) - 連続投稿制限ページ（UTF-8化）
- [thanks.html](patipati/thanks.html) - サンクスページ1（UTF-8化）
- thanks2.html～thanks5.html - サンクスページ2～5（UTF-8化）

### ドキュメント

- [MIGRATION_UTF8.md](MIGRATION_UTF8.md) - UTF-8移行ガイド（詳細な技術情報）

## 主な技術的特徴

### 1. エンコーディング自動検出

既存のログファイルやブラックリストファイルのエンコーディングを自動的に検出して読み込みます。

```perl
# sub.plに実装された自動検出関数
@logs = &read_file_auto_encoding($log_file);
```

対応エンコーディング：

- UTF-8（新規ファイル）
- Shift_JIS（既存ファイル）
- EUC-JP（既存ファイル）

### 2. 入力データの柔軟な処理

フォームから送信されるデータのエンコーディングを自動検出します。

```perl
# index.cgiで実装
my $enc = guess_encoding($value, qw/utf8 shiftjis euc-jp/);
if (ref($enc)) {
    $value = $enc->decode($value);
}
```

これにより、外部システムから`charset=Shift_JIS`で呼び出された場合でも正しく処理できます。

### 3. ファイル保存形式

- **読み込み**: 自動検出（UTF-8/Shift_JIS/EUC-JP）
- **書き込み**: 常にUTF-8

```perl
# 新規ファイルはすべてUTF-8で保存
open(OUT,">:utf8", "$log_file");
```

### 4. メール送信

日本語メールの標準である**ISO-2022-JP**を使用します。

```perl
my $subject_jis = encode('iso-2022-jp', $subject);
my $msg_jis = encode('iso-2022-jp', $msg);
```

## 動作確認

以下の項目を確認してください：

- [ ] 拍手フォームの表示
- [ ] 日本語メッセージの送信
- [ ] サンクスページの表示
- [ ] 既存ログの正常な表示（Shift_JIS/EUC-JPログも含む）
- [ ] 管理画面（view.cgi / view2.cgi）での表示
- [ ] ブラックリスト機能

## トラブルシューティング

### 文字化けが発生する場合

**原因**: エディタでファイルを保存する際にUTF-8以外のエンコーディングで保存された

**対処法**: ファイルを**UTF-8（BOMなし）**で保存し直してください。

### "Wide character in print" 警告が出る場合

**原因**: 出力時のbinmode設定が正しくない

**対処法**: 各CGIファイルで、以下のコードが実行されていることを確認してください。

```perl
binmode(STDOUT, ":utf8");
```

### Encode::Guessモジュールがない場合

**対処法**:

```bash
cpan Encode::Guess
```

または、システム管理者に相談してPerlモジュールをインストールしてもらってください。

## 既存データの移行（オプション）

既存のログファイルを完全にUTF-8に変換したい場合は、[MIGRATION_UTF8.md](MIGRATION_UTF8.md)の「既存データの移行」セクションを参照してください。

**注意**: 自動検出機能があるため、この移行作業は必須ではありません。既存ファイルはそのままでも正常に動作します。

## メリット

✅ **技術的メリット**

- すべてのファイルがUTF-8で統一され、管理が容易
- 最新のPerlバージョンで動作保証
- モダンなエディタで快適に編集可能
- Gitでの差分管理が容易

✅ **互換性**

- 既存のShift_JIS/EUC-JPログファイルも自動的に読み込み可能
- 外部システムからの異なるエンコーディングでの呼び出しにも対応
- 段階的な移行が可能

✅ **保守性**

- 古いjacode.plライブラリへの依存を解消
- 標準のEncodeモジュールを使用
- コードの可読性が向上

## 詳細情報

UTF-8移行の詳細な技術情報、トラブルシューティング、既存データの移行手順については、[MIGRATION_UTF8.md](MIGRATION_UTF8.md)を参照してください。

## ライセンス

元の PatiPati システムのライセンスに準じます。

---

**最終更新**: 2025年（UTF-8移行完了）
**バージョン**: PatiPati 4.3 + Towa + UTF-8対応版
