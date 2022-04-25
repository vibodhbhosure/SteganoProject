import os
import wave

import streamlit as st
from stegano import exifHeader as stg
from PIL import Image

MAX_COLOR_VALUE = 256
MAX_BIT_VALUE = 8

def make_image(data, resolution):
    image = Image.new("RGB", resolution)
    image.putdata(data)

    return image

def remove_n_least_significant_bits(value, n):
    value = value >> n
    return value << n

def get_n_least_significant_bits(value, n):
    value = value << MAX_BIT_VALUE - n
    value = value % MAX_COLOR_VALUE
    return value >> MAX_BIT_VALUE - n

def get_n_most_significant_bits(value, n):
    return value >> MAX_BIT_VALUE - n

def shit_n_bits_to_8(value, n):
    return value << MAX_BIT_VALUE - n

def encodeimginimg(image_to_hide, image_to_hide_in, n_bits):
    width, height = image_to_hide.size

    hide_image = image_to_hide.load()
    hide_in_image = image_to_hide_in.load()

    data = []

    for y in range(height):
        for x in range(width):
            # (107, 3, 10)
            # most sig bits
            r_hide, g_hide, b_hide = hide_image[x, y]

            r_hide = get_n_most_significant_bits(r_hide, n_bits)
            g_hide = get_n_most_significant_bits(g_hide, n_bits)
            b_hide = get_n_most_significant_bits(b_hide, n_bits)

            # remove lest n sig bits
            r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]

            r_hide_in = remove_n_least_significant_bits(r_hide_in, n_bits)
            g_hide_in = remove_n_least_significant_bits(g_hide_in, n_bits)
            b_hide_in = remove_n_least_significant_bits(b_hide_in, n_bits)

            data.append((r_hide + r_hide_in,
                         g_hide + g_hide_in,
                         b_hide + b_hide_in))

    return make_image(data, image_to_hide.size)

def decodeimginimg(image_to_decode, n_bits):
    width, height = image_to_decode.size
    encoded_image = image_to_decode.load()

    data = []

    for y in range(height):
        for x in range(width):
            r_encoded, g_encoded, b_encoded = encoded_image[x, y]

            r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
            g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
            b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

            r_encoded = shit_n_bits_to_8(r_encoded, n_bits)
            g_encoded = shit_n_bits_to_8(g_encoded, n_bits)
            b_encoded = shit_n_bits_to_8(b_encoded, n_bits)

            data.append((r_encoded, g_encoded, b_encoded))

    return make_image(data, image_to_decode.size)

def Encode(img, text):
    global fileopen
    with open(os.path.join("", img.name), "wb") as f:
        f.write(img.getbuffer())
    FileOpen = "" + img.name
    stg.hide(FileOpen, "NewImg.jpg", text)
    with open("NewImg.jpg",'rb') as file:
        st.download_button(label="Download Image",file_name='Encoded_Image.jpg', data=file, mime='image/jpg')

def Decode(dimg):
    global dfileopen
    with open(os.path.join("", dimg.name), "wb") as f:
        f.write(dimg.getbuffer())
    dfileopen = "" + dimg.name
    text = stg.reveal(dfileopen)
    st.header('Decoded Text:')
    st.subheader(text)
    return text

t = st.title("Image Steganography")
st.header("")
st.header("")
st.subheader('Select the type of file:')
imag = st.radio('', ('Image', 'Audio', 'Video'))
if imag == 'Image':
    st.subheader('Type of operation:')
    imgencd = st.radio('', ('Encode', 'Decode'))
    if imgencd == 'Encode':
        st.subheader('Upload Image as JPG:')
        filebyte = st.file_uploader("", accept_multiple_files=False, type='jpg')
        if filebyte is not None:
            st.image(filebyte)
            st.subheader('Select Option:')
            opt = st.radio("", ('Text', 'Text File', 'Image'))
            if opt == 'Text':
                st.subheader('Enter Text:')
                txt_input = st.text_input("")
                if txt_input and st.button("Encode") is not None: Encode(filebyte, txt_input)
            elif opt == 'Text File':
                st.subheader('Upload File as TXT:')
                txt_file = st.file_uploader("", accept_multiple_files=False, type='txt')
                if txt_file is not None:
                    with open(os.path.join("", txt_file.name), "wb") as f:
                        f.write(txt_file.getbuffer())
                    with open(txt_file.name) as f:
                        data = f.readline()
                        if data and st.button("Encode") is not None:Encode(filebyte, data)
            elif opt == 'Image':
                st.subheader('Upload File To Hide:')
                new_file = st.file_uploader("", accept_multiple_files=False, type=['png', 'jpg', 'jpeg'])
                if new_file is not None:
                    try:
                        with open(os.path.join("",new_file.name), "wb") as f, open(os.path.join("",filebyte.name), "wb") as e:
                            f.write(new_file.getbuffer())
                            e.write(filebyte.getbuffer())
                        base_image = Image.open(filebyte.name)
                        base_image.save(filebyte.name.split('.')[0]+'.tiff', 'TIFF')
                        base_image = Image.open(filebyte.name.split('.')[0]+'.tiff')
                        hide_image = Image.open(new_file.name)
                        hide_image.save(new_file.name.split('.')[0]+'.tiff', 'TIFF')
                        hide_image = Image.open(new_file.name.split('.')[0]+'.tiff')
                        encodeimginimg(hide_image, base_image, 2).save("Encoded_Image.jpg")
                        with open("Encoded_Image.jpg", 'rb') as file:
                            st.download_button(label="Download Image", file_name='Encoded_Image.jpg', data=file,
                                           mime='image/jpg')
                    except:
                        st.warning("Encoding Error - Please try with other Image!")


    elif imgencd == 'Decode':
        st.subheader('Upload Image as JPG:')
        dimg = st.file_uploader("", type='jpg')
        if dimg is not None:
            st.image(dimg)
            if st.button("Decode"):
                try:
                    text = Decode(dimg)
                except:
                    print()
                try:
                    with open(os.path.join("",dimg.name), 'wb') as file:
                        file.write(dimg.getbuffer())
                    image_to_decode = Image.open(dimg.name)
                    decodeimginimg(image_to_decode, 2).save('Decoded_Image.jpg')
                    with open("Decoded_Image.jpg", 'rb') as file:
                        st.download_button(label="Download Image", file_name='Decoded_Image.jpg', data=file,
                                       mime='image/jpg')
                except:
                    st.warning("Decoding Error - Please try with other Image!")

if imag == 'Audio':
    t.title("Audio Steganography")
    st.subheader("Type of operation:")
    audopt = st.radio("", ('Encode','Decode'))
    if audopt == 'Encode':
        st.subheader("Upload Audio as WAV:")
        base_audio = st.file_uploader("", accept_multiple_files=False, type='wav')
        if base_audio is not None:
            st.subheader("Enter Text:")
            string = st.text_input("")
            if st.button("Decode"):
                with open(os.path.join("",base_audio.name), 'wb') as aud:
                    aud.write(base_audio.getbuffer())
                audio = wave.open(base_audio.name, mode="rb")
                frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
                string = string + int((len(frame_bytes) - (len(string) * 8 * 8)) / 8) * '#'
                bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in string])))
                for i, bit in enumerate(bits):
                    frame_bytes[i] = (frame_bytes[i] & 254) | bit
                frame_modified = bytes(frame_bytes)
                newAudio = wave.open('Encoded_Audio.wav', 'wb')
                newAudio.setparams(audio.getparams())
                newAudio.writeframes(frame_modified)
                newAudio.close()
                audio.close()
                with open('Encoded_Audio.wav', 'rb') as file:
                    st.download_button(label="Download Audio", file_name='Encoded_Audio.wav', data=file,
                                       mime='audio/vnd.wav')

    elif audopt == 'Decode':
        st.subheader("Upload Audio as WAV:")
        enc_audio = st.file_uploader("", accept_multiple_files=False, type='wav')
        if enc_audio is not None:
            with open(os.path.join("",enc_audio.name), 'wb') as aud:
                aud.write(enc_audio.getbuffer())
            audio = wave.open(enc_audio.name, mode='rb')
            frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
            extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
            string = "".join(chr(int("".join(map(str, extracted[i:i + 8])), 2)) for i in range(0, len(extracted), 8))
            decoded = string.split("###")[0]
            st.subheader("Encoded Text:")
            st.markdown(decoded)
            audio.close()