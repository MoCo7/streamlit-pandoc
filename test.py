import streamlit as st
import pypandoc
import os
from generate_lua_filter import generate_lua_filter  # Lua フィルタ生成関数をインポート

# Streamlit アプリタイトル
st.title("📄 テキスト変換ツール")

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
output_format = st.selectbox("変換先フォーマットを選んでください", ["docx", "html", "plain", "top"])

# 「top」選択時のみ、数値入力フィールドを表示
chapter_number = None
heading_depth = None

if output_format == "top":
    st.subheader("🔢 追加設定（top専用）")
    chapter_number = st.number_input("章番号", min_value=0, step=1, value=1)
    heading_depth = st.number_input("見出しの採番の深さ", min_value=1, step=1, value=3)

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

        # `top` の場合は Lua フィルタを生成して `top.lua` に保存
        if output_format == "top":
            lua_script = generate_lua_filter(chapter_number, heading_depth)  # Lua スクリプトを取得
            with open("top.lua", "w", encoding="utf-8") as f:
                f.write(lua_script)  # ここで書き出し処理を実行

            # `top.lua` が正しく生成されたかチェック
            if not os.path.exists("top.lua"):
                st.error("❌ Lua フィルタの生成に失敗しました！（top.lua が見つかりません）")
                st.stop()  # ここで処理を停止

        # 変換処理
        try:
            output_ext = "docx" if output_format == "docx" else "html" if output_format == "html" else "txt"
            output_path = f"converted.{output_ext}"

            # `top` の場合、-t top.lua を渡す
            extra_args = ["-t", "top.lua"] if output_format == "top" else []

            pypandoc.convert_text(
                text_content, output_format if output_format != "top" else "plain",
                format=input_format, outputfile=output_path, extra_args=extra_args
            )

            st.success(f"✅ 変換成功！({output_ext} ファイルが作成されました)")

            # MIME タイプの設定
            mime_type = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if output_format == "docx"
                else "text/html" if output_format == "html"
                else "text/plain"
            )

            # ダウンロードボタンを表示
            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"📥 {output_ext.upper()}ファイルをダウンロード",
                    data=f,
                    file_name=output_path,
                    mime=mime_type,
                )

            os.remove(output_path)  # 不要になったファイルを削除

            # `top.lua` も削除
            if output_format == "top" and os.path.exists("top.lua"):
                os.remove("top.lua")

        except Exception as e:
            st.error(f"❌ 変換失敗: {e}")
