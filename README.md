# Phân tích 4 đề thi tuyển sinh lớp 10 môn Tiếng Anh TP.HCM

Thư mục này chứa dữ liệu và báo cáo phân tích 4 đề:

- 2023–2024 chính thức
- 2024–2025 chính thức (có đáp án ở cuối PDF)
- 2025–2026 chính thức
- 2026 chính thức

**GitHub Pages:** https://gowwre.github.io/engprep-analysis/

## Đọc báo cáo

- `index.html` — trang vào GitHub Pages, tự chuyển đến báo cáo.
- `BAO-CAO-PHAN-TICH.md` — bản Markdown đầy đủ.
- `bao-cao-phan-tich.html` — bản HTML có mục lục, biểu đồ và bảng; mở bằng trình duyệt.
- `figures/` — 6 biểu đồ dùng trong báo cáo.

## Dữ liệu

- `exam_items.csv` — 160 item đã mã hoá (40 câu × 4 đề).
- `passages.csv` — thống kê 8 đoạn cloze/reading.
- `summary.json` — số liệu tổng hợp theo đề.
- `section_summary.csv`, `skill_summary.csv`, `grammar_summary.csv`, `answer_summary.csv` — các bảng tổng hợp nhanh.

Các cột chính trong `exam_items.csv`:

| Cột | Ý nghĩa |
|---|---|
| `exam_id` | 2023, 2024, 2025, 2026 |
| `item` | Số câu 1–40 |
| `section` | Phần I–VII |
| `format` | MCQ, True/False, Gap-fill, Rewrite, Rearrange… |
| `skill_group` | Nhóm kỹ năng |
| `subskill` | Tiểu kỹ năng |
| `grammar_topic` | Chủ điểm ngữ pháp (nếu có) |
| `cognitive` | Nhận biết / Vận dụng / Suy luận / Sản sinh |
| `answer` | Đáp án |
| `key_status` | `official` hoặc `inferred` |
| `confidence` | Độ tin cậy của đáp án tự giải |

## Tạo lại

```bash
cd /home/radriar/Documents/EngPrep
python3 analysis/build_dataset.py
python3 analysis/make_charts.py
cd analysis
pandoc BAO-CAO-PHAN-TICH.md \
  --standalone \
  --template=report-template.html \
  --css=report.css \
  --toc --toc-depth=2 \
  --lua-filter=strip-title.lua \
  --metadata title="Đề thi tuyển sinh lớp 10 môn Tiếng Anh TP.HCM" \
  --metadata subtitle="Phân tích dữ liệu 4 đề: 2023 – 2026" \
  --metadata pagetitle="Phân tích 4 đề thi tuyển sinh 10 môn Tiếng Anh TP.HCM" \
  --metadata lang=vi \
  -o bao-cao-phan-tich.html
```

## Lưu ý

- Chỉ đề 2024–2025 có đáp án chính thức. Các đáp án còn lại là gợi ý, được đánh dấu `inferred` trong CSV.
- Đề 2026 là **đề chính thức**; đề tham khảo 2026 gần như trùng với đề chính thức nên không được tính riêng trong thống kê.
- Việc phân loại kỹ năng/mức nhận thức là một cách mã hoá chủ quan; nên dùng để so sánh tương đối.
- Các PDF gốc không được đưa vào repo; dữ liệu đã mã hoá nằm trong `exam_items.csv` và `passages.csv`.
