EFF++ Prompts (CFAD + MTS)

Manipulated (paired CFAD)
```
System: You compare a real face image and a manipulated one.
User: [REAL_IMAGE], [FAKE_IMAGE]
Instruction:
1) Begin with "Yes" or "No".
2) If manipulated, describe concrete artifacts and locations in 1–2 short sentences.
3) Mention the manipulation family summary: <{MTS_SUMMARY_FOR_METHOD}>.
Question: Is this image manipulated?
Style: Yes/No + one short paragraph (<=60 words). Do not guess identity/source/tool names.
```

Real (single image)
```
System: You check whether a face image is manipulated.
User: [REAL_IMAGE]
Instruction:
1) Start with "No" if unmanipulated, then briefly note natural cues (texture/lighting/boundary).
2) Keep it short (<=40 words). Do not speculate identity/source.
Question: Is this image manipulated?
```

Notes:
- MTS text must come from config/mts_summaries.json and match `method` exactly.
- For paired CFAD, always provide location words (e.g., jawline/hairline/nasolabial/cheek/eye region) and artifact words (e.g., boundary smoothing/color mismatch/texture smear/warping/shadow break).
