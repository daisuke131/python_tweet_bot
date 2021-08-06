import os
import subprocess
from pathlib import Path

CSV_FOLDER_PATH = os.path.join(os.getcwd(), "csv")
dir = Path(CSV_FOLDER_PATH)
dir.mkdir(parents=True, exist_ok=True)


def write_csv(csv_path, df):
    # 行番号なしで出力
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    subprocess.Popen(["explorer", CSV_FOLDER_PATH], shell=True)
