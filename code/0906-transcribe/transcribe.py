# -*- coding: utf-8 -*-
"""whisper large-v3 逐字转写脚本：WAV -> JSON(全文+分段+质量指标)"""
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="whisper 逐字转写")
    parser.add_argument("audio", help="输入音频文件(wav)")
    parser.add_argument("output_json", help="输出 JSON 路径")
    parser.add_argument("--model", default="large-v3", help="whisper 模型名")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.is_file():
        print(f"错误: 音频文件不存在: {audio_path}", file=sys.stderr)
        return 1

    import whisper

    print(f"加载模型 {args.model} ...", flush=True)
    model = whisper.load_model(args.model)

    print("开始转写(GPU fp16)...", flush=True)
    result = model.transcribe(str(audio_path), fp16=True, verbose=False)

    segments = [
        {
            "id": s["id"],
            "start": round(s["start"], 2),
            "end": round(s["end"], 2),
            "text": s["text"].strip(),
            "avg_logprob": round(s["avg_logprob"], 4),
            "no_speech_prob": round(s["no_speech_prob"], 4),
        }
        for s in result["segments"]
    ]

    low_conf = [s for s in segments if s["avg_logprob"] < -1.0]
    payload = {
        "language": result["language"],
        "full_text": result["text"].strip(),
        "segments": segments,
        "stats": {
            "segment_count": len(segments),
            "low_confidence_count": len(low_conf),
            "mean_avg_logprob": round(
                sum(s["avg_logprob"] for s in segments) / len(segments), 4
            ) if segments else None,
        },
    }

    out = Path(args.output_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"语言: {payload['language']}")
    print(f"分段数: {payload['stats']['segment_count']}")
    print(f"低置信段(avg_logprob<-1.0): {payload['stats']['low_confidence_count']}")
    print(f"平均logprob: {payload['stats']['mean_avg_logprob']}")
    print(f"结果已写入: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
