#!/usr/bin/env python3
"""Build an item-level dataset for the four HCMC Grade-10 English papers.

Outputs:
  analysis/exam_items.csv
  analysis/summary.json
  analysis/passages.csv
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE

EXAMS = [
    {
        "id": "2023",
        "label": "2023–2024 chính thức",
        "short": "2023",
        "file": "TS-10-TA-TPHCM-2023-2024-1.pdf",
        "official": True,
        "key_status": "inferred",
    },
    {
        "id": "2024",
        "label": "2024–2025 chính thức",
        "short": "2024",
        "file": "de-tieng-anh-2776.pdf",
        "official": True,
        "key_status": "official",
    },
    {
        "id": "2025",
        "label": "2025–2026 chính thức",
        "short": "2025",
        "file": "de-thi-ts10-nam-hoc-2025-2026-mon-tieng-anh-72283.pdf",
        "official": True,
        "key_status": "inferred",
    },
    {
        "id": "2026R",
        "label": "2026 đề tham khảo",
        "short": "2026R",
        "file": "english-thanh-nien-3232.pdf",
        "official": False,
        "key_status": "inferred",
    },
]

# item, section, format, skill_group, subskill, grammar_topic, cognitive, answer, confidence, note
ITEMS = {
    "2023": [
        (1, "I", "MCQ", "Pronunciation", "-ed ending", "", "Recognition", "B", "High", "consisted /ɪd/; còn lại /t/ hoặc /d/"),
        (2, "I", "MCQ", "Pronunciation", "vowel <i>", "", "Recognition", "B", "High", "lighting /aɪ/; còn lại /ɪ/"),
        (3, "I", "MCQ", "Stress", "2-syllable stress", "", "Recognition", "D", "High", "eager nhấn âm 1; còn lại âm 2"),
        (4, "I", "MCQ", "Stress", "3-syllable stress", "", "Recognition", "B", "High", "responses nhấn âm 2; còn lại âm 1"),
        (5, "I", "MCQ", "Grammar", "conjunction", "connector", "Application", "B", "High", "both ... and"),
        (6, "I", "MCQ", "Grammar", "preposition of time", "preposition", "Application", "C", "High", "on + ngày"),
        (7, "I", "MCQ", "Vocabulary", "natural disaster", "", "Recognition", "B", "High", "disaster"),
        (8, "I", "MCQ", "Grammar", "preposition", "preposition", "Application", "C", "High", "between"),
        (9, "I", "MCQ", "Grammar", "relative pronoun", "relative clause", "Application", "A", "High", "who cho người"),
        (10, "I", "MCQ", "Grammar", "verb pattern", "verb pattern", "Application", "A", "High", "encourage sb to do"),
        (11, "I", "MCQ", "Grammar", "present continuous", "tense/verb form", "Application", "D", "High", "is getting on"),
        (12, "I", "MCQ", "Vocabulary", "abstract noun", "", "Recognition", "C", "High", "inspiration"),
        (13, "I", "MCQ", "Communication", "encouraging", "", "Inference", "A", "Medium", "Good luck in the exam!"),
        (14, "I", "MCQ", "Communication", "responding to apology", "", "Inference", "D", "High", "That's OK. We've just started."),
        (15, "II", "MCQ", "Sign/Notice", "water safety notice", "", "Inference", "D", "Medium", "Don't leave the tap on"),
        (16, "II", "MCQ", "Sign/Notice", "contest notice", "", "Inference", "D", "High", "300-word limit"),
        (17, "III", "MCQ", "Cloze", "phrasal verb", "", "Application", "A", "High", "found out"),
        (18, "III", "MCQ", "Cloze", "conjunction", "connector", "Application", "B", "High", "because"),
        (19, "III", "MCQ", "Cloze", "noun", "", "Application", "A", "High", "temperature"),
        (20, "III", "MCQ", "Cloze", "superlative", "comparison", "Application", "C", "High", "highest"),
        (21, "III", "MCQ", "Cloze", "to-infinitive", "tense/verb form", "Application", "D", "High", "something ... to know"),
        (22, "III", "MCQ", "Cloze", "intensifier", "comparison", "Application", "C", "High", "even higher"),
        (23, "IV", "True/False", "Reading", "T/F - literal", "", "Inference", "True", "High", "5 người: bố, mẹ, 2 chị, 1 cậu"),
        (24, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "False", "High", "về nhà sau bữa trưa"),
        (25, "IV", "True/False", "Reading", "T/F - inference", "", "Inference", "False", "High", "mẹ thường tự trang trí"),
        (26, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "True", "High", "cậu bé mua mũ"),
        (27, "IV", "MCQ", "Reading", "main idea", "", "Inference", "A", "High", "cách gia đình chuẩn bị"),
        (28, "IV", "MCQ", "Reading", "detail/inference", "", "Inference", "C", "High", "mẹ bận việc nhà"),
        (29, "V", "Gap-fill", "Word formation", "adjective", "", "Application", "beneficial", "High", "benefit → beneficial"),
        (30, "V", "Gap-fill", "Word formation", "noun (person)", "", "Application", "contestant", "High", "contest → contestant"),
        (31, "V", "Gap-fill", "Word formation", "adjective", "", "Application", "homeless", "High", "home → homeless"),
        (32, "V", "Gap-fill", "Word formation", "adverb", "", "Application", "Nearly", "High", "near → Nearly"),
        (33, "V", "Gap-fill", "Word formation", "noun", "", "Application", "conclusion", "High", "conclude → conclusion"),
        (34, "V", "Gap-fill", "Word formation", "verb (V-ing)", "", "Application", "surfing", "High", "surf → surfing"),
        (35, "VI", "Rearrange", "Sentence construction", "sentence ordering", "", "Production", "Nuclear power is not only expensive but also dangerous to our environment.", "High", ""),
        (36, "VI", "Rearrange", "Sentence construction", "sentence ordering", "", "Production", "The host band started off the concert by presenting a mashup of their hit songs.", "High", ""),
        (37, "VII", "Rewrite", "Sentence transformation", "conditional type 1", "", "Production", "If you change the way you learn vocabulary, you can improve your English.", "High", ""),
        (38, "VII", "Rewrite", "Sentence transformation", "reported speech / suggest", "", "Production", "Robert suggested that those empty bottles be collected for recycling.", "High", ""),
        (39, "VII", "Rewrite", "Sentence transformation", "result so ... that", "", "Production", "Tom is very lazy, so he can't get good marks at school.", "High", ""),
        (40, "VII", "Rewrite", "Sentence transformation", "gerund collocation", "", "Production", "Michael is fond of playing football after school.", "High", ""),
    ],
    "2024": [
        (1, "I", "MCQ", "Pronunciation", "-s ending", "", "Recognition", "C", "Official", "predicts /s/; còn lại /z/"),
        (2, "I", "MCQ", "Pronunciation", "vowel <a>", "", "Recognition", "B", "Official", "campus /æ/; còn lại /eɪ/ hoặc /ə/"),
        (3, "I", "MCQ", "Stress", "2-syllable stress", "", "Recognition", "B", "Official", "visit nhấn âm 1; còn lại âm 2"),
        (4, "I", "MCQ", "Stress", "3-syllable stress", "", "Recognition", "A", "Official", "official nhấn âm 2; còn lại âm 1"),
        (5, "I", "MCQ", "Grammar", "wish", "wish", "Application", "D", "Official", "I wish you could go"),
        (6, "I", "MCQ", "Grammar", "causative", "causative", "Application", "A", "Official", "have sb do"),
        (7, "I", "MCQ", "Grammar", "preposition", "preposition", "Application", "C", "Official", "interested in"),
        (8, "I", "MCQ", "Grammar", "tag question", "tag question", "Application", "D", "Official", "aren't we?"),
        (9, "I", "MCQ", "Grammar", "conjunction", "connector", "Application", "C", "Official", "because"),
        (10, "I", "MCQ", "Grammar", "verb pattern", "verb pattern", "Application", "B", "Official", "forget to do"),
        (11, "I", "MCQ", "Grammar", "present simple", "tense/verb form", "Application", "A", "Official", "has two days off"),
        (12, "I", "MCQ", "Vocabulary", "adjective", "", "Recognition", "A", "Official", "terrific"),
        (13, "I", "MCQ", "Communication", "accepting a suggestion", "", "Inference", "B", "Official", "That sounds great!"),
        (14, "I", "MCQ", "Communication", "giving permission", "", "Inference", "C", "Official", "Of course. You can."),
        (15, "II", "MCQ", "Sign/Notice", "toilet notice", "", "Inference", "C", "Medium", "không xả rác vào toilet"),
        (16, "II", "MCQ", "Sign/Notice", "booking notice", "", "Inference", "A", "High", "phải đặt trước"),
        (17, "III", "MCQ", "Cloze", "adjective", "", "Application", "B", "Official", "friendly"),
        (18, "III", "MCQ", "Cloze", "noun", "", "Application", "C", "Official", "beaches"),
        (19, "III", "MCQ", "Cloze", "relative pronoun", "relative clause", "Application", "D", "Official", "who"),
        (20, "III", "MCQ", "Cloze", "noun", "", "Application", "A", "Official", "festival"),
        (21, "III", "MCQ", "Cloze", "determiner", "determiner", "Application", "C", "Official", "another"),
        (22, "III", "MCQ", "Cloze", "preposition", "preposition", "Application", "D", "Official", "impression on"),
        (23, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "False", "Official", "cần thiết, không phải không cần"),
        (24, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "True", "Official", ""),
        (25, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "False", "Official", "năng lượng mặt trời dồi dào"),
        (26, "IV", "True/False", "Reading", "T/F - inference", "", "Inference", "True", "Official", ""),
        (27, "IV", "MCQ", "Reading", "reference", "", "Inference", "B", "Official", "them = electronics"),
        (28, "IV", "MCQ", "Reading", "main idea", "", "Inference", "C", "Official", "Let's save energy"),
        (29, "V", "Gap-fill", "Word formation", "noun", "", "Application", "preparation", "Official", "prepare → preparation"),
        (30, "V", "Gap-fill", "Word formation", "adjective", "", "Application", "experienced", "Official", "experience → experienced"),
        (31, "V", "Gap-fill", "Word formation", "verb", "", "Application", "beautify", "Official", "beauty → beautify"),
        (32, "V", "Gap-fill", "Word formation", "adjective", "", "Application", "effective", "Official", "effect → effective"),
        (33, "V", "Gap-fill", "Word formation", "noun", "", "Application", "assistance", "Official", "assist → assistance"),
        (34, "V", "Gap-fill", "Word formation", "adverb", "", "Application", "successfully", "Official", "succeed → successfully"),
        (35, "VI", "Rearrange", "Sentence construction", "sentence ordering", "", "Production", "Every one of us should follow the example set by Uncle Hồ, our beloved leader.", "Official", ""),
        (36, "VI", "Rearrange", "Sentence construction", "sentence ordering", "", "Production", "Studying abroad gives students opportunities to learn about different cultures.", "Official", ""),
        (37, "VII", "Rewrite", "Sentence transformation", "gerund collocation", "", "Production", "The children are keen on making models of animals in their free time.", "Official", ""),
        (38, "VII", "Rewrite", "Sentence transformation", "conditional type 2 / advice", "", "Production", "If I were you, I would go to the dentist twice a year.", "Official", ""),
        (39, "VII", "Rewrite", "Sentence transformation", "present perfect since", "", "Production", "It has been two years since she last participated in a competition.", "Official", ""),
        (40, "VII", "Rewrite", "Sentence transformation", "reason clause", "", "Production", "Because he performed well, he was nominated as Singer of the Year.", "Official", ""),
    ],
    "2025": [
        (1, "I", "MCQ", "Pronunciation", "-ed ending", "", "Recognition", "D", "High", "attacked /t/; còn lại /d/"),
        (2, "I", "MCQ", "Pronunciation", "vowel <a>", "", "Recognition", "C", "High", "lack /æ/; còn lại /eɪ/"),
        (3, "I", "MCQ", "Stress", "2-syllable stress", "", "Recognition", "A", "High", "answer nhấn âm 1; còn lại âm 2"),
        (4, "I", "MCQ", "Stress", "3-syllable stress", "", "Recognition", "B", "High", "tradition nhấn âm 2; còn lại âm 1"),
        (5, "I", "MCQ", "Vocabulary", "phrasal verb", "", "Recognition", "B", "High", "look them up"),
        (6, "I", "MCQ", "Grammar", "preposition of time", "preposition", "Application", "A", "High", "on + ngày"),
        (7, "I", "MCQ", "Grammar", "past simple", "tense/verb form", "Application", "C", "High", "went"),
        (8, "I", "MCQ", "Grammar", "verb choice", "verb pattern", "Application", "B", "High", "prefer"),
        (9, "I", "MCQ", "Grammar", "conjunction", "connector", "Application", "C", "High", "but"),
        (10, "I", "MCQ", "Grammar", "relative pronoun", "relative clause", "Application", "C", "High", "that"),
        (11, "I", "MCQ", "Vocabulary", "adjective", "", "Recognition", "D", "High", "excited"),
        (12, "I", "MCQ", "Grammar", "preposition", "preposition", "Application", "A", "High", "for a walk"),
        (13, "I", "MCQ", "Communication", "accepting a suggestion", "", "Inference", "A", "High", "Let's do it!"),
        (14, "I", "MCQ", "Communication", "asking about time", "", "Inference", "C", "High", "What time does the movie start?"),
        (15, "II", "MCQ", "Sign/Notice", "water safety sign", "", "Inference", "A", "Medium", "không được nhảy xuống nước"),
        (16, "II", "MCQ", "Sign/Notice", "canteen promotion", "", "Inference", "C", "High", "mua trà sữa, tặng cookie thứ Ba"),
        (17, "III", "MCQ", "Cloze", "preposition", "preposition", "Application", "B", "High", "as a hobby"),
        (18, "III", "MCQ", "Cloze", "verb", "", "Application", "C", "High", "joined"),
        (19, "III", "MCQ", "Cloze", "quantifier", "quantifier", "Application", "A", "High", "Some of the elderly"),
        (20, "III", "MCQ", "Cloze", "noun", "", "Application", "D", "High", "recipes"),
        (21, "III", "MCQ", "Cloze", "verb pattern", "verb pattern", "Application", "C", "High", "listening to"),
        (22, "III", "MCQ", "Cloze", "comparative", "comparison", "Application", "B", "High", "better"),
        (23, "IV", "True/False", "Reading", "T/F - literal", "", "Inference", "True", "High", ""),
        (24, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "False", "High", "thể thao giúp tập trung"),
        (25, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "False", "High", "thể thao giảm stress"),
        (26, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "True", "High", ""),
        (27, "IV", "MCQ", "Reading", "main idea", "", "Inference", "B", "High", "lợi ích thể thao"),
        (28, "IV", "MCQ", "Reading", "NOT mentioned", "", "Inference", "A", "High", "chế độ ăn cân bằng không có trong bài"),
        (29, "V", "Gap-fill", "Word formation", "noun", "", "Application", "attraction", "High", "attract → attraction"),
        (30, "V", "Gap-fill", "Word formation", "adjective", "", "Application", "pleasant", "High", "please → pleasant"),
        (31, "V", "Gap-fill", "Word formation", "verb (V-ing)", "", "Application", "preparing", "High", "prepare → preparing"),
        (32, "V", "Gap-fill", "Word formation", "adverb", "", "Application", "Amazingly", "High", "amaze → Amazingly"),
        (33, "V", "Gap-fill", "Word formation", "noun (plural)", "", "Application", "scientists", "High", "science → scientists"),
        (34, "V", "Gap-fill", "Word formation", "adjective", "", "Application", "damaging", "High", "damage → damaging"),
        (35, "VI", "Dictionary gap-fill", "Sentence construction", "dictionary use", "", "Production", "provide information", "Medium", "2 từ; theo entry 'provide'"),
        (36, "VI", "Dictionary gap-fill", "Sentence construction", "dictionary use", "", "Production", "provides an opportunity", "Medium", "3 từ; theo entry 'provide'"),
        (37, "VII", "Rewrite", "Sentence transformation", "phrasal verb", "", "Production", "Our car broke down on the way to the beach.", "High", ""),
        (38, "VII", "Rewrite", "Sentence transformation", "conditional type 1 / unless", "", "Production", "Unless he catches the first metro, he will be late for the conference.", "High", ""),
        (39, "VII", "Rewrite", "Sentence transformation", "present perfect since", "", "Production", "She hasn't written to her grandparents since last April.", "High", ""),
        (40, "VII", "Rewrite", "Sentence transformation", "result such ... that", "", "Production", "It was such awful weather that we couldn't go picnicking as planned.", "High", ""),
    ],
    "2026R": [
        (1, "I", "MCQ", "Pronunciation", "-ed ending", "", "Recognition", "B", "High", "frightened /d/; còn lại /ɪd/"),
        (2, "I", "MCQ", "Pronunciation", "vowel <e>", "", "Recognition", "A", "High", "chemist /k/; còn lại /s/"),
        (3, "I", "MCQ", "Stress", "2-syllable stress", "", "Recognition", "A", "High", "listen nhấn âm 1; còn lại âm 2"),
        (4, "I", "MCQ", "Stress", "3-syllable stress", "", "Recognition", "D", "High", "important nhấn âm 2; còn lại âm 1"),
        (5, "I", "MCQ", "Grammar", "preposition of place", "preposition", "Application", "A", "High", "in the fridge"),
        (6, "I", "MCQ", "Grammar", "conjunction", "connector", "Application", "D", "High", "or"),
        (7, "I", "MCQ", "Grammar", "past simple", "tense/verb form", "Application", "C", "High", "went"),
        (8, "I", "MCQ", "Vocabulary", "collocation", "", "Recognition", "A", "High", "traffic jams"),
        (9, "I", "MCQ", "Vocabulary", "adjective", "", "Recognition", "C", "High", "honest"),
        (10, "I", "MCQ", "Grammar", "relative pronoun", "relative clause", "Application", "C", "High", "that"),
        (11, "I", "MCQ", "Vocabulary", "noun", "", "Recognition", "B", "High", "subtitles"),
        (12, "I", "MCQ", "Vocabulary", "adjective", "", "Recognition", "A", "High", "convenient"),
        (13, "I", "MCQ", "Communication", "asking about health", "", "Inference", "B", "High", "What's the matter with you?"),
        (14, "I", "MCQ", "Communication", "declining an offer", "", "Inference", "D", "High", "No, thanks"),
        (15, "II", "MCQ", "Sign/Notice", "e-cigarette ban", "", "Inference", "C", "High", "E-cigarettes are not allowed"),
        (16, "II", "MCQ", "Sign/Notice", "sale notice", "", "Inference", "C", "High", "half price for two weeks = 14 days"),
        (17, "III", "MCQ", "Cloze", "to-infinitive", "tense/verb form", "Application", "C", "High", "make sb appear"),
        (18, "III", "MCQ", "Cloze", "comparative", "comparison", "Application", "D", "High", "easier to spread"),
        (19, "III", "MCQ", "Cloze", "conjunction", "connector", "Application", "A", "High", "When"),
        (20, "III", "MCQ", "Cloze", "noun", "", "Application", "C", "Medium", "damage a person's fame/reputation"),
        (21, "III", "MCQ", "Cloze", "preposition", "preposition", "Application", "C", "High", "effect on"),
        (22, "III", "MCQ", "Cloze", "adverb / linker", "", "Application", "D", "Medium", "loại trừ; các phương án còn lại sai nghĩa"),
        (23, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "True", "High", "pitons là dụng cụ leo núi"),
        (24, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "False", "High", "xuất phát gần đỉnh"),
        (25, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "True", "High", "xuống, lên, ngang sườn núi"),
        (26, "IV", "True/False", "Reading", "T/F - detail", "", "Inference", "True", "High", "đỉnh lúc 3 giờ chiều"),
        (27, "IV", "MCQ", "Reading", "best title", "", "Inference", "D", "High", "Cliff Trail – The Hike of A Lifetime"),
        (28, "IV", "MCQ", "Reading", "feeling/inference", "", "Inference", "A", "High", "fear and excitement"),
        (29, "V", "Gap-fill", "Word formation", "adjective", "", "Application", "global", "High", "globe → global"),
        (30, "V", "Gap-fill", "Word formation", "verb (V-ing)", "", "Application", "entertaining", "High", "entertain → entertaining"),
        (31, "V", "Gap-fill", "Word formation", "adjective", "", "Application", "patient", "High", "patience → patient"),
        (32, "V", "Gap-fill", "Word formation", "noun", "", "Application", "exhibition", "High", "exhibit → exhibition"),
        (33, "V", "Gap-fill", "Word formation", "adverb", "", "Application", "illegally", "High", "legal → illegally"),
        (34, "V", "Gap-fill", "Word formation", "noun (plural)", "", "Application", "explorers", "High", "explore → explorers"),
        (35, "VI", "Phrase bank", "Sentence construction", "lexical chunk", "", "Production", "break the habit", "High", "cụm cố định"),
        (36, "VI", "Phrase bank", "Sentence construction", "lexical chunk", "", "Production", "eating habits", "High", "cụm cố định"),
        (37, "VII", "Rewrite", "Sentence transformation", "wish", "", "Production", "Brenda wishes she had her own locker at school.", "High", ""),
        (38, "VII", "Rewrite", "Sentence transformation", "mind + V-ing", "", "Production", "Lucie doesn't mind helping her friends with exercises after class.", "High", ""),
        (39, "VII", "Rewrite", "Sentence transformation", "phrasal verb", "", "Production", "The shop has run out of roses.", "High", ""),
        (40, "VII", "Rewrite", "Sentence transformation", "contrast although/despite", "", "Production", "Although the project was practical, nobody wanted to carry it out.", "High", ""),
    ],
}

SECTION_META = {
    "I": ("Trắc nghiệm ngữ âm, ngữ pháp, từ vựng, giao tiếp", 14, 3.5),
    "II": ("Biển báo / thông báo", 2, 0.5),
    "III": ("Cloze test (6 chỗ trống)", 6, 1.5),
    "IV": ("Đọc hiểu (4 T/F + 2 MCQ)", 6, 1.5),
    "V": ("Word formation (6 câu)", 6, 1.5),
    "VI": ("Sắp xếp câu / từ điển / cụm từ", 2, 0.5),
    "VII": ("Viết lại câu (4 câu)", 4, 1.0),
}

PASSAGES = {
    "2023": {
        "cloze": "Good evening. Welcome to our Fun Science Program. This week we have received a lot of questions about life on the moon. We have talked to some experts and these are what we have found out. There is no water or air on the moon. It is all silent because there is no air. Of course there will be no music, no sounds. There are no rivers and no lakes. At night it is very cold. The temperature goes down to 151 C below zero. But during the day it rises to 100 C above zero. There are great round holes on the moon. They are called craters. There are more than 30,000 of them. There are also high mountains. The highest mountains on the moon are about 26,000 feet or 8,000 meters. And here is something very interesting for you to know on the moon you weigh one sixth of what you weigh on the earth. If you weigh 50 kilos, on the moon you will weigh only a little more than 8 kilos. You will be able to jump very high, even higher than any high jump Olympic champions. You can take very long steps as well. And. Maybe you won't sleep very well because one day on the moon lasts two weeks. So, is there life on the moon? I'll leave the question for you to answer yourselves in the group discussion.",
        "reading": "Of all the holidays, I think the best is Mother's Day. It is very special to a rather big family like mine. I realize how much Mother has done for years, and all the wonderful things she has done for her children. So this year Father, my two sisters and I, the only boy in the family, decided to make Mother's Day a special occasion for our Mother. Father took a holiday from his office; my sisters and I came home from school after lunch. We planned to make it a day just like Christmas. We decorated the house with colorful flowers, candles and a small greeting over the fireplace. Mother usually did so at Christmas by herself. My sisters dressed themselves in their best. Father wore the new tie that Mother had bought for him on his birthday. I was so excited with the idea that I was the person who bought Mother a new silk hat from the money Father had secretly given to me before. We wanted to give Mother a big surprise. We hired a motor car which would take us all for a beautiful drive into the country nearby. Mother rarely had a treat like that. She is busy cooking and cleaning almost all the time. And of course, the country would be so lovely, the driving over miles of greenery in the country would be specially exciting to Mother. Mother deserved them all.",
        "cloze_topic": "Life on the moon (science)",
        "reading_topic": "Mother's Day (family/culture)",
    },
    "2024": {
        "cloze": "Da Nang, a famous holiday destination in the center of Vietnam, ranks as one of the best cities that are worth a visit. Beautiful natural landscapes and friendly local people are contributing factors to this city's recognition. With the blue sea, sandy beaches, and spectacular mountains, Da Nang captivates not only domestic but also foreign tourists who want to enjoy magnificent scenery. Visiting My Khe Beach and Ba Na Hills, which features the Golden Bridge, is considered a must when you are in Da Nang. In addition, attending Da Nang's International Fireworks festival is a memorable experience. With its annual splendid performances, this event is an unforgettable celebration. The locals' hospitality is another factor that makes a deep impression on visitors.",
        "reading": "Conserving energy is really important for the environment as well as for your wallets. Doing simple things like turning off lights when you leave a room, unplugging electronics when you are not using them, and using energy-saving devices can help a great deal. You can also use renewable energy sources like solar or wind power to save more energy. Now scientists can convert sunlight directly into electricity, and this energy from the sun offers a clean and a abundant source of power that can be harnessed almost anywhere on Earth. Wind farms, both onshore and offshore, have become a familiar sight in many regions, providing a reliable source of renewable power that can help reduce human dependence on fossil fuels and lessen the negative impacts of climate change. When you save energy, you are not just helping the planet, and you are also saving money on your electricity bill. Even small changes in your daily habits can makes a big difference over time, which is good for both the Earth and your bank account. Remember, every little bit helps, so let us all do our part to conserve energy and make the world a better place for our future generations.",
        "cloze_topic": "Da Nang tourism (places/travel)",
        "reading_topic": "Energy conservation (environment)",
    },
    "2025": {
        "cloze": "Dear Mai, I hope this letter finds you well. Thanks to your lovely letter, which advised me to do something as a hobby but still beneficial for the community, I'm delighted to let you know that I have joined the school cooking club. Now I cook meals for old people in our neighborhood every Friday. We usually make simple dishes such as rice, soup, fish, and vegetables. We also come to the homes of those who find it difficult to go out and about and give them the fresh food. Some of the elderly who live alone feel very happy to see us. I love their smiles when they receive the meals. They often share their favorite recipes, which helps us enrich our offered menu. Sometimes, we even sing songs together to create a joyful atmosphere. I enjoy talking with them and listening to their stories. Interestingly, they are willing to tell us about their families and how optimistic they are about their grandchildren's future. It's always great to help others and learn kindness. I know you are doing the same thing at your school too. Let's both try to make our community better! Love, Lan",
        "reading": "Today, many teenagers are attracted to screen-based activities such as online games, social media or web surfing. But if they haven't tried playing a sport yet, now is the perfect time to give it a try! Playing sports offers numerous benefits for teenagers, both physically and mentally. It helps them stay healthy by keeping their bodies active. Physical activities make teens' hearts stronger and give them more energy. Sports help the brain work better, so teens can focus more easily in class. Through sports, teens develop teamwork and sportsmanship. Team sports teach them that the team's success depends on how well the players work together. They learn to prioritise the team's interests over individual performance. These ways of thinking aren't just good for school - they're useful in everyday life too. Moreover, sports help teens manage time effectively so that they can become more organized and responsible. On top of that, playing sports is a great way to reduce stress. Spending time with friends through games also makes teens more relaxed and socially connected. To conclude, playing sports helps teenagers be physically fitter, think more positively, and build better relationships. Therefore, teenagers should take up a sport they enjoy.",
        "cloze_topic": "School cooking club for the elderly (community)",
        "reading_topic": "Teenagers and sports (health/lifestyle)",
    },
    "2026R": {
        "cloze": "Deepfake technology has challenged the relationship between seeing and believing. A deepfake is a digitally changed image, video or audio recording that makes a person appear to say or do something they never actually said or did. Although image controlling is not new, recent advantages in artificial intelligence have made the deepfake more realistic, cheaper to produce, and easier to spread. As a result, deepfakes have come into entertainment, business and personal life. When a deepfake is released, it continues to influence public opinion. A convincing fake video at a sensitive moment could damage a person's fame, affect opinions, or create panic before the truth is proved. Misinformation has a bad effect on the public even after it is corrected. Dangerously, deepfakes even make the public disbelieve and doubt all real information. Therefore, everyone should treat information with caution.",
        "reading": "I do a lot of mountain hiking, not climbing, so you know I'm talking about using feet, not ropes or pitons, to get me wherever I want, but my first law of relaxation is never to do a sport where a mistake can mean death. I recently discovered the hike of a lifetime: Cliff Trail on Vermont's highest peak, the 4,393-foot (1,338-meter) Mount Mansfield. There are many ways to climb the Mansfield, but Cliff Trail starts near the top, so I took a van there. I was hiking with a local guide. When we reached our destination, we hiked down a short path to Cliff Trail. For the rest of the morning, instead of going ever upwards, we climbed down wooden ladders, passed up rock faces, and crossed the side of the mountain. Besides mostly using feet, we used hands to hold onto roots, arms to pull us over steep rocks, and shoulders to get through narrow passages. Occasionally, my guide pushed and pulled me through the difficult spots. I was both scared and excited. We started at 10 a.m., reached the summit around 3 p.m., and stopped there for a long slow look at Vermont. The view was marvellous.",
        "cloze_topic": "Deepfake / AI (technology)",
        "reading_topic": "Mountain hiking on Cliff Trail (travel/outdoors)",
    },
}


def syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    groups = re.findall(r"[aeiouy]{1,2}", w)
    return max(1, len(groups))


def text_stats(text: str) -> dict:
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", text)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
    n_w, n_s = len(words), max(1, len(sentences))
    n_syl = sum(syllables(w) for w in words)
    ttr = len({w.lower() for w in words}) / n_w if n_w else 0
    fre = 206.835 - 1.015 * (n_w / n_s) - 84.6 * (n_syl / n_w)
    fkgl = 0.39 * (n_w / n_s) + 11.8 * (n_syl / n_w) - 15.59
    return {
        "words": n_w,
        "sentences": n_s,
        "avg_sentence_length": round(n_w / n_s, 1),
        "type_token_ratio": round(ttr, 3),
        "flesch_reading_ease": round(fre, 1),
        "flesch_kincaid_grade": round(fkgl, 1),
        "syllables_per_word": round(n_syl / n_w, 2) if n_w else 0,
    }


def main() -> None:
    rows = []
    for exam in EXAMS:
        for rec in ITEMS[exam["id"]]:
            item, section, fmt, skill, sub, grammar, cog, answer, conf, note = rec
            rows.append(
                {
                    "exam_id": exam["id"],
                    "exam_label": exam["label"],
                    "official": exam["official"],
                    "item": item,
                    "section": section,
                    "format": fmt,
                    "skill_group": skill,
                    "subskill": sub,
                    "grammar_topic": grammar,
                    "cognitive": cog,
                    "answer": answer,
                    "key_status": exam["key_status"],
                    "confidence": conf,
                    "points": 0.25,
                    "note": note,
                }
            )

    fieldnames = list(rows[0].keys())
    with (OUT / "exam_items.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Aggregations
    summary = {"exams": {}, "overall": {}}
    for exam in EXAMS:
        eid = exam["id"]
        erows = [r for r in rows if r["exam_id"] == eid]
        summary["exams"][eid] = {
            "label": exam["label"],
            "official": exam["official"],
            "items": len(erows),
            "sections": {
                s: {
                    "items": sum(1 for r in erows if r["section"] == s),
                    "points": round(sum(r["points"] for r in erows if r["section"] == s), 2),
                }
                for s in SECTION_META
            },
            "skills": dict(Counter(r["skill_group"] for r in erows)),
            "cognitive": dict(Counter(r["cognitive"] for r in erows)),
            "grammar_topics": dict(
                Counter(r["grammar_topic"] for r in erows if r["grammar_topic"])
            ),
            "mcq_answers": dict(
                Counter(
                    r["answer"]
                    for r in erows
                    if r["format"] == "MCQ" and r["answer"] in "ABCD"
                )
            ),
            "tf_answers": dict(
                Counter(r["answer"] for r in erows if r["format"] == "True/False")
            ),
        }

    summary["overall"] = {
        "items": len(rows),
        "skills": dict(Counter(r["skill_group"] for r in rows)),
        "cognitive": dict(Counter(r["cognitive"] for r in rows)),
        "sections": {
            s: {
                "items": sum(1 for r in rows if r["section"] == s),
                "points_per_paper": SECTION_META[s][2],
            }
            for s in SECTION_META
        },
        "mcq_answers": dict(
            Counter(r["answer"] for r in rows if r["format"] == "MCQ" and r["answer"] in "ABCD")
        ),
        "tf_answers": dict(Counter(r["answer"] for r in rows if r["format"] == "True/False")),
    }

    with (OUT / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Passage statistics
    pass_rows = []
    for eid, p in PASSAGES.items():
        for kind in ("cloze", "reading"):
            stats = text_stats(p[kind])
            pass_rows.append(
                {
                    "exam_id": eid,
                    "kind": kind,
                    "topic": p[f"{kind}_topic"],
                    **stats,
                }
            )
    with (OUT / "passages.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(pass_rows[0].keys()))
        writer.writeheader()
        writer.writerows(pass_rows)

    # Compact summary tables for reuse
    with (OUT / "section_summary.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["section", "items_per_paper", "points_per_paper", "percent"])
        for s, (_, n, pts) in SECTION_META.items():
            w.writerow([s, n, pts, f"{pts / 10:.0%}"])

    with (OUT / "skill_summary.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["skill_group", "items", "percent"])
        for skill, n in sorted(summary["overall"]["skills"].items(), key=lambda x: -x[1]):
            w.writerow([skill, n, f"{n / 160:.1%}"])

    with (OUT / "grammar_summary.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        exam_ids = [e["id"] for e in EXAMS]
        w.writerow(["grammar_topic", *exam_ids, "total"])
        for topic in sorted(
            {t for e in EXAMS for t in summary["exams"][e["id"]]["grammar_topics"]},
            key=lambda t: -sum(summary["exams"][e["id"]]["grammar_topics"].get(t, 0) for e in EXAMS),
        ):
            vals = [summary["exams"][e["id"]]["grammar_topics"].get(topic, 0) for e in EXAMS]
            w.writerow([topic, *vals, sum(vals)])

    with (OUT / "answer_summary.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["exam_id", "A", "B", "C", "D", "True", "False"])
        for e in EXAMS:
            eid = e["id"]
            mcq = summary["exams"][eid]["mcq_answers"]
            tf = summary["exams"][eid]["tf_answers"]
            w.writerow([eid, *(mcq.get(k, 0) for k in "ABCD"), tf.get("True", 0), tf.get("False", 0)])

    print(f"Wrote {len(rows)} items -> {OUT / 'exam_items.csv'}")
    print(f"Wrote {len(pass_rows)} passages -> {OUT / 'passages.csv'}")
    print(json.dumps(summary["overall"], ensure_ascii=False, indent=2))
    print("\nPassage stats:")
    for r in pass_rows:
        print(
            f"{r['exam_id']:>5} {r['kind']:<7} {r['words']:>3}w "
            f"{r['sentences']:>2}s avg={r['avg_sentence_length']:>4} "
            f"TTR={r['type_token_ratio']:.2f} FRE={r['flesch_reading_ease']:>5} "
            f"FKGL={r['flesch_kincaid_grade']:>4} | {r['topic']}"
        )


if __name__ == "__main__":
    main()
