"""
quick_demo.py — 内蔵カメラ or Continuity Camera で YOLOv8 動作確認
依存: pip install ultralytics opencv-python
使い方: python quick_demo.py [--camera INDEX]
"""
import argparse
import logging
import time

import cv2
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# 車載用に絞ったクラス（COCO ID）— 定数なので tuple
# person, bicycle, car, motorcycle, bus, truck, traffic light, stop sign
TARGET_CLASSES: tuple[int, ...] = (0, 1, 2, 3, 5, 7, 9, 11)

# フレーム取得が連続でこの回数失敗したら終了する
MAX_READ_FAILURES = 30


def _conf_type(value: str) -> float:
    """--conf を 0.0〜1.0 の範囲に制限する argparse 用バリデータ。"""
    f = float(value)
    if not 0.0 < f < 1.0:
        raise argparse.ArgumentTypeError(
            f"--conf は 0.0〜1.0 の範囲で指定してください (got {f})"
        )
    return f


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析する。"""
    parser = argparse.ArgumentParser(description="YOLOv8 quick demo")
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="カメラインデックス (default: 0)",
    )
    parser.add_argument(
        "--model",
        default="yolov8s.pt",
        help="モデルファイル (default: yolov8s.pt)",
    )
    parser.add_argument(
        "--conf",
        type=_conf_type,
        default=0.45,
        help="信頼度閾値 0.0〜1.0 (default: 0.45)",
    )
    return parser.parse_args()


def main() -> None:
    """カメラからフレームを取得して YOLOv8 推論結果をリアルタイム表示する。"""
    args = parse_args()

    logger.info("モデル読み込み: %s", args.model)
    model = YOLO(args.model)  # 初回起動時は自動ダウンロード

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        cap.release()  # 未オープンでも release は安全
        logger.error("カメラ (index=%d) を開けませんでした", args.camera)
        logger.error("  内蔵カメラ: --camera 0")
        logger.error("  Continuity Camera: --camera 1 (または 2)")
        return

    logger.info("起動完了。q キーで終了。")

    prev_time = time.perf_counter()
    consecutive_failures = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                consecutive_failures += 1
                logger.warning(
                    "フレームを取得できませんでした (%d/%d)",
                    consecutive_failures,
                    MAX_READ_FAILURES,
                )
                if consecutive_failures >= MAX_READ_FAILURES:
                    logger.error("フレーム取得に連続して失敗したため終了します")
                    break
                time.sleep(0.1)
                continue
            consecutive_failures = 0

            results = model(
                frame,
                classes=list(TARGET_CLASSES),
                conf=args.conf,
                verbose=False,
            )
            annotated = results[0].plot()

            # ループ全体のスループット FPS（推論＋描画を含む）
            now = time.perf_counter()
            fps = 1.0 / (now - prev_time) if now != prev_time else 0.0
            prev_time = now

            cv2.putText(
                annotated,
                f"FPS: {fps:.1f}  model: {args.model}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.imshow("YOLOv8 Quick Demo — press q to quit", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Demo stopped.")


if __name__ == "__main__":
    main()
