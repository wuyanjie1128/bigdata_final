import os
import base64
import streamlit as st
from openai import OpenAI

from animal_data import (
    ANIMAL_CATEGORIES,
    ANIMALS_DATA,
    get_animals_by_category,
)

# -------------------------
# Basic page config
# -------------------------
st.set_page_config(
    page_title="Animal Vision & Encyclopedia",
    page_icon="🐾",
    layout="wide",
)

# -------------------------
# i18n (UI strings)
# Streamlit 多语言常见做法是用字典 + session_state 切换。:contentReference[oaicite:0]{index=0}
# -------------------------
LANGS = {
    "English": "en",
    "中文": "zh",
    "한국어": "ko",
}

UI = {
    "en": {
        "app_title": "Animal Vision & Encyclopedia",
        "tabs": ["🏠 Home", "🐶 Pet Identifier", "📚 Animal Encyclopedia"],
        "home_intro_title": "Welcome!",
        "home_intro_body": (
            "This site lets you identify animals (especially pets) from images "
            "and explore an animal encyclopedia by category."
        ),
        "model_section_title": "Model settings",
        "api_key_missing": (
            "No API key found. Set environment variable `DASHSCOPE_API_KEY` "
            "to enable vision identification."
        ),
        "upload_label": "Upload an image",
        "identify_btn": "Identify",
        "identifying": "Identifying...",
        "result": "Result",
        "pet_prompt_title": "Pet-focused recognition",
        "pet_prompt_help": (
            "This mode is optimized for common pets (dog, cat, rabbit, hamster, bird, etc.)."
        ),
        "ency_title": "Browse by category",
        "select_category": "Choose a category",
        "animals_count": "Animals in this category",
        "show_details": "Show details",
        "fun_facts": "Fun facts",
        "habitat": "Habitat",
        "diet": "Diet",
        "scientific_name": "Scientific name",
        "common_name": "Common name",
        "language_label": "Language",
        "footer_hint": "Language selector (UI)",
    },
    "zh": {
        "app_title": "动物识别 & 动物百科",
        "tabs": ["🏠 主页", "🐶 宠物识别", "📚 动物百科"],
        "home_intro_title": "欢迎！",
        "home_intro_body": "你可以用图片识别动物（特别是宠物），并按分类浏览动物百科。",
        "model_section_title": "模型设置",
        "api_key_missing": (
            "未检测到 API Key。请设置环境变量 `DASHSCOPE_API_KEY` 以启用识别功能。"
        ),
        "upload_label": "上传图片",
        "identify_btn": "开始识别",
        "identifying": "识别中...",
        "result": "识别结果",
        "pet_prompt_title": "宠物优先识别",
        "pet_prompt_help": "该模式对常见宠物（狗、猫、兔子、仓鼠、鸟等）做更细致描述。",
        "ency_title": "按分类浏览",
        "select_category": "选择分类",
        "animals_count": "本分类动物数量",
        "show_details": "查看详情",
        "fun_facts": "有趣事实",
        "habitat": "栖息地",
        "diet": "食性",
        "scientific_name": "学名",
        "common_name": "常用名",
        "language_label": "网站语言",
        "footer_hint": "语言选择（UI）",
    },
    "ko": {
        "app_title": "동물 인식 & 동물 백과",
        "tabs": ["🏠 홈", "🐶 반려동물 인식", "📚 동물 백과"],
        "home_intro_title": "환영합니다!",
        "home_intro_body": "이미지로 동물(특히 반려동물)을 인식하고 분류별 백과를 둘러볼 수 있습니다.",
        "model_section_title": "모델 설정",
        "api_key_missing": (
            "API 키가 없습니다. 인식 기능을 사용하려면 "
            "환경 변수 `DASHSCOPE_API_KEY` 를 설정하세요."
        ),
        "upload_label": "이미지 업로드",
        "identify_btn": "인식하기",
        "identifying": "인식 중...",
        "result": "결과",
        "pet_prompt_title": "반려동물 중심 인식",
        "pet_prompt_help": "개, 고양이, 토끼, 햄스터, 새 등 흔한 반려동물을 더 자세히 설명합니다.",
        "ency_title": "분류별 탐색",
        "select_category": "분류 선택",
        "animals_count": "이 분류의 동물 수",
        "show_details": "상세 보기",
        "fun_facts": "재미있는 사실",
        "habitat": "서식지",
        "diet": "먹이",
        "scientific_name": "학명",
        "common_name": "일반명",
        "language_label": "언어",
        "footer_hint": "언어 선택(UI)",
    },
}

# -------------------------
# Language state
# -------------------------
if "lang_code" not in st.session_state:
    st.session_state.lang_code = "en"  # default English

def set_lang():
    st.session_state.lang_code = LANGS[st.session_state.lang_choice]

# A lightweight "bottom-left-ish" selector:
# Streamlit doesn't natively support true fixed-position widgets reliably.
# We place it at the bottom of the page to keep it simple and stable.
# (More aggressive CSS hacks are brittle across Streamlit versions.) :contentReference[oaicite:1]{index=1}
def language_selector():
    st.markdown("---")
    cols = st.columns([1, 6])
    with cols[0]:
        st.selectbox(
            UI[st.session_state.lang_code]["language_label"],
            options=list(LANGS.keys()),
            index=list(LANGS.values()).index(st.session_state.lang_code),
            key="lang_choice",
            on_change=set_lang,
        )
    with cols[1]:
        st.caption(UI[st.session_state.lang_code]["footer_hint"])

# -------------------------
# Model client
# Using OpenAI-compatible client with DashScope base_url.
# -------------------------
def get_client():
    api_key = os.getenv("DASHSCOPE_API_KEY", "")
    base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url=base_url)

def image_to_data_url(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    mime = uploaded_file.type or "image/png"
    b64 = base64.b64encode(bytes_data).decode("utf-8")
    return f"data:{mime};base64,{b64}", bytes_data

def build_pet_prompt(lang_code):
    if lang_code == "zh":
        return (
            "请判断图片中是否有常见宠物（狗、猫、兔子、仓鼠、鹦鹉等）。"
            "如果是：\n"
            "1) 宠物类型与可能的品种/亚种（尽量给出置信度/不确定性说明）\n"
            "2) 外观特征\n"
            "3) 年龄阶段与体态（如可判断）\n"
            "4) 饲养与护理建议（简短）\n"
            "5) 有趣的小知识\n"
            "如果不是宠物但仍是动物，请按动物科普方式简要介绍。"
            "如果没有动物，请描述主要内容。"
        )
    if lang_code == "ko":
        return (
            "이미지에 흔한 반려동물(개, 고양이, 토끼, 햄스터, 앵무새 등)이 있는지 판단하세요."
            "있다면:\n"
            "1) 종류 및 가능한 품종/아종(불확실성도 함께)\n"
            "2) 외형 특징\n"
            "3) 나이 단계/체형(가능하면)\n"
            "4) 간단한 사육·관리 팁\n"
            "5) 재미있는 지식\n"
            "반려동물이 아니어도 동물이 있으면 간단히 소개하고,"
            "동물이 없으면 주요 내용을 설명하세요."
        )
    # en
    return (
        "Check whether the image contains a common pet (dog, cat, rabbit, hamster, parrot, etc.). "
        "If yes, provide:\n"
        "1) Pet type and possible breed/subspecies (mention uncertainty)\n"
        "2) Key visual traits\n"
        "3) Age stage/body condition if you can infer\n"
        "4) Brief care tips\n"
        "5) A fun fact\n"
        "If it's an animal but not a typical pet, give a short wildlife-style description. "
        "If no animal is present, describe the main content."
    )

def call_vision_pet(uploaded_file, lang_code):
    client = get_client()
    if client is None:
        return False, UI[lang_code]["api_key_missing"]

    model = os.getenv("QWEN_VL_MODEL", "qwen-vl-plus")
    data_url, _ = image_to_data_url(uploaded_file)

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": build_pet_prompt(lang_code)},
                    ],
                }
            ],
        )
        return True, resp.choices[0].message.content
    except Exception as e:
        return False, str(e)

# -------------------------
# UI
# -------------------------
lang = st.session_state.lang_code
st.title(UI[lang]["app_title"])

tabs = st.tabs(UI[lang]["tabs"])

# ---- Home tab
with tabs[0]:
    st.subheader(UI[lang]["home_intro_title"])
    st.write(UI[lang]["home_intro_body"])

    st.markdown("#### " + UI[lang]["model_section_title"])
    st.write(
        "- `DASHSCOPE_API_KEY` (required for identification)\n"
        "- `DASHSCOPE_BASE_URL` (optional)\n"
        "- `QWEN_VL_MODEL` (optional, default: qwen-vl-plus)\n"
    )

# ---- Pet Identifier tab
with tabs[1]:
    st.subheader(UI[lang]["pet_prompt_title"])
    st.caption(UI[lang]["pet_prompt_help"])

    uploaded = st.file_uploader(
        UI[lang]["upload_label"],
        type=["png", "jpg", "jpeg", "webp", "bmp"],
    )

    col1, col2 = st.columns([1, 1])

    if uploaded:
        with col1:
            st.image(uploaded, use_container_width=True)

        with col2:
            if st.button(UI[lang]["identify_btn"], type="primary"):
                with st.spinner(UI[lang]["identifying"]):
                    ok, text = call_vision_pet(uploaded, lang)

                st.markdown("### " + UI[lang]["result"])
                if ok:
                    st.write(text)
                else:
                    st.error(text)
    else:
        st.info(UI[lang]["upload_label"])

# ---- Encyclopedia tab
with tabs[2]:
    st.subheader(UI[lang]["ency_title"])

    category_options = []
    for cid, cinfo in ANIMAL_CATEGORIES.items():
        display_name = cinfo["name"].get(lang, cinfo["name"]["en"])
        category_options.append((cid, display_name))

    # Sort by display name for nicer UI
    category_options = sorted(category_options, key=lambda x: x[1].lower())

    selected_display = st.selectbox(
        UI[lang]["select_category"],
        options=[name for _, name in category_options],
    )
    selected_category = [cid for cid, name in category_options if name == selected_display][0]

    animals = get_animals_by_category(selected_category)
    st.caption(f"{UI[lang]['animals_count']}: {len(animals)}")

    # Grid cards
    cols = st.columns(3)
    i = 0
    for aid, a in animals.items():
        col = cols[i % 3]
        i += 1
        with col:
            with st.container(border=True):
                # Prefer local name if exists, else English common name
                common = a.get(f"common_name_{lang}") or a.get("common_name_en")
                st.markdown(f"**{common}**")
                st.caption(f"{UI[lang]['scientific_name']}: {a.get('scientific_name', '—')}")
                st.write(a.get(f"summary_{lang}") or a.get("summary_en", ""))

                with st.expander(UI[lang]["show_details"]):
                    st.markdown(f"**{UI[lang]['habitat']}**: {a.get(f'habitat_{lang}') or a.get('habitat_en', '—')}")
                    st.markdown(f"**{UI[lang]['diet']}**: {a.get(f'diet_{lang}') or a.get('diet_en', '—')}")
                    facts = a.get(f"fun_facts_{lang}") or a.get("fun_facts_en", [])
                    if facts:
                        st.markdown(f"**{UI[lang]['fun_facts']}**")
                        for f in facts:
                            st.write(f"- {f}")

# ---- Language selector at bottom
language_selector()
