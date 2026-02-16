# ---------------- Localisation Lab (new, with JSON + leaderboard) ----------------
def localisation_lab():
    st.title("🌍 Localisation Lab")
    st.write(
        "Interactive exercises on localisation (English ↔ Arabic). "
        "Work here is saved to the same JSON/leaderboard as the core lab."
    )

    # Identify student so we can save work
    student_name = st.text_input("Enter your name (for saving localisation work)")
    if not student_name:
        st.info("Please enter your name to start.")
        return

    submissions = load_json(SUBMISSIONS_FILE)
    if student_name not in submissions:
        submissions[student_name] = {}

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
        key="loc_ex_select",
    )

    # Helper to save a localisation submission and show feedback/metrics
    def save_loc_submission(
        ex_id: str,
        source_text: str,
        main_text: str,
        reflection_text: str,
    ):
        if not main_text.strip():
            st.warning("Nothing to save yet — please write your main answer first.")
            return

        # Time + 'keystrokes'
        start_key = f"loc_start_{student_name}_{ex_id}"
        if start_key not in st.session_state:
            st.session_state[start_key] = time.time()
        time_spent = time.time() - st.session_state[start_key]

        keystrokes = len(main_text)

        metrics = evaluate_translation(
            main_text,
            mt_text=None,
            reference=None,
            task_type="Localisation",
            source_text=source_text,
        )

        # Build submission record (note: we only strictly *need* the standard fields)
        submissions[student_name][ex_id] = {
            "source_text": source_text,
            "mt_text": None,
            "student_text": main_text,
            "task_type": "Localisation",
            "time_spent_sec": round(time_spent, 2),
            "keystrokes": keystrokes,
            "metrics": metrics,
            "reflection": reflection_text,
        }
        save_json(SUBMISSIONS_FILE, submissions)

        # Simple participation-based points + small bonus for reasonable length ratio
        points = 15
        lr = metrics.get("length_ratio")
        try:
            if lr is not None and 0.8 <= lr <= 1.3:
                points += 5
        except Exception:
            pass
        update_leaderboard(student_name, points)

        st.success("Localisation submission saved and leaderboard updated!")

        # Show metrics
        def _fmt(v):
            return "—" if v is None else v

        st.subheader("Your Metrics (Localisation)")
        st.markdown(f"""
- **Length Ratio** (target/src): {_fmt(metrics['length_ratio'])}
- **BLEU**: {_fmt(metrics['BLEU'])}
- **chrF++**: {_fmt(metrics['chrF++'])}
- **BERTScore F1**: {_fmt(metrics['BERTScore_F1'])}
- **Time Spent**: {round(time_spent, 2)} sec
- **Characters Typed**: {keystrokes}
""")

        extra = quick_linguistic_hints(source_text, main_text)
        feedback_msgs = generate_feedback(
            metrics,
            "Localisation",
            source_text,
            main_text,
            extra_hints=extra,
        )

        st.subheader("Adaptive Feedback")
        if feedback_msgs:
            for m in feedback_msgs:
                st.markdown(m)
        else:
            st.info("No specific issues triggered. Focus on cohesion, clarity, and consistent localisation choices.")

        st.subheader("Leaderboard (including localisation tasks)")
        show_leaderboard()

    # ---- Exercise implementations ----

    def exercise_1():
        ex_id = "LOC_1"
        source_text = (
            "Download our app today and enjoy free shipping on all orders over $50. "
            "Offer valid through July 4. Call 1-800-555-0199 for assistance."
        )

        st.header("1️⃣ Translation vs Localisation")

        with st.form(f"loc_form_{ex_id}"):
            st.subheader("Source Text (English → Arabic)")
            st.markdown(f"> {source_text}")

            st.markdown("### Step 1 – Translation")
            literal = st.text_area(
                "Write your **initial translation into Arabic** (before localisation):",
                key="loc_ex1_translation",
                height=140,
            )

            st.markdown("### Step 2 – Identify Localisation Elements")
            elements = st.text_area(
                "List at least **5 elements** that require localisation "
                "(e.g., currency, dates, phone formats, cultural references):",
                key="loc_ex1_elements",
                height=120,
            )

            st.markdown("### Step 3 – Market-specific Localisation")
            col1, col2 = st.columns(2)
            with col1:
                uae = st.text_area(
                    "Write a **localised version for the UAE**:",
                    key="loc_ex1_uae",
                    height=160,
                )
            with col2:
                ksa = st.text_area(
                    "Write a **localised version for Saudi Arabia**:",
                    key="loc_ex1_ksa",
                    height=160,
                )

            st.markdown("### Step 4 – Reflection")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                ling = st.text_area("**Linguistic changes**", key="loc_ex1_ling", height=100)
            with col_b:
                cult = st.text_area("**Cultural changes**", key="loc_ex1_cult", height=100)
            with col_c:
                func = st.text_area("**Functional/technical changes**", key="loc_ex1_func", height=100)

            submitted = st.form_submit_button("Save & get feedback")

        with st.expander("👩‍🏫 Instructor notes / discussion points"):
            st.markdown(
                "- Currency (USD → AED/SAR) and thresholds\n"
                "- Date format and local holidays vs July 4\n"
                "- Phone number format and local support channels\n"
                "- Register and marketing tone in Arabic\n"
                "- App store and e-commerce conventions in UAE/KSA"
            )

        if submitted:
            reflection = (
                "Elements needing localisation:\n" + elements.strip() + "\n\n"
                "Linguistic changes:\n" + ling.strip() + "\n\n"
                "Cultural changes:\n" + cult.strip() + "\n\n"
                "Functional/technical changes:\n" + func.strip()
            )
            # Use UAE version as the main 'evaluated' text
            save_loc_submission(ex_id, source_text, uae, reflection)

    def exercise_2():
        ex_id = "LOC_2"
        source_text = (
            "Celebrate Black Friday with unbelievable deals! "
            "Grab your favorite winter outfits before the snow hits!"
        )

        st.header("2️⃣ Cultural Adaptation in Advertising")

        with st.form(f"loc_form_{ex_id}"):
            st.subheader("Source Text (English → Arabic)")
            st.markdown(f"> {source_text}")

            st.markdown("### Step 1 – Literal Translation")
            literal = st.text_area(
                "Write a **literal translation into Arabic**:",
                key="loc_ex2_literal",
                height=140,
            )

            st.markdown("### Step 2 – Localised Version for a Gulf Audience")
            gulf = st.text_area(
                "Now write a **localised version for a Gulf audience**:",
                key="loc_ex2_localised",
                height=160,
            )

            st.markdown("### Step 3 – Strategic Choices")
            bf_choice = st.radio(
                "What do you do with **“Black Friday”**?",
                [
                    "Keep as Black Friday (in English or transliterated)",
                    "Use an existing local term (e.g. White Friday)",
                    "Rebrand it completely",
                    "Other (explain below)",
                ],
                key="loc_ex2_bf_choice",
            )
            bf_notes = st.text_area(
                "Explain your choice regarding **Black Friday**:",
                key="loc_ex2_bf_notes",
                height=100,
            )

            season_notes = st.text_area(
                "How did you handle the **seasonal / winter** reference?",
                key="loc_ex2_season_notes",
                height=100,
            )

            submitted = st.form_submit_button("Save & get feedback")

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Visibility of Western commercial culture vs local practices\n"
                "- Relevance of winter imagery in Gulf advertising\n"
                "- Domestication vs foreignisation in marketing contexts"
            )

        if submitted:
            reflection = (
                "Literal translation:\n" + literal.strip() + "\n\n"
                "Decision on Black Friday:\n" + bf_choice + "\n" + bf_notes.strip() + "\n\n"
                "Seasonal adaptation notes:\n" + season_notes.strip()
            )
            # Use the Gulf-localised version as main text
            save_loc_submission(ex_id, source_text, gulf, reflection)

    def exercise_3():
        ex_id = "LOC_3"
        items = [
            "The conference starts on 03/12/2026 at 9:00 AM.",
            "The package weighs 5 pounds and measures 12 inches.",
            "Prices are listed in USD.",
            "Submit your résumé before October 1.",
        ]
        source_text = "\n".join(items)

        st.header("3️⃣ Conventions: Dates, Units & Currency")
        st.write("Translate and localise the following items into Arabic:")

        with st.form(f"loc_form_{ex_id}"):
            answers = []
            for i, item in enumerate(items, start=1):
                st.markdown(f"**{i}. {item}**")
                ans = st.text_area(
                    f"Your localised Arabic version for item {i}:",
                    key=f"loc_ex3_item_{i}",
                    height=80,
                )
                answers.append(ans)

            st.markdown("### Reflection")
            amb = st.text_area(
                "Where could **ambiguity or misunderstanding** arise if conventions are not localised properly?",
                key="loc_ex3_ambiguity",
                height=120,
            )

            risk = st.text_area(
                "What are the **practical risks** (e.g., legal, financial, usability) of not localising these elements?",
                key="loc_ex3_risk",
                height=120,
            )

            submitted = st.form_submit_button("Save & get feedback")

        with st.expander("👩‍🏫 Instructor notes / hints"):
            st.markdown(
                "- Date format ambiguity (03/12 vs 12/03)\n"
                "- Metric vs imperial units\n"
                "- Currency conversion and symbol localisation\n"
                "- CV vs résumé vs سيرة ذاتية"
            )

        if submitted:
            main_text = "\n".join(answers)
            reflection = (
                "Ambiguity notes:\n" + amb.strip() + "\n\n"
                "Risk notes:\n" + risk.strip()
            )
            save_loc_submission(ex_id, source_text, main_text, reflection)

    def exercise_4():
        ex_id = "LOC_4"
        source_text = "Welcome back, Sarah! We missed you. Ready to pick up where you left off?"

        st.header("4️⃣ Tone & Website/App UX")

        with st.form(f"loc_form_{ex_id}"):
            st.subheader("Source Text (English → Arabic)")
            st.markdown(f"> {source_text}")

            st.markdown("### Step 1 – Neutral MSA Translation")
            neutral = st.text_area(
                "Write a **neutral Modern Standard Arabic** translation:",
                key="loc_ex4_neutral",
                height=120,
            )

            st.markdown("### Step 2 – Contextual Localisation")

            col1, col2 = st.columns(2)
            with col1:
                gov = st.text_area(
                    "Localise for a **formal government portal**:",
                    key="loc_ex4_gov",
                    height=140,
                )
            with col2:
                fashion = st.text_area(
                    "Localise for a **fashion e-commerce website**:",
                    key="loc_ex4_fashion",
                    height=140,
                )

            st.markdown("### Step 3 – Tone & Trust")
            tone_trust = st.text_area(
                "How do **tone** and **register** affect user trust and engagement in each context?",
                key="loc_ex4_tone_trust",
                height=140,
            )

            submitted = st.form_submit_button("Save & get feedback")

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Use of vocatives and name forms in Arabic\n"
                "- Degree of warmth vs distance in institutional voices\n"
                "- Second person pronoun choices (singular/plural, gender)"
            )

        if submitted:
            reflection = (
                "Neutral MSA version:\n" + neutral.strip() + "\n\n"
                "Government vs fashion tone notes:\n" + tone_trust.strip()
            )
            # Use the fashion e-commerce version as main text (more localised / informal)
            save_loc_submission(ex_id, source_text, fashion, reflection)

    def exercise_5():
        ex_id = "LOC_5"
        source_text = (
            "احصل على أفضل صفقات الجمعة السوداء الآن! الشحن مجاني لكل الطلبات أكثر من 50 دولار. "
            "اتصل بنا على 1-800-555-0199."
        )

        st.header("5️⃣ Post-editing: Error Detection & Localisation")

        with st.form(f"loc_form_{ex_id}"):
            st.subheader("Poorly Localised Arabic Banner")
            st.markdown(f"> {source_text}")

            st.markdown("### Step 1 – Identify Problems")
            issues = st.text_area(
                "List the **issues** you can spot:",
                key="loc_ex5_issues",
                height=140,
            )

            st.markdown("### Step 2 – Revised Version for UAE Market")
            revised = st.text_area(
                "Write an improved, **fully localised version for the UAE**:",
                key="loc_ex5_revised",
                height=160,
            )

            st.markdown("### Step 3 – Error Classification")
            col1, col2 = st.columns(2)
            with col1:
                ling = st.text_area("**Linguistic errors**", key="loc_ex5_ling", height=100)
                cult = st.text_area("**Cultural errors**", key="loc_ex5_cult", height=100)
            with col2:
                func = st.text_area("**Functional/technical errors**", key="loc_ex5_func", height=100)
                tech = st.text_area("**Formatting/numbering/other**", key="loc_ex5_tech", height=100)

            submitted = st.form_submit_button("Save & get feedback")

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Appropriateness of “الجمعة السوداء” vs alternatives\n"
                "- Currency choice (dollars vs dirhams)\n"
                "- Phone number format and localisation\n"
                "- Register and marketing style in Arabic"
            )

        if submitted:
            reflection = (
                "Issues spotted:\n" + issues.strip() + "\n\n"
                "Linguistic errors:\n" + ling.strip() + "\n\n"
                "Cultural errors:\n" + cult.strip() + "\n\n"
                "Functional/technical errors:\n" + func.strip() + "\n\n"
                "Formatting/other:\n" + tech.strip()
            )
            save_loc_submission(ex_id, source_text, revised, reflection)

    def exercise_6():
        ex_id = "LOC_6"
        source_text = "Track your calories, crush your goals, and stay summer-ready all year long!"

        st.header("6️⃣ App Store Description Localisation")

        with st.form(f"loc_form_{ex_id}"):
            st.subheader("Source Text (English → Arabic)")
            st.markdown(f"> {source_text}")

            st.markdown("### Step 1 – Base Translation")
            base = st.text_area(
                "Write a **base translation into Arabic**:",
                key="loc_ex6_base",
                height=120,
            )

            st.markdown("### Step 2 – Variant A: Conservative Audience")
            conservative = st.text_area(
                "Localise for a more **conservative audience** (focus on health, well-being, moderation):",
                key="loc_ex6_conservative",
                height=140,
            )

            st.markdown("### Step 3 – Variant B: Youth-focused Fitness App")
            youth = st.text_area(
                "Localise for a **youth-oriented fitness app** (energetic, motivational tone):",
                key="loc_ex6_youth",
                height=140,
            )

            st.markdown("### Step 4 – Strategic Discussion")
            reg_notes = st.text_area(
                "How did you adapt **register**, **imagery**, and **implicit values** in each version?",
                key="loc_ex6_register",
                height=140,
            )

            submitted = st.form_submit_button("Save & get feedback")

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Body image vs health framing\n"
                "- Use of motivational vs neutral language\n"
                "- Sensitivity to cultural norms around appearance"
            )

        if submitted:
            reflection = (
                "Base translation:\n" + base.strip() + "\n\n"
                "Register/imagery/values notes:\n" + reg_notes.strip()
            )
            # Use youth-focused version as main text
            save_loc_submission(ex_id, source_text, youth, reflection)

    def exercise_7():
        ex_id = "LOC_7"
        # Source is conceptual, but we still pass something for hints/ratio
        source_text = (
            "Two versions of the same promotional text: Version A (literal) "
            "and Version B (heavily localised)."
        )

        st.header("7️⃣ Strategy & Theory Reflection")

        with st.form(f"loc_form_{ex_id}"):
            st.write(
                "Imagine you have two Arabic versions of the same English promotional text:\n"
                "- **Version A:** literal translation\n"
                "- **Version B:** heavily localised adaptation\n\n"
                "You can either paste real examples below or answer hypothetically."
            )

            st.markdown("### Step 1 – (Optional) Paste Texts")
            ver_a = st.text_area("Paste **Version A (literal)** here:", key="loc_ex7_a", height=140)
            ver_b = st.text_area("Paste **Version B (localised)** here:", key="loc_ex7_b", height=140)

            st.markdown("### Step 2 – Skopos & Effect")
            skopos = st.text_area(
                "Which version better fulfils the **Skopos** (purpose) of the text, and why?",
                key="loc_ex7_skopos",
                height=140,
            )

            st.markdown("### Step 3 – Domestication vs Foreignisation")
            dom_for = st.text_area(
                "Where do you see **domestication** and **foreignisation** in the localised version?",
                key="loc_ex7_dom_for",
                height=140,
            )

            st.markdown("### Step 4 – Limits of Localisation")
            limits = st.text_area(
                "When does localisation risk becoming **over-adaptation** or even **rewriting**? Give examples.",
                key="loc_ex7_limits",
                height=140,
            )

            submitted = st.form_submit_button("Save & get feedback")

        with st.expander("👩‍🏫 Instructor notes / prompts"):
            st.markdown(
                "- Link discussion to Skopos theory\n"
                "- Discuss ethical and professional limits to adaptation\n"
                "- Consider client brief and audience expectations"
            )

        if submitted:
            main_text = ver_b if ver_b.strip() else ver_a
            reflection = (
                "Skopos analysis:\n" + skopos.strip() + "\n\n"
                "Domestication/foreignisation notes:\n" + dom_for.strip() + "\n\n"
                "Limits of localisation:\n" + limits.strip()
            )
            save_loc_submission(ex_id, source_text, main_text, reflection)

    # ---- Router ----
    # Initialise per-exercise timer on first visit
    ex_id_map = {
        "1️⃣ Translation vs Localisation": "LOC_1",
        "2️⃣ Cultural Adaptation in Advertising": "LOC_2",
        "3️⃣ Conventions: Dates, Units, Currency": "LOC_3",
        "4️⃣ Tone & Website/App UX": "LOC_4",
        "5️⃣ Post-editing: Error Detection": "LOC_5",
        "6️⃣ App Store Description": "LOC_6",
        "7️⃣ Strategy & Theory Reflection": "LOC_7",
    }
    current_ex_id = ex_id_map[exercise]
    start_key = f"loc_start_{student_name}_{current_ex_id}"
    if start_key not in st.session_state:
        st.session_state[start_key] = time.time()

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
