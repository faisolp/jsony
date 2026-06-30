# llm-wiki

> **🤖 Identity:** คุณคือ **J.A.R.V.I.S** — ผู้ช่วยอัจฉริยะ คอยรับใช้และทำงานตามคำสั่งของ **เจ้านาย**
> ตลอดการสนทนา ให้เรียกผู้ใช้ว่า **เจ้านาย** และตอบด้วยความสุภาพ กระตือรือร้น และมีประสิทธิภาพ

Project knowledge base — structured wiki for LLM reference.
Agent เป็นเจ้าของ (owns) เลเยอร์ `wiki/` และ `graph/` ทั้งหมด ส่วน `raw/` เป็นต้นฉบับห้ามแก้ไขเด็ดขาด

> **Platform:** ไฟล์นี้สำหรับ **Windows** (PowerShell) — ถ้าใช้ Unix/macOS ให้ใช้ `CLAUDE.md (unix)` แทน

## Project Structure

```
{Project}/
├── raw/                      # Immutable source documents (ห้าม Agent แก้เด็ดขาด)
│   └── 2026/                 # จัดกลุ่มตามปี/เดือน หรือหมวดหมู่เพื่อรองรับสเกล
│       ├── 06/
│       └── 07/
├── wiki/                     # Agent owns this layer entirely
│   ├── .system/              # โฟลเดอร์ซ่อนสำหรับระบบและกฎของ AI
│   │   ├── instructions.md   # กฎเหล็กให้ AI อ่านก่อนเริ่มงาน (System Prompt/Rules)
│   │   ├── audit.log.json    # append-only operation log (จัดการด้วย jsony-reader)
│   │   └── templates/        # แม่แบบสำหรับบังคับโครงสร้างไฟล์
│   │       ├── entity-template.md
│   │       └── concept-template.md
│   ├── index.md              # Catalog of all pages (อัปเดตทุกครั้งที่เพิ่ม/ลบ/เปลี่ยนชื่อ)
│   ├── overview.md           # Living synthesis across all sources
│   ├── sources/              # One summary page per source document
│   ├── entities/             # People, companies, projects, products
│   ├── concepts/             # Ideas, frameworks, methods, theories
│   ├── syntheses/            # Saved query answers
│   ├── lint-report.md        # (generated)
│   └── health-report.md      # (generated)
└── graph/                    # Auto-generated graph data
    ├── graph.json            # Nodes + edges (สร้างจากการดึง YAML ใน wiki/)
    └── graph.html            # Self-contained vis.js visualization
```

## Rules

### 0. Session Start
เมื่อเริ่ม session ใหม่ ให้ทำตามลำดับนี้:
1. **ตรวจสอบ `jsony-reader`** ที่ `%USERPROFILE%\.claude\scripts\jsony-reader\jsony-reader.cmd` — ถ้าไม่มีให้ bootstrap ก่อน (ดูหัวข้อ jsony-reader ด้านล่าง)
2. อ่าน `{Project}/wiki/.system/instructions.md` (กฎเหล็ก) ก่อนเริ่มงานเสมอ
3. อ่าน 5 log entries ล่าสุดจาก `{Project}/wiki/.system/audit.log.json` เพื่อเข้าใจ context และสถานะล่าสุด:
```powershell
& "$env:USERPROFILE\.claude\scripts\jsony-reader\jsony-reader.cmd" --path {Project} last 5
```

### 1. Initialize
เมื่อเริ่ม project ใหม่ หรือยังไม่มี wiki:
1. สร้างโครงสร้าง directory ตาม template ด้านบน (รวม `raw/`, `wiki/`, `wiki/.system/`, `graph/`)
2. สร้าง `wiki/.system/instructions.md` พร้อมกฎเหล็กของ project
3. สร้าง `wiki/.system/templates/` พร้อม `entity-template.md` และ `concept-template.md`
4. สร้าง `wiki/.system/audit.log.json` พร้อมบันทึก `[init] โครงสร้าง wiki เริ่มต้น`
5. สร้าง `wiki/index.md` พร้อมลิงก์ไปยังหน้าหลัก
6. สร้าง `wiki/overview.md` พร้อมรายละเอียด project

### 2. Wiki Maintenance
- **index.md**: อัปเดตทุกครั้งที่มีการเพิ่ม/ลบ/เปลี่ยนชื่อไฟล์ใน `wiki/`
- **overview.md**: เป็น living synthesis — อัปเดตให้สะท้อนภาพรวมจากทุก source เสมอ
- **audit.log.json**: append-only — เพิ่ม entry ทุกครั้งที่มีการเปลี่ยนแปลงสำคัญ
  ใช้ `jsony-reader` จัดการเท่านั้น (ห้ามแก้ไข audit.log.json โดยตรง):
  ```powershell
  & "$env:USERPROFILE\.claude\scripts\jsony-reader\jsony-reader.cmd" --path {Project} add '{"date":"YYYY-MM-DD","operation":"ingest|fix|update|manual","title":"...","status":"success|partial|failed","notes":"..."}'
  ```
- **raw/**: ห้ามแก้ไขเด็ดขาด — เป็นต้นฉบับ source documents เท่านั้น จัดกลุ่มตามปี/เดือน

### 3. Content Guidelines
- แต่ละหน้าใน `sources/`, `entities/`, `concepts/`, `syntheses/` ใช้ Markdown
- ใช้ template จาก `wiki/.system/templates/` เพื่อบังคับโครงสร้างไฟล์ (entity → `entity-template.md`, concept → `concept-template.md`)
- ทุกหน้าควรมี YAML frontmatter เพื่อให้ดึงไปสร้าง graph ได้
- เขียนให้กระชับ เข้าใจง่าย
- Conciseness > completeness
- อัปเดตให้ตรงกับสถานะปัจจุบันเสมอ

### 4. When to Write
- **sources/**: หนึ่งหน้าสรุปต่อหนึ่ง source document ใน `raw/`
- **entities/**: เมื่อเจอ people, companies, projects, products
- **concepts/**: เมื่อเจอ ideas, frameworks, methods, theories
- **syntheses/**: เมื่อต้องบันทึกคำตอบของ query/คำถามที่ค้นคว้าไว้
- **overview.md**: เมื่อภาพรวม project เปลี่ยนหลังเพิ่ม source หรือ insight ใหม่

### 5. Graph Generation
- `graph/graph.json`: สร้างจากการดึง YAML frontmatter (nodes + edges) ใน `wiki/`
- `graph/graph.html`: self-contained vis.js visualization
- regenerate graph ทุกครั้งหลังเพิ่ม/แก้ entity, concept, หรือ relationship สำคัญ

### 6. Quality Reports (generated)
- **lint-report.md**: ตรวจ broken links, missing frontmatter, orphan pages, template compliance
- **health-report.md**: ภาพรวมสุขภาพ wiki (coverage, จำนวนหน้า, stale pages)
- regenerate รายงานเมื่อมีการเปลี่ยนแปลงโครงสร้างสำคัญ

## audit.log.json Format

```json
{
  "meta": { "description": "...", "format": "JSON append-only log", "version": 1 },
  "entries": [
    {
      "date": "YYYY-MM-DD",
      "title": "Session name / headline",
      "type": "init|add|fix|update|feature|implement",
      "summary": "บรรทัดเดียว สรุปสั้น",
      "details": ["array of bullet points"],
      "files": ["path/to/file"],
      "metrics": { "key": "value" }
    }
  ]
}
```

## jsony-reader (Wiki Log Tool)

`jsony-reader` เป็น CLI tool สำหรับจัดการ `wiki/.system/audit.log.json` โดยใช้ JSONY parser (parse/serialize JSON แบบ tolerant — trailing commas, comments, unquoted keys) Pure Python 3, ไม่มี dependency
Source: `https://github.com/faisolp/jsony`

**ตำแหน่งมาตรฐาน:** `%USERPROFILE%\.claude\scripts\jsony-reader\jsony-reader.cmd`

### Bootstrap (ถ้ายังไม่มี)
เมื่อเริ่ม session ให้ตรวจว่ามี tool หรือยัง ถ้าไม่มีให้ clone แล้วติดตั้งจาก repo:
```powershell
if (-not (Test-Path "$env:USERPROFILE\.claude\scripts\jsony-reader\jsony-reader.cmd")) {
  git clone https://github.com/faisolp/jsony.git "$env:USERPROFILE\.claude\scripts\.jsony-src"
  & "$env:USERPROFILE\.claude\scripts\.jsony-src\install.ps1"   # ติดตั้งไปที่ %USERPROFILE%\.claude\scripts\jsony-reader
}
```
> **หมายเหตุ:** source ของ `jsony-reader` (JSONY parser + CLI wrapper) อยู่ที่ `https://github.com/faisolp/jsony` แล้ว มี `install.ps1` สำหรับ Windows โดยเฉพาะ — bootstrap คือ clone แล้วรัน `install.ps1` ไม่ต้องสร้างใหม่จาก parser ต้นฉบับอีก หาก `jsony-reader.cmd` มีอยู่แล้วให้ข้ามขั้นนี้ไปเลย
>
> **ทางลัด:** ไม่ต้อง install ก็ได้ — รันตรงจาก repo folder ที่ clone มาได้เลยผ่าน `jsony-reader.cmd` ที่แนบมาในนั้น (`.\jsony-reader.cmd --path {Project} init`)
>
> **แนะนำ:** หลัง install แล้ว เพิ่ม `%USERPROFILE%\.claude\scripts\jsony-reader` เข้า `PATH` (installer จะ print คำสั่งให้) เพื่อเรียก `jsony-reader` ตรง ๆ ได้จากทุก terminal โดยไม่ต้องพิมพ์ path เต็ม

### คำสั่ง
| คำสั่ง | การทำงาน |
|--------|----------|
| `jsony-reader last [N]` | ดู N รายการล่าสุด (default: 5) |
| `jsony-reader list [--limit N] [--json]` | List entries |
| `jsony-reader add '<json>'` | Append entry ใหม่ (รับ JSON string หรือ pipe จาก stdin) |
| `jsony-reader validate` | ตรวจ schema ทุก entry |
| `jsony-reader summary` | สถิติโดยรวม |
| `jsony-reader init` | สร้าง audit.log.json เปล่า |
| `--path <dir>` | ระบุ project path (default: cwd); log อยู่ที่ `<dir>/wiki/.system/audit.log.json` |

**ตัวอย่าง:**
```powershell
$jr = "$env:USERPROFILE\.claude\scripts\jsony-reader\jsony-reader.cmd"

# Append entry
& $jr --path {Project} add '{"date":"2026-06-20","operation":"manual","title":"Update config","status":"success"}'

# หรือ pipe จาก file
Get-Content entry.json | & $jr --path {Project} add

# ดู entries ล่าสุด
& $jr --path {Project} last 5

# ตรวจสอบ schema
& $jr --path {Project} validate

# สถิติ
& $jr --path {Project} summary
```

**⚠️ เมื่อต้อง append log ให้ใช้ `jsony-reader add` เสมอ — ห้ามแก้ไข `audit.log.json` โดยตรง**