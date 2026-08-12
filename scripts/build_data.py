"""Regenerate data/registry.json (auto-fetch) and data/watchlist.json (directory).

Two honest tiers:
  * REGISTRY  -> companies on a real, fetchable system (ATS or the ByteDance
                 adapter). These produce live role rows in README.md.
                 `verified` marks whether the token/config was hand-confirmed;
                 unverified ones just log-and-skip if the token is wrong.
  * WATCHLIST -> the native-Asian-giant tail + S&P 500 APAC branches whose
                 bespoke portals we don't auto-parse. Real careers-page links,
                 rendered to DIRECTORY.md, liveness-checked. This is also where
                 YOU append sources (see CONTRIBUTING).

Run:  python scripts/build_data.py
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# ---------------------------------------------------------------------------
# TIER 1 — AUTO-FETCH REGISTRY
# ats + token (+ per-adapter config). verified=True only where the token was
# confirmed from a real apply URL; False = best-effort, may need fixing.
# ---------------------------------------------------------------------------
REGISTRY = [
    # --- Quant / trading on Greenhouse ---
    {"company": "Optiver", "ats": "greenhouse", "token": "optiver", "verified": True},
    {"company": "Virtu Financial", "ats": "greenhouse", "token": "virtu", "verified": True},
    {"company": "PDT Partners", "ats": "greenhouse", "token": "pdtpartners", "verified": True},
    {"company": "Marshall Wace", "ats": "greenhouse", "token": "mwinternshipprogram", "verified": True},
    {"company": "Chicago Trading Company", "ats": "greenhouse", "token": "chicagotradingcampus", "verified": True},
    {"company": "Hyannisport Research", "ats": "greenhouse", "token": "hyannisportresearch", "verified": True},
    {"company": "DRW", "ats": "greenhouse", "token": "drweng", "verified": False},
    {"company": "Akuna Capital", "ats": "greenhouse", "token": "akunacapital", "verified": False},
    {"company": "Millennium", "ats": "greenhouse", "token": "millennium", "verified": False},
    {"company": "Squarepoint Capital", "ats": "greenhouse", "token": "squarepointcapital", "verified": False},
    {"company": "Flow Traders", "ats": "greenhouse", "token": "flowtraders", "verified": False},
    {"company": "Da Vinci Derivatives", "ats": "greenhouse", "token": "davinciderivatives", "verified": False},
    {"company": "Maven Securities", "ats": "greenhouse", "token": "mavensecurities", "verified": False},
    {"company": "Five Rings", "ats": "greenhouse", "token": "fiverings", "verified": False},
    {"company": "Belvedere Trading", "ats": "greenhouse", "token": "belvederetrading", "verified": False},
    {"company": "Old Mission", "ats": "greenhouse", "token": "oldmissioncapital", "verified": False},

    # --- Tech on Greenhouse / Lever / Ashby (APAC offices) ---
    {"company": "Palantir", "ats": "lever", "token": "palantir", "verified": True},
    {"company": "Stripe", "ats": "greenhouse", "token": "stripe", "verified": False},
    {"company": "Databricks", "ats": "greenhouse", "token": "databricks", "verified": False},
    {"company": "Canva", "ats": "lever", "token": "canva", "verified": False},
    {"company": "Airwallex", "ats": "lever", "token": "airwallex", "verified": False},
    {"company": "Nium", "ats": "greenhouse", "token": "nium", "verified": False},
    {"company": "Western Digital", "ats": "smartrecruiters", "token": "WesternDigital", "verified": True},

    # --- Tier-2 custom: ByteDance platform (huge APAC intern volume) ---
    {"company": "ByteDance", "ats": "bytedance",
     "api_host": "https://jobs.bytedance.com", "web_host": "https://jobs.bytedance.com/en",
     "portal_type": 6, "keyword": "intern", "verified": True},
    {"company": "TikTok", "ats": "bytedance",
     "api_host": "https://careers.tiktok.com", "web_host": "https://careers.tiktok.com",
     "portal_type": 6, "keyword": "intern", "verified": False},
]

# ---------------------------------------------------------------------------
# TIER 3 — WATCH-LIST DIRECTORY  (browse links, not auto-parsed)
# {company, region, url, note}
# ---------------------------------------------------------------------------
def w(company, region, url, note=""):
    return {"company": company, "region": region, "url": url, "note": note}

WATCHLIST = [
    # ---- Quant / trading (bespoke portals) ----
    w("Jane Street", "Hong Kong", "https://www.janestreet.com/join-jane-street/internships/", "HK Summer 2027 QT + SWE live"),
    w("Citadel", "Hong Kong / Singapore", "https://www.citadel.com/careers/internships/"),
    w("Citadel Securities", "Hong Kong / Singapore", "https://www.citadelsecurities.com/careers/"),
    w("Hudson River Trading", "Singapore", "https://www.hudsonrivertrading.com/careers/", "SWE Summer 2027 (SG) live"),
    w("IMC Trading", "Sydney / Hong Kong", "https://www.imc.com/ap/careers"),
    w("Jump Trading", "Singapore", "https://www.jumptrading.com/careers/"),
    w("Two Sigma", "Hong Kong", "https://careers.twosigma.com/careers/"),
    w("SIG Susquehanna", "Sydney / Hong Kong", "https://careers.sig.com/"),
    w("Tower Research Capital", "Singapore", "https://www.tower-research.com/open-positions/"),
    w("WorldQuant", "Singapore / Hong Kong", "https://www.worldquant.com/career-listing/"),
    w("Point72 / Cubist", "Hong Kong / Singapore", "https://careers.point72.com/"),
    w("Balyasny (BAM)", "Hong Kong / Singapore", "https://bambusdev.wd1.myworkdayjobs.com/BAM"),
    w("XTX Markets", "Singapore", "https://www.xtxmarkets.com/careers/"),
    w("Qube Research & Technologies", "Hong Kong / Singapore", "https://www.qube-rt.com/careers"),
    w("G-Research", "Singapore", "https://www.gresearch.com/careers/"),
    w("Radix Trading", "Singapore", "https://radix-trading.com/"),

    # ---- Global big tech (APAC offices) ----
    w("Google", "Singapore / Taipei / Tokyo", "https://www.google.com/about/careers/applications/jobs/results/?employment_type=INTERN", "STEP + SWE Summer 2027"),
    w("Meta", "Singapore", "https://www.metacareers.com/jobs/?is_intern=1"),
    w("Amazon", "Singapore / Tokyo / Bengaluru", "https://www.amazon.jobs/en/search?base_query=intern&loc_query=Singapore"),
    w("Microsoft", "Singapore / Beijing / Bengaluru", "https://careers.microsoft.com/students/us/en/search-results"),
    w("Apple", "Singapore / Shanghai / Tokyo", "https://jobs.apple.com/en-us/search?team=internships-STDNT-INTRN"),
    w("NVIDIA", "Shanghai / Singapore / Taipei", "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"),
    w("Netflix", "Singapore / Tokyo", "https://explore.jobs.netflix.net/careers"),
    w("Uber", "Singapore / Bengaluru", "https://www.uber.com/us/en/careers/list/?query=intern"),
    w("Agoda", "Bangkok / Singapore", "https://careersatagoda.com/"),
    w("Atlassian", "Sydney / Bengaluru", "https://www.atlassian.com/company/careers/early-career"),
    w("Salesforce", "Singapore / Tokyo", "https://careers.salesforce.com/en/jobs/"),
    w("Adobe", "Bengaluru / Singapore", "https://careers.adobe.com/us/en/c/university-jobs"),
    w("SAP", "Singapore / Tokyo", "https://jobs.sap.com/"),
    w("Dyson", "Singapore", "https://careers.dyson.com/en-gb/", "Global HQ in Singapore"),

    # ---- S&P 500 finance (APAC branches) ----
    w("Goldman Sachs", "Hong Kong / Singapore / Tokyo", "https://www.goldmansachs.com/careers/students/programs/"),
    w("Morgan Stanley", "Hong Kong / Singapore", "https://www.morganstanley.com/people-opportunities/students-graduates"),
    w("J.P. Morgan", "Hong Kong / Singapore", "https://careers.jpmorgan.com/global/en/students/programs"),
    w("Citi", "Hong Kong / Singapore", "https://jobs.citi.com/campus"),
    w("Bank of America", "Hong Kong / Singapore", "https://campus.bankofamerica.com/"),
    w("BlackRock", "Hong Kong / Singapore", "https://careers.blackrock.com/early-careers/"),
    w("Bloomberg", "Hong Kong / Singapore / Tokyo", "https://careers.bloomberg.com/job/search?q=intern"),
    w("Mastercard", "Singapore", "https://careers.mastercard.com/us/en/students-and-graduates"),
    w("Visa", "Singapore", "https://corporate.visa.com/en/jobs/"),
    w("PayPal", "Singapore", "https://careers.pypl.com/home/"),
    w("Standard Chartered", "Singapore / Hong Kong", "https://www.sc.com/en/careers/students-graduates/"),
    w("HSBC", "Hong Kong / Singapore", "https://www.hsbc.com/careers/students-and-graduates"),
    w("Nomura", "Tokyo / Hong Kong", "https://www.nomura.com/careers/"),
    w("Macquarie", "Hong Kong / Singapore", "https://www.macquarie.com/careers/students-and-graduates.html"),

    # ---- S&P 500 hardware / semiconductor (big APAC fabs & R&D) ----
    w("Micron", "Singapore / Taiwan / Japan", "https://careers.micron.com/careers", "Large Singapore fabs"),
    w("Intel", "Shanghai / Bengaluru / Penang", "https://jobs.intel.com/en/students-and-graduates"),
    w("Qualcomm", "Hyderabad / Shanghai / Seoul", "https://careers.qualcomm.com/careers"),
    w("AMD", "Singapore / Shanghai / Bengaluru", "https://careers.amd.com/careers-home/jobs"),
    w("Texas Instruments", "Bengaluru / Shanghai", "https://careers.ti.com/"),
    w("Applied Materials", "Singapore / Taiwan", "https://careers.appliedmaterials.com/careers"),
    w("GlobalFoundries", "Singapore", "https://gf.com/careers/", "Singapore is a major hub"),
    w("Seagate", "Singapore / Thailand", "https://www.seagate.com/careers/"),
    w("Dell Technologies", "Singapore / Bengaluru", "https://jobs.dell.com/en/university-relations"),
    w("Cisco", "Bengaluru / Singapore", "https://jobs.cisco.com/jobs/SearchJobs/intern"),
    w("Oracle", "Bengaluru / Singapore", "https://careers.oracle.com/en/sites/jobsearch/"),

    # ---- Native Asian giants (bespoke / login / regional portals) ----
    # CHINA
    w("Tencent", "Shenzhen / Beijing", "https://careers.tencent.com/en-us/search.html"),
    w("Alibaba", "Hangzhou / Beijing", "https://talent.alibaba.com/campus/home"),
    w("Ant Group", "Hangzhou", "https://talent.antgroup.com/campus"),
    w("Baidu", "Beijing", "https://talent.baidu.com/"),
    w("Meituan", "Beijing", "https://zhaopin.meituan.com/"),
    w("JD.com", "Beijing", "https://campus.jd.com/"),
    w("NetEase", "Hangzhou / Guangzhou", "https://campus.163.com/"),
    w("Xiaomi", "Beijing", "https://hr.xiaomi.com/campus"),
    w("Huawei", "Shenzhen", "https://career.huawei.com/reccampportal/portal5/campus-recruitment.html"),
    w("SenseTime", "Hong Kong / Shanghai", "https://www.sensetime.com/en/join-us"),
    w("DiDi", "Beijing", "https://talent.didiglobal.com/"),
    w("Bilibili", "Shanghai", "https://jobs.bilibili.com/campus"),
    # KOREA
    w("Samsung Electronics", "Seoul / Suwon", "https://www.samsungcareers.com/"),
    w("SK Hynix", "Seoul / Icheon", "https://recruit.skhynix.com/"),
    w("LG Electronics", "Seoul", "https://www.lgcareers.com/"),
    w("Naver", "Seongnam", "https://recruit.navercorp.com/"),
    w("Kakao", "Seoul / Jeju", "https://careers.kakao.com/"),
    w("Coupang", "Seoul", "https://www.coupang.jobs/en/"),
    w("Krafton", "Seoul", "https://www.krafton.com/en/careers/"),
    w("Hyundai Motor", "Seoul", "https://careers.hyundai.com/"),
    w("Seoulstart (intl-student aggregator)", "Seoul", "https://seoulstart.com/jobs/internships", "D-10 visa, English-friendly roles"),
    # JAPAN
    w("Rakuten", "Tokyo", "https://rakuten.careers/"),
    w("LY Corporation (LINE / Yahoo)", "Tokyo", "https://www.lycorp.co.jp/en/recruit/"),
    w("Mercari", "Tokyo", "https://careers.mercari.com/"),
    w("Sony", "Tokyo", "https://www.sony.com/en/SonyInfo/Careers/"),
    w("Nintendo", "Kyoto", "https://www.nintendo.co.jp/jobs/"),
    w("SoftBank", "Tokyo", "https://www.softbank.jp/recruit/"),
    w("Preferred Networks", "Tokyo", "https://www.preferred.jp/en/careers/"),
    # SEA / INDIA
    w("Sea / Shopee / Garena", "Singapore", "https://career.sea.com/"),
    w("Grab", "Singapore / Kuala Lumpur / Jakarta", "https://www.grab.careers/en/"),
    w("GoTo (Gojek / Tokopedia)", "Jakarta / Singapore", "https://www.gotocompany.com/en/careers"),
    w("Razer", "Singapore", "https://careers.razer.com/"),
    w("Flipkart", "Bengaluru", "https://www.flipkartcareers.com/"),
    w("Zomato", "Gurugram", "https://www.zomato.com/careers"),
    w("Paytm", "Noida", "https://paytm.com/careers"),
]


def main():
    DATA.mkdir(exist_ok=True)
    (DATA / "registry.json").write_text(
        json.dumps(REGISTRY, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / "watchlist.json").write_text(
        json.dumps(WATCHLIST, indent=2, ensure_ascii=False), encoding="utf-8")
    fetchable = len(REGISTRY)
    verified = sum(1 for r in REGISTRY if r.get("verified"))
    print(f"registry.json : {fetchable} auto-fetch entries ({verified} verified)")
    print(f"watchlist.json: {len(WATCHLIST)} directory entries")


if __name__ == "__main__":
    main()
