
from PIL import ImageTk,Image
from stegano import exifHeader as stg
import streamlit as st
import os
# decoding the file

def Encode(img,text):
    global FileOpen
    with open(os.path.join("tempdir",img.name),"wb") as f:
        f.write(img.getbuffer())
    FileOpen = "tempdir\\"+img.name
    stg.hide(FileOpen,"NewImg.jpg",text)



st.title("Image Steganography")
imag = st.checkbox('Image')
if imag:
    text = st.text_input("Enter text to encode")
    filebytes = st.file_uploader("Upload a File", type='jpg')
    if filebytes and text is not None:
        st.image(filebytes)
        st.button("Encode",on_click=Encode(filebytes,text))
        st.success("Image Encoded Successfully")