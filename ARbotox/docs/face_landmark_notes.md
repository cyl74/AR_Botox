
# Face Landmarker Notes

Refer to face_landmarker.py for details on the implementations.

---

Face Landmarks
---
There are a total of 478 landmark points from the detector result. Each point has a Normalized (x,y,z) value.


---

Face Blendshapes
---

After running detector on the frame/image, the result contains data about the face blendshape that was read. 
This model outputs labels to specific landmark points as different points of the facial anatomy.

It is a subset of 146 landmarks from 478 landmarks
0, 1, 4, 5, 6, 7, 8, 10, 13, 14, 17, 21, 33, 37, 39, 40, 46, 52, 53, 54, 55, 58, 61, 63, 65, 66, 67, 70, 78, 80,
81, 82, 84, 87, 88, 91, 93, 95, 103, 105, 107, 109, 127, 132, 133, 136, 144, 145, 146, 148, 149, 150, 152, 153, 154, 155, 157,
158, 159, 160, 161, 162, 163, 168, 172, 173, 176, 178, 181, 185, 191, 195, 197, 234, 246, 249, 251, 263, 267, 269, 270, 276, 282,
283, 284, 285, 288, 291, 293, 295, 296, 297, 300, 308, 310, 311, 312, 314, 317, 318, 321, 323, 324, 332, 334, 336, 338, 356,
361, 362, 365, 373, 374, 375, 377, 378, 379, 380, 381, 382, 384, 385, 386, 387, 388, 389, 390, 397, 398, 400, 402, 405,
409, 415, 454, 466, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477
----
An example of what is stored
in ```detection_result.face_blendshapes```:

```
[[
Category(index=0, score=6.324190167106281e-07, display_name='', category_name='_neutral'), 
Category(index=1, score=0.0005110223428346217, display_name='', category_name='browDownLeft'), 
Category(index=2, score=0.00015273834287654608, display_name='', category_name='browDownRight'), 
Category(index=3, score=0.6250090599060059, display_name='', category_name='browInnerUp'), 
Category(index=4, score=0.6250942945480347, display_name='', category_name='browOuterUpLeft'), 
Category(index=5, score=0.6313396692276001, display_name='', category_name='browOuterUpRight'), 
Category(index=6, score=1.479985803598538e-05, display_name='', category_name='cheekPuff'), 
Category(index=7, score=1.4979718798713293e-06, display_name='', category_name='cheekSquintLeft'), 
Category(index=8, score=2.1117028836670215e-07, display_name='', category_name='cheekSquintRight'), 
Category(index=9, score=0.17103981971740723, display_name='', category_name='eyeBlinkLeft'), 
Category(index=10, score=0.14476324617862701, display_name='', category_name='eyeBlinkRight'), 
Category(index=11, score=0.47322794795036316, display_name='', category_name='eyeLookDownLeft'), 
Category(index=12, score=0.4712037146091461, display_name='', category_name='eyeLookDownRight'), 
Category(index=13, score=0.026086581870913506, display_name='', category_name='eyeLookInLeft'),
Category(index=14, score=0.18526020646095276, display_name='', category_name='eyeLookInRight'), 
Category(index=15, score=0.17457792162895203, display_name='', category_name='eyeLookOutLeft'), 
Category(index=16, score=0.013710242696106434, display_name='', category_name='eyeLookOutRight'), 
Category(index=17, score=0.01212392095476389, display_name='', category_name='eyeLookUpLeft'), 
Category(index=18, score=0.00747067853808403, display_name='', category_name='eyeLookUpRight'), 
Category(index=19, score=0.26114901900291443, display_name='', category_name='eyeSquintLeft'), 
Category(index=20, score=0.2848570942878723, display_name='', category_name='eyeSquintRight'), 
Category(index=21, score=0.00441537331789732, display_name='', category_name='eyeWideLeft'), 
Category(index=22, score=0.004234365187585354, display_name='', category_name='eyeWideRight'), 
Category(index=23, score=3.567859675968066e-05, display_name='', category_name='jawForward'), 
Category(index=24, score=0.003205548506230116, display_name='', category_name='jawLeft'), 
Category(index=25, score=0.048104509711265564, display_name='', category_name='jawOpen'), 
Category(index=26, score=0.0006901141023263335, display_name='', category_name='jawRight'), 
Category(index=27, score=0.003151414915919304, display_name='', category_name='mouthClose'), 
Category(index=28, score=0.0003097092267125845, display_name='', category_name='mouthDimpleLeft'), 
Category(index=29, score=0.0008072639466263354, display_name='', category_name='mouthDimpleRight'), 
Category(index=30, score=0.001244815532118082, display_name='', category_name='mouthFrownLeft'), 
Category(index=31, score=0.0013021520571783185, display_name='', category_name='mouthFrownRight'), 
Category(index=32, score=0.013409939594566822, display_name='', category_name='mouthFunnel'), 
Category(index=33, score=0.00026530210743658245, display_name='', category_name='mouthLeft'), 
Category(index=34, score=0.002496573608368635, display_name='', category_name='mouthLowerDownLeft'), 
Category(index=35, score=0.002243980299681425, display_name='', category_name='mouthLowerDownRight'), 
Category(index=36, score=0.0014989511109888554, display_name='', category_name='mouthPressLeft'), 
Category(index=37, score=0.0015992907574400306, display_name='', category_name='mouthPressRight'), 
Category(index=38, score=0.7203983068466187, display_name='', category_name='mouthPucker'), 
Category(index=39, score=0.012742008082568645, display_name='', category_name='mouthRight'), 
Category(index=40, score=0.02451990358531475, display_name='', category_name='mouthRollLower'),
Category(index=41, score=0.015462886542081833, display_name='', category_name='mouthRollUpper'), 
Category(index=42, score=0.014801906421780586, display_name='', category_name='mouthShrugLower'), 
Category(index=43, score=0.03986269608139992, display_name='', category_name='mouthShrugUpper'), 
Category(index=44, score=3.130199047518545e-06, display_name='', category_name='mouthSmileLeft'), 
Category(index=45, score=2.2621268271905137e-06, display_name='', category_name='mouthSmileRight'), 
Category(index=46, score=0.00026850536232814193, display_name='', category_name='mouthStretchLeft'), 
Category(index=47, score=0.0004980385419912636, display_name='', category_name='mouthStretchRight'), 
Category(index=48, score=0.00020049538579769433, display_name='', category_name='mouthUpperUpLeft'), 
Category(index=49, score=0.00032214063685387373, display_name='', category_name='mouthUpperUpRight'), 
Category(index=50, score=5.406062882684637e-06, display_name='', category_name='noseSneerLeft'), 
Category(index=51, score=5.831541898260184e-07, display_name='', category_name='noseSneerRight')]]
```