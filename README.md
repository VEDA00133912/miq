# Make it a Quote
## 使い方
- `pip install -r requirements.txt`を実行
- `python main.py`で起動
- `http://localhost:3000/`でアクセスする
## エンドポイント
- `/`で生成
## パラメーター
- type: タイプ
    - `color` カラーアイコン
    - `mono` モノクロ(デフォルトでこれが適用されます)
- name: 名前
- user_name: ユーザー名
- content: 内容
- icon: アイコン(URL)
# 変更内容
くまのみぼっとで使う用にいろいろ変更してるので..
- typeパラメータを変更
 - colorとmonoに変更。monoは指定しなくてもいいけど
- BRANDの値とデフォルトの要素をくまのみBOT用に変更
- nameの内容をusernameからdisplayNameに変更
- idを廃止して本家と同じuser_nameに変更
# 今後の改善点
- 長い内容だとはみ出してしまうことがあるので中に収まるように文字サイズの調整とかどうにかしていきたい
