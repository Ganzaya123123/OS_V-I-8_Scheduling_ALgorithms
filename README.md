# V-1-8 – CPU төлөвлөлтийн алгоритмууд (Scheduling Algorithms)

**Хичээл:** F.CSM302 Үйлдлийн систем, Бие даалт 1 (БД1)
**Хуваарилалтын код:** V-1-8 (V өдөр, 1-р цаг, 8-р сэдэв)
**Сурах бичиг:** Operating System Concepts (2018), 5-р бүлэг "CPU Scheduling", Programming Project

**Багийн гишүүд:** B210910822, B231910041, B241910005, B241910028, B241940016, B242270137
(нэр, хариуцсан ажлыг `docs/team.json` болон тайлангийн Хавсралт A-д бичсэн)

![Gantt Chart](docs/screenshots/ui_priority.png)

## Зорилго
FCFS, SJF, Priority, Round Robin, Priority + Round Robin гэсэн таван CPU төлөвлөлтийн алгоритмыг хэрэгжүүлж,
процессын ирэх цаг, CPU ээлж, эрэмбэ, квантыг өөрчилж дахин туршиж болох болгосон. Үр дүнг **D3.js Gantt Chart**-аар
харуулж, процесс бүрийн хүлээлтийн хугацаа (waiting), эргэлтийн хугацаа (turnaround), response time-ийг тооцно.

## Quick Start
Шаардлага: **Python 3.9 эсвэл түүнээс дээш**. Нэмэлт сан суулгах шаардлагагүй, интернет хэрэггүй.

```bash
git clone https://github.com/Ganzaya123123/OS_V-I-8_Scheduling_ALgorithms.git
cd OS_V-I-8_Scheduling_ALgorithms
python3 src/server.py            # 8000 порт завгүй бол: --port 8080
```
Хөтөч дээр **http://127.0.0.1:8000** хаягийг нээж, "Жишээ" жагсаалтаас сонгоод **Төлөвлөлт ажиллуулах** товчийг дарна.
Зогсоох: `Ctrl+C`. (Windows дээр `python3` олдохгүй бол `python` эсвэл `py` гэж бичнэ.)

### Командын мөр (номын форматтай)
Даалгаврын файлын мөр бүр: `[даалгаврын нэр], [эрэмбэ], [CPU ээлж]`, жишээ нь `T1, 4, 20`.
```bash
python3 src/cli.py examples/textbook_tasks.txt PRIORITY
python3 src/cli.py examples/textbook_tasks.txt RR --quantum 10
python3 src/cli.py examples/textbook_tasks.txt PRIORITY_RR --priority-order low
```
Алгоритм: `FCFS`, `SJF`, `PRIORITY`, `RR`, `PRIORITY_RR`.
Буруу файл өгвөл мөр бүрийн алдааг Монгол хэлээр хэвлэж, гарах код 1 байна (`examples/bad_tasks.txt`-ээр турших).

## Тест
```bash
python3 -m unittest discover -s tests -v     # Ran 28 tests ... OK
```
Номын болон лекцийн жишээ (FCFS 17, SJF 7, RR 5.67, Priority 8.2), номын T1..T5 даалгавар, сул (idle) завсар, ирэлтээр
тасалдуулах, захын болон буруу оролтын тестүүд орсон.

## Бүтэц
| Зам | Агуулга |
|---|---|
| `src/schedulers.py` | Алгоритмууд, оролтын шалгалт, task файл задлагч |
| `src/server.py` | Локал вэб сервер, `POST /api/schedule`, `/static/` |
| `src/cli.py` | Номын форматтай файлыг уншдаг командын мөрийн хувилбар |
| `src/static/index.html` | UI: процессын хүснэгт, D3 Gantt Chart, тоглуулагч |
| `src/static/vendor/` | D3.js v7.9.0 (`d3.min.js`) ба лиценз |
| `tests/` | Unit тест (номын жишээ, захын болон алдааны тохиолдол) |
| `examples/` | `.txt` даалгаврын файл, `.json` сценари (UI-ийн "файл ачаалах"-д) |
| `docs/` | Тайлан, Manual (PDF), screenshot, PDF үүсгэгч `build_docs.py` |

Дэлгэрэнгүйг [тайлан](docs/V-1-8_BD1_Report.pdf) ба [Manual](docs/V-1-8_Manual.pdf)-аас үзнэ.

## Тохиролцоо ба дүрэм
- Номын төсөл: эрэмбэ **1-ээс 10**, **их тоо = өндөр эрэмбэ** (анхдагч). UI болон CLI-д `low` (бага тоо = өндөр эрэмбэ)
  сонголт бий. Энэ нь лекцийн 5.3 хэсгийн жишээний дүрэм.
- Round Robin-ий квант анхдагчаар **10 ms** (ном), өөрчилж болно.
- Task файл: `[нэр], [эрэмбэ], [CPU ээлж]`, бүх даалгавар 0 цагт ирнэ. UI болон JSON сценарид ирэх цагийг нэмж өгч болно.
- Priority + RR: өндөр эрэмбэтэй нь эхэлж, адил эрэмбэтэй нь квантаар ээлжлэн ажиллана; өндөр эрэмбэтэй процесс шинээр
  ирвэл одоогийнхыг тасалдуулна.
- Response time = CPU анх авсан цаг - ирэх цаг. Waiting = turnaround - CPU ээлж. Turnaround = дуусах цаг - ирэх цаг.
- Оролтын хязгаар: ихдээ 50 процесс, утга ≤ 100000, эрэмбэ 1..10, бүх утга бүхэл тоо.

## Нэр томьёо
| Код / UI | Монгол | English |
|---|---|---|
| arrival | Ирэх цаг | arrival time |
| burst | CPU ээлж | CPU burst |
| priority | Эрэмбэ | priority |
| quantum | Квант | time quantum |
| waiting | Хүлээлтийн хугацаа | waiting time |
| turnaround | Эргэлтийн хугацаа | turnaround time |
| response | Response time | response time |
| idle | Сул (idle) | idle |
| FCFS / SJF / Priority / RR | Эхэнд ирсэн нь эхэлж үйлчлүүлэх / Богино-ажил-эхэнд / Эрэмбэлэлттэй төлөвлөлт / Round Robin | - |

## Known issues
- Context switch-ийн зардал, I/O ээлж, SRTF, multilevel feedback queue, aging хэрэгжээгүй.
- Хугацаа бүхэл тоо. Сервер зөвхөн локал (`127.0.0.1`) дээр ажиллана.
- Серверийн логт `GET /favicon.ico 404` гарах нь хэвийн.

## Гуравдагч талын код, сан, AI
- **Сан:** серверт зөвхөн Python стандарт сан. UI-д **D3.js v7.9.0** (ISC лиценз, https://d3js.org) ашигласан бөгөөд
  интернэтгүй ажиллуулахын тулд `src/static/vendor/d3.min.js`-ээр репозиторид хадгалсан.
- **AI ашигласан тухай:** код, тест, тайлан, Manual-ийн эхийг бэлтгэхэд AI туслах (Claude, Anthropic) ашигласан. Баг код,
  тестийг өөрсдөө ажиллуулж, UI-ийн screenshot-ыг авч шалгасан бөгөөд туршилтаас илэрсэн алдааг (алдаа гарахад хуучин
  Gantt Chart дэлгэц дээр үлдэх) зассан.
