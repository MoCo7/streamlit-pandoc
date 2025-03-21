import streamlit as st
import zipfile
import xml.etree.ElementTree as ET
import markdown
from bs4 import BeautifulSoup
from io import BytesIO

st.title("📑 IDML・Markdownスタイルマッピングアプリ")

uploaded_idml = st.file_uploader("📂 IDMLファイルをアップロード", type=["idml"])

styles = {"ParagraphStyle": [], "CharacterStyle": []}

if uploaded_idml:
    with zipfile.ZipFile(uploaded_idml) as z:
        with z.open('Resources/Styles.xml') as styles_xml:
            tree = ET.parse(styles_xml)
            root = tree.getroot()
            for para_style in root.findall(".//ParagraphStyle"):
                styles["ParagraphStyle"].append(para_style.get('Name'))
            for char_style in root.findall(".//CharacterStyle"):
                styles["CharacterStyle"].append(char_style.get('Name'))

    st.success("✅ Styles.xmlを取得しました！")
    st.write("段落スタイル:", styles["ParagraphStyle"])
    st.write("文字スタイル:", styles["CharacterStyle"])

md_option = st.radio("Markdown入力方法を選択してください", ["直接入力", "ファイルアップロード"])

md_text = ""
if md_option == "直接入力":
    md_text = st.text_area("Markdownを入力してください", height=200)
elif md_option == "ファイルアップロード":
    uploaded_md = st.file_uploader("📂 Markdownファイルをアップロード", type=["md"])
    if uploaded_md:
        md_text = uploaded_md.read().decode('utf-8')

if md_text:
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, 'html.parser')

    md_elements = {
        "見出し(h1-h6)": list({f"h{level.name[-1]}" for level in soup.find_all(['h1','h2','h3','h4','h5','h6'])}),
        "太字": ["strong"] if soup.find_all('strong') else [],
        "イタリック": ["em"] if soup.find_all('em') else [],
        "箇条書き": ["ul"] if soup.find_all('ul') else [],
        "番号つき箇条書き": ["ol"] if soup.find_all('ol') else [],
    }

    st.info("🧐 Markdown要素を検出しました！")
    st.write(md_elements)

    st.header("🔧 スタイルマッピング設定")

    mapping = {}
    for element, detected in md_elements.items():
        if detected:
            mapping[element] = st.selectbox(
                f"{element}に対応するInDesignスタイルを選択",
                options=["（指定なし）"] + styles["ParagraphStyle"] + styles["CharacterStyle"],
                index=1
            )

    def style_to_js(style_full_name, style_type="paragraph"):
        parts = style_full_name.split(":")
        if len(parts) == 1:
            return f'doc.{style_type}Styles.item("{parts[0]}")'
        else:
            group, style = parts[0], parts[1]
            return f'doc.{style_type}StyleGroups.item("{group}").{style_type}Styles.item("{style}")'

    if st.button("💻 検索置換スクリプトを生成"):
        script_lines = [
            "// InDesign検索置換スクリプト生成（JavaScript）\n",
            "var doc = app.activeDocument;\n",
            "app.findGrepPreferences = app.changeGrepPreferences = null;\n"
        ]

        for h in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            if mapping.get("見出し(h1-h6)") and soup.find_all(h):
                style_name = mapping["見出し(h1-h6)"]
                js_style = style_to_js(style_name, "paragraph")
                script_lines.append(
                    f'app.findGrepPreferences.findWhat = "(?<=^).+";\n'
                    f'app.changeGrepPreferences.appliedParagraphStyle = {js_style};\n'
                    f'doc.changeGrep();\n'
                )
                break

        if mapping.get("太字"):
            style_name = mapping["太字"]
            js_style = style_to_js(style_name, "character")
            script_lines.append(
                f'app.findGrepPreferences.findWhat = "(?<=\\*\\*).+?(?=\\*\\*)";\n'
                f'app.changeGrepPreferences.appliedCharacterStyle = {js_style};\n'
                f'doc.changeGrep();\n'
            )

        script_lines.append("app.findGrepPreferences = app.changeGrepPreferences = null;")

        script_text = "\n".join(script_lines)

        st.code(script_text, language="javascript")

        script_filename = "find_replace.jsx"
        script_file = BytesIO(script_text.encode('utf-8'))
        st.download_button(
            label="📥 スクリプトをダウンロード",
            data=script_file,
            file_name=script_filename,
            mime="application/javascript"
        )
