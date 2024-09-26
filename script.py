import os
import sys
import fnmatch

def read_pattern_list(pattern_file):
    pattern_items = set()
    with open(pattern_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 行からコメントを除去し、前後の空白を削除
            line = line.split('#', 1)[0].strip()
            if line:
                pattern_items.add(line)
    return pattern_items

def should_include(item_rel_path, mode, pattern_list):
    if mode == 'ignore':
        # パターンに一致しなければ含める
        for pattern in pattern_list:
            if fnmatch.fnmatch(item_rel_path, pattern):
                return False
        return True
    elif mode == 'obey':
        # パターンに一致すれば含める
        for pattern in pattern_list:
            if fnmatch.fnmatch(item_rel_path, pattern):
                return True
        return False
    else:
        # すべて含める
        return True

def generate_tree(dir_path, rel_path, prefix, files_to_include, tree_lines, mode, pattern_list):
    try:
        contents = os.listdir(dir_path)
    except PermissionError:
        # アクセスできないディレクトリはスキップ
        return
    # ディレクトリとファイルを分ける
    contents_dirs = []
    contents_files = []
    for item in contents:
        item_full_path = os.path.join(dir_path, item)
        item_rel_path = os.path.join(rel_path, item) if rel_path else item
        if not should_include(item_rel_path, mode, pattern_list):
            continue
        if os.path.isdir(item_full_path):
            contents_dirs.append(item)
        else:
            contents_files.append(item)
    contents = contents_dirs + contents_files
    # ポインタを準備
    pointers = ['├─'] * (len(contents) - 1) + ['└─']
    for pointer, item in zip(pointers, contents):
        item_full_path = os.path.join(dir_path, item)
        item_rel_path = os.path.join(rel_path, item) if rel_path else item
        tree_line = prefix + pointer + item
        tree_lines.append(tree_line)
        if os.path.isdir(item_full_path):
            # 次のレベルのための接頭辞を準備
            if pointer == '├─':
                extension = '│  '
            else:
                extension = '   '
            # サブディレクトリを再帰的に処理
            generate_tree(item_full_path, item_rel_path, prefix + extension, files_to_include, tree_lines, mode, pattern_list)
        else:
            # ファイルを収集
            files_to_include.append((item_full_path, item_rel_path))

def main():
    if len(sys.argv) != 2:
        print("使用法: python script.py <フォルダパス>")
        sys.exit(1)
    folder_path = sys.argv[1]
    # フォルダパスを正規化
    folder_path = os.path.abspath(folder_path)
    # カレントディレクトリを取得
    current_dir = os.getcwd()
    ignore_file = os.path.join(current_dir, 'ignore.txt')
    obey_file = os.path.join(current_dir, 'obey.txt')
    ignore_exists = os.path.isfile(ignore_file)
    obey_exists = os.path.isfile(obey_file)
    # モードとパターンリストを初期化
    mode = 'none'
    pattern_list = []
    if ignore_exists and obey_exists:
        # 両方存在する場合、ユーザーに選択させる
        print("ignore.txtとobey.txtが見つかりました。どちらを使用しますか？")
        choice = input("ignore.txtを使用する場合は 'ignore'、obey.txtを使用する場合は 'obey' を入力してください: ")
        if choice == 'ignore':
            mode = 'ignore'
            pattern_list = read_pattern_list(ignore_file)
            print("ignore.txtを認識しましたので、記載されているファイルは無視します。")
        elif choice == 'obey':
            mode = 'obey'
            pattern_list = read_pattern_list(obey_file)
            print("obey.txtを認識しましたので、記載されているファイルのみを表示します。")
        else:
            print("不正な入力です。プログラムを終了します。")
            sys.exit(1)
    elif ignore_exists:
        mode = 'ignore'
        pattern_list = read_pattern_list(ignore_file)
        print("ignore.txtを認識しましたので、記載されているファイルは無視します。")
    elif obey_exists:
        mode = 'obey'
        pattern_list = read_pattern_list(obey_file)
        print("obey.txtを認識しましたので、記載されているファイルのみを表示します。")
    else:
        print("ignore.txtとobey.txtが見つかりませんでした。指定されたフォルダのすべてのファイルを表示します。")
    # 変数を初期化
    files_to_include = []
    tree_lines = []
    # ルートフォルダから開始
    root_name = os.path.basename(folder_path)
    tree_lines.append(root_name)
    generate_tree(folder_path, '', '', files_to_include, tree_lines, mode, pattern_list)
    # 出力をファイルに書き込む
    output_file = 'output.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        # 階層構造を書き込む
        for line in tree_lines:
            f.write(line + '\n')
        f.write('\n')
        # ファイルの内容を書き込む
        for file_full_path, file_rel_path in files_to_include:
            f.write(f'【{file_rel_path}】\n')
            try:
                with open(file_full_path, 'r', encoding='utf-8') as file_content:
                    f.write(file_content.read())
            except Exception as e:
                f.write(f'ファイル {file_rel_path} を読み込む際にエラーが発生しました: {e}\n')
            f.write('\n\n')
    print(f"出力が {output_file} に書き込まれました")

if __name__ == '__main__':
    main()
