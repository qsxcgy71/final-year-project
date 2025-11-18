# EFF++ Alignment QA Panel

- Seed: 42
- Frames per identity: 3
- Methods: original, Deepfakes, Face2Face, FaceSwap, NeuralTextures

## Split `train`

### Identity `910`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/train/910/original/frame_0000.jpg | data/effpp_cache/crops/train/910/original/frame_0000.jpg |
| 0 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/910/original/frame_0000.jpg | data/effpp_cache/crops/train/910/Face2Face/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/train/910/original/frame_0001.jpg | data/effpp_cache/crops/train/910/original/frame_0001.jpg |
| 1 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/910/original/frame_0001.jpg | data/effpp_cache/crops/train/910/Face2Face/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/train/910/original/frame_0002.jpg | data/effpp_cache/crops/train/910/original/frame_0002.jpg |
| 2 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/910/original/frame_0002.jpg | data/effpp_cache/crops/train/910/Face2Face/frame_0002.jpg |

### Identity `462`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/train/462/original/frame_0000.jpg | data/effpp_cache/crops/train/462/original/frame_0000.jpg |
| 0 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/462/original/frame_0000.jpg | data/effpp_cache/crops/train/462/Deepfakes/frame_0000.jpg |
| 0 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/462/original/frame_0000.jpg | data/effpp_cache/crops/train/462/Face2Face/frame_0000.jpg |
| 0 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/462/original/frame_0000.jpg | data/effpp_cache/crops/train/462/FaceSwap/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/train/462/original/frame_0001.jpg | data/effpp_cache/crops/train/462/original/frame_0001.jpg |
| 1 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/462/original/frame_0001.jpg | data/effpp_cache/crops/train/462/Deepfakes/frame_0001.jpg |
| 1 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/462/original/frame_0001.jpg | data/effpp_cache/crops/train/462/Face2Face/frame_0001.jpg |
| 1 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/462/original/frame_0001.jpg | data/effpp_cache/crops/train/462/FaceSwap/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/train/462/original/frame_0002.jpg | data/effpp_cache/crops/train/462/original/frame_0002.jpg |
| 2 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/462/original/frame_0002.jpg | data/effpp_cache/crops/train/462/Deepfakes/frame_0002.jpg |
| 2 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/462/original/frame_0002.jpg | data/effpp_cache/crops/train/462/Face2Face/frame_0002.jpg |
| 2 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/462/original/frame_0002.jpg | data/effpp_cache/crops/train/462/FaceSwap/frame_0002.jpg |

### Identity `708`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/train/708/original/frame_0000.jpg | data/effpp_cache/crops/train/708/original/frame_0000.jpg |
| 0 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/708/original/frame_0000.jpg | data/effpp_cache/crops/train/708/Deepfakes/frame_0000.jpg |
| 0 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/train/708/original/frame_0000.jpg | data/effpp_cache/crops/train/708/NeuralTextures/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/train/708/original/frame_0001.jpg | data/effpp_cache/crops/train/708/original/frame_0001.jpg |
| 1 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/708/original/frame_0001.jpg | data/effpp_cache/crops/train/708/Deepfakes/frame_0001.jpg |
| 1 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/train/708/original/frame_0001.jpg | data/effpp_cache/crops/train/708/NeuralTextures/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/train/708/original/frame_0002.jpg | data/effpp_cache/crops/train/708/original/frame_0002.jpg |
| 2 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/708/original/frame_0002.jpg | data/effpp_cache/crops/train/708/Deepfakes/frame_0002.jpg |
| 2 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/train/708/original/frame_0002.jpg | data/effpp_cache/crops/train/708/NeuralTextures/frame_0002.jpg |

### Identity `600`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/train/600/original/frame_0000.jpg | data/effpp_cache/crops/train/600/original/frame_0000.jpg |
| 0 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/600/original/frame_0000.jpg | data/effpp_cache/crops/train/600/Deepfakes/frame_0000.jpg |
| 0 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/600/original/frame_0000.jpg | data/effpp_cache/crops/train/600/Face2Face/frame_0000.jpg |
| 0 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/600/original/frame_0000.jpg | data/effpp_cache/crops/train/600/FaceSwap/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/train/600/original/frame_0001.jpg | data/effpp_cache/crops/train/600/original/frame_0001.jpg |
| 1 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/600/original/frame_0001.jpg | data/effpp_cache/crops/train/600/Deepfakes/frame_0001.jpg |
| 1 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/600/original/frame_0001.jpg | data/effpp_cache/crops/train/600/Face2Face/frame_0001.jpg |
| 1 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/600/original/frame_0001.jpg | data/effpp_cache/crops/train/600/FaceSwap/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/train/600/original/frame_0002.jpg | data/effpp_cache/crops/train/600/original/frame_0002.jpg |
| 2 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/600/original/frame_0002.jpg | data/effpp_cache/crops/train/600/Deepfakes/frame_0002.jpg |
| 2 | Face2Face | Yes, explanation pending | Expression transfer; artifacts cluster near mouth corners and nasolabial folds. | data/effpp_cache/crops/train/600/original/frame_0002.jpg | data/effpp_cache/crops/train/600/Face2Face/frame_0002.jpg |
| 2 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/600/original/frame_0002.jpg | data/effpp_cache/crops/train/600/FaceSwap/frame_0002.jpg |

### Identity `805`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/train/805/original/frame_0000.jpg | data/effpp_cache/crops/train/805/original/frame_0000.jpg |
| 0 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/805/original/frame_0000.jpg | data/effpp_cache/crops/train/805/Deepfakes/frame_0000.jpg |
| 0 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/805/original/frame_0000.jpg | data/effpp_cache/crops/train/805/FaceSwap/frame_0000.jpg |
| 0 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/train/805/original/frame_0000.jpg | data/effpp_cache/crops/train/805/NeuralTextures/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/train/805/original/frame_0001.jpg | data/effpp_cache/crops/train/805/original/frame_0001.jpg |
| 1 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/805/original/frame_0001.jpg | data/effpp_cache/crops/train/805/Deepfakes/frame_0001.jpg |
| 1 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/805/original/frame_0001.jpg | data/effpp_cache/crops/train/805/FaceSwap/frame_0001.jpg |
| 1 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/train/805/original/frame_0001.jpg | data/effpp_cache/crops/train/805/NeuralTextures/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/train/805/original/frame_0002.jpg | data/effpp_cache/crops/train/805/original/frame_0002.jpg |
| 2 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/train/805/original/frame_0002.jpg | data/effpp_cache/crops/train/805/Deepfakes/frame_0002.jpg |
| 2 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/train/805/original/frame_0002.jpg | data/effpp_cache/crops/train/805/FaceSwap/frame_0002.jpg |
| 2 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/train/805/original/frame_0002.jpg | data/effpp_cache/crops/train/805/NeuralTextures/frame_0002.jpg |


## Split `val`

### Identity `794`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/val/794/original/frame_0000.jpg | data/effpp_cache/crops/val/794/original/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/val/794/original/frame_0001.jpg | data/effpp_cache/crops/val/794/original/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/val/794/original/frame_0002.jpg | data/effpp_cache/crops/val/794/original/frame_0002.jpg |

### Identity `925`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/val/925/original/frame_0000.jpg | data/effpp_cache/crops/val/925/original/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/val/925/original/frame_0001.jpg | data/effpp_cache/crops/val/925/original/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/val/925/original/frame_0002.jpg | data/effpp_cache/crops/val/925/original/frame_0002.jpg |

### Identity `773`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/val/773/original/frame_0000.jpg | data/effpp_cache/crops/val/773/original/frame_0000.jpg |
| 0 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/val/773/original/frame_0000.jpg | data/effpp_cache/crops/val/773/FaceSwap/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/val/773/original/frame_0001.jpg | data/effpp_cache/crops/val/773/original/frame_0001.jpg |
| 1 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/val/773/original/frame_0001.jpg | data/effpp_cache/crops/val/773/FaceSwap/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/val/773/original/frame_0002.jpg | data/effpp_cache/crops/val/773/original/frame_0002.jpg |
| 2 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/val/773/original/frame_0002.jpg | data/effpp_cache/crops/val/773/FaceSwap/frame_0002.jpg |

### Identity `698`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/val/698/original/frame_0000.jpg | data/effpp_cache/crops/val/698/original/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/val/698/original/frame_0001.jpg | data/effpp_cache/crops/val/698/original/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/val/698/original/frame_0002.jpg | data/effpp_cache/crops/val/698/original/frame_0002.jpg |

### Identity `322`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/val/322/original/frame_0000.jpg | data/effpp_cache/crops/val/322/original/frame_0000.jpg |
| 0 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/val/322/original/frame_0000.jpg | data/effpp_cache/crops/val/322/Deepfakes/frame_0000.jpg |
| 0 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/val/322/original/frame_0000.jpg | data/effpp_cache/crops/val/322/FaceSwap/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/val/322/original/frame_0001.jpg | data/effpp_cache/crops/val/322/original/frame_0001.jpg |
| 1 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/val/322/original/frame_0001.jpg | data/effpp_cache/crops/val/322/Deepfakes/frame_0001.jpg |
| 1 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/val/322/original/frame_0001.jpg | data/effpp_cache/crops/val/322/FaceSwap/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/val/322/original/frame_0002.jpg | data/effpp_cache/crops/val/322/original/frame_0002.jpg |
| 2 | Deepfakes | Yes, explanation pending | Learned face replacement; watch for boundary seams and texture inconsistency. | data/effpp_cache/crops/val/322/original/frame_0002.jpg | data/effpp_cache/crops/val/322/Deepfakes/frame_0002.jpg |
| 2 | FaceSwap | Yes, explanation pending | Graphics-based whole face swap; jawline and hairline often misalign or show color mismatch. | data/effpp_cache/crops/val/322/original/frame_0002.jpg | data/effpp_cache/crops/val/322/FaceSwap/frame_0002.jpg |


## Split `test`

### Identity `389`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/test/389/original/frame_0000.jpg | data/effpp_cache/crops/test/389/original/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/test/389/original/frame_0001.jpg | data/effpp_cache/crops/test/389/original/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/test/389/original/frame_0002.jpg | data/effpp_cache/crops/test/389/original/frame_0002.jpg |

### Identity `875`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/test/875/original/frame_0000.jpg | data/effpp_cache/crops/test/875/original/frame_0000.jpg |
| 0 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/test/875/original/frame_0000.jpg | data/effpp_cache/crops/test/875/NeuralTextures/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/test/875/original/frame_0001.jpg | data/effpp_cache/crops/test/875/original/frame_0001.jpg |
| 1 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/test/875/original/frame_0001.jpg | data/effpp_cache/crops/test/875/NeuralTextures/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/test/875/original/frame_0002.jpg | data/effpp_cache/crops/test/875/original/frame_0002.jpg |
| 2 | NeuralTextures | Yes, explanation pending | Neural texture rendering; specular highlights and fine detail may smear or flicker. | data/effpp_cache/crops/test/875/original/frame_0002.jpg | data/effpp_cache/crops/test/875/NeuralTextures/frame_0002.jpg |

### Identity `954`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/test/954/original/frame_0000.jpg | data/effpp_cache/crops/test/954/original/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/test/954/original/frame_0001.jpg | data/effpp_cache/crops/test/954/original/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/test/954/original/frame_0002.jpg | data/effpp_cache/crops/test/954/original/frame_0002.jpg |

### Identity `099`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/test/099/original/frame_0000.jpg | data/effpp_cache/crops/test/099/original/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/test/099/original/frame_0001.jpg | data/effpp_cache/crops/test/099/original/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/test/099/original/frame_0002.jpg | data/effpp_cache/crops/test/099/original/frame_0002.jpg |

### Identity `470`
- Frame indices: 128
- Methods: original:✓ | Deepfakes:✓ | Face2Face:✓ | FaceSwap:✓ | NeuralTextures:✓

| Rank | Method | Answer | Technique | Real Frame | Target Frame |
| --- | --- | --- | --- | --- | --- |
| 0 | original | No, explanation pending |  | data/effpp_cache/crops/test/470/original/frame_0000.jpg | data/effpp_cache/crops/test/470/original/frame_0000.jpg |
| 1 | original | No, explanation pending |  | data/effpp_cache/crops/test/470/original/frame_0001.jpg | data/effpp_cache/crops/test/470/original/frame_0001.jpg |
| 2 | original | No, explanation pending |  | data/effpp_cache/crops/test/470/original/frame_0002.jpg | data/effpp_cache/crops/test/470/original/frame_0002.jpg |

