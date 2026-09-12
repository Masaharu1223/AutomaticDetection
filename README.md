# car-vision 🚗

![Python](https://img.shields.io/badge/Python-3.12.7-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Ultralytics](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?style=for-the-badge&logo=ultralytics&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Ruff](https://img.shields.io/badge/Lint-Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black)
![Mypy](https://img.shields.io/badge/Type%20Check-Mypy-2A6DB2?style=for-the-badge&logo=python&logoColor=white)

**MacBook Pro M5 RAM 24GB + iPhone（Continuity Camera）でリアルタイム物体検出機能を実装しました。**

データサイエンスが流行った数年前に授業で実装したことがある検知システムをClaude Code + Codexで実装したらどれくらいで、どのくらいの検知精度できるのか。
そんな疑問を抱き、実装してみました。
本PJでは、YOLOv8 を Apple Neural Engine（Core ML）向けに最適化し、ByteTrack 追跡を組み合わせたリアルタイム物体検出システムの**プロトタイプ**です（Core ML変換・ByteTrack統合は「今後の予定」にある通り未実装）。
上述のように、Claude Code + Codexを用いて壁打ちからテスト・デプロイまで僅か10分程度で実装いたしました。

---

## デモ

<img width="600" height="301" alt="DetectionDemo_600p" src="https://github.com/user-attachments/assets/28d1ada6-afc1-4cdb-a027-d609c15fafe0" />

---

## 特徴

- **Apple Neural Engine 最適化（予定）** — Core ML 変換で M5 チップの Neural Engine をフル活用
- **ByteTrack 物体追跡（予定）** — フレームをまたいで同一物体に ID を付与、デモ映えする追跡表示
- **HUD オーバーレイ（予定）** — FPS・検出クラス数・モデル名をリアルタイム表示
- **物体クラスに絞り込み** — 人・車・トラック・バイク・自転車・信号機・止まれ標識のみ検出
- **セットアップ一発** — `pip install -r requirements.txt` だけで動く

---

## 必要な環境変数・コマンド一覧

### 環境変数

このプロジェクトは `.env` 等の環境変数を使用しません（不要）。

### コマンド一覧

| コマンド | 説明 |
|---|---|
| `python quick_demo.py` | 内蔵カメラでクイックデモを起動 |
| `python quick_demo.py --camera 1` | 指定インデックスのカメラ（iPhone 等）で起動 |
| `python quick_demo.py --model yolov8n.pt` | 使用モデルを変更（高速） |
| `python quick_demo.py --conf 0.65` | 信頼度閾値を変更（0.0〜1.0） |
| `ruff check .` | Lint 実行 |
| `mypy quick_demo.py` | 型チェック実行 |

`q` キーでデモを終了（`quick_demo.py` 内で `cv2.waitKey` により判定）。

---

## ディレクトリ構成

```
.
├── CLAUDE.md          # プロジェクト設計仕様書（将来のアーキテクチャ・HUD・エラー設計など）
├── quick_demo.py       # YOLOv8 動作確認用クイックデモスクリプト（現状の唯一の実行コード）
├── requirements.txt     # 依存ライブラリ一覧（ultralytics / opencv-python / pyyaml）
├── pyproject.toml       # ruff（Lint）/ mypy（型チェック）設定
├── .gitignore          # モデル重み（*.pt）・ログ・キャッシュを除外
└── README.md
```

> `yolov8s.pt` / `yolov8m.pt` はモデル重みファイルのため `.gitignore` 対象で、リポジトリには含まれません（初回実行時に自動ダウンロードされます）。
> `detection/` `overlay/` `benchmark/` などの本番構成は `CLAUDE.md` に設計済みですが未実装です。

---

## 使用したハードウェア構成

| 機器 | 仕様 |
|---|---|
| MacBook Pro | M5 / 24GB RAM |
| カメラ | iPhone（Continuity Camera） |
| 接続 | USB または Wi-Fi（Continuity Camera） |

---

## 開発環境の構築手順

### 1. 前提条件

- macOS Ventura 以降
- Python 3.12.7（[pyenv](https://github.com/pyenv/pyenv) 推奨）

> **pyenv を使う場合の注意点**：Python ビルド前に `xz` を先にインストールしてください。
> `xz` なしでビルドすると `_lzma` モジュールが欠落し `torchvision` が動作しないです。

```bash
brew install xz

export LDFLAGS="-L/opt/homebrew/opt/xz/lib"
export CPPFLAGS="-I/opt/homebrew/opt/xz/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/xz/lib/pkgconfig"
pyenv install 3.12.7
pyenv local 3.12.7
```

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3.（任意）Lint / 型チェックツールの導入

`pyproject.toml` に ruff（Lint）・mypy（型チェック、strict モード）の設定がありますが、
`requirements.txt` には含まれていないため開発時は別途インストールしてください。

```bash
pip install ruff mypy

ruff check .
mypy quick_demo.py
```

---

## 使い方

### クイックデモ（動作確認）

```bash
# 内蔵カメラ
python quick_demo.py

# iPhone（Continuity Camera）
python quick_demo.py --camera 1

# モデルサイズを変えて精度/速度を比較
python quick_demo.py --model yolov8n.pt   # 高速
python quick_demo.py --model yolov8m.pt   # 高精度

# 誤検知が多い場合は信頼度を上げる
python quick_demo.py --conf 0.65
```

`q` キーで終了。

### カメラインデックスの確認

```bash
python -c "
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f'index={i}  {w}x{h}')
        cap.release()
"
```

---

## モデル性能（Core ML 変換後の期待 FPS / M5、目標値）

| モデル | mAP | 期待 FPS |
|---|---|---|
| YOLOv8n（nano） | 37.3 | 60〜100 FPS |
| YOLOv8s（small） | 44.9 | 40〜60 FPS |
| YOLOv8m（medium） | 50.2 | 25〜40 FPS |

> Core ML 変換は未実装のため、現状の `quick_demo.py` は PyTorch（`.pt`）モデルで動作し、上表の FPS には未到達です。

---

## 検出する物体（COCO）

`person` / `bicycle` / `car` / `motorcycle` / `bus` / `truck` / `traffic light` / `stop sign`

---

## トラブルシューティング

### `ModuleNotFoundError: No module named '_lzma'`

pyenv で Python をビルドする前に `xz` が入っていないと発生します。[開発環境の構築手順](#開発環境の構築手順) の手順通り `brew install xz` を先に実行してから Python を再ビルドしてください。

### カメラ (index=0) を開けませんでした

指定したカメラインデックスにカメラが存在しません。[カメラインデックスの確認](#カメラインデックスの確認) のスクリプトで利用可能なインデックスを確認し、`--camera` オプションで指定し直してください。内蔵カメラは通常 `0`、Continuity Camera は `1` または `2` になることが多いです。

### フレーム取得に連続して失敗したため終了します

カメラが動作中に切断された場合に表示されます（`quick_demo.py` は連続 30 回失敗で自動終了します）。USB 接続を確認し、再度カメラを認識させてから起動し直してください。

### 検出結果に誤検知が多い

`--conf` オプションで信頼度閾値を上げてください（例: `python quick_demo.py --conf 0.65`）。

<!-- TODO: Issue/PR での既知の問題があれば追記 -->

---

## 今後の予定

- [ ] マルチスレッド実装（CameraThread / InferenceThread / DisplayThread）
- [ ] ByteTrack 追跡の統合
- [ ] Core ML 変換スクリプト（Neural Engine 最適化）
- [ ] HUD オーバーレイ（クラス別カウント・推論 FPS 表示）
- [ ] FPS ベンチマーク（n/s/m モデル比較）
- [ ] セットアップスクリプト（`bash setup.sh` 一発）

---

## ライセンス

MIT
