import streamlit as st

st.title("私の初めてのWebアプリ")
name = st.text_input("あなたの名前を入力してください")
if name:
    st.write(f"こんにちは、{name}さん！")