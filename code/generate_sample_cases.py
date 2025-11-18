import json
from pathlib import Path
from typing import Dict, List

def load_progress(path: Path) -> List[Dict[str, object]]:
    records = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line))
    return records

def build_cases(records: List[Dict[str, object]], question_id: str, base_faces: Path, limit: int = 4) -> Dict[str, List[Dict[str, object]]]:
    buckets = {"tp": [], "tn": [], "fp": [], "fn": []}
    for item in records:
        label = int(item.get('label', 0))
        stats = item.get('questions', {}).get(question_id)
        if not stats:
            continue
        yes = stats.get('yes', 0)
        total = stats.get('total', 0)
        pred = stats.get('prediction', False)
        if label == 1 and pred:
            key = 'tp'
        elif label == 0 and not pred:
            key = 'tn'
        elif label == 0 and pred:
            key = 'fp'
        else:
            key = 'fn'
        if len(buckets[key]) >= limit:
            continue
        method = item.get('method', '')
        split = item.get('split', '')
        label_str = 'real' if label == 0 else 'fake'
        video_id = str(item.get('video_id') or item.get('video_key'))
        face_dir = base_faces / split / label_str / method / video_id
        frame_path = None
        if face_dir.exists():
            frames = sorted(face_dir.glob('frame_*.jpg'))
            if frames:
                frame_path = str(frames[0].relative_to(base_faces.parent.parent))
        buckets[key].append({
            'video_id': video_id,
            'split': split,
            'label': label,
            'method': method,
            'yes': yes,
            'total': total,
            'yes_rate': yes / total if total else 0.0,
            'frame': frame_path,
        })
    return buckets

def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    rankings = json.loads((project_root / 'mfa' / 'ffpp_c23' / 'mfa_feature_rankings.json').read_text(encoding='utf-8'))
    top_question = rankings['ranking'][0]['id'] if rankings['ranking'] else None
    if not top_question:
        raise RuntimeError('No question rankings found')

    val_records = load_progress(project_root / 'mfa' / 'ffpp_c23' / 'mfa_ffpp_val_progress.jsonl')
    test_records = load_progress(project_root / 'mfa' / 'ffpp_c23' / 'mfa_ffpp_test_progress.jsonl')
    base_faces = project_root / 'data' / 'processed' / 'ffpp_c23' / 'faces_224'

    samples = {
        'question_id': top_question,
        'val': build_cases(val_records, top_question, base_faces),
        'test': build_cases(test_records, top_question, base_faces),
    }

    out_dir = project_root / 'reports'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'sample_cases.json').write_text(json.dumps(samples, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Sample cases written to reports/sample_cases.json')

if __name__ == '__main__':
    main()
