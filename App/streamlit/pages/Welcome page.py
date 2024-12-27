import streamlit as st 

st.logo("/Users/bianp/Desktop/logo_appli.png", size="large")
st.write("# :rainbow[Welcome to the Fridge Decoder App] ")

intro = ''' ## Home from a long day of work at 8 pm ? Let us take the stress out of dinner. :bouquet:
## We'll find delicious recipes based on the ingredients you have in your fridge, so you can enjoy a perfect meal by yourself or with others !
'''
st.markdown(intro)

st.image("/Users/bianp/Desktop/logo_appli.png")

instructions = ''' ### How to use the app?
### Go to the app tab and type the ingredients in the search bar.
### For example, if you have eggs and avocado in your fridge, you can type: egg and then avocado.
### Just like this:
'''
st.markdown(instructions)

st.image("/Users/bianp/Desktop/tuto_search.png")

st.markdown('### And you will find this recommended recipe :')

st.image("/Users/bianp/Desktop/egg_avocado_search.png")

st.markdown('###  :blue[Warning : All ingredients should be typed in singular. Enjoy !]')

st.markdown('## Also do not hesitate to evaluate the recipe at the end of the page')

sentiment_mapping = ["one", "two", "three", "four", "five"]
selected = st.feedback("stars")
if selected is not None:
    st.markdown(f"You selected {sentiment_mapping[selected]} star(s).")