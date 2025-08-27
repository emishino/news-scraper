# top_keywords_by_day.py
# --- これをファイルの一番上に追加 ---
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
# ------------------------------------
import unicodedata
import pandas as pd
import glob, os, re
from collections import Counter
import matplotlib as mpl
mpl.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "MS Gothic"]  # 使える日本語フォントを順番に
mpl.rcParams["axes.unicode_minus"] = False  # －（マイナス）も文字化けしないように


import matplotlib.pyplot as plt
from matplotlib import rcParams

# 日本語フォントを設定（WindowsならMS Gothic / Meiryoなど）
rcParams['font.family'] = 'Meiryo'


# ---- CSVを全取得して結合（日付はファイル名から） ----
files = sorted(glob.glob("news_*.csv"))
if not files:
    raise SystemExit("news_*.csv がありません。先に news_scraper.py を実行してCSVを作成してください。")

frames = []
for f in files:
    df = pd.read_csv(f)
    date = os.path.basename(f).replace("news_", "").replace(".csv", "")
    df["date"] = date
    frames.append(df)

data = pd.concat(frames, ignore_index=True)
data.columns = [c.strip().lower() for c in data.columns]
data["date"] = pd.to_datetime(data["date"], errors="coerce").dt.strftime("%Y-%m-%d")
titles = data[["date", "title"]].dropna()

# ---- トークナイズ（Janomeがあれば精度UP） ----
def tokenize_with_janome(text):
    try:
        from janome.tokenizer import Tokenizer
    except ImportError:
        return None
    t = Tokenizer()
    terms = []
    for token in t.tokenize(text):
        base = token.base_form if token.base_form != "*" else token.surface
        base = unicodedata.normalize("NFKC", base)  # 全角→半角など正規化
        pos = token.part_of_speech.split(",")
        # 名詞以外、または数字系の名詞は除外
        if pos[0] != "名詞":
            continue
        if "数" in pos:          # 名詞-数 を除外
            continue
        if base.isdigit():       # 半角数字のみ
            continue
        if re.fullmatch(r"[0-9]+", base):
            continue
        if len(base) < 2:
            continue
        terms.append(base)
    return terms


def tokenize_simple(text):
    # 正規化（全角→半角、結合文字の統一）
    text = unicodedata.normalize("NFKC", str(text))
    # URL除去
    text = re.sub(r"https?://\S+", " ", text)
    # 2文字以上の日本語/英数を拾う
    pattern = re.compile(r"[ぁ-んァ-ン一-龥A-Za-z0-9]{2,}")
    stop = set("""
        これ それ あれ ため など そして また
        する なる できる 行う いる ある もの こと よう
        さん 月 日 年 今日 明日 昨日
        ニュース NEWS 速報 写真 画像 動画 PR Yahoo https www com jp article
    """.split())
    terms = []
    for w in pattern.findall(text):
        # 完全に英数字だけの短い語（ノイズ）や数字だけは除外
        if w.isdigit():
            continue
        if re.fullmatch(r"[0-9]+", w):
            continue
        if w in stop:
            continue
        terms.append(w)
    return terms


def tokenize(text):
    t = tokenize_with_janome(text)
    return t if t is not None else tokenize_simple(text)

# ---- 日別に頻出キーワードTOPを作成 ----
top_n = 15
rows = []
for date, grp in titles.groupby("date"):
    terms = []
    for title in grp["title"]:
        terms.extend(tokenize(title))
    cnt = Counter(terms)
    for kw, c in cnt.most_common(top_n):
        rows.append({"date": date, "keyword": kw, "count": c})

top_df = pd.DataFrame(rows).sort_values(["date", "count"], ascending=[True, False])
out_csv = "top_keywords_by_day.csv"
top_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
print(f"日別TOP{top_n}を {out_csv} に保存しました。")

# ---- ヒートマップ風（上位キーワード×日付） ----
M = 30
global_top = (
    top_df.groupby("keyword")["count"].sum()
    .sort_values(ascending=False)
    .head(M).index.tolist()
)
pivot = (
    top_df.assign(
        date=pd.to_datetime(top_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    )
    .pivot_table(index="keyword", columns="date", values="count",
                 aggfunc="sum", fill_value=0)
)

# 列（横軸）を日付の昇順で並べる
cols_sorted = sorted(pivot.columns, key=lambda x: pd.to_datetime(x))
pivot = pivot[cols_sorted]



plt.figure(figsize=(max(8, len(pivot.columns)*0.6), max(8, len(pivot.index)*0.35)))
plt.imshow(pivot.values, aspect="auto")
plt.xticks(
    range(len(pivot.columns)),
    [pd.to_datetime(c).strftime("%Y-%m-%d") for c in pivot.columns],
    rotation=45, ha="right"
)

plt.yticks(range(len(pivot.index)), pivot.index)
plt.title("Top Keywords by Day (count)")
plt.colorbar(label="Count")
plt.tight_layout()
out_png = "top_keywords_by_day.png"
plt.savefig(out_png)
plt.close()
print(f"ヒートマップを {out_png} に保存しました。")
print("読み込んだCSV:", files)

