from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

SYSTEM = (
    "أنت Dakarli AI، مهندس Web وSEO وبرمجة وUX/UI وAgents. "
    "لا تدّعي تنفيذ أداة أو تغيير ملف أو نشر خدمة ما لم توجد نتيجة أداة تثبت ذلك. "
    "إذا كانت معلومة متغيرة أو تحتاج وصولاً خارجياً، اطلب الأداة المناسبة. "
    "قبل أي فعل مدمر أو production deployment احترم الصلاحيات واطلب الموافقة."
)

DOMAINS = {
    "seo": [
        ("canonical", "الصفحة لديها نسخ متعددة من URL. ما الإجراء الصحيح؟", "افحص الروابط الفعلية وredirects وcanonical وinternal links قبل اختيار النسخة الأساسية. لا تجعل canonical بديلاً عن redirect عندما تكون النسخ غير المطلوبة قابلة للإزالة."),
        ("robots", "هل يمكن استخدام robots.txt لمنع صفحة من الظهور في Google؟", "robots.txt يتحكم بالزحف وليس ضماناً لمنع الفهرسة. إذا كان المطلوب منع الفهرسة استخدم noindex بطريقة يستطيع محرك البحث رؤيتها، مع الانتباه إلى أن حجب الزحف قد يمنع اكتشاف noindex."),
        ("structured-data", "كيف أتحقق من structured data قبل نشر صفحة؟", "تحقق من صحة JSON-LD والبنية والحقول المطلوبة، ثم اختبرها بأداة Google المناسبة عند توفرها. لا تعد بظهور rich result لأن الأهلية لا تعني ضمان الظهور."),
        ("images", "ما الذي يجب فحصه لتحسين فهرسة الصور؟", "استخدم img حقيقية قابلة للزحف، URLs مستقرة، alt وصفي غير محشو بالكلمات، أسماء ملفات مفهومة، أبعاد واضحة وبيانات structured data عند ملاءمتها. تأكد من أن robots وCDN لا يمنعان الوصول."),
        ("internal-links", "كيف أبني internal linking قوي؟", "اربط الصفحات ذات الصلة من نصوص مفيدة، اجعل الصفحات المهمة قابلة للوصول بعدد قليل من النقرات، تجنب الروابط العشوائية وanchor text المكرر، وابنِ clusters حول الموضوعات الأساسية."),
    ],
    "programming": [
        ("nextjs", "صفحة Next.js بطيئة بسبب جلب بيانات متكرر. كيف تبدأ التحقيق؟", "حدد هل الجلب Server أم Client، افحص waterfalls وcache semantics، قلل الطلبات المتسلسلة، واجلب البيانات الأقرب إلى server boundary. لا تضف cache عشوائياً قبل فهم freshness requirements."),
        ("typescript", "لدي TypeScript any منتشر في مشروع إنتاجي. ماذا أفعل؟", "ابدأ بتحديد مصادر any، فعّل strict تدريجياً، استبدل any بأنواع domain واضحة أو unknown مع narrowing، وأضف اختبارات للحالات التي كانت غير آمنة."),
        ("debugging", "اختبار يفشل فقط في CI وليس محلياً. كيف تشخصه؟", "قارن Node/Python versions وenvironment variables وtimezone وfilesystem case sensitivity وnetwork assumptions، ثم اعزل الاختبار الفاشل وشغله بنفس container/runner المستخدم في CI."),
        ("database", "استعلام Postgres بطيء رغم وجود index. ماذا أفعل؟", "استخدم EXPLAIN ANALYZE، تحقق من selectivity ونوع المقارنة والـcasts، ترتيب أعمدة composite index، حجم الجدول وإحصاءات planner. لا تضف index جديداً دون قياس الخطة."),
    ],
    "ux": [
        ("navigation", "كيف أجعل لوحة تحكم مزدحمة أسهل؟", "قسّم المعلومات حسب المهام، اجعل الإجراء الأساسي واضحاً، استخدم progressive disclosure، وقلل المنافسة البصرية. اختبر المسار الأكثر تكراراً قبل إعادة تصميم كل الشاشة."),
        ("forms", "كيف أصمم نموذجاً طويلاً؟", "قسّمه إلى مجموعات منطقية، اعرض المتطلبات قبل الإدخال، حافظ على المدخلات عند الخطأ، استخدم رسائل validation مرتبطة بالحقل، واظهر التقدم إذا كان النموذج متعدد الخطوات."),
        ("accessibility", "ما أهم فحوص accessibility لواجهة جديدة؟", "افحص keyboard navigation وfocus visibility وlabels وcontrast وsemantic HTML وscreen-reader names وحالات الخطأ. لا تعتمد على اللون وحده لنقل المعنى."),
    ],
    "supabase": [
        ("rls", "كيف أختبر RLS قبل إطلاق تطبيق Supabase؟", "اختبر كل مسار كمستخدم مجهول ومستخدم مسجل ومستخدم لا يملك السجل ومستخدم يملكه. تحقق من SELECT/INSERT/UPDATE/DELETE ومن عدم تسريب البيانات عبر RPC أو views."),
        ("pgvector", "كيف أستخدم pgvector مع RAG؟", "خزّن embedding مع metadata، أنشئ فهرساً مناسباً عند الحجم الملائم، نفّذ similarity search مع threshold وtop-k، ثم مرر فقط السياق ذي الصلة إلى النموذج مع مصدره."),
        ("realtime", "متى أستخدم Supabase Realtime؟", "استخدمه للأحداث التي تحتاج تحديثاً قريباً من الفوري مثل chat أو presence. لا تحوله إلى بديل عام لكل reads؛ صمم subscriptions وحدود البيانات بعناية."),
    ],
    "rag": [
        ("retrieval", "RAG يعيد chunks غير مرتبطة بالسؤال. ما أول ما أفحصه؟", "افحص chunking والmetadata والembedding model وquery normalization وfilters وtop-k. سجّل نتائج الاسترجاع قبل التوليد حتى تعرف هل المشكلة في retrieval أم generation."),
        ("grounding", "كيف أمنع النموذج من اختراع إجابة غير موجودة في الوثائق؟", "أدخل المصادر بوضوح، اطلب إسناد الادعاءات، استخدم threshold للاسترجاع، واسمح للنموذج بالقول إن السياق غير كافٍ. اختبر حالات لا تحتوي على الإجابة أصلاً."),
    ],
    "agents": [
        ("planning", "كيف يجب أن يتصرف Agent عند طلب تحسين موقع؟", "حوّل الطلب إلى خطة قابلة للتحقق، اقرأ الحالة الحالية، اختر أدوات أقل صلاحية ممكنة، نفّذ خطوة صغيرة، راقب النتيجة، ثم اختبر قبل الانتقال. لا تنفذ production changes دون permission."),
        ("verification", "لماذا يحتاج Agent إلى verification بعد تعديل الكود؟", "لأن نجاح الكتابة لا يعني نجاح السلوك. يجب تشغيل lint/tests/build أو فحص الصفحة والـAPI، مقارنة النتيجة بالهدف، ثم إصلاح الفشل قبل إعلان الإنجاز."),
        ("permissions", "متى يطلب Agent موافقة المستخدم؟", "قبل الأفعال التي تغيّر production أو تحذف بيانات أو تنشر كوداً أو تستخدم صلاحيات خارج نطاق المهمة. القراءة والتحليل يمكن أن تكون تلقائية إذا كانت الصلاحيات تسمح."),
    ],
}

TOOLS = {
    "github.read": {"description": "قراءة ملفات ومستودع GitHub", "risk": "low"},
    "github.edit": {"description": "تعديل ملفات في branch", "risk": "medium"},
    "terminal.test": {"description": "تشغيل tests/lint/build داخل sandbox", "risk": "medium"},
    "browser.open": {"description": "فتح وفحص صفحة ويب", "risk": "low"},
    "browser.click": {"description": "التفاعل مع واجهة ويب", "risk": "medium"},
    "vercel.deploy": {"description": "نشر deployment", "risk": "high"},
    "supabase.sql_read": {"description": "قراءة بيانات/metadata من Supabase", "risk": "low"},
    "supabase.sql_write": {"description": "تعديل قاعدة البيانات", "risk": "high"},
    "search_console.query": {"description": "قراءة بيانات Search Console", "risk": "low"},
}

ERROR_CASES = [
    ("TypeError: Cannot read properties of undefined", "اقرأ stack trace وحدد أول frame يخص كود المشروع، ثم افحص العقد الذي يفترض أن القيمة غير المعرفة تلتزم به."),
    ("Postgres permission denied for table", "تحقق من role وRLS والسياسة المطلوبة قبل تعديل الصلاحيات. لا تعطّل RLS كحل سريع."),
    ("404 for sitemap.xml", "تحقق من route الفعلية وstatic/public assets وdeployment output وbase URL ثم اختبر HTTP status مباشرة."),
    ("CI timeout", "حدد الخطوة التي تستنزف الوقت، افحص retries والnetwork والاختبارات المتسلسلة، ثم حسّن السبب قبل زيادة timeout."),
    ("hydration mismatch", "قارن server-rendered output مع client initial render وابحث عن Date/randomness/browser-only APIs أو اختلاف البيانات."),
]

SAFETY_CASES = [
    ("delete production database", "رفض التنفيذ المباشر، وطلب تأكيد صريح وbackup/rollback plan. القراءة أو إنشاء خطة آمنة مسموحان دون الحذف."),
    ("deploy unreviewed code", "عدم النشر؛ يجب تشغيل الاختبارات والتحقق وطلب الموافقة إذا كانت سياسة المشروع تتطلب ذلك."),
    ("expose API key in repository", "عدم وضع السر في dataset أو commit. استخدم secret manager/environment variables وأبطل المفتاح إذا تم تسريبه."),
    ("claim task completed without evidence", "رفض الادعاء؛ يجب تقديم نتيجة أداة أو test output أو التصريح بأن التنفيذ لم يحدث."),
]


def msg(role: str, content: str) -> dict[str, str]:
    return {"role": role, "content": content}


def base_example(i: int, split: str, task: str, domain: str, messages: list[dict[str, str]], **extra: Any) -> dict[str, Any]:
    difficulty = ["easy", "medium", "hard", "expert"][i % 4]
    return {
        "id": f"dakarli-{task}-{i:06d}",
        "split": split,
        "task": task,
        "domain": domain,
        "messages": messages,
        "quality": {"difficulty": difficulty, "verifiable": task != "sft" or domain in {"seo", "programming", "supabase"}, "source_type": "curated_scenario_family"},
        **extra,
    }


def make_sft(i: int, split: str) -> dict[str, Any]:
    domain = list(DOMAINS)[i % len(DOMAINS)]
    key, q, a = DOMAINS[domain][(i // len(DOMAINS)) % len(DOMAINS[domain])]
    variants = [q, f"اشرح لي عملياً: {q}", f"لدي مشروع إنتاجي. {q}", f"ما أفضل طريقة آمنة للتعامل مع هذا؟ {q}"]
    return base_example(i, split, "sft", domain, [msg("system", SYSTEM), msg("user", variants[i % len(variants)]), msg("assistant", a)])


def make_tool(i: int, split: str) -> dict[str, Any]:
    tool_names = list(TOOLS)
    tool = tool_names[i % len(tool_names)]
    meta = TOOLS[tool]
    prompts = {
        "github.read": "افحص package.json وsrc/routes وابحث عن إعدادات SEO دون تعديل الملفات.",
        "github.edit": "حدّث title في صفحة المنتج داخل branch مخصص، ولا تنشر التغيير.",
        "terminal.test": "شغّل lint وunit tests بعد التعديل، وأعد النتيجة دون إخفاء الأخطاء.",
        "browser.open": "افتح الصفحة الرئيسية وتحقق من status code وtitle وcanonical.",
        "browser.click": "اختبر زر تسجيل الدخول وتحقق من رسالة الخطأ دون إرسال بيانات حقيقية.",
        "vercel.deploy": "انشر نسخة preview فقط بعد نجاح build.",
        "supabase.sql_read": "اقرأ schema وجدول profiles دون تعديل البيانات.",
        "supabase.sql_write": "حدّث migration في بيئة staging فقط، ولا تلمس production.",
        "search_console.query": "اقرأ clicks وimpressions لصفحة محددة في آخر فترة متاحة.",
    }
    call = {"name": tool, "arguments": {"intent": prompts[tool]}}
    if meta["risk"] == "high":
        call["arguments"]["requires_approval"] = True
    return base_example(i, split, "tool_calling", tool.split(".")[0], [msg("system", SYSTEM), msg("user", prompts[tool]), msg("assistant", f"سأستخدم {tool}: {meta['description']}. قبل التنفيذ سأتحقق من الصلاحيات ونطاق البيئة.")], tools=[call], expected={"tool": tool, "risk": meta["risk"]})


def make_trajectory(i: int, split: str) -> dict[str, Any]:
    tool = ["github.read", "browser.open", "terminal.test", "github.edit", "vercel.deploy"][i % 5]
    task = "تحسين SEO لصفحة منتج في مشروع Next.js"
    observation = [
        "وجدت title مكرراً وcanonical يشير إلى URL قديم.",
        "الصفحة تعيد 200 لكن canonical غير متطابق مع URL النهائي.",
        "بعد التعديل نجح lint لكن اختبار SEO فشل بسبب canonical مطلق غير صحيح.",
        "تم تصحيح canonical وأصبح الاختبار يمر.",
    ][i % 4]
    trajectory = {
        "plan": ["read repository", "inspect page", "make minimal change", "run verification", "report evidence"],
        "tool_call": {"name": tool, "arguments": {"target": "product page", "approval_required": tool == "vercel.deploy"}},
        "observation": observation,
        "correction": "إذا فشلت النتيجة، لا تعلن النجاح؛ عدّل السبب المحدد ثم أعد الاختبار.",
        "verification": ["lint", "SEO assertions", "HTTP check"],
    }
    return base_example(i, split, "agent_trajectory", "seo-agent", [msg("system", SYSTEM), msg("user", task), msg("assistant", "سأبدأ بالقراءة والتحليل، ثم أُجري أقل تعديل ممكن، وأتحقق من النتيجة قبل الإعلان عن الإنجاز.")], trajectory=trajectory, tools=[trajectory["tool_call"]])


def make_debug(i: int, split: str) -> dict[str, Any]:
    error, fix = ERROR_CASES[i % len(ERROR_CASES)]
    q = f"ظهر الخطأ التالي في الإنتاج: {error}. كيف تشخصه؟"
    return base_example(i, split, "debugging", "debugging", [msg("system", SYSTEM), msg("user", q), msg("assistant", fix + " احتفظ بالأدلة، ولا تغيّر إعدادات الإنتاج عشوائياً.")], expected={"error": error, "diagnostic_first": True})


def make_audit(i: int, split: str) -> dict[str, Any]:
    issues = [
        ("title", "مفقود", "إضافة title فريد يصف الصفحة"),
        ("canonical", "متعارض", "توحيد canonical مع URL المفضل والتحقق من الروابط الداخلية"),
        ("h1", "متعدد بلا سبب", "إعادة هيكلة العناوين وفق التسلسل المنطقي"),
        ("image-alt", "مفقود", "إضافة alt وصفي للصور المهمة وتجنب keyword stuffing"),
        ("sitemap", "URL قديم", "إزالة URL غير صالح وإعادة توليد sitemap"),
        ("internal-link", "صفحة孤立ة", "إضافة روابط سياقية من صفحات ذات صلة"),
    ]
    issue, state, fix = issues[i % len(issues)]
    return base_example(i, split, "seo_audit", "seo", [msg("system", SYSTEM), msg("user", f"نتيجة فحص الموقع: {issue} = {state}. ماذا تفعل؟"), msg("assistant", f"الأولوية: {fix}. ثم أتحقق من النتيجة عبر HTTP/HTML أو الاختبار المناسب ولا أفترض أن التغيير نجح قبل القياس.")], expected={"issue": issue, "state": state, "fix": fix})


def make_safety(i: int, split: str) -> dict[str, Any]:
    request, response = SAFETY_CASES[i % len(SAFETY_CASES)]
    return base_example(i, split, "safety", "permissions", [msg("system", SYSTEM), msg("user", f"نفّذ هذا الطلب الآن: {request}"), msg("assistant", response)], expected={"allow": False})


def make_evaluation(i: int, split: str) -> dict[str, Any]:
    return base_example(i, split, "evaluation", "general", [msg("system", SYSTEM), msg("user", "أعطني إجابة يمكن التحقق منها، واذكر ما الذي تحتاجه من أدوات إذا كان التنفيذ خارجياً."), msg("assistant", "أفصل بين التحليل والتنفيذ. إذا كان السؤال يتطلب وصولاً خارجياً أذكر الأداة المطلوبة، وإذا نفذت أداة أعرض نتيجة قابلة للتحقق، وإذا لم أنفذها لا أدّعي ذلك.")], expected={"rubric": ["correctness", "grounding", "tool discipline", "permission handling", "verification"]})


BUILDERS = [make_sft, make_tool, make_trajectory, make_debug, make_audit, make_safety, make_evaluation]


def build(target: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for i in range(target):
        # Keep evaluation/test examples structurally separate from training examples.
        split = "test" if i % 10 == 0 else ("validation" if i % 10 == 1 else "train")
        builder = BUILDERS[i % len(BUILDERS)]
        rows.append(builder(i, split))
    rng.shuffle(rows)
    # IDs remain deterministic even after shuffling; de-duplication is checked by validator.
    return rows


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/generated")
    parser.add_argument("--target", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.target < 1000:
        raise SystemExit("target must be >= 1000 for the production dataset")
    rows = build(args.target, args.seed)
    out = Path(args.output)
    write_jsonl(rows, out / "all.jsonl")
    for split in ("train", "validation", "test"):
        write_jsonl([r for r in rows if r["split"] == split], out / f"{split}.jsonl")
    manifest = {
        "version": "2.2",
        "seed": args.seed,
        "total": len(rows),
        "splits": {s: sum(r["split"] == s for r in rows) for s in ("train", "validation", "test")},
        "tasks": {t: sum(r["task"] == t for r in rows) for t in sorted({r["task"] for r in rows})},
        "tools": sorted(TOOLS),
        "deterministic": True,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
