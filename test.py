import streamlit as st
import pypandoc
import os

# Streamlit アプリタイトル
st.title("📄 Markdown 変換ツール")

# 変換先フォーマットを選択
output_format = st.selectbox("変換先フォーマットを選んでください", ["docx", "html"])

# ファイルアップロード
uploaded_file = st.file_uploader("Markdownファイルをアップロードしてください", type=["md"])

if uploaded_file:
    # 一時ファイルに保存
    input_path = "uploaded.md"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 出力ファイル名
    output_ext = "docx" if output_format == "docx" else "html"
    output_path = f"converted.{output_ext}"

    # Pandocで変換
    try:
        pypandoc.convert_file(
            input_path, output_format, format="md", outputfile=output_path
        )
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

        # 後処理: 一時ファイルの削除
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        st.error(f"❌ 変換失敗: {e}")

# import streamlit as st
# st.caption('キャプション `<caption>`')
# st.text('''
# 	Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris vel velit leo.
# 	Suspendisse fermentum augue metus, ac lacinia ipsum varius sit amet.
# 	Nullam sagittis, tellus id finibus tincidunt, elit mi pellentesque sem, sed suscipit mi lectus non quam.''')

# st.code('''
# import streamlit as st
# st.snow()''',
# 	language='python',
# 	line_numbers=True)
