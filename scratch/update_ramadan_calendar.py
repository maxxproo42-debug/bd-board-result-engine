# -*- coding: utf-8 -*-
"""
Update templates/index.html to include:
1. Direct 'রমজান ক্যালেন্ডার' button in desktop top navbar and mobile drawer
2. Dedicated Upcoming Holy Ramadan 30-Day Calendar (১ম - ৩০তম রোজা) with:
   - Dynamic upcoming Ramadan detection (1446 AH / 1447 AH / 1448 AH)
   - Mode switcher: 'আসন্ন পবিত্র মাহে রমজান (১ম - ৩০তম রোজা)' vs 'চলতি মাস (আজ থেকে ৩০ দিন)'
   - Moon-sighting adjuster (-1 day / normal / +1 day) for Bangladesh National Moon Sighting Committee alignment
   - 3 Ashra indicators (রহমত, মাগফিরাত, নাজাত)
   - Laylatul Qadr odd nights highlighted (২১, ২৩, ২৫, ২৭, ২৯ রোজা)
   - Ahle Hadith / Shaikh Abdur Razzaq bin Yousuf authentic Sehri-Iftar rules & Masnoon Duas
3. Smart 3-stage live countdown (Today's Sehri end -> Today's Iftar -> Tomorrow's Sehri end)
4. Midnight auto-rollover so the entire timetable & Ramadan calendar auto-updates daily without refreshing.
"""

import sys

TARGET_FILE = r"c:\Users\MD SHAIFUL ISLAM\Desktop\edu\dinajpur_hsc_app\templates\index.html"

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# -----------------------------------------------------------------------------
# 1. Add Desktop Nav Item & Mobile Nav Item for 'রমজান ক্যালেন্ডার'
# -----------------------------------------------------------------------------
desktop_nav_target = """            <li>
                <button type="button" class="nav-link-btn" id="nav-item-prayer" onclick="switchTab('prayer')">
                    🕌 নামাজের সময় ও সেহরি-ইফতার
                </button>
            </li>"""

desktop_nav_replacement = """            <li>
                <button type="button" class="nav-link-btn" id="nav-item-prayer" onclick="switchTab('prayer')">
                    🕌 নামাজের সময় ও সেহরি-ইফতার
                </button>
            </li>
            <li>
                <button type="button" class="nav-link-btn" id="nav-item-ramadan" onclick="openRamadanCalendar()" style="color:#fbbf24; border-color:rgba(245,158,11,0.35);">
                    🌙 রমজান ক্যালেন্ডার
                </button>
            </li>"""

assert desktop_nav_target in content, "Desktop nav target not found"
content = content.replace(desktop_nav_target, desktop_nav_replacement, 1)

mobile_nav_target = """        <button type="button" class="nav-link-btn" onclick="switchTab('prayer'); closeMobileNav();">
            🕌 নামাজের সময় ও সেহরি-ইফতার সূচি (৬৪ জেলা)
        </button>"""

mobile_nav_replacement = """        <button type="button" class="nav-link-btn" onclick="switchTab('prayer'); closeMobileNav();">
            🕌 নামাজের সময় ও সেহরি-ইফতার সূচি (৬৪ জেলা)
        </button>
        <button type="button" class="nav-link-btn" onclick="openRamadanCalendar(); closeMobileNav();" style="border-left: 3px solid #f59e0b; color:#fbbf24;">
            🌙 পবিত্র মাহে রমজান ক্যালেন্ডার (১ম - ৩০তম রোজা সেহরি ও ইফতার)
        </button>"""

assert mobile_nav_target in content, "Mobile nav target not found"
content = content.replace(mobile_nav_target, mobile_nav_replacement, 1)

# -----------------------------------------------------------------------------
# 2. Add Ramadan CSS in <style>
# -----------------------------------------------------------------------------
css_target = """        .roza-badge {"""

css_addition = """        /* Ramadan Calendar Mode Controls & Indicators */
        .ramadan-mode-group {
            display: inline-flex;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 3px;
            gap: 3px;
        }
        .ramadan-mode-btn {
            background: transparent;
            border: none;
            color: #94a3b8;
            padding: 0.45rem 0.85rem;
            font-size: 0.82rem;
            font-weight: 700;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .ramadan-mode-btn.active {
            background: linear-gradient(135deg, #10b981, #059669);
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.35);
        }
        .ramadan-ctrl-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 0.8rem 1rem;
            margin-bottom: 1rem;
        }
        .ramadan-ashra-badge-row {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
            margin-bottom: 0.85rem;
            font-size: 0.8rem;
        }
        .ashra-pill {
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }
        .ashra-pill.rahmat { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
        .ashra-pill.magfirat { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
        .ashra-pill.najat { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
        .qadr-badge {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: #000;
            font-weight: 800;
            font-size: 0.68rem;
            padding: 0.12rem 0.45rem;
            border-radius: 4px;
            display: inline-block;
            margin-top: 2px;
            box-shadow: 0 0 8px rgba(245, 158, 11, 0.4);
            white-space: nowrap;
        }
        .moon-offset-btn {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #cbd5e1;
            padding: 0.35rem 0.65rem;
            font-size: 0.78rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .moon-offset-btn:hover, .moon-offset-btn.active {
            background: #f59e0b;
            color: #000;
            font-weight: 800;
            border-color: #f59e0b;
        }
        .ramadan-print-header { display: none; }

        .roza-badge {"""

assert css_target in content, "CSS target not found"
content = content.replace(css_target, css_addition, 1)

# -----------------------------------------------------------------------------
# 3. Update @media print to produce a stunning Wall Calendar
# -----------------------------------------------------------------------------
print_target = """        @media print {
            body { background: #ffffff !important; color: #000000 !important; }
            .top-nav, .app-header, .tabs-nav, .glass-card, .btn-print, .app-footer, .no-print { display: none !important; }
            .result-container { display: block !important; }
            .sheet-card { box-shadow: none !important; border: 1px solid #000000 !important; }
            #prayer-section { display: block !important; background: #ffffff !important; color: #000000 !important; }
            .prayer-quick-bar, .prayer-district-picker, .prayer-hero-grid, .forbidden-banner, .dua-container { display: none !important; }
            .ramadan-table-card { border: 1px solid #000 !important; background: transparent !important; }
            .ramadan-tbl th { background: #eee !important; color: #000 !important; }
            .ramadan-tbl td { color: #000 !important; }
        }"""

print_replacement = """        @media print {
            body { background: #ffffff !important; color: #000000 !important; font-family: 'Hind Siliguri', Arial, sans-serif !important; }
            .top-nav, .app-header, .tabs-nav, .glass-card:not(#prayer-section), .btn-print, .app-footer, .no-print, .prayer-quick-bar, .prayer-district-picker, .prayer-hero-grid, .extra-times-grid, .forbidden-banner, .ramadan-ctrl-bar, .ramadan-table-actions { display: none !important; }
            #prayer-section { display: block !important; background: #ffffff !important; color: #000000 !important; box-shadow: none !important; border: none !important; padding: 0 !important; margin: 0 !important; }
            .ramadan-table-card { border: none !important; background: transparent !important; box-shadow: none !important; padding: 0 !important; }
            .ramadan-print-header { display: block !important; text-align: center; margin-bottom: 12px; border-bottom: 2px solid #000; padding-bottom: 8px; }
            .ramadan-print-header h2 { font-size: 16pt; margin: 0 0 4px 0; color: #000; }
            .ramadan-print-header p { font-size: 10pt; margin: 0; color: #333; }
            .ramadan-scroll-wrap { max-height: none !important; overflow: visible !important; border: 1px solid #333 !important; }
            .ramadan-tbl { width: 100% !important; border-collapse: collapse !important; font-size: 9.5pt !important; color: #000 !important; }
            .ramadan-tbl th { background: #e2e8f0 !important; color: #000 !important; border: 1px solid #94a3b8 !important; padding: 5px 6px !important; font-weight: 800 !important; }
            .ramadan-tbl td { color: #000 !important; border: 1px solid #cbd5e1 !important; padding: 4px 6px !important; }
            .ramadan-tbl tr:nth-child(even) td { background: #f8fafc !important; }
            .roza-badge { background: transparent !important; color: #000 !important; border: none !important; font-weight: 800 !important; padding: 0 !important; }
            .qadr-badge { background: #fef3c7 !important; color: #92400e !important; border: 1px solid #b45309 !important; font-size: 7.5pt !important; }
        }"""

assert print_target in content, "Print target not found"
content = content.replace(print_target, print_replacement, 1)

# -----------------------------------------------------------------------------
# 4. Replace Ramadan HTML card with full Dedicated Upcoming Ramadan Component
# -----------------------------------------------------------------------------
import re

old_card_pattern = re.compile(
    r'<!-- 30-Day Ramadan / Monthly Schedule Table -->.*?<div class="ramadan-table-card">.*?</div>\s*</div>\s*</section>',
    re.DOTALL
)

new_ramadan_html = """<!-- 30-Day Dedicated Ramadan Calendar & Monthly Schedule -->
        <div class="ramadan-table-card" id="ramadan-table-card">
            <!-- Dedicated Print Header (Only visible in Print/PDF) -->
            <div class="ramadan-print-header">
                <div style="font-size:14pt; font-family:'Amiri', serif; font-weight:bold;">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
                <h2 id="print-ramadan-title">পবিত্র মাহে রমজান — পূর্ণাঙ্গ সেহরি ও ইফতারের সময়সূচি</h2>
                <p>জেলা: <b id="print-ramadan-dist">ঢাকা</b> · মানদণ্ড: <b>শায়খ আব্দুর রাজ্জাক বিন ইউসুফ ও আহলে হাদীস (সহিহ হাদিস সম্মত)</b></p>
                <p style="font-size:8.5pt; color:#555; margin-top:2px;">* সুবহে সাদিক পর্যন্ত সেহরি · সূর্যাস্তের সাথে সাথে অনতিবিলম্বে ইফতার · ১ গুণ ছায়ায় আসর (মিছলে আওয়াল)</p>
            </div>

            <!-- Ramadan Table Top Heading & Actions -->
            <div class="ramadan-table-head">
                <div class="ramadan-table-title">
                    <span style="font-size:1.4rem;">🌙</span> 
                    <div>
                        <span id="ramadan-tbl-heading">আসন্ন পবিত্র মাহে রমজান — পূর্ণাঙ্গ সেহরি ও ইফতারের ক্যালেন্ডার</span>
                        <div style="font-size:0.8rem; font-weight:normal; color:#38bdf8; margin-top:2px;">
                            🕌 আহলে হাদীস ও শায়খ আব্দুর রাজ্জাক বিন ইউসুফ মানদণ্ড (১ম থেকে ৩০তম রোজা)
                        </div>
                    </div>
                </div>
                <div class="ramadan-table-actions">
                    <button type="button" class="btn btn-secondary no-print" onclick="window.print()" style="padding:0.45rem 0.95rem; font-size:0.85rem; display:inline-flex; align-items:center; gap:0.4rem; background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.35); border-radius:8px; color:#fbbf24; cursor:pointer; font-weight:700;">
                        🖨️ রমজান ক্যালেন্ডার প্রিন্ট / PDF সংরক্ষণ
                    </button>
                </div>
            </div>

            <!-- Control Bar: Mode Toggle + Season Selector + Moon Sighting Adjuster -->
            <div class="ramadan-ctrl-bar no-print">
                <!-- Mode Switcher -->
                <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                    <span style="font-size:0.82rem; color:#94a3b8; font-weight:700;">ক্যালেন্ডার ধরন:</span>
                    <div class="ramadan-mode-group">
                        <button type="button" class="ramadan-mode-btn active" id="btn-mode-upcoming" onclick="setRamadanMode('upcoming')">
                            🌙 আসন্ন মাহে রমজান (১ম - ৩০তম রোজা)
                        </button>
                        <button type="button" class="ramadan-mode-btn" id="btn-mode-rolling" onclick="setRamadanMode('rolling')">
                            📅 চলতি মাস (আজ থেকে ৩০ দিন)
                        </button>
                    </div>
                </div>

                <!-- Season & Moon Offset Controls -->
                <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap;">
                    <div id="ramadan-year-ctrl" style="display:flex; align-items:center; gap:0.4rem;">
                        <span style="font-size:0.82rem; color:#94a3b8; font-weight:700;">রমজান বছর:</span>
                        <select id="ramadan-season-select" onchange="changeRamadanSeason(this.value)" style="background:rgba(15,23,42,0.9); color:#f8fafc; border:1px solid rgba(255,255,255,0.18); border-radius:8px; padding:0.35rem 0.65rem; font-size:0.82rem; font-weight:700; cursor:pointer;">
                            <!-- Populated dynamically -->
                        </select>
                    </div>

                    <div id="ramadan-moon-ctrl" style="display:flex; align-items:center; gap:0.35rem;">
                        <span style="font-size:0.82rem; color:#94a3b8; font-weight:700;" title="জাতীয় চাঁদ দেখা কমিটির ঘোষণার প্রেক্ষিতে ১ ক্লিকে সমন্বয় করুন">চাঁদ দেখা:</span>
                        <button type="button" class="moon-offset-btn" id="moon-offset-minus" onclick="setMoonOffset(-1)" title="চাঁদ ১ দিন আগে দেখা গেলে">-১ দিন</button>
                        <button type="button" class="moon-offset-btn active" id="moon-offset-zero" onclick="setMoonOffset(0)" title="স্বাভাবিক সম্ভাব্য তারিখ">সম্ভাব্য</button>
                        <button type="button" class="moon-offset-btn" id="moon-offset-plus" onclick="setMoonOffset(1)" title="চাঁদ ১ দিন পর দেখা গেলে">+১ দিন</button>
                    </div>
                </div>
            </div>

            <!-- Ashra Indicators & District Context Bar -->
            <div class="ramadan-ashra-badge-row">
                <span class="ashra-pill rahmat">🟢 ১ম দশক (১-১০ রোজা): রহমত</span>
                <span class="ashra-pill magfirat">🔵 ২য় দশক (১১-২০ রোজা): মাগফিরাত</span>
                <span class="ashra-pill najat">🟡 ৩য় দশক (২১-৩০ রোজা): নাজাত ও শবে কদর</span>
                <span style="margin-left:auto; font-size:0.82rem; color:#94a3b8;">
                    নির্বাচিত জেলা: <b id="ramadan-tbl-dist-name" style="color:#38bdf8;">ঢাকা</b> · <span id="ramadan-date-span-info" style="color:#e2e8f0;"></span>
                </span>
            </div>

            <!-- Notes on Sahih Hadith / Shaikh Abdur Razzaq bin Yousuf -->
            <div style="font-size:0.82rem; color:#94a3b8; margin-bottom:0.85rem; line-height:1.5; background:rgba(255,255,255,0.03); border-left:3px solid #10b981; padding:0.5rem 0.85rem; border-radius:0 8px 8px 0;">
                <b style="color:#34d399;">সহিহ সুন্নাহ নির্দেশিকা:</b> 
                (১) <b>সেহরি:</b> সুবহে সাদিক পর্যন্ত সেহরি খাওয়া যাবে (সূরা বাকারা ১৮৭)। 
                (২) <b>ইফতার:</b> সূর্যাস্তের সাথে সাথে অনতিবিলম্বে ইফতার করা সুন্নত (সহিহ বুখারী ১৯৫৭)। 
                (৩) <b>আসর:</b> ছায়া ১ গুণ (মিছলে আওয়াল)। 
                (৪) <b>নিয়ত:</b> অন্তরের ইচ্ছাই নিয়ত; মুখে প্রচলিত 'নাওয়াইতু আন আছুমা...' পড়া বিদআত।
            </div>

            <!-- Full Ramadan Table -->
            <div class="ramadan-scroll-wrap">
                <table class="ramadan-tbl">
                    <thead>
                        <tr>
                            <th style="width:90px; text-align:center;">রোজা নং</th>
                            <th>তারিখ ও বার</th>
                            <th style="color:#38bdf8;">সেহরি শেষ (সুবহে সাদিক)</th>
                            <th style="color:#34d399;">ফজর শুরু</th>
                            <th>সূর্যোদয়</th>
                            <th>যোহর</th>
                            <th>আসর (মিছলে আওয়াল)</th>
                            <th style="color:#fbbf24;">ইফতার (সূর্যাস্ত)</th>
                            <th>এশা</th>
                        </tr>
                    </thead>
                    <tbody id="ramadan-table-body">
                        <!-- Populated dynamically -->
                    </tbody>
                </table>
            </div>

            <!-- Post-Table Authentic Duas & Instructions -->
            <div class="dua-container" style="margin-top:1.2rem; padding-top:0.5rem;">
                <div class="dua-card" style="border-left:4px solid #fbbf24;">
                    <div class="dua-title">
                        <span>✨</span>
                        <div>
                            <b>ইফতারের সহিহ মাসনূন দোয়া (আবু দাউদ ২৩৫৭)</b>
                            <span class="dua-ref">শায়খ আব্দুর রাজ্জাক বিন ইউসুফ নির্দেশিত সহিহ হাদিস</span>
                        </div>
                    </div>
                    <div class="dua-arabic">ذَهَبَ الظَّمَأُ وَابْتَلَّتِ الْعُرُوقُ وَثَبَتَ الأَجْرُ إِنْ شَاءَ اللَّهُ</div>
                    <div class="dua-bangla">উচ্চারণ: 'যাহাবায জামা'উ ওয়াবতাল্লাতিল উরূকু ওয়া ছাবাতাল আজরু ইনশাআল্লাহ।'</div>
                    <div class="dua-meaning">অর্থ: 'পিপাসা দূর হলো, শিরা-উপশিরা সিক্ত হলো এবং ইনশাআল্লাহ প্রতিদান নিশ্চিত হলো।'</div>
                </div>

                <div class="dua-card" style="border-left:4px solid #f59e0b;">
                    <div class="dua-title">
                        <span>🌙</span>
                        <div>
                            <b>লাইলাতুল কদরের সহিহ দোয়া (তিরমিযী ৩৫১৩)</b>
                            <span class="dua-ref">রমজানের শেষ দশকের বিজোড় রাতগুলোতে আমলযোগ্য</span>
                        </div>
                    </div>
                    <div class="dua-arabic">اللَّهُمَّ إِنَّكَ عَفُوٌّ تُحِبُّ الْعَفْوَ فَاعْفُ عَنِّي</div>
                    <div class="dua-bangla">উচ্চারণ: 'আল্লাহুম্মা ইন্নাকা 'আফুউউন তুহিব্বুল 'আফওয়া ফা'ফু 'আন্নী।'</div>
                    <div class="dua-meaning">অর্থ: 'হে আল্লাহ! নিশ্চয় আপনি ক্ষমাশীল, ক্ষমা করা পছন্দ করেন। অতএব আমাকে ক্ষমা করে দিন।'</div>
                </div>
            </div>
        </div>
    </section>"""

new_content, count = old_card_pattern.subn(new_ramadan_html, content)
assert count == 1, f"Failed to replace old ramadan card (count={count})"
content = new_content

# -----------------------------------------------------------------------------
# 5. Replace JavaScript: renderRamadanTable + updatePrayerTimes + Ramadan State
# -----------------------------------------------------------------------------
old_js_start = content.find("function updatePrayerTimes() {")
old_js_end = content.find("function initPrayerDistrictSelect() {")
assert old_js_start != -1 and old_js_end != -1, "JS boundaries not found"

new_js = """    // ============================================================
    // RAMADAN SEASONS & DEDICATED CALENDAR CONFIG
    // ============================================================
    const RAMADAN_SEASONS = [
        { key: '1447', hijri: '১৪৪৭ হিজরী (২০২৬)', enYear: 2026, start: new Date(2026, 1, 18), days: 30 }, // Feb 18, 2026
        { key: '1448', hijri: '১৪৪৮ হিজরী (২০২৭)', enYear: 2027, start: new Date(2027, 1, 8), days: 30 },  // Feb 8, 2027
        { key: '1446', hijri: '১৪৪৬ হিজরী (২০২৫)', enYear: 2025, start: new Date(2025, 2, 2), days: 30 },  // Mar 2, 2025
        { key: '1449', hijri: '১৪৪৯ হিজরী (২০২৮)', enYear: 2028, start: new Date(2028, 0, 28), days: 30 }  // Jan 28, 2028
    ];

    let currentRamadanMode = 'upcoming'; // 'upcoming' or 'rolling'
    let currentRamadanSeasonKey = '1447';
    let currentMoonOffsetDays = 0; // -1, 0, +1
    let lastCheckedDate = null;

    function getUpcomingRamadanSeason() {
        const now = new Date();
        for (const s of RAMADAN_SEASONS) {
            const seasonEnd = new Date(s.start.getTime() + 32 * 24 * 60 * 60 * 1000);
            if (now <= seasonEnd) return s;
        }
        return RAMADAN_SEASONS[0];
    }

    function initRamadanSeasonDropdown() {
        const sel = document.getElementById('ramadan-season-select');
        if (!sel || sel.options.length > 0) return;

        const def = getUpcomingRamadanSeason();
        currentRamadanSeasonKey = def.key;

        let opts = '';
        RAMADAN_SEASONS.forEach(s => {
            const isSel = (s.key === currentRamadanSeasonKey) ? 'selected' : '';
            opts += `<option value="${s.key}" ${isSel}>পবিত্র মাহে রমজান ${s.hijri}</option>`;
        });
        sel.innerHTML = opts;
    }

    function changeRamadanSeason(key) {
        currentRamadanSeasonKey = key;
        renderRamadanTable(currentPrayerDistrict);
    }

    function setRamadanMode(mode) {
        currentRamadanMode = mode;
        const btnUp = document.getElementById('btn-mode-upcoming');
        const btnRo = document.getElementById('btn-mode-rolling');
        const yearCtrl = document.getElementById('ramadan-year-ctrl');
        const moonCtrl = document.getElementById('ramadan-moon-ctrl');

        if (mode === 'upcoming') {
            if (btnUp) btnUp.classList.add('active');
            if (btnRo) btnRo.classList.remove('active');
            if (yearCtrl) yearCtrl.style.display = 'flex';
            if (moonCtrl) moonCtrl.style.display = 'flex';
        } else {
            if (btnUp) btnUp.classList.remove('active');
            if (btnRo) btnRo.classList.add('active');
            if (yearCtrl) yearCtrl.style.display = 'none';
            if (moonCtrl) moonCtrl.style.display = 'none';
        }
        renderRamadanTable(currentPrayerDistrict);
    }

    function setMoonOffset(offset) {
        currentMoonOffsetDays = offset;
        ['minus', 'zero', 'plus'].forEach(id => {
            const btn = document.getElementById(`moon-offset-${id}`);
            if (btn) btn.classList.remove('active');
        });
        if (offset === -1 && document.getElementById('moon-offset-minus')) document.getElementById('moon-offset-minus').classList.add('active');
        if (offset === 0 && document.getElementById('moon-offset-zero')) document.getElementById('moon-offset-zero').classList.add('active');
        if (offset === 1 && document.getElementById('moon-offset-plus')) document.getElementById('moon-offset-plus').classList.add('active');
        renderRamadanTable(currentPrayerDistrict);
    }

    function openRamadanCalendar() {
        switchTab('prayer');
        setRamadanMode('upcoming');
        setTimeout(() => {
            const el = document.getElementById('ramadan-table-card');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 120);
    }

    // ============================================================
    // LIVE DAILY PRAYER & COUNTDOWN ENGINE (AUTO UPDATES 24/7)
    // ============================================================
    function updatePrayerTimes() {
        const now = new Date();

        // Midnight Auto-Rollover: If date changed, automatically refresh table highlights
        if (lastCheckedDate !== null && lastCheckedDate !== now.getDate()) {
            renderRamadanTable(currentPrayerDistrict);
        }
        lastCheckedDate = now.getDate();

        const times = calcAstronomicalTimes(now, currentPrayerDistrict);
        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        const tomorrowTimes = calcAstronomicalTimes(tomorrow, currentPrayerDistrict);

        const el = (id) => document.getElementById(id);

        // Update 5 Waqt Times
        if (el('w-fajr-main')) el('w-fajr-main').innerText = `${formatTime12(times.fajr, false)} AM`;
        if (el('w-fajr-start')) el('w-fajr-start').innerText = formatTime12(times.fajr);
        if (el('w-fajr-end')) el('w-fajr-end').innerText = formatTime12(times.sunrise);

        if (el('w-dhuhr-main')) el('w-dhuhr-main').innerText = `${formatTime12(times.dhuhr, false)} PM`;
        if (el('w-dhuhr-start')) el('w-dhuhr-start').innerText = formatTime12(times.dhuhr);
        if (el('w-dhuhr-end')) el('w-dhuhr-end').innerText = formatTime12(times.asr);

        if (el('w-asr-main')) el('w-asr-main').innerText = `${formatTime12(times.asr, false)} PM`;
        if (el('w-asr-start')) el('w-asr-start').innerText = formatTime12(times.asr);
        if (el('w-asr-end')) el('w-asr-end').innerText = formatTime12(times.sunset);

        if (el('w-maghrib-main')) el('w-maghrib-main').innerText = `${formatTime12(times.maghrib, false)} PM`;
        if (el('w-maghrib-start')) el('w-maghrib-start').innerText = formatTime12(times.maghrib);
        if (el('w-maghrib-end')) el('w-maghrib-end').innerText = formatTime12(times.isha);

        if (el('w-isha-main')) el('w-isha-main').innerText = `${formatTime12(times.isha, false)} PM`;
        if (el('w-isha-start')) el('w-isha-start').innerText = formatTime12(times.isha);
        if (el('w-isha-end')) el('w-isha-end').innerText = formatTime12(tomorrowTimes.fajr);

        // Extra Times
        if (el('ex-sunrise')) el('ex-sunrise').innerText = formatTime12(times.sunrise);
        if (el('ex-sunset')) el('ex-sunset').innerText = formatTime12(times.sunset);
        if (el('ex-tahajjud')) el('ex-tahajjud').innerText = formatTime12(times.tahajjud);
        if (el('ex-ishraq')) el('ex-ishraq').innerText = formatTime12(times.ishraq);
        if (el('ex-duha')) el('ex-duha').innerText = formatTime12(times.duha);

        // Forbidden Times
        if (el('fb-sunrise')) el('fb-sunrise').innerText = `${formatTime12(times.sunrise)} হতে ${formatTime12(times.ishraq)} পর্যন্ত`;
        const solarNoonStart = new Date(times.dhuhr.getTime() - 10 * 60 * 1000);
        if (el('fb-zawal')) el('fb-zawal').innerText = `${formatTime12(solarNoonStart)} হতে ${formatTime12(times.dhuhr)} পর্যন্ত`;
        const sunsetForbiddenStart = new Date(times.sunset.getTime() - 15 * 60 * 1000);
        if (el('fb-sunset')) el('fb-sunset').innerText = `${formatTime12(sunsetForbiddenStart)} হতে ${formatTime12(times.sunset)} পর্যন্ত`;

        // Determine Current & Next Waqt
        const waqts = [
            { key: 'fajr', name: 'ফজর', cardId: 'waqt-card-fajr', start: times.fajr, end: times.sunrise },
            { key: 'ishraq', name: 'ইশরাক/সূর্যোদয়', cardId: null, start: times.sunrise, end: times.dhuhr },
            { key: 'dhuhr', name: 'যোহর', cardId: 'waqt-card-dhuhr', start: times.dhuhr, end: times.asr },
            { key: 'asr', name: 'আসর', cardId: 'waqt-card-asr', start: times.asr, end: times.sunset },
            { key: 'maghrib', name: 'মাগরিব', cardId: 'waqt-card-maghrib', start: times.maghrib, end: times.isha },
            { key: 'isha', name: 'এশা', cardId: 'waqt-card-isha', start: times.isha, end: tomorrowTimes.fajr }
        ];

        let currWaqt = null;
        let nextWaqt = null;

        if (now < times.fajr) {
            currWaqt = { key: 'isha', name: 'এশা (রাত্রি)', cardId: 'waqt-card-isha', end: times.fajr };
            nextWaqt = { name: 'ফজর', start: times.fajr };
        } else {
            for (let i = 0; i < waqts.length; i++) {
                const w = waqts[i];
                if (now >= w.start && now < w.end) {
                    currWaqt = w;
                    for (let j = i + 1; j < waqts.length; j++) {
                        if (waqts[j].cardId) {
                            nextWaqt = waqts[j];
                            break;
                        }
                    }
                    if (!nextWaqt) nextWaqt = { name: 'ফজর', start: tomorrowTimes.fajr };
                    break;
                }
            }
        }

        if (!currWaqt) {
            currWaqt = { key: 'isha', name: 'এশা', cardId: 'waqt-card-isha', end: tomorrowTimes.fajr };
            nextWaqt = { name: 'ফজর', start: tomorrowTimes.fajr };
        }

        // Highlight Active Waqt Card
        document.querySelectorAll('.waqt-card').forEach(c => {
            c.classList.remove('active-waqt');
            const badge = c.querySelector('.waqt-active-badge');
            if (badge) badge.remove();
        });

        if (currWaqt.cardId && el(currWaqt.cardId)) {
            const card = el(currWaqt.cardId);
            card.classList.add('active-waqt');
            if (!card.querySelector('.waqt-active-badge')) {
                const b = document.createElement('div');
                b.className = 'waqt-active-badge';
                b.innerHTML = '● এখন এই ওয়াক্ত চলছে';
                card.appendChild(b);
            }
        }

        // Hero Card 2: Next Waqt Countdown
        const timeToWaqtEnd = Math.max(0, currWaqt.end.getTime() - now.getTime());
        if (el('hero-curr-waqt-name')) el('hero-curr-waqt-name').innerText = `চলমান: ${currWaqt.name}`;
        if (el('hero-next-waqt-timer')) el('hero-next-waqt-timer').innerText = formatDurationRemaining(timeToWaqtEnd);
        if (el('hero-next-waqt-name')) el('hero-next-waqt-name').innerText = nextWaqt ? nextWaqt.name : '--';
        if (el('hero-next-waqt-start')) el('hero-next-waqt-start').innerText = nextWaqt ? formatTime12(nextWaqt.start) : '--:--';

        // Hero Card 1: Smart 3-State Sehri / Iftar Countdown
        if (now < times.sehriEnd) {
            // 1. Early morning before Sehri End: Count down to TODAY'S Sehri
            const timeToSehri = times.sehriEnd.getTime() - now.getTime();
            if (el('hero-countdown-label')) el('hero-countdown-label').innerText = 'আজকের সেহরি শেষ হতে বাকি:';
            if (el('hero-countdown-timer')) el('hero-countdown-timer').innerText = formatDurationRemaining(timeToSehri);
            if (el('hero-iftar-subtext')) el('hero-iftar-subtext').innerHTML = `আজকের সেহরি শেষ: <b style="color:#38bdf8; margin-left:5px;">${formatTime12(times.sehriEnd)}</b> (ফজর: ${formatTime12(times.fajr)})`;
        } else if (now < times.maghrib) {
            // 2. Daytime while Fasting: Count down to TODAY'S Iftar
            const timeToIftar = times.maghrib.getTime() - now.getTime();
            if (el('hero-countdown-label')) el('hero-countdown-label').innerText = 'আজকের ইফতারের বাকি সময়:';
            if (el('hero-countdown-timer')) el('hero-countdown-timer').innerText = formatDurationRemaining(timeToIftar);
            if (el('hero-iftar-subtext')) el('hero-iftar-subtext').innerHTML = `আজকের ইফতার: <b style="color:#fbbf24; margin-left:5px;">${formatTime12(times.maghrib)}</b>`;
        } else {
            // 3. Evening / Night after Iftar: Count down to TOMORROW'S Sehri
            const timeToTomorrowSehri = tomorrowTimes.sehriEnd.getTime() - now.getTime();
            if (el('hero-countdown-label')) el('hero-countdown-label').innerText = 'আগামীকাল সেহরি শেষ হতে বাকি:';
            if (el('hero-countdown-timer')) el('hero-countdown-timer').innerText = formatDurationRemaining(timeToTomorrowSehri);
            if (el('hero-iftar-subtext')) el('hero-iftar-subtext').innerHTML = `আগামীকালের সেহরি শেষ: <b style="color:#38bdf8; margin-left:5px;">${formatTime12(tomorrowTimes.sehriEnd)}</b> (ফজর: ${formatTime12(tomorrowTimes.fajr)})`;
        }

        // Header Quick Bar Ticker
        if (el('pq-current-waqt')) el('pq-current-waqt').innerText = currWaqt.name;
        if (el('pq-current-range')) el('pq-current-range').innerText = `(শেষ হতে বাকি ${formatDurationBn(timeToWaqtEnd)})`;
        if (el('pq-iftar-time')) el('pq-iftar-time').innerText = formatTime12(times.maghrib);
        if (el('pq-sehri-time')) el('pq-sehri-time').innerText = formatTime12(now < times.sehriEnd ? times.sehriEnd : tomorrowTimes.sehriEnd);

        // Hijri Year/Date Badge
        if (el('prayer-hijri-date')) {
            el('prayer-hijri-date').innerText = `হিজরি ১৪৪৭-৪৮ · ${times.maghrib > now ? 'আজকের রোজা' : 'পরবর্তী সেহরি'}`;
        }
    }

    // ============================================================
    // DEDICATED 30-DAY RAMADAN CALENDAR RENDERER
    // ============================================================
    function renderRamadanTable(districtKey) {
        const tbody = document.getElementById('ramadan-table-body');
        if (!tbody) return;

        const dist = PRAYER_DISTRICTS[districtKey] || PRAYER_DISTRICTS['dhaka'];
        const distLabel = document.getElementById('ramadan-tbl-dist-name');
        if (distLabel) distLabel.innerText = dist.name;
        if (document.getElementById('print-ramadan-dist')) document.getElementById('print-ramadan-dist').innerText = dist.name;

        const now = new Date();
        const currentY = now.getFullYear();
        const currentM = now.getMonth();
        const currentD = now.getDate();

        const bnDayNames = ['রবিবার', 'সোমবার', 'মঙ্গলবার', 'বুধবার', 'বৃহস্পতিবার', 'শুক্রবার', 'শনিবার'];
        const bnMonths = ['জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'];

        // Determine Start Date & Heading based on Mode
        let startDate;
        let calendarTitle = '';

        if (currentRamadanMode === 'upcoming') {
            const season = RAMADAN_SEASONS.find(s => s.key === currentRamadanSeasonKey) || RAMADAN_SEASONS[0];
            startDate = new Date(season.start.getFullYear(), season.start.getMonth(), season.start.getDate() + currentMoonOffsetDays);
            calendarTitle = `আসন্ন পবিত্র মাহে রমজান ${season.hijri} — পূর্ণাঙ্গ সেহরি ও ইফতার ক্যালেন্ডার`;
            if (document.getElementById('print-ramadan-title')) {
                document.getElementById('print-ramadan-title').innerText = `পবিত্র মাহে রমজান ${season.hijri} — পূর্ণাঙ্গ সেহরি ও ইফতারের সময়সূচি`;
            }
        } else {
            startDate = new Date(currentY, currentM, currentD);
            calendarTitle = `চলতি মাসের ৩০ দিনের পূর্ণাঙ্গ নামাজ ও সেহরি-ইফতারের সময়সূচি (${dist.name} জেলা)`;
            if (document.getElementById('print-ramadan-title')) {
                document.getElementById('print-ramadan-title').innerText = `চলতি মাসের ৩০ দিনের নামাজ ও সেহরি-ইফতারের সময়সূচি (${dist.name})`;
            }
        }

        const headingEl = document.getElementById('ramadan-tbl-heading');
        if (headingEl) headingEl.innerText = calendarTitle;

        const startSpanStr = `${toBnNum(startDate.getDate())} ${bnMonths[startDate.getMonth()]}`;
        const endRowDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate() + 29);
        const endSpanStr = `${toBnNum(endRowDate.getDate())} ${bnMonths[endRowDate.getMonth()]} ${toBnNum(endRowDate.getFullYear())}`;
        const spanInfoEl = document.getElementById('ramadan-date-span-info');
        if (spanInfoEl) spanInfoEl.innerText = `সময়কাল: ${startSpanStr} হতে ${endSpanStr}`;

        let rowsHtml = '';
        for (let i = 0; i < 30; i++) {
            const rowDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate() + i);
            const times = calcAstronomicalTimes(rowDate, districtKey);
            const isToday = (rowDate.toDateString() === now.toDateString());

            const rozaNum = toBnNum(i + 1);
            let rozaStage = '';
            let qadrBadge = '';

            if (currentRamadanMode === 'upcoming') {
                if (i < 10) rozaStage = '<span style="font-size:0.68rem; color:#34d399; display:block;">(১ম দশক - রহমত)</span>';
                else if (i < 20) rozaStage = '<span style="font-size:0.68rem; color:#38bdf8; display:block;">(২য় দশক - মাগফিরাত)</span>';
                else rozaStage = '<span style="font-size:0.68rem; color:#f59e0b; display:block;">(৩য় দশক - নাজাত)</span>';

                // Laylatul Qadr odd nights (21, 23, 25, 27, 29 Ramadan)
                if (i === 20 || i === 22 || i === 24 || i === 26 || i === 28) {
                    qadrBadge = '<span class="qadr-badge">✨ কদর বিজোড় রাত</span>';
                }
            } else {
                rozaStage = `<span style="font-size:0.68rem; color:#94a3b8; display:block;">(দিন ${rozaNum})</span>`;
            }

            const dayStr = `${toBnNum(rowDate.getDate())} ${bnMonths[rowDate.getMonth()]}, ${bnDayNames[rowDate.getDay()]}`;

            rowsHtml += `
                <tr class="${isToday ? 'highlight-today' : ''}">
                    <td style="font-weight:700; text-align:center;">
                        <span class="roza-badge">${rozaNum}</span>
                        ${rozaStage}
                        ${qadrBadge}
                    </td>
                    <td>
                        <b>${dayStr}</b>
                        ${isToday ? '<span style="font-size:0.72rem; background:#f59e0b; color:#000; padding:0.1rem 0.4rem; border-radius:4px; margin-left:5px; font-weight:800;">আজ</span>' : ''}
                    </td>
                    <td style="color:#38bdf8; font-weight:700;">${formatTime12(times.sehriEnd, false)} AM</td>
                    <td style="color:#34d399; font-weight:700;">${formatTime12(times.fajr, false)} AM</td>
                    <td>${formatTime12(times.sunrise, false)} AM</td>
                    <td>${formatTime12(times.dhuhr, false)} PM</td>
                    <td>${formatTime12(times.asr, false)} PM</td>
                    <td style="color:#fbbf24; font-weight:800; font-size:1rem;">${formatTime12(times.maghrib, false)} PM</td>
                    <td>${formatTime12(times.isha, false)} PM</td>
                </tr>
            `;
        }

        tbody.innerHTML = rowsHtml;
    }
"""

content = content[:old_js_start] + new_js + content[old_js_end:]

# -----------------------------------------------------------------------------
# 6. Update initPrayerEngine & initPrayerSection to initialize Ramadan Season Dropdown
# -----------------------------------------------------------------------------
init_prayer_target = """    function initPrayerSection() {
        initPrayerDistrictSelect();
        updatePrayerTimes();
        renderRamadanTable(currentPrayerDistrict);
    }

    function initPrayerEngine() {
        initPrayerDistrictSelect();
        updatePrayerTimes();
        if (prayerIntervalId) clearInterval(prayerIntervalId);
        prayerIntervalId = setInterval(updatePrayerTimes, 1000);
    }"""

init_prayer_replacement = """    function initPrayerSection() {
        initPrayerDistrictSelect();
        initRamadanSeasonDropdown();
        updatePrayerTimes();
        renderRamadanTable(currentPrayerDistrict);
    }

    function initPrayerEngine() {
        initPrayerDistrictSelect();
        initRamadanSeasonDropdown();
        updatePrayerTimes();
        renderRamadanTable(currentPrayerDistrict);
        if (prayerIntervalId) clearInterval(prayerIntervalId);
        prayerIntervalId = setInterval(updatePrayerTimes, 1000);
    }"""

assert init_prayer_target in content, "initPrayerEngine target not found"
content = content.replace(init_prayer_target, init_prayer_replacement, 1)

# Write back with explicit UTF-8
with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: index.html updated successfully with dedicated Upcoming Ramadan Calendar and Auto-update engine!")
