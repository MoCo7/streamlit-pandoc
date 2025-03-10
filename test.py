import streamlit as st
import pypandoc
import os

# Streamlit アプリタイトル
st.title("📄 テキスト変換ツール（Lua フィルタ対応）")

# 入力フォーマットの選択（デフォルトは Markdown）
input_format = st.radio("入力フォーマットを選んでください", ["md", "org", "rst"], index=0)

# 入力方法の選択
input_method = st.radio("入力方法を選んでください", ["テキスト入力", "ファイルアップロード"])

# ユーザー入力を保持する変数
uploaded_file = None
text_content = None

if input_method == "テキスト入力":
    text_content = st.text_area(f"{input_format.upper()} を入力してください", height=300)
else:
    uploaded_file = st.file_uploader(f"{input_format.upper()} ファイルをアップロードしてください", type=[input_format])

# 変換先フォーマットを選択
output_format = st.selectbox("変換先フォーマットを選んでください", ["docx", "html", "plain"])

# Lua フィルタの適用を選択
use_lua_filter = st.selectbox("Lua フィルタを適用しますか？", ["なし", "top"])

# 変換処理
if st.button("変換実行"):
    if not text_content and not uploaded_file:
        st.error("❌ テキストの入力またはファイルのアップロードが必要です！")
    else:
        # ファイルアップロードの場合、内容を取得
        if uploaded_file:
            input_path = f"uploaded.{input_format}"
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ファイルを読み込んでテキストとして扱う
            with open(input_path, "r", encoding="utf-8") as f:
                text_content = f.read()
            
            os.remove(input_path)  # 不要になったファイルを削除

        # 変換処理
        try:
            output_ext = "docx" if output_format == "docx" else "html" if output_format == "html" else "txt"
            output_path = f"converted.{output_ext}"

            # Lua フィルタを適用する場合
            extra_args = []
            if use_lua_filter == "top" and os.path.exists("top.lua"):
                extra_args = ["--lua-filter", "top.lua"]

            pypandoc.convert_text(
                text_content, output_format, format=input_format, outputfile=output_path, extra_args=extra_args
            )

            st.success(f"✅ 変換成功！({output_ext} ファイルが作成されました)")

            # ダウンロードボタンを表示
            mime_type = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if output_format == "docx"
                else "text/html" if output_format == "html"
                else "text/plain"
            )

            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"📥 {output_ext.upper()}ファイルをダウンロード",
                    data=f,
                    file_name=output_path,
                    mime=mime_type,
                )

            os.remove(output_path)  # 不要になったファイルを削除

        except Exception as e:
            st.error(f"❌ 変換失敗: {e}")
