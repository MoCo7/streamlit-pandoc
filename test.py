import streamlit as st
import pypandoc
import os

# Streamlit アプリタイトル
st.title("📄 Markdown 変換ツール")

# 入力方法の選択
input_method = st.radio("入力方法を選んでください", ["テキスト入力", "ファイルアップロード"])

# Markdown入力（ユーザーの選択によって表示を切り替える）
uploaded_file = None
md_text = None

if input_method == "テキスト入力":
    md_text = st.text_area("Markdownを入力してください", height=300)
else:
    uploaded_file = st.file_uploader("Markdownファイルをアップロードしてください", type=["md"])

# 変換先フォーマットを選択
output_format = st.selectbox("変換先フォーマットを選んでください", ["docx", "html"])

# 変換処理
if st.button("変換実行"):
    if not md_text and not uploaded_file:
        st.error("❌ Markdown の入力が必要です！")
    else:
        # 入力されたMarkdownの準備
        if uploaded_file:
            input_path = "uploaded.md"
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ファイルを読み込んでテキストとして扱う
            with open(input_path, "r", encoding="utf-8") as f:
                md_text = f.read()
            
            os.remove(input_path)  # 不要になったファイルを削除

        # 変換処理
        try:
            output_ext = "docx" if output_format == "docx" else "html"
            output_path = f"converted.{output_ext}"

            pypandoc.convert_text(md_text, output_format, format="md", outputfile=output_path)

            st.success(f"✅ 変換成功！({output_ext} ファイルが作成されました)")

            # ダウンロードボタンを表示
            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"📥 {output_ext.upper()}ファイルをダウンロード",
                    data=f,
                    file_name=output_path,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    if output_format == "docx"
                    else "text/html",
                )

            os.remove(output_path)  # 不要になったファイルを削除

        except Exception as e:
            st.error(f"❌ 変換失敗: {e}")
