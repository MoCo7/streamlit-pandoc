import streamlit as st
st.caption('キャプション `<caption>`')
st.text('''
	Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris vel velit leo.
	Suspendisse fermentum augue metus, ac lacinia ipsum varius sit amet.
	Nullam sagittis, tellus id finibus tincidunt, elit mi pellentesque sem, sed suscipit mi lectus non quam.''')

st.code('''
import streamlit as st
st.snow()''',
	language='python',
	line_numbers=True)
