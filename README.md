このPythonスクリプトは、指定したフォルダ内のファイルやフォルダを階層構造で表示し、その内容を一つのテキストファイル（output.txt）にまとめます。

【機能】
指定したフォルダの階層構造をツリー形式で表示
各ファイルの内容を一つのテキストファイルに統合
ignore.txt または obey.txt を使用して、表示・除外するファイルやフォルダを制御

【使い方】
script.py を任意のディレクトリに保存します。

ignore.txt または obey.txt の作成（任意）

ignore.txt: 除外したいファイルやフォルダを記述
obey.txt: 表示したいファイルやフォルダを記述
これらのファイルは、スクリプトを実行するディレクトリに配置してください。

【スクリプトの実行】

コマンドラインで以下を実行します。


python script.py <フォルダパス>

例：
python script.py ./my_project


【実行結果】

output.txt ファイルが生成されます。
ignore.txt や obey.txt が存在する場合、スクリプトが自動的に検出し適用します。

【注意事項】
ignore.txt と obey.txt が両方存在する場合、どちらを使用するか尋ねられます。
ファイルのエンコーディングは、UTF-8で保存してください。
パスの指定は、指定したフォルダのルートからの相対パスで記述してください。
コメント行は、# を使用して無視されます。