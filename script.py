import os
import sys
import fnmatch

def normalize_path(path):
    return path.replace('\\', '/')

def should_include(item_rel_path, is_dir, mode, pattern_list):
    if mode == 'ignore':
        # 隠しファイルやディレクトリを無視
        if item_rel_path.startswith('.'):
            return False
        # パターンに一致しなければ含める
        for pattern in pattern_list:
            if fnmatch.fnmatch(item_rel_path, pattern) or (is_dir and fnmatch.fnmatch(item_rel_path + '/', pattern)):
                return False
        return True
    elif mode == 'obey':
        # パターンに一致すれば含める
        for pattern in pattern_list:
            if fnmatch.fnmatch(item_rel_path, pattern) or (is_dir and fnmatch.fnmatch(item_rel_path + '/', pattern)):
                return True
        return False
    else:
        # すべて含める
        return True

def has_included_files(dir_path, rel_path, mode, pattern_list):
    try:
        with os.scandir(dir_path) as entries:  # os.scandirを使用して隠しファイルも含める
            for entry in entries:
                item_full_path = entry.path
                item_rel_path = os.path.join(rel_path, entry.name) if rel_path else entry.name
                # パス区切り文字を統一
                item_rel_path_normalized = normalize_path(item_rel_path)
                is_directory = entry.is_dir(follow_symlinks=False)
                if should_include(item_rel_path_normalized, is_directory, mode, pattern_list):
                    if is_directory:
                        if has_included_files(item_full_path, item_rel_path, mode, pattern_list):
                            return True
                    else:
                        return True
                elif is_directory:
                    # ディレクトリ内をさらにチェック
                    if has_included_files(item_full_path, item_rel_path, mode, pattern_list):
                        return True
    except PermissionError:
        return False
    return False

def generate_tree(dir_path, rel_path, prefix, files_to_include, tree_lines, mode, pattern_list):
    try:
        with os.scandir(dir_path) as entries:  # os.scandirを使用して隠しファイルも含める
            contents_dirs = []
            contents_files = []
            for entry in sorted(entries, key=lambda e: e.name):
                item_full_path = entry.path
                item_rel_path = os.path.join(rel_path, entry.name) if rel_path else entry.name
                # パス区切り文字を統一
                item_rel_path_normalized = normalize_path(item_rel_path)
                is_directory = entry.is_dir(follow_symlinks=False)
                include_item = False
                if is_directory:
                    if has_included_files(item_full_path, item_rel_path, mode, pattern_list):
                        include_item = True
                else:
                    include_item = should_include(item_rel_path_normalized, is_directory, mode, pattern_list)
                if include_item:
                    if is_directory:
                        contents_dirs.append(entry.name)
                    else:
                        contents_files.append(entry.name)
            contents = contents_dirs + contents_files
            if not contents:
                return
            # ポインタを準備
            pointers = ['├─'] * (len(contents) - 1) + ['└─']
            for pointer, item in zip(pointers, contents):
                item_full_path = os.path.join(dir_path, item)
                item_rel_path = os.path.join(rel_path, item) if rel_path else item
                tree_line = prefix + pointer + item
                tree_lines.append(tree_line)
                is_directory = os.path.isdir(item_full_path)
                if is_directory:
                    if pointer == '├─':
                        extension = '│  '
                    else:
                        extension = '   '
                    generate_tree(item_full_path, item_rel_path, prefix + extension, files_to_include, tree_lines, mode, pattern_list)
                else:
                    files_to_include.append((item_full_path, normalize_path(item_rel_path)))
    except PermissionError:
        return

def read_pattern_list(pattern_file):
    pattern_items = set()
    with open(pattern_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 行からコメントを除去し、前後の空白を削除
            line = line.split('#', 1)[0].strip()
            if line:
                # パス区切り文字を統一
                line = normalize_path(line)
                pattern_items.add(line)
    return pattern_items

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
    # パターンリストのパス区切り文字を統一
    pattern_list = [normalize_path(pattern) for pattern in pattern_list]
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
