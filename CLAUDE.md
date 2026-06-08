# 車載リアルタイム物体検出プロジェクト

## プロジェクト概要

車に取り付けたカメラからリアルタイムに物体を検出するソフトウェアの開発。
GitHubへの成果公開を目的とし、リアルタイム性を最優先とする。

---

## ハードウェア構成

### メイン処理機

| 項目 | 内容 |
|---|---|
| 機種 | MacBook Pro M5 |
| RAM | 24GB |
| 活用ポイント | Apple Neural Engine（Core ML経由） |

### カメラ

#### オプション A：iPhone（Continuity Camera）推奨

| 項目 | 内容 |
|---|---|
| 対応機種 | iPhone 12 以降 |
| 対応OS | iPhone: iOS 16+ / Mac: macOS Ventura+ |
| 解像度/FPS | 1920×1080 @ 30FPS |
| 接続 | USB（充電しながら使用可・安定）またはワイヤレス（Wi-Fi） |
| コスト | 追加費用ゼロ（既持ちの iPhone を利用） |
| OpenCV アクセス | `cv2.VideoCapture(index)` で仮想デバイスとして認識 |
| 注意点 | 長時間使用時の iPhone 発熱・バッテリー消費に注意 |

#### オプション B：外部 USB カメラ（本番運用向け）

| 項目 | 内容 |
|---|---|
| 推奨製品 | ロジクール C922 |
| 解像度/FPS | 1080p @ **30FPS**（※60FPS は 720p のみ） |
| 720p/60FPS | 60FPS が必要な場合は 720p に設定 |
| 接続 | 有線 USB 3.0（UVC 規格） |

> **デフォルト設定**: 720p@60fps（リアルタイム性優先）/ 必要に応じて 1080p@30fps に切替可

### その他必要機材

| パーツ | 製品例 | 価格目安 |
|---|---|---|
| 車載マウント | ダッシュボード吸盤式 | 約1,500〜3,000円 |
| USB-C → USB-A ハブ | USB 3.0対応 | 約2,000円 |

**合計目安：約15,000〜17,000円**

---

## ソフトウェア構成

| 要素 | 技術選定 |
|---|---|
| 物体検出モデル | YOLOv8 |
| Neural Engine活用 | Core ML変換 |
| 物体追跡 | ByteTrack |
| カメラ入力 | OpenCV |
| 言語 | Python 3.12.7（pyenv local で固定） |

### Core ML変換（Neural Engine最適化）

```python
from ultralytics import YOLO

model = YOLO("yolov8s.pt")  # s（small）を基準モデルとして使用
model.export(format="coreml")  # Apple Neural Engine向けに変換
```

> **モデルサイズはプロジェクト全体で `s`（small）に統一する。**
> nano（n）は FPS ベンチマーク比較用として benchmark/ スクリプトで測定する。

### 環境構築（pyenv）

> **重要な落とし穴**: pyenv で Python をビルドする前に `xz` が無いと `_lzma` C拡張が組み込まれず、
> `torchvision` の import 時に `ModuleNotFoundError: No module named '_lzma'` で失敗する。
> 必ず `xz` を先に入れてから Python をビルドすること。

```bash
# 1. xz を先にインストール（_lzma の前提）
brew install xz

# 2. xz を検出させてプロジェクト用 Python をビルド
export LDFLAGS="-L/opt/homebrew/opt/xz/lib"
export CPPFLAGS="-I/opt/homebrew/opt/xz/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/xz/lib/pkgconfig"
pyenv install 3.12.7

# 3. このプロジェクトでだけ 3.12.7 を使う
cd ~/AutomaticDetection
pyenv local 3.12.7      # .python-version が作られる

# 4. 依存ライブラリをインストール
pip install -r requirements.txt
```

### 期待FPS（Core ML変換後）

| モデル | FPS |
|---|---|
| YOLOv8n（nano） | 60〜100 FPS |
| YOLOv8s（small） | 40〜60 FPS |
| YOLOv8m（medium） | 25〜40 FPS |

---

## データフロー

```
[カメラ] ──USB 3.0──▶ [MacBook Pro M5] ──▶ [検出結果表示]
                              │
                        Neural Engine
                        Core ML / YOLOv8
                        ByteTrack追跡
```

---

## デモ・開発時の仮カメラ構成

本番カメラ購入前の開発・デモに使用できる代替手段：

| 方法 | 詳細 |
|---|---|
| MacBook内蔵カメラ | 追加費用ゼロ・今すぐ利用可能 |
| iPhone（Continuity Camera） | iOS17 + macOS Sonoma以降・USB接続・高画質 |
| 車載動画ファイル | 再現性が高くデモに最適 |

---

## GitHubリポジトリ構成案

```
car-vision/
├── README.md                  # デモGIF・構成図・ベンチマーク掲載
├── config.yaml                # ユーザー設定（git 管理対象）
├── config_default.yaml        # デフォルト値のリファレンス
├── requirements.txt           # 依存ライブラリ一覧
├── .gitignore                 # models/*.mlpackage / *.pt / logs/ を除外
├── detection/
│   ├── main.py                # メインループ・スレッド管理・シャットダウン制御
│   ├── detector.py            # CoreML 対応 YOLO ラッパー
│   ├── tracker.py             # ByteTrack 物体追跡
│   └── models.py              # Track / DetectionResult データクラス
├── overlay/
│   └── hud.py                 # FPS・ラベル・クラス数 HUD 表示
├── benchmark/
│   └── fps_benchmark.py       # n/s/m モデル FPS 比較計測スクリプト
├── scripts/
│   └── setup_mac.sh           # brew + pip 一発セットアップ
├── models/
│   └── export_coreml.py       # CoreML 変換スクリプト（.pt → .mlpackage）
└── logs/                      # ログ出力ディレクトリ（.gitignore 対象）
    └── .gitkeep
```

**`.gitignore` に含めるもの：**
```
models/*.mlpackage
models/*.pt
logs/*.log
output/
__pycache__/
*.pyc
.DS_Store
```

---

## GitHub公開に向けた差別化ポイント

- **Core ML / Neural Engine最適化** → FPSベンチマーク比較表をREADMEに掲載
- **ByteTrackによる物体追跡** → 同一物体へのID付与でデモ動画が映える
- **HUD表示** → 速度・FPS・検出クラス数のオーバーレイ
- **デモGIF** → 録画した検出映像をREADMEに掲載
- **セットアップスクリプト** → `bash setup.sh` 一発で環境構築

---

## スレッド構成とデータフロー（詳細設計）

### スレッド分離方針

リアルタイム性を確保するため、カメラキャプチャ・推論・表示を **3スレッドに分離** する。
各スレッド間は `queue.Queue(maxsize=1)` でつなぎ、常に最新フレームのみを保持する。

```
┌─────────────────────────────────────────────────────┐
│ CameraThread                                         │
│  VideoCapture.read()  →  frameQueue（maxsize=1）    │
│  古いフレームは非ブロッキングで破棄                  │
└──────────────────┬──────────────────────────────────┘
                   │ np.ndarray（BGR フレーム）
                   ▼
┌─────────────────────────────────────────────────────┐
│ InferenceThread                                      │
│  YOLOv8（CoreML）推論 → ByteTrack 追跡             │
│  →  resultQueue（maxsize=1）                        │
└──────────────────┬──────────────────────────────────┘
                   │ DetectionResult（tracks, meta）
                   ▼
┌─────────────────────────────────────────────────────┐
│ DisplayThread（メインスレッド）                      │
│  HUD 描画 →  cv2.imshow()                          │
│  キー入力： q=終了 / s=スクリーンショット保存        │
└─────────────────────────────────────────────────────┘
```

### キュー設計

| キュー | 型 | maxsize | 破棄ポリシー |
|---|---|---|---|
| frameQueue | `queue.Queue` | 1 | get_nowait で取り出し、入れ替え |
| resultQueue | `queue.Queue` | 1 | 同上 |

### DetectionResult データ構造

```python
@dataclass
class Track:
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2

@dataclass
class DetectionResult:
    frame: np.ndarray
    tracks: list[Track]
    inference_fps: float
    timestamp: datetime
```

---

## HUD 表示仕様（詳細設計）

### レイアウト（1080p 基準）

```
┌──────────────────────────────────────────────────────────┐
│ 表示FPS: 42.3  推論FPS: 28.1                  14:23:05  │
│                                                           │
│      ┌──────────────┐                                   │
│      │ #3           │  ← トラッキング ID                │
│      │ car  0.91    │  ← クラス名 + 信頼度              │
│      └──────────────┘                                   │
│                                                           │
│ car:3  person:2  truck:1           yolov8s-coreml        │
└──────────────────────────────────────────────────────────┘
```

### HUD 要素一覧

| 位置 | 表示内容 | 例 |
|---|---|---|
| 左上 | 表示FPS / 推論FPS | `Display: 42.3 FPS  Infer: 28.1 FPS` |
| 右上 | 現在時刻 | `14:23:05` |
| バウンディングボックス | トラックID・クラス名・信頼度 | `#3 car 0.91` |
| 左下 | クラス別検出数 | `car:3  person:2  truck:1` |
| 右下 | 使用モデル名 | `yolov8s-coreml` |

### クラス別カラー定義

```python
CLASS_COLORS = {
    "person":        (0, 255, 127),   # 緑
    "car":           (255, 200,   0),  # 黄
    "truck":         (255, 100,   0),  # オレンジ
    "bus":           (255,   0,   0),  # 赤
    "motorcycle":    (200,   0, 255),  # 紫
    "bicycle":       (0, 200, 255),   # 水色
    "traffic light": (0, 255, 255),   # シアン
    "stop sign":     (255,   0, 100),  # ピンク
}
```

---

## 設定ファイル設計（config.yaml）

```yaml
model:
  path: "models/yolov8s.mlpackage"   # CoreML 変換済みモデル（パスが唯一の真実）
  conf_threshold: 0.45
  iou_threshold: 0.70
  target_classes:                     # COCO クラス ID（車載用に絞り込み）
    - 0   # person
    - 1   # bicycle
    - 2   # car
    - 3   # motorcycle
    - 5   # bus
    - 7   # truck
    - 9   # traffic light
    - 11  # stop sign

camera:
  index: 0          # 0=内蔵カメラ / 1=Continuity Camera or 外部 USB
  width: 1280       # デフォルト 720p（リアルタイム性優先）
  height: 720
  fps: 60           # 1080p を使う場合は width:1920 height:1080 fps:30 に変更

tracker:            # ByteTrack パラメータ
  track_thresh: 0.50
  track_buffer: 30
  match_thresh: 0.80

hud:
  show_fps: true
  show_class_count: true
  show_timestamp: true
  show_model_name: true
  font_scale: 0.6
  line_thickness: 2

output:
  save_video: false
  output_dir: "output/"
```

### 設定の優先順位

```
コマンドライン引数 > config.yaml > デフォルト値
```

起動例：

```bash
python detection/main.py --config config.yaml --model-size n --camera 1
```

---

## エラーハンドリング設計

### エラー種別と対処方針

| エラー種別 | 発生タイミング | 対処 |
|---|---|---|
| カメラ未検出 | 起動時 | エラーメッセージ表示して即終了 |
| カメラ切断 | 動作中 | 3秒間隔で5回リトライ→失敗で終了 |
| 空フレーム受信 | 動作中 | スキップして次フレームへ（ログ警告） |
| モデルファイル未発見 | 起動時 | 即終了（CoreML変換コマンドをガイド表示） |
| CoreMLロード失敗 | 起動時 | 即終了（Python版にフォールバックするか確認） |
| 推論エラー | 動作中 | スキップして次フレームへ（ログ警告） |
| キュータイムアウト | 動作中 | 次フレームへ（致命的ではない） |

### 起動時チェック順序

```python
# main.py 起動時のバリデーション順序
1. config.yaml の存在・パース確認
2. モデルファイル（.mlpackage）の存在確認
3. カメラデバイスの接続確認（cv2.VideoCapture(index).isOpened()）
4. 書き込みディレクトリの権限確認（output/ が save_video=true の場合）
```

### スレッドシャットダウン設計

`threading.Event` を使い、全スレッドに終了シグナルを送る。

```python
stop_event = threading.Event()

# DisplayThread（メインスレッド）で q キー検出時
if cv2.waitKey(1) & 0xFF == ord('q'):
    stop_event.set()           # 全スレッドに終了シグナル

# 各スレッドのループ条件
while not stop_event.is_set():
    ...

# メインスレッドで全スレッドの終了を待機
camera_thread.join(timeout=3.0)
inference_thread.join(timeout=3.0)
cap.release()
cv2.destroyAllWindows()
```

### カメラ再接続ロジック

```python
MAX_RETRY = 5
RETRY_INTERVAL_SEC = 3.0

def reconnect_camera(config) -> cv2.VideoCapture | None:
    for attempt in range(MAX_RETRY):
        cap = cv2.VideoCapture(config.camera.index)
        if cap.isOpened():
            return cap
        logger.warning(f"Camera reconnect attempt {attempt+1}/{MAX_RETRY}")
        time.sleep(RETRY_INTERVAL_SEC)
    return None  # 全試行失敗
```

### ログ設計

```python
# ログレベル定義
DEBUG   : フレームスキップ回数、キューサイズ変化
INFO    : 起動・終了、モデルロード完了、FPS統計（5秒ごと）
WARNING : 空フレーム、推論スキップ、カメラ再接続試行
ERROR   : 致命的エラー（終了前に出力）
```

ログフォーマット：

```
2024-06-08 14:23:05 [INFO ] Model loaded: yolov8s.mlpackage (CoreML)
2024-06-08 14:23:05 [INFO ] Camera opened: index=0, 1920x1080 @60fps
2024-06-08 14:23:10 [INFO ] Running: display=42.1fps infer=28.3fps
2024-06-08 14:24:01 [WARN ] Empty frame received, skipping (count=3)
2024-06-08 14:25:30 [ERROR] Camera disconnected. Retrying 1/5...
```

ログ出力先：標準出力 + `logs/detector_YYYYMMDD.log`

---

## 次のステップ

1. カメラ・マウント・USBハブを購入
2. iPhoneまたは内蔵カメラでデモ用コードを作成・動作確認
3. Core ML変換でNeural Engineを最大活用
4. ByteTrack追跡を統合
5. GitHubにREADME＋デモGIFで公開
