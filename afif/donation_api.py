# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from afif import dibsy


def _localize(text, lang):
	"""Resolve a translatable field's value for the given site language.

	Program/Project titles & descriptions use Frappe's per-string "Translation"
	doctype (translatable: 1 fields). We look up the stored translation for the
	requested language and fall back to the field's own value when there is
	none - which is correct whichever language that raw value happens to be
	authored in.
	"""
	if not text:
		return text
	translated = frappe.db.get_value("Translation", {"source_text": text, "language": lang}, "translated_text")
	return translated or text


def _normalize_lang(lang):
	return lang if lang in ("ar", "en") else "ar"


@frappe.whitelist(allow_guest=True)
def get_programs(lang=None):
	lang = _normalize_lang(lang)

	programs = frappe.get_all(
		"Donation Program",
		filters={"published": 1},
		fields=["name", "title", "intro"],
		order_by="creation desc",
		ignore_permissions=True,
	)
	for program in programs:
		program["title"] = _localize(program["title"], lang)
		program["intro"] = _localize(program["intro"], lang)
	return programs


@frappe.whitelist(allow_guest=True)
def get_projects(program, lang=None):
	lang = _normalize_lang(lang)

	if not frappe.db.exists("Donation Program", {"name": program, "published": 1}):
		frappe.throw(_("Donation Program not found"), frappe.DoesNotExistError)

	projects = frappe.get_all(
		"Donation Project",
		filters={"program": program, "published": 1},
		fields=[
			"name",
			"title",
			"quote",
			"body",
			"required_amount",
			"donated_amount",
			"percentage",
		],
		order_by="creation desc",
		ignore_permissions=True,
	)
	for project in projects:
		project["title"] = _localize(project["title"], lang)
		project["quote"] = _localize(project["quote"], lang)
		project["body"] = _localize(project["body"], lang)
	return projects


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=60 * 60)
def create_donation(donation_project, amount, donor_name=None, donor_mobile=None, donor_email=None):
	project = frappe.db.get_value(
		"Donation Project",
		{"name": donation_project, "published": 1},
		["name"],
		as_dict=True,
	)
	if not project:
		frappe.throw(_("Donation Project not found"), frappe.DoesNotExistError)

	amount = frappe.utils.flt(amount)
	if amount <= 0:
		frappe.throw(_("Amount must be greater than 0"))

	donation = frappe.get_doc({
		"doctype": "Donation",
		"donation_project": project.name,
		"amount": amount,
		"donor_name": donor_name,
		"donor_mobile": donor_mobile,
		"donor_email": donor_email,
	})
	donation.insert(ignore_permissions=True)
	frappe.db.commit()

	checkout = dibsy.create_payment(donation)

	return {
		"reference_id": donation.reference_id,
		"amount": donation.amount,
		"currency": donation.currency,
		"payment_url": checkout["payment_url"],
	}


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=30, seconds=60 * 60)
def get_status(reference_id):
	donation = frappe.db.get_value(
		"Donation",
		{"reference_id": reference_id},
		["payment_status", "amount", "currency", "donor_name"],
		as_dict=True,
	)
	if not donation:
		frappe.throw(_("Donation not found"), frappe.DoesNotExistError)

	return donation


def _set_translation(source_text, translated_text, language="en"):
	if frappe.db.exists("Translation", {"source_text": source_text, "language": language}):
		return
	frappe.get_doc({
		"doctype": "Translation",
		"language": language,
		"source_text": source_text,
		"translated_text": translated_text,
	}).insert(ignore_permissions=True)


def seed_test_donation_data():
	programs = [
		{
			"title": "التعليم",
			"title_en": "Education",
			"intro": (
				"مساهمتك في مساعدة طلاب العلم هي الاجر الباقي والصدقة الجارية التي تتناقلها الاجيال وتزيد لك في الاجر.\n"
				"إذا مات ابن آدم انقطع عمله إلا من ثلاث: صدقة جارية، أو علم يُنتفع به، أو ولد صالح يدعو له (رواه مسلم)"
			),
			"intro_en": (
				"Your contribution to helping students of knowledge is a lasting reward and an ongoing charity passed down "
				"through generations, increasing your reward.\n"
				"\"When a person dies, their deeds end except for three: ongoing charity, beneficial knowledge, or a "
				"righteous child who prays for them\" (Narrated by Muslim)"
			),
			"projects": [
				{
					"title": "دعم الطلاب المتسربين عن التعليم",
					"title_en": "Supporting Students Who Have Dropped Out of Education",
					"body": (
						"حال الفقر وقلة ذات اليد دون الحاق أبنائهم بالمدارس، احرص على صدقة جارية لك بالمساهمة في "
						"تعليم الطلاب الفقراء والمتعففين"
					),
					"body_en": (
						"Poverty and limited means have prevented some families from enrolling their children in "
						"school. Secure an ongoing charity for yourself by contributing to the education of poor "
						"and underprivileged students."
					),
				},
				{
					"title": "حقيبة مدرسية",
					"title_en": "School Bag",
					"body": (
						"تبرعك يساعد أسرة متعففة في تكاليف اللوازم الدراسية لأبنائها\n"
						"تقدم لهم مساعدتك في شكل كوبون مشتريات من أحد متاجر القرطاسية في قطر"
					),
					"body_en": (
						"Your donation helps an underprivileged family cover the cost of school supplies for their "
						"children.\n"
						"Your help is provided to them as a purchase voucher from a stationery store in Qatar."
					),
				},
				{
					"title": "رسوم دراسية ومواصلات",
					"title_en": "Tuition Fees and Transportation",
					"body": (
						"أثقلتهم الرسوم الدراسية أعنهم لتساهم في الحد من تسرب أطفال من مقاعد الدراسة\n"
						"يتم دفع تبرعك بالكامل لصالح المدرسة مباشرة لسداد الرسوم المستحقة"
					),
					"body_en": (
						"Tuition fees have become a heavy burden for them — help them and contribute to reducing "
						"children dropping out of school.\n"
						"Your donation is paid in full directly to the school to settle the outstanding fees."
					),
				},
				{
					"title": "دعم طلاب الجامعة",
					"title_en": "Supporting University Students",
					"body": (
						"كم طالب مجتهد وصل الى أبواب الجامعة ثم توقف حلمه فقط لأن الرسوم أكبر من قدرته ولأن الحلم لا "
						"يجب أن يقف بسبب المال، أطلقنا برنامج المنح الجامعية ليكون الجسر بين الطموح والواقع، ساهم معنا "
						"بتبرعك لتساعد طالباً على الاستمرار في دراسته ولتحفظ حلماً من الضياع ولنساهم معاً في بناء "
						"انسان متعلم قادر ونافع لمجتمعه."
					),
					"body_en": (
						"How many diligent students have reached the doors of university only for their dream to "
						"stop simply because the fees exceeded their means — and because a dream should never be "
						"halted by money. We launched the university scholarship program to be the bridge between "
						"ambition and reality. Contribute with your donation to help a student continue their "
						"studies, preserve a dream from being lost, and join us in building an educated person who "
						"is capable and beneficial to their community."
					),
				},
			],
		},
		{
			"title": "صحة",
			"title_en": "Health",
			"intro": (
				"تعتمد مؤسسة عفيف الخيرية في استراتيجيتها بالتوسع في جملة من المشاريع في مجال الصحة التي تخدم بعضها "
				"بعضاً وتقدم فرصاً لحياة بدون ألم.\n"
				"كن جزءاً من ذلك البلسم وخفف من معاناة من يتألم وأعد نور الأمل لمن خفت لديهم."
			),
			"intro_en": (
				"Afif Charity Foundation's strategy relies on expanding a range of health projects that complement "
				"one another and offer opportunities for a life without pain.\n"
				"Be part of that remedy — ease the suffering of those in pain and restore the light of hope to "
				"those who have lost it."
			),
			"projects": [
				{
					"title": "رسوم مريض غسيل كلوي دموي",
					"title_en": "Hemodialysis Patient Fees",
					"body": (
						"مرضى الغسيل الكلوي لا يطلبون الكثير،،، فقط فرصة ليعيشوا بكرامة\n"
						"يتم تحويل تبرعك لصالح جلسات مرضى الغسيل الكلوي الدموي فإنك بهذا التبرع تزرع الطمأنينة في قلب "
						"أنهكه المرض"
					),
					"body_en": (
						"Dialysis patients don't ask for much — just a chance to live with dignity.\n"
						"Your donation is transferred to cover hemodialysis sessions; with this donation you plant "
						"reassurance in a heart exhausted by illness."
					),
				},
				{
					"title": "رسوم مريض قلب (عملية جراحية)",
					"title_en": "Heart Patient Fees (Surgical Operation)",
					"body": (
						"تكاليف عملية جراحية لمريض قلب يحمي أسرة من الضياع\n"
						"مساهمتك تصل لحساب مستحقيها بشكل مباشر في مؤسسة حمد الطبية"
					),
					"body_en": (
						"Covering the cost of a heart surgery protects a family from ruin.\n"
						"Your contribution reaches its recipient directly at Hamad Medical Corporation."
					),
				},
				{
					"title": "أطفال مرضى مستشفى سدرة",
					"title_en": "Sick Children at Sidra Hospital",
					"body": (
						"في أروقة مستشفى سدرة هناك أطفال لا يلعبون في الساحات بل يقضون أيامهم بين الأسرة البيضاء "
						"والأجهزة الطبية، يبتسمون رغم الألم ويحلمون أن يعودوا أطفالاً كما يجب أن يكونوا، بتبرعك لهم "
						"تساهم في علاج جسد صغير وتزرع أملاً في قلب أم لا تنام"
					),
					"body_en": (
						"In the corridors of Sidra Hospital there are children who don't play in playgrounds, but "
						"spend their days among white beds and medical equipment. They smile despite the pain and "
						"dream of becoming children again as they should be. With your donation to them, you "
						"contribute to treating a small body and plant hope in the heart of a mother who cannot "
						"sleep."
					),
				},
				{
					"title": "كراسي متحركة",
					"title_en": "Wheelchairs",
					"body": (
						"هناك أشخاص من ذوي الإعاقة حُبسوا في بيوتهم بسبب عدم توفر كرسي متحرك مناسب\n"
						"ساهم وغير حياتهم بتبرعك السخي"
					),
					"body_en": (
						"There are people with disabilities confined to their homes because a suitable wheelchair "
						"isn't available.\n"
						"Contribute and change their lives with your generous donation."
					),
				},
			],
		},
		{
			"title": "اجتماعي",
			"title_en": "Social",
			"intro": (
				"نسعى في مؤسسة عفيف الخيرية لتأمين والمساهمة في سد احتياجات الأسر المستهدفة من المواد الغذائية "
				"الأساسية للفئات الأشد ضعفاً وحاجة، وضمان سد حاجاتهم لعيش كريم آمن وصحة ورفاه قادم."
			),
			"intro_en": (
				"At Afif Charity Foundation, we work to secure and help meet the basic food needs of targeted "
				"families among the most vulnerable and in-need groups, ensuring their needs are met for a "
				"dignified, secure life and future health and well-being."
			),
			"projects": [
				{
					"title": "دعم الأسر المتعففة داخل قطر",
					"title_en": "Supporting Underprivileged Families Inside Qatar",
					"body": (
						"عن أنس بن مالك رضي الله عنه قال: قال رسول الله صلى الله عليه وسلم: ما آمن بي من بات شبعان "
						"وجاره جائع إلى جنبه وهو يعلم به - سد حاجتهم\n"
						"يتم تحويل تبرعك بالكامل لصالح الأسرة مباشرة في شكل مساعدات مالية مقطوعة - المعيشة، كوبونات "
						"شرائية."
					),
					"body_en": (
						"Anas ibn Malik (may Allah be pleased with him) narrated that the Messenger of Allah (peace "
						"be upon him) said: \"He does not believe in me whoever sleeps full while his neighbor "
						"beside him is hungry and he knows it\" — meet their need.\n"
						"Your donation is transferred in full directly to the family in the form of a one-time "
						"financial assistance — living expenses, purchase vouchers."
					),
				},
				{
					"title": "غارمين",
					"title_en": "Debtors (Gharimeen)",
					"body": (
						"يندرج ضمن البرامج الاجتماعية بند المتعثرين والغارمين، ونهدف في مؤسسة عفيف الخيرية إلى "
						"تفريج تلك الكرب التي تشكل خطراً حقيقياً على هدم نسيج المجتمع وتفكك وحدة الأسرة ممن وقعوا في "
						"قبضة ديون لم يتمكنوا من سدادها.\n"
						"\"من نفس عن مؤمن كربة من كرب الدنيا، نفس الله عنه كربة من كرب يوم القيامة\"\n"
						"وقعوا في مصائد هموم الليل وذل النهار - نفس كربة بالتفريج على غارم وآخر متعثر في دفع الإيجار\n"
						"يتم تحويل عطائك للجهة المطالبة بالكامل"
					),
					"body_en": (
						"Among the social programs is the category of those in financial distress and debtors. At "
						"Afif Charity Foundation, we aim to relieve the hardship that poses a real threat to the "
						"fabric of society and the breakdown of family unity for those caught in the grip of debts "
						"they were unable to repay.\n"
						"\"Whoever relieves a believer's distress in this world, Allah will relieve his distress on "
						"the Day of Judgment\"\n"
						"They have fallen into the traps of sleepless nights and daytime humiliation — relieve the "
						"distress of a debtor or someone struggling to pay rent.\n"
						"Your gift is transferred to the claiming party in full."
					),
				},
			],
		},
		{
			"title": "التدريب والتمكين",
			"title_en": "Training and Empowerment",
			"intro": "الشباب ليسوا مشكلة تنتظر الحل بل طاقة تنتظر الفرصة.",
			"intro_en": "Young people are not a problem waiting to be solved, but energy waiting for an opportunity.",
			"projects": [
				{
					"title": "التدريب والتمكين",
					"title_en": "Training and Empowerment",
					"body": (
						"فكرة وتدريب أو فرصة حقيقية قد تغير مسار شاب ومن ثم تغير مجتمعاً كاملاً، بدعمك لبرامج تمكين "
						"الشباب تفتح باب التعليم والتدريب وتحول الطموح إلى إنجاز وتصنع قائداً ورائداً مبتكراً."
					),
					"body_en": (
						"An idea, training, or a real opportunity can change the course of a young person's life, "
						"and in turn change an entire community. By supporting youth empowerment programs, you "
						"open the door to education and training, turn ambition into achievement, and shape an "
						"innovative leader and pioneer."
					),
				},
			],
		},
		{
			"title": "مشاريع موسمية",
			"title_en": "Seasonal Projects",
			"intro": (
				"إعانة المتعففين والفقراء بكفهم السؤال، وتجسيد الاحتفالات والمواسم والمناسبات في صور برامج ومشاريع "
				"موسمية تبقي جسور الخير متواصلة وممتدة طوال العام مع تلك الأسر.\n"
				"أسعدهم بلفتة كريمة منك لتكتمل بها فرحة تلك المواسم في قلوبهم."
			),
			"intro_en": (
				"Supporting the poor and needy so they need not ask others, and giving form to celebrations, "
				"seasons, and occasions through seasonal programs and projects that keep the bridges of charity "
				"connected and extended throughout the year with these families.\n"
				"Bring them joy with a generous gesture from you, so their happiness in these seasons is complete."
			),
			"projects": [
				{
					"title": "كوبونات سلال غذائية (رمضان)",
					"title_en": "Food Basket Vouchers (Ramadan)",
					"body": (
						"قال رسول الله صلى الله عليه وسلم: \"أحب الأعمال إلى الله سرورٌ تدخله على مسلم\"\n"
						"في رمضان ليس الجميع يجد مائدة عامرة، لكن القلوب العامرة بالعطاء تجعل الخير يصل للجميع، "
						"فهناك أسر تنتظر سلة رمضانية تخفف عنهم هم السؤال وتمنحهم شعور الكرامة في شهر الرحمة، تبرعك "
						"يؤمن الغذاء لأسرة محتاجة وتدخل السرور على قلوب صائمة وتشاركهم بركة الشهر الفضيل"
					),
					"body_en": (
						"The Messenger of Allah (peace be upon him) said: \"The most beloved deeds to Allah are the "
						"joy you bring to a Muslim.\"\n"
						"In Ramadan, not everyone finds a bountiful table, but hearts full of generosity make "
						"goodness reach everyone. There are families waiting for a Ramadan basket that spares them "
						"the need to ask and gives them a sense of dignity in the month of mercy. Your donation "
						"secures food for a needy family, brings joy to fasting hearts, and lets you share in the "
						"blessing of the holy month."
					),
				},
				{
					"title": "سقيا ماء",
					"title_en": "Providing Drinking Water",
					"body": (
						"عن أبي هريرة رضي الله عنه قال: \"ليس صدقة أعظم أجراً من ماء\"\n"
						"قيمة لا تذكر وأثر يبقى ويكبر\n"
						"يتم تزويد مبردات المياه الموزعة في المساجد والأحياء بقوارير مياه ليستفيد منها عابر السبيل "
						"والمارة"
					),
					"body_en": (
						"Abu Hurairah (may Allah be pleased with him) narrated: \"There is no charity greater in "
						"reward than water.\"\n"
						"A negligible cost, yet an impact that endures and grows.\n"
						"Water coolers distributed in mosques and neighborhoods are supplied with bottled water for "
						"passersby to benefit from."
					),
				},
				{
					"title": "عمرة لغير المقتدرين",
					"title_en": "Umrah for Those Who Cannot Afford It",
					"body": (
						"عيون مشتاقة لبيت الله الحرام، حال بينهم وبين بلوغه قلة ذات اليد، ساهم واكفل معتمر يدعو لك "
						"ويبقى الأجر والأثر، تبرعك ينفق بالكامل على المعتمرين من خلال شركات حجيج معتمدة."
					),
					"body_en": (
						"Eyes longing for the sacred House of Allah, kept from reaching it by limited means. "
						"Contribute and sponsor a pilgrim who will pray for you, leaving behind lasting reward and "
						"impact. Your donation is spent in full on the pilgrims through accredited Hajj and Umrah "
						"companies."
					),
				},
			],
		},
	]

	for program in programs:
		program_name = frappe.db.get_value("Donation Program", {"title": program["title"]})
		if not program_name:
			program_doc = frappe.get_doc({
				"doctype": "Donation Program",
				"title": program["title"],
				"intro": program["intro"],
				"published": 1,
			})
			program_doc.insert(ignore_permissions=True)
			program_name = program_doc.name

		_set_translation(program["title"], program["title_en"])
		_set_translation(program["intro"], program["intro_en"])

		for project in program["projects"]:
			if not frappe.db.exists("Donation Project", {"title": project["title"], "program": program_name}):
				frappe.get_doc({
					"doctype": "Donation Project",
					"program": program_name,
					"title": project["title"],
					"body": project["body"],
					"published": 1,
					"required_amount": 10000,
					"donated_amount": 0,
				}).insert(ignore_permissions=True)

			_set_translation(project["title"], project["title_en"])
			_set_translation(project["body"], project["body_en"])

	frappe.db.commit()
	return "seeded"
