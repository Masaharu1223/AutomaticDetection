# car-vision 🚗

**MacBook Pro M5 + iPhone（Continuity Camera）でリアルタイム車載物体検出**

YOLOv8 を Apple Neural Engine（Core ML）向けに最適化し、ByteTrack 追跡を組み合わせた車載リアルタイム物体検出システム。

---

## デモ

> *(デモ GIF を撮影後にここへ掲載)*

---

## 特徴

- **Apple Neural Engine 最適化** — Core ML 変換で M5 チップの Neural Engine をフル活用
- **ByteTrack 物体追跡** — フレームをまたいで同一物体に ID を付与、デモ映えする追跡表示
- **HUD オーバーレイ** — FPS・検出クラス数・モデル名をリアルタイム表示
- **車載クラスに絞り込み** — 人・車・トラック・バイク・自転車・信号機・止まれ標識のみ検出
- **セットアップ一発** — `pip install -r requirements.txt` だけで動く

---

## ハードウェア構成

| 機器 | 仕様 |
|---|---|
| MacBook Pro | M5 / 24GB RAM |
| カメラ | iPhone（Continuity Camera）または Logicool C922 |
| 接続 | USB または Wi-Fi（Continuity Camera） |

---

## セットアップ

### 1. 前提条件

- macOS Ventura 以降
- Python 3.12.7（[pyenv](https://github.com/pyenv/pyenv) 推奨）

> **pyenv を使う場合の注意点**：Python ビルド前に `xz` を先にインストールしてください。
> `xz` なしでビルドすると `_lzma` モジュールが欠落し `torchvision` が動作しません。

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

## モデル性能（Core ML 変換後の期待 FPS / M5）

| モデル | mAP | 期待 FPS |
|---|---|---|
| YOLOv8n（nano） | 37.3 | 60〜100 FPS |
| YOLOv8s（small） | 44.9 | 40〜60 FPS |
| YOLOv8m（medium） | 50.2 | 25〜40 FPS |

---

## 検出クラス（COCO）

`person` / `bicycle` / `car` / `motorcycle` / `bus` / `truck` / `traffic light` / `stop sign`

---

## 今後の予定

- [ ] マルチスレッド実装（CameraThread / InferenceThread / DisplayThread）
- [ ] ByteTrack 追跡の統合
- [ ] Core ML 変換スクリプト（Neural Engine 最適化）
- [ ] HUD オーバーレイ（クラス別カウント・推論 FPS 表示）
- [ ] FPS ベンチマーク（n/s/m モデル比較）
- [ ] セットアップスクリプト（`bash setup.sh` 一発）
- [ ] デモ GIF を README に掲載

---

## ライセンス

MIT
