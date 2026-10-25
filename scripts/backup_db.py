"""用 SQLite backup API 生成一致性快照；不向控制台打印用户数据。"""
import argparse
import sqlite3
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    dest = Path(args.destination).resolve()
    if not source.is_file():
        parser.error("源数据库不存在")
    if dest.exists():
        parser.error("目标文件已存在，请使用新的备份文件名")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as src:
        with sqlite3.connect(dest) as target:
            src.backup(target)
    print("数据库快照已创建，请另行安全保存。")

if __name__ == "__main__":
    main()
