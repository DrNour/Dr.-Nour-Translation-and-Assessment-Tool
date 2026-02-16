import streamlit as st

def run_localisation_lab():
    st.title("🌍 Localisation Lab")
    st.write(
        "Interactive exercises on localisation (English ↔ Arabic). "
        "Students can translate, localise, reflect, and classify issues."
    )

    exercise = st.sidebar.selectbox(
        "Choose a localisation exercise",
        [
            "1️⃣ Translation vs Localisation",
            "2️⃣ Cultural Adaptation in Advertising",
            "3️⃣ Conventions: Dates, Units, Currency",
            "4️⃣ Tone & Website/App UX",
            "5️⃣ Post-editing: Error Detection",
            "6️⃣ App Store Description",
            "7️⃣ Strategy & Theory Reflection",
        ],
        key="localisation_ex_select",
    )

    # ── Exercise implementations ──────────────────────────────────────────────

    def exercise_1():
        st.header("1️⃣ Translation vs Localisation")

        st.subheader("Source Text (English → Arabic)")
        st.markdown(
            "> Download our app today and enjoy free shipping on all orders over $50. "
            "Offer valid through July 4. Call 1-800-555-0199 for assistance."
        )

        st.markdown("### Step 1 – Translation")
        st.text_area(
            "Write your **initial translation into Arabic** (before localisation):",
            key="ex1_translation",
            height=140,
        )

        st.markdown("### Step 2 – Identify Localisation Elements")
        st.write("Which elements need localisation (not just literal translation)?")

        st.text_area(
            "List at least **5 elements** that require localisation "
            "(e.g., currency, dates, phone formats, cultural references):",
            key="ex1_elements",
            height=120,
        )

        st.markdown("### Step 3 – Market-specific Localisation")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### a) UAE Market (English → Arabic)")
            st.text_area(
                "Write a **localised version for the UAE**:",
                key="ex1_uae",
                height=160,
            )

        with col2:
            st.markdown("#### b) Saudi Market (English → Arabic)")
            st.text_area(
                "Write a **localised version for Saudi Arabia**:",
                key="ex1_ksa",
                height=160,
            )

        st.markdown("### Step 4 – Reflection")
        st.write("Classify the types of changes you made:")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.text_area("**Linguistic changes**", key="ex1_ling", height=100)
        with col_b:
            st.text_area("**Cultural changes**", key="ex1_cult", height=100)
        with col_c:
            st.text_area("**Functional/technical changes**", key="ex1_func", height=100)

        with st.expander("👩‍🏫 Instructor notes / discussion points"):
            st.markdown(
                "- Currency (USD → AED/SAR) and thresholds\n"
                "- Date format and local holidays vs July 4\n"
                "- Phone number format and local support channels\n"
                "- Register and marketing tone in Arabic\n"
                "- App store and e-commerce conventions in UAE/KSA"
            )

    def exercise_2():
        st.header("2️⃣ Cultural Adaptation in Advertising")

        st.subheader("Source Text (English → Arabic)")
        st.markdown(
            "> Celebrate Black Friday with unbelievable deals! "
            "Grab your favorite winter outfits before the snow hits!"
        )

        st.markdown("### Step 1 – Literal Translation")
        st.text_area(
            "Write a **literal translation into Arabic**:",
            key="ex2_literal",
            height=140,
        )

        st.markdown("### Step 2 – Localised Version for a Gulf Audience")
        st.text_area(
            "Now write a **localised version for a Gulf audience**:",
            key="ex2_localised",
            height=160,
        )

        st.markdown("### Step 3 – Strategic Choices")
        st.write("How would you handle these?")

        st.radio(
            "What do you do with **“Black Friday”**?",
            [
                "Keep as Black Friday (in English or transliterated)",
                "Use an existing local term (e.g. White Friday)",
                "Rebrand it completely",
                "Other (explain below)",
            ],
            key="ex2_bf_choice",
        )
        st.text_area(
            "Explain your choice regarding **Black Friday**:",
            key="ex2_bf_notes",
            height=100,
        )

        st.text_area(
            "How did you handle the **seasonal / winter** reference?",
            key="ex2_season_notes",
            height=100,
        )

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Visibility of Western commercial culture vs local practices\n"
                "- Relevance of winter imagery in Gulf advertising\n"
                "- Domestication vs foreignisation in marketing contexts"
            )

    def exercise_3():
        st.header("3️⃣ Conventions: Dates, Units & Currency")

        st.write("Translate and localise the following items into Arabic:")

        items = [
            "1. The conference starts on 03/12/2026 at 9:00 AM.",
            "2. The package weighs 5 pounds and measures 12 inches.",
            "3. Prices are listed in USD.",
            "4. Submit your résumé before October 1.",
        ]

        for i, item in enumerate(items, start=1):
            st.markdown(f"**{item}**")
            st.text_area(
                f"Your localised Arabic version for item {i}:",
                key=f"ex3_item_{i}",
                height=80,
            )

        st.markdown("### Reflection")
        st.text_area(
            "Where could **ambiguity or misunderstanding** arise if conventions are not localised properly?",
            key="ex3_ambiguity",
            height=120,
        )

        st.text_area(
            "What are the **practical risks** (e.g., legal, financial, usability) of not localising these elements?",
            key="ex3_risk",
            height=120,
        )

        with st.expander("👩‍🏫 Instructor notes / hints"):
            st.markdown(
                "- Date format ambiguity (03/12 vs 12/03)\n"
                "- Metric vs imperial units\n"
                "- Currency conversion and symbol localisation\n"
                "- CV vs résumé vs سيرة ذاتية"
            )

    def exercise_4():
        st.header("4️⃣ Tone & Website/App UX")

        st.subheader("Source Text (English → Arabic)")
        st.markdown(
            "> Welcome back, Sarah! We missed you. Ready to pick up where you left off?"
        )

        st.markdown("### Step 1 – Neutral MSA Translation")
        st.text_area(
            "Write a **neutral Modern Standard Arabic** translation:",
            key="ex4_neutral",
            height=120,
        )

        st.markdown("### Step 2 – Contextual Localisation")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### a) Formal government portal")
            st.text_area(
                "Localise for a **formal government portal**:",
                key="ex4_gov",
                height=140,
            )
        with col2:
            st.markdown("#### b) E-commerce fashion website")
            st.text_area(
                "Localise for a **fashion e-commerce website**:",
                key="ex4_fashion",
                height=140,
            )

        st.markdown("### Step 3 – Tone & Trust")
        st.text_area(
            "How do **tone** and **register** affect user trust and engagement in each context?",
            key="ex4_tone_trust",
            height=140,
        )

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Use of vocatives and name forms in Arabic\n"
                "- Degree of warmth vs distance in institutional voices\n"
                "- Second person pronoun choices (singular/plural, gender)"
            )

    def exercise_5():
        st.header("5️⃣ Post-editing: Error Detection & Localisation")

        st.subheader("Poorly Localised Arabic Banner")
        st.markdown(
            "> احصل على أفضل صفقات الجمعة السوداء الآن! الشحن مجاني لكل الطلبات أكثر من 50 دولار. اتصل بنا على 1-800-555-0199."
        )

        st.markdown("### Step 1 – Identify Problems")
        st.write("What is wrong with this localisation?")
        st.text_area(
            "List the **issues** you can spot:",
            key="ex5_issues",
            height=140,
        )

        st.markdown("### Step 2 – Revised Version for UAE Market")
        st.text_area(
            "Write an improved, **fully localised version for the UAE**:",
            key="ex5_revised",
            height=160,
        )

        st.markdown("### Step 3 – Error Classification")
        st.write("For each category, briefly describe any relevant errors:")

        col1, col2 = st.columns(2)
        with col1:
            st.text_area("**Linguistic errors**", key="ex5_ling", height=100)
            st.text_area("**Cultural errors**", key="ex5_cult", height=100)
        with col2:
            st.text_area("**Functional/technical errors**", key="ex5_func", height=100)
            st.text_area("**Formatting/numbering/other**", key="ex5_tech", height=100)

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Appropriateness of “الجمعة السوداء” vs alternatives\n"
                "- Currency choice (dollars vs dirhams)\n"
                "- Phone number format and localisation\n"
                "- Register and marketing style in Arabic"
            )

    def exercise_6():
        st.header("6️⃣ App Store Description Localisation")

        st.subheader("Source Text (English → Arabic)")
        st.markdown(
            "> Track your calories, crush your goals, and stay summer-ready all year long!"
        )

        st.markdown("### Step 1 – Base Translation")
        st.text_area(
            "Write a **base translation into Arabic**:",
            key="ex6_base",
            height=120,
        )

        st.markdown("### Step 2 – Variant A: Conservative Audience")
        st.text_area(
            "Localise for a more **conservative audience** (focus on health, well-being, moderation):",
            key="ex6_conservative",
            height=140,
        )

        st.markdown("### Step 3 – Variant B: Youth-focused Fitness App")
        st.text_area(
            "Localise for a **youth-oriented fitness app** (energetic, motivational tone):",
            key="ex6_youth",
            height=140,
        )

        st.markdown("### Step 4 – Strategic Discussion")
        st.text_area(
            "How did you adapt **register**, **imagery**, and **implicit values** in each version?",
            key="ex6_register",
            height=140,
        )

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Body image vs health framing\n"
                "- Use of motivational vs neutral language\n"
                "- Sensitivity to cultural norms around appearance"
            )

    def exercise_7():
        st.header("7️⃣ Strategy & Theory Reflection")

        st.write(
            "Imagine you have two Arabic versions of the same English promotional text:\n"
            "- **Version A:** literal translation\n"
            "- **Version B:** heavily localised adaptation\n\n"
            "You can either paste real examples below or answer hypothetically."
        )

        st.markdown("### Step 1 – (Optional) Paste Texts")
        st.text_area("Paste **Version A (literal)** here:", key="ex7_a", height=140)
        st.text_area("Paste **Version B (localised)** here:", key="ex7_b", height=140)

        st.markdown("### Step 2 – Skopos & Effect")
        st.text_area(
            "Which version better fulfils the **Skopos** (purpose) of the text, and why?",
            key="ex7_skopos",
            height=140,
        )

        st.markdown("### Step 3 – Domestication vs Foreignisation")
        st.text_area(
            "Where do you see **domestication** and **foreignisation** in the localised version?",
            key="ex7_dom_for",
            height=140,
        )

        st.markdown("### Step 4 – Limits of Localisation")
        st.text_area(
            "When does localisation risk becoming **over-adaptation** or even **rewriting**? Give examples.",
            key="ex7_limits",
            height=140,
        )

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Link discussion to Skopos theory\n"
                "- Discuss ethical and professional limits to adaptation\n"
                "- Consider client brief and audience expectations"
            )

    # ── Router ────────────────────────────────────────────────────────────────
    if exercise == "1️⃣ Translation vs Localisation":
        exercise_1()
    elif exercise == "2️⃣ Cultural Adaptation in Advertising":
        exercise_2()
    elif exercise == "3️⃣ Conventions: Dates, Units, Currency":
        exercise_3()
    elif exercise == "4️⃣ Tone & Website/App UX":
        exercise_4()
    elif exercise == "5️⃣ Post-editing: Error Detection":
        exercise_5()
    elif exercise == "6️⃣ App Store Description":
        exercise_6()
    elif exercise == "7️⃣ Strategy & Theory Reflection":
        exercise_7()
