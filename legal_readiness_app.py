import streamlit as st
from typing import Dict, List, Tuple

st.set_page_config(
    page_title="Warfighter Legal Readiness",
    page_icon="⚖️",
    layout="wide",
)

# ---------- Configuration ----------
LEGAL_LOCATOR_URL = "https://legalassistance.law.af.mil/"
MILITARY_ONESOURCE_URL = "https://www.militaryonesource.mil/financial-legal/legal/"
USERRA_URL = "https://www.dol.gov/agencies/vets/programs/userra"
SCRA_URL = "https://www.justice.gov/servicemembers/servicemembers-civil-relief-act-scra"
SGLI_URL = "https://www.benefits.va.gov/insurance/sgli-increase-faqs.asp"
DEATH_GRATUITY_URL = "https://militarypay.defense.gov/benefits/death-gratuity/"

SECTIONS = [
    "Welcome",
    "About You",
    "Wills & Estate Planning",
    "Asset Check",
    "Reemployment Rights (USERRA)",
    "Civil Lawsuits & Consumer Protection (SCRA)",
    "Military Administrative Matters",
    "Immigration",
    "Powers of Attorney",
    "Other Legal Questions",
    "Dwell Time",
    "Results",
]

ENCOURAGEMENT = {
    1: "You are off to a strong start.",
    3: "Nice work — you are making steady progress.",
    5: "You are about halfway through.",
    7: "Keep going — your personalized checklist is taking shape.",
    9: "Just a few more questions.",
    10: "Almost done — your next steps are coming up.",
}

# ---------- Helpers ----------
def ensure_state() -> None:
    defaults = {
        "step": 0,
        "answers": {},
        "issues": [],
        "next_steps": [],
        "documents": [],
        "resources": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_answer(key: str, value):
    st.session_state.answers[key] = value


def get_answer(key: str, default=None):
    return st.session_state.answers.get(key, default)


def go_next():
    st.session_state.step = min(st.session_state.step + 1, len(SECTIONS) - 1)


def go_prev():
    st.session_state.step = max(st.session_state.step - 1, 0)


def nav_buttons(show_back: bool = True, show_next: bool = True, next_label: str = "Next"):
    c1, c2, c3 = st.columns([1, 5, 1])
    with c1:
        if show_back and st.button("← Back"):
            go_prev()
            st.rerun()
    with c3:
        if show_next and st.button(next_label):
            go_next()
            st.rerun()


def info_box(title: str, body: str):
    with st.expander(title):
        st.write(body)


def add_issue(level: str, code: str, label: str, why: str):
    st.session_state.issues.append({
        "level": level,
        "code": code,
        "label": label,
        "why": why,
    })


def add_step(text: str):
    if text not in st.session_state.next_steps:
        st.session_state.next_steps.append(text)


def add_doc(text: str):
    if text not in st.session_state.documents:
        st.session_state.documents.append(text)


def add_resource(label: str, url: str):
    item = {"label": label, "url": url}
    if item not in st.session_state.resources:
        st.session_state.resources.append(item)


def analyze_answers() -> Tuple[str, List[Dict], List[str], List[str], List[Dict]]:
    issues: List[Dict] = []
    steps: List[str] = []
    docs: List[str] = []
    resources: List[Dict] = []

    def issue(level: str, code: str, label: str, why: str):
        issues.append({"level": level, "code": code, "label": label, "why": why})

    def step(text: str):
        if text not in steps:
            steps.append(text)

    def doc(text: str):
        if text not in docs:
            docs.append(text)

    def resource(label: str, url: str):
        item = {"label": label, "url": url}
        if item not in resources:
            resources.append(item)

    a = st.session_state.answers

    # Estate and family
    if a.get("married") == "Yes" and a.get("separated_divorce") == "Yes":
        issue("red", "marital_change", "Marital status change during estate planning", "A current separation or divorce can affect how a will should be written and reviewed before deployment.")
        step("Schedule an appointment with legal assistance to review or prepare a will.")
        doc("Any separation, divorce, or court paperwork.")

    if a.get("has_children") == "Yes" and a.get("custody_dispute") == "Yes":
        issue("red", "custody_dispute", "Custody or support dispute", "Unresolved family law issues can affect caregiving, compliance with court orders, and deployment readiness.")
        step("Gather custody, support, and parenting-order documents.")
        step("Schedule an appointment with legal assistance to discuss family law and estate planning.")
        doc("Custody orders, support orders, divorce decrees, and parenting plans.")

    if a.get("children_special_needs") == "Yes":
        issue("red", "special_needs_guardianship", "Child or dependent may need guardianship planning", "Planning ahead can reduce delays and uncertainty if a child has special needs or may require a guardian.")
        step("Discuss guardianship and estate-planning documents with legal assistance.")
        doc("Any guardianship, medical, school, or special-needs planning documents.")

    if a.get("all_children_shared_spouse") == "No":
        issue("yellow", "blended_family", "Blended family estate-planning issue", "State intestacy rules may not match your wishes in a blended-family situation.")
        step("Review your estate plan to make sure it reflects your wishes for all children and family members.")

    if a.get("spouse_deploying") == "Yes":
        issue("yellow", "dual_deploying", "Both spouses deploying", "Dual deployment may increase the need for clear estate planning and care arrangements.")
        step("Review who should receive your property and who should care for dependents during deployment.")

    if a.get("ever_married_other_parent") == "Yes":
        issue("yellow", "prior_marriage", "Prior marriage may affect current estate plan", "An older will may no longer match your current wishes.")
        step("Review any older will or estate-planning documents for updates.")
        doc("Your current or prior will, if available.")

    if a.get("family_care_plan_complete") == "No":
        level = "red" if a.get("dependents") == "Yes" else "yellow"
        issue(level, "family_care", "Family Care Plan may be incomplete", "Planning ahead helps ensure dependents are cared for and reduces stress during deployment.")
        step("Complete or update your Family Care Plan with your unit.")
        doc("Any existing Family Care Plan materials and caregiver information.")

    if a.get("disinherit_someone") == "Yes":
        issue("yellow", "disinherit", "You want to disinherit a family member", "This is an estate-planning issue that should be documented clearly in a will.")
        step("Discuss your distribution wishes with an attorney.")

    if a.get("healthcare_poa") == "No":
        issue("yellow", "hc_poa", "No healthcare power of attorney identified", "If you become seriously ill or incapacitated, a trusted person may need authority to make healthcare decisions for you.")
        step("Consider preparing a healthcare power of attorney.")

    # Asset check
    if a.get("owns_real_estate") == "Yes":
        issue("yellow", "real_estate", "Real property owned", "Owning a house or land can make estate planning more important.")
        step("Review how your house or land is titled and whether your estate documents match your wishes.")
        doc("Property deeds or mortgage records, if available.")

    if a.get("specific_gifts") == "Yes":
        issue("yellow", "specific_gifts", "Specific gifts planned", "A will may be the best place to document gifts to a friend, relative, or charity.")
        step("Make a list of specific gifts you want included in your estate plan.")

    if a.get("assets_over_1m") == "Yes":
        issue("yellow", "high_value_estate", "High-value estate", "A larger estate may require more complex planning beyond routine legal assistance.")
        step("Consider legal assistance first, then ask whether a civilian estate-planning specialist is needed.")

    if a.get("owns_business") == "Yes":
        issue("yellow", "business_owner", "Business ownership affects estate planning", "Business succession and transfer issues may require more specialized planning.")
        step("Gather business formation or ownership records for your appointment.")
        doc("Business ownership, formation, or operating documents.")

    if a.get("assets_in_trust") == "Yes":
        issue("yellow", "trust_assets", "Assets held in a trust", "Trust assets may operate differently from a will and should be reviewed together.")
        step("Bring any trust documents to legal assistance for review.")
        doc("Trust documents and related schedules, if available.")

    # USERRA
    if a.get("component") == "Reserve / National Guard" and a.get("civilian_job") == "Yes":
        if a.get("employer_concern") == "Yes":
            issue("red", "userra", "Possible USERRA problem with civilian employer", "USERRA may protect your return-to-work rights and benefits.")
            step("Document your communications with your employer.")
            step("Schedule an appointment with legal assistance to discuss USERRA rights.")
            doc("Any written communications with your employer about deployment or reemployment.")
            resource("USERRA information (U.S. Department of Labor)", USERRA_URL)
        elif a.get("told_employer") == "No":
            issue("yellow", "employer_notice", "Employer notice may still be needed", "Early communication with your employer may help reduce problems before deployment.")
            step("Notify your employer about your deployment orders if you have not already done so.")
            resource("USERRA information (U.S. Department of Labor)", USERRA_URL)

    # SCRA / Civil
    if a.get("court_case") == "Yes":
        issue("red", "court_case", "Civil court case identified", "You may have rights under the SCRA, and timing matters.")
        step("Schedule an appointment with legal assistance to discuss whether an SCRA stay may apply.")
        doc("Court notices, pleadings, hearing dates, and any related correspondence.")
        resource("SCRA information (U.S. Department of Justice)", SCRA_URL)

    if a.get("lease_termination") == "Yes":
        issue("red", "lease_termination", "Possible early lease termination issue", "You may have rights under the SCRA, but the process should be handled correctly.")
        step("Gather your lease and deployment orders.")
        step("Schedule an appointment with legal assistance before ending your lease.")
        doc("Your lease, deployment orders, and landlord contact information.")
        resource("SCRA information (U.S. Department of Justice)", SCRA_URL)

    if a.get("interest_above_6") == "Yes":
        issue("red", "interest_rate", "Loan or financial obligation above 6%", "The SCRA may cap interest on eligible pre-service obligations at 6%.")
        step("Gather statements for loans or financial obligations with interest above 6%.")
        step("Schedule an appointment with legal assistance to discuss SCRA protections.")
        doc("Loan statements, promissory notes, credit card statements, and creditor notices.")
        resource("SCRA information (U.S. Department of Justice)", SCRA_URL)

    # Military admin
    if a.get("military_action") == "Yes":
        issue("red", "military_action", "Military legal or administrative action identified", "These matters can affect readiness and may require prompt legal guidance.")
        step("Speak with the appropriate military attorney as soon as possible.")
        doc("Letters of reprimand, Article 15 paperwork, or related documents.")

    if a.get("under_investigation") == "Yes":
        issue("red", "investigation", "Investigation identified", "Investigations can affect readiness and may require immediate legal attention.")
        step("Consult the appropriate military attorney promptly.")
        doc("Any notice of investigation or related paperwork.")

    if a.get("dd93_current") == "No":
        issue("yellow", "dd93", "DD Form 93 may need updating", "Accurate emergency data helps the Army contact the right people and direct benefits appropriately.")
        step("Review and update your DD Form 93.")

    if a.get("red_cross_info") == "No":
        issue("yellow", "red_cross", "Emergency contact information may be incomplete", "Emergency message contact information helps support your family during deployment.")
        step("Provide relocation dates and emergency contact information through the appropriate channels.")

    if a.get("change_sgli") == "Yes":
        issue("yellow", "sgli", "SGLI beneficiary review requested", "Outdated beneficiary designations may direct benefits somewhere you do not intend.")
        step("Review and update your SGLI beneficiary designations.")
        resource("SGLI information (VA)", SGLI_URL)
        resource("Military Death Gratuity information (DoD)", DEATH_GRATUITY_URL)

    # Immigration
    if a.get("open_immigration_case") == "Yes":
        issue("red", "immigration_case", "Open immigration matter", "Immigration matters can be time-sensitive and may require specialized guidance.")
        step("Gather all USCIS notices and case documents.")
        step("Schedule an appointment with legal assistance to discuss the matter and whether civilian counsel is needed.")
        doc("USCIS notices, receipts, interview notices, and immigration filings.")

    if a.get("green_card") == "Yes" and a.get("green_card_expiring") == "Yes":
        issue("red", "green_card", "Green Card expires soon", "Expiration or near-expiration may require timely action.")
        step("Gather your Permanent Resident Card and related immigration records.")
        step("Discuss extension or renewal options with an attorney.")
        doc("Green Card and any USCIS notices.")

    if a.get("seeking_citizenship") == "Yes":
        issue("yellow", "citizenship", "Citizenship process identified", "Deployment may affect timing, paperwork, or follow-up requirements.")
        step("Review your citizenship timeline and gather your USCIS paperwork.")

    if a.get("immigration_sponsor") == "Yes":
        issue("yellow", "immigration_sponsor", "Immigration sponsorship identified", "Sponsorship obligations or paperwork may need review before deployment.")
        step("Gather sponsorship forms and supporting documents.")

    # POA
    if a.get("needs_poa") == "Yes":
        issue("yellow", "poa", "Power of attorney may be helpful", "You may need someone to handle finances, housing, or other personal matters while you are away.")
        step("Identify the person you trust to act for you and list the tasks they may need to handle.")

    # Catchall
    if a.get("other_legal_questions") == "Yes":
        issue("yellow", "other_legal_questions", "Additional legal questions identified", "A legal assistance attorney may be able to address issues not covered in this checklist.")
        step("Write down your additional legal questions so you can raise them during your appointment.")

    # Dwell time
    if a.get("deployed_last_18_months") == "Yes":
        issue("yellow", "dwell_time", "Possible dwell-time concern", "This issue may require a more specific legal or command review depending on the facts.")
        step("Gather deployment dates and any documents related to dwell-time waivers or prior mobilizations.")

    # Common resources
    if issues:
        resource("Armed Forces Legal Assistance Locator", LEGAL_LOCATOR_URL)
        resource("Military OneSource legal resources", MILITARY_ONESOURCE_URL)

    # Default next steps if no issue found
    if not issues:
        step("No immediate legal issue was identified based on your answers.")
        step("You may still contact legal assistance if you want to review your documents or plan ahead.")
        resource("Armed Forces Legal Assistance Locator", LEGAL_LOCATOR_URL)
        resource("Military OneSource legal resources", MILITARY_ONESOURCE_URL)

    if any(i["level"] == "red" for i in issues):
        rec = "red"
    elif any(i["level"] == "yellow" for i in issues):
        rec = "yellow"
    else:
        rec = "green"

    return rec, issues, steps, docs, resources


# ---------- Screens ----------
def render_header():
    step = st.session_state.step
    total_steps = len(SECTIONS) - 1
    progress = step / total_steps
    st.progress(progress)
    st.caption(f"Step {step + 1} of {len(SECTIONS)} — {SECTIONS[step]}")
    if step in ENCOURAGEMENT:
        st.info(ENCOURAGEMENT[step])


def screen_welcome():
    st.title("Warfighter Legal Readiness Program")
    st.write(
        "We are here to help you figure out whether you may have legal needs before deployment and, "
        "if necessary, connect you with a lawyer who can help."
    )
    st.write(
        "This process is intended to be simple, fast, and informative. Your answers are **not** a substitute "
        "for legal advice, but they may help you decide whether to contact an attorney. Legal assistance attorneys "
        "may be available at no cost to eligible clients."
    )
    st.success("Please read each question carefully and answer based on your current situation.")
    nav_buttons(show_back=False, next_label="Start")


def screen_about_you():
    st.header("About You")
    component = st.radio(
        "Are you currently:",
        ["Active Duty", "Reserve / National Guard", "Other"],
        index=["Active Duty", "Reserve / National Guard", "Other"].index(get_answer("component", "Active Duty")),
    )
    set_answer("component", component)

    dependents = st.radio("Do you have dependents?", ["Yes", "No"], index=0 if get_answer("dependents", "Yes") == "Yes" else 1)
    set_answer("dependents", dependents)

    married = st.radio("Are you married?", ["Yes", "No"], index=0 if get_answer("married", "Yes") == "Yes" else 1)
    set_answer("married", married)

    if component == "Reserve / National Guard":
        civilian_job = st.radio("Do you have a civilian job?", ["Yes", "No"], index=0 if get_answer("civilian_job", "Yes") == "Yes" else 1)
        set_answer("civilian_job", civilian_job)

    nav_buttons()


def screen_estate():
    st.header("Wills & Estate Planning")
    info_box(
        "Learn more: What is a will?",
        "A will is a legal document that explains who should receive your money and property after your death, "
        "who should care for your children if needed, and who should carry out your wishes. If you do not have a will, state law may decide these issues for you."
    )
    info_box(
        "Learn more: What does 'intestate' mean?",
        "'Intestate' means dying without a will. If this happens, state law determines who gets your property and how it is divided."
    )

    if get_answer("married") == "Yes":
        sep = st.radio("Are you currently separated, going through legal separation, or divorce?", ["Yes", "No"], index=0 if get_answer("separated_divorce", "No") == "Yes" else 1)
        set_answer("separated_divorce", sep)

    children = st.radio("Do you have children?", ["Yes", "No"], index=0 if get_answer("has_children", "No") == "Yes" else 1)
    set_answer("has_children", children)

    if children == "Yes":
        custody = st.radio("Do you have any children whose custody or support is currently in dispute?", ["Yes", "No"], index=0 if get_answer("custody_dispute", "No") == "Yes" else 1)
        set_answer("custody_dispute", custody)

        special_needs = st.radio("Do any of your children have special needs or require a legal guardian?", ["Yes", "No"], index=0 if get_answer("children_special_needs", "No") == "Yes" else 1)
        set_answer("children_special_needs", special_needs)

        info_box(
            "Learn more: Guardianship",
            "Planning ahead can help avoid delays and reduce uncertainty about who would care for your children or dependents if something happens to you."
        )

        if get_answer("married") == "Yes":
            shared = st.radio(
                "Are all of your children the biological or legally adopted children of your spouse?",
                ["Yes", "No"],
                index=0 if get_answer("all_children_shared_spouse", "Yes") == "Yes" else 1,
            )
            set_answer("all_children_shared_spouse", shared)
            spouse_dep = st.radio("Is your spouse also deploying at this time?", ["Yes", "No"], index=0 if get_answer("spouse_deploying", "No") == "Yes" else 1)
            set_answer("spouse_deploying", spouse_dep)
        else:
            fcp = st.radio("Do you have a Family Care Plan and is it complete and certified by your unit?", ["Yes", "No"], index=0 if get_answer("family_care_plan_complete", "Yes") == "Yes" else 1)
            set_answer("family_care_plan_complete", fcp)
            ever_married = st.radio("Have you ever been married to the person you had children with?", ["Yes", "No"], index=0 if get_answer("ever_married_other_parent", "No") == "Yes" else 1)
            set_answer("ever_married_other_parent", ever_married)

        disinherit = st.radio(
            "Do you want to disinherit any child, parent, or sibling who might otherwise inherit under state law?",
            ["Yes", "No"],
            index=0 if get_answer("disinherit_someone", "No") == "Yes" else 1,
        )
        set_answer("disinherit_someone", disinherit)

    hc_poa = st.radio(
        "Do you have a healthcare power of attorney in place to make decisions for you if you become seriously ill or incapacitated and unable to make decisions for yourself?",
        ["Yes", "No"],
        index=0 if get_answer("healthcare_poa", "Yes") == "Yes" else 1,
    )
    set_answer("healthcare_poa", hc_poa)

    info_box(
        "Learn more: Healthcare power of attorney",
        "A healthcare power of attorney allows someone you trust to make medical decisions for you if you become seriously ill or incapacitated and cannot make decisions yourself."
    )

    nav_buttons()


def screen_asset_check():
    st.header("Asset Check")
    info_box(
        "Learn more: Probate vs. non-probate assets",
        "Probate assets may go through a legal process before they are distributed. Non-probate assets usually pass automatically based on beneficiary designations, joint ownership, or certain account arrangements. Even if you have a will, some assets may not be controlled by it."
    )

    owns_real_estate = st.radio("Do you own a house or land?", ["Yes", "No"], index=0 if get_answer("owns_real_estate", "No") == "Yes" else 1)
    set_answer("owns_real_estate", owns_real_estate)

    specific_gifts = st.radio("Do you have specific things you want to give to a friend or a charity?", ["Yes", "No"], index=0 if get_answer("specific_gifts", "No") == "Yes" else 1)
    set_answer("specific_gifts", specific_gifts)

    assets_over_1m = st.radio("Do you have more than $1,000,000 worth of money and property?", ["Yes", "No"], index=0 if get_answer("assets_over_1m", "No") == "Yes" else 1)
    set_answer("assets_over_1m", assets_over_1m)

    owns_business = st.radio("Do you own a business?", ["Yes", "No"], index=0 if get_answer("owns_business", "No") == "Yes" else 1)
    set_answer("owns_business", owns_business)

    assets_in_trust = st.radio("Is your money or property held in a trust?", ["Yes", "No"], index=0 if get_answer("assets_in_trust", "No") == "Yes" else 1)
    set_answer("assets_in_trust", assets_in_trust)

    st.info(
        "**Military benefits you should know about**\n\n"
        "Because of your military service, you may have two very valuable benefits that can go to your loved ones if something happens to you:\n\n"
        "- Servicemembers’ Group Life Insurance (SGLI) can provide up to **$500,000**\n"
        "- The Military Death Gratuity provides **$100,000**\n\n"
        "These benefits will only go to the people you choose if your forms are up to date. Your personalized checklist at the end will help you take the right steps to protect these benefits."
    )

    nav_buttons()


def screen_userra():
    st.header("Reemployment Rights (USERRA)")
    info_box(
        "Learn more: USERRA basics",
        "USERRA protects certain civilian employment rights for service members, including reemployment rights after qualifying service."
    )
    if get_answer("component") == "Reserve / National Guard" and get_answer("civilian_job") == "Yes":
        told = st.radio("Did you tell your employer about your deployment?", ["Yes", "No"], index=0 if get_answer("told_employer", "Yes") == "Yes" else 1)
        set_answer("told_employer", told)
        concern = st.radio(
            "Is your employer worried or saying you might not have a job when you come back?",
            ["Yes", "No"],
            index=0 if get_answer("employer_concern", "No") == "Yes" else 1,
        )
        set_answer("employer_concern", concern)
    else:
        st.write("This section applies primarily to Soldiers in the Reserve or National Guard who have civilian employment.")
    nav_buttons()


def screen_scra():
    st.header("Civil Lawsuits & Consumer Protection (SCRA)")
    info_box(
        "Learn more: SCRA protections",
        "The Servicemembers Civil Relief Act can provide protections related to civil court cases, certain lease terminations, and interest-rate reductions on eligible pre-service obligations."
    )

    court_case = st.radio("Do you have any cases in court right now?", ["Yes", "No"], index=0 if get_answer("court_case", "No") == "Yes" else 1)
    set_answer("court_case", court_case)

    lease = st.radio(
        "Do you rent a home or apartment and need to end your lease early while you deploy?",
        ["Yes", "No"],
        index=0 if get_answer("lease_termination", "No") == "Yes" else 1,
    )
    set_answer("lease_termination", lease)

    interest = st.radio(
        "Do you have any existing loans or financial obligations where the rate of interest is above 6%?",
        ["Yes", "No"],
        index=0 if get_answer("interest_above_6", "No") == "Yes" else 1,
    )
    set_answer("interest_above_6", interest)

    nav_buttons()


def screen_military_admin():
    st.header("Military Administrative Matters")
    info_box(
        "Learn more: DD Form 93",
        "DD Form 93 helps identify who should receive emergency notifications and who may receive certain benefits."
    )
    info_box(
        "Learn more: Family Care Plan",
        "A Family Care Plan outlines who will care for dependents and how their needs will be met during your absence."
    )

    military_action = st.radio(
        "Are you facing military legal or administrative action? (Letter of Reprimand, Article 15, Security Clearance issue, or appeal-related matter)",
        ["Yes", "No"],
        index=0 if get_answer("military_action", "No") == "Yes" else 1,
    )
    set_answer("military_action", military_action)

    under_investigation = st.radio("Is the military or the police investigating you?", ["Yes", "No"], index=0 if get_answer("under_investigation", "No") == "Yes" else 1)
    set_answer("under_investigation", under_investigation)

    dd93_current = st.radio("Is your Record of Emergency Data (DD Form 93) up to date?", ["Yes", "No"], index=0 if get_answer("dd93_current", "Yes") == "Yes" else 1)
    set_answer("dd93_current", dd93_current)

    red_cross_info = st.radio(
        "Have you provided relocation dates and emergency unit contact information through the appropriate emergency message channels?",
        ["Yes", "No"],
        index=0 if get_answer("red_cross_info", "Yes") == "Yes" else 1,
    )
    set_answer("red_cross_info", red_cross_info)

    if get_answer("dependents") == "Yes":
        fcp = st.radio("Do you have a Family Care Plan and is it complete and certified by your unit?", ["Yes", "No"], index=0 if get_answer("family_care_plan_complete", "Yes") == "Yes" else 1)
        set_answer("family_care_plan_complete", fcp)

    change_sgli = st.radio(
        "Do you wish to change your elected beneficiaries or percentages for Servicemembers’ Group Life Insurance (SGLI)?",
        ["Yes", "No"],
        index=0 if get_answer("change_sgli", "No") == "Yes" else 1,
    )
    set_answer("change_sgli", change_sgli)

    nav_buttons()


def screen_immigration():
    st.header("Immigration")
    info_box(
        "Learn more: Immigration matters",
        "Immigration issues can be time-sensitive and may require specialized legal support depending on the case."
    )

    open_case = st.radio("Do you or your family have an open case with immigration services (USCIS)?", ["Yes", "No"], index=0 if get_answer("open_immigration_case", "No") == "Yes" else 1)
    set_answer("open_immigration_case", open_case)

    green_card = st.radio("Do you have a Green Card (Permanent Resident Card)?", ["Yes", "No"], index=0 if get_answer("green_card", "No") == "Yes" else 1)
    set_answer("green_card", green_card)

    if green_card == "Yes":
        green_exp = st.radio("Is your Green Card expired or set to expire within 1 year?", ["Yes", "No"], index=0 if get_answer("green_card_expiring", "No") == "Yes" else 1)
        set_answer("green_card_expiring", green_exp)

    citizen = st.radio("Are you trying to become a U.S. citizen?", ["Yes", "No"], index=0 if get_answer("seeking_citizenship", "No") == "Yes" else 1)
    set_answer("seeking_citizenship", citizen)

    sponsor = st.radio(
        "Are you currently, or do you plan to be, an immigration sponsor for someone seeking status based on your sponsorship?",
        ["Yes", "No"],
        index=0 if get_answer("immigration_sponsor", "No") == "Yes" else 1,
    )
    set_answer("immigration_sponsor", sponsor)

    nav_buttons()


def screen_poa():
    st.header("Powers of Attorney")
    info_box(
        "Learn more: General vs. special power of attorney",
        "A special power of attorney gives limited authority for specific tasks. A general power of attorney gives broader authority. In many cases, a special power of attorney is the safer and more tailored choice."
    )

    needs_poa = st.radio(
        "Based on your current situation, do you want a trusted person to have authority to handle some of your affairs while you are deployed?",
        ["Yes", "No"],
        index=0 if get_answer("needs_poa", "No") == "Yes" else 1,
    )
    set_answer("needs_poa", needs_poa)

    nav_buttons()


def screen_catchall():
    st.header("Other Legal Questions")
    other = st.radio("Do you have any other legal questions for a lawyer?", ["Yes", "No"], index=0 if get_answer("other_legal_questions", "No") == "Yes" else 1)
    set_answer("other_legal_questions", other)
    nav_buttons()


def screen_dwell_time():
    st.header("Dwell Time")
    st.caption("This section is informational and may require a more specific review depending on the facts.")
    deployed = st.radio("Have you been deployed in the last 18 months?", ["Yes", "No"], index=0 if get_answer("deployed_last_18_months", "No") == "Yes" else 1)
    set_answer("deployed_last_18_months", deployed)
    nav_buttons(next_label="See Results")


def screen_results():
    rec, issues, steps, docs, resources = analyze_answers()

    st.header("Your Results")
    if rec == "red":
        st.error("**Strongly Recommended: Speak with a Legal Assistance Attorney**")
        st.write("Based on your responses, you may have one or more issues that could affect your legal readiness before deployment.")
    elif rec == "yellow":
        st.warning("**Recommended: Consider Scheduling an Appointment**")
        st.write("Your responses suggest you may benefit from legal guidance or document preparation before deployment.")
    else:
        st.success("**No Immediate Legal Appointment Indicated**")
        st.write("Based on your responses, no immediate legal issue was identified. You may still contact legal assistance if you would like help planning ahead.")

    if issues:
        st.subheader("Why this matters")
        for item in issues:
            icon = "🔴" if item["level"] == "red" else "🟡"
            st.write(f"{icon} **{item['label']}** — {item['why']}")

    st.subheader("Your Next Steps")
    for s in steps:
        st.write(f"- {s}")

    if docs:
        st.subheader("Documents to Gather")
        for d in docs:
            st.write(f"- {d}")

    st.subheader("Helpful Resources")
    for r in resources:
        st.write(f"- [{r['label']}]({r['url']})")

    st.divider()
    st.write("You can use the sidebar to restart the questionnaire at any time.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back"):
            go_prev()
            st.rerun()
    with c2:
        if st.button("Restart"):
            st.session_state.step = 0
            st.session_state.answers = {}
            st.rerun()


# ---------- Main ----------
ensure_state()

with st.sidebar:
    st.title("Warfighter Legal Readiness")
    st.write("Guided legal readiness screening prototype")
    st.caption("Prototype interface for policy and workflow review")
    selected = st.selectbox("Jump to section", list(range(len(SECTIONS))), format_func=lambda i: SECTIONS[i], index=st.session_state.step)
    if selected != st.session_state.step:
        st.session_state.step = selected
        st.rerun()

render_header()

screen_map = {
    0: screen_welcome,
    1: screen_about_you,
    2: screen_estate,
    3: screen_asset_check,
    4: screen_userra,
    5: screen_scra,
    6: screen_military_admin,
    7: screen_immigration,
    8: screen_poa,
    9: screen_catchall,
    10: screen_dwell_time,
    11: screen_results,
}

screen_map[st.session_state.step]()
