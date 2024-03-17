import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector 
from PIL import Image
import cv2
import os
import re
import matplotlib.pyplot as plt

icon = Image.open("Icon.png")
st.set_page_config(page_title= "BizCardX",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded"
                   )

st.markdown("<h1 style='text-align: center; color: white;'>BizCard: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

st.markdown(f""" <style>.stApp {{
                    position: absolute;
                    width: 100%;
                    overflow: hidden;
                    height: 100%;
                    bottom: -1px;
                    background : url("https://www.freevector.com/uploads/vector/preview/30347/Creative_Geometric_Background.jpg");
                    background-size: cover}}
                    </style>""",unsafe_allow_html=True) 

#selected = option_menu(None, ["Home","Upload & Extract","Modify"], 
#                       icons=["house","cloud-upload","pencil-square"],
#                       default_index=0,
#                      orientation="horizontal",
#                      styles={"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "-2px", "hover-color": "#6495ED"},
#                               "icon": {"font-size": "30px"},
#                              "container" : {"max-width": "5000px"},
#                              "nav-link-selected": {"background-color": "#6495ED"}})
selected = st.selectbox("Select an option", ["HOME", "UPLOAD & EXTRACT", "MODIFY"], 
                        format_func=lambda x: f'{x}',
                        help="Choose an option",
                        key=None)
reader =easyocr.Reader(["en"],gpu=False)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
 )
print(mydb)
mycursor = mydb.cursor(buffered=True)
#mycursor.execute('CREATE DATABASE Bizcard')
mycursor.execute("USE Bizcard")
mycursor.execute('''CREATE TABLE IF NOT EXISTS Card_Details
                (ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                Company_name TEXT,
                Card_holder TEXT,
                Designation TEXT,
                Mobile_number VARCHAR(50),
                Email TEXT,
                Website TEXT,
                Area TEXT,
                City TEXT,
                State TEXT,
                Pin_code VARCHAR(10),
                Image LONGBLOB
                )''')

if selected == "HOME":
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("## :black[**Technologies Used :**]")
        st.write("#### 🔹Python")
        st.write("#### 🔹Pandas")
        st.write("#### 🔹MySQL")
        st.write("#### 🔹EasyOCR")
        st.write("#### 🔹Streamlit")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.markdown("### :black[**Overview :**]")
        st.write("#### 🔹In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR.")
        st.write("#### 🔹You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image.")
        st.write("#### 🔹The database would be able to store multiple entries, each with its own business card image and extracted information.")
        st.write(" ")
        st.write(" ")
        st.write(" ")
    with col2:
        st.image("Biz1.jpg",use_column_width=True)

if selected == "UPLOAD & EXTRACT":
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
        
    if uploaded_card is not None:
        
        def save_card(uploaded_card):
            with open(os.path.join("Biz_cards",uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())   
        save_card(uploaded_card)
        
        def loaded_card(image,text): 
            for (bbox, text, prob) in text: 
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0,0,255), 2)
            plt.rcParams['figure.figsize'] = (15,15)
            plt.axis('off')
            plt.imshow(image)
        col1,col2 = st.columns(2,gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the Bizcard")
            st.image(uploaded_card)
        with col2:
            st.markdown("#     ")
            st.markdown("#     ")       
            with st.spinner("Please wait processing image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd()+ "\\" + "Biz_cards"+ "\\"+ uploaded_card.name
                image = cv2.imread(saved_img)
                text = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                st.pyplot(loaded_card(image,text))
        saved_img = os.getcwd()+ "\\" + "Biz_cards"+ "\\"+ uploaded_card.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)

        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        
        data = {"Company_name" : [],
                "Card_holder" : [],
                "Designation" : [],
                "Mobile_number" :[],
                "Email" : [],
                "Website" : [],
                "Area" : [],
                "City" : [],
                "State" : [],
                "Pin_code" : [],
                "Image" : img_to_binary(saved_img)
               }

        def get_data(res):
            for ind,i in enumerate(res):
# To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["Website"].append(i)
                elif "WWW" in i:
                    data["Website"] = res[4] +"." + res[5]

# To get EMAIL ID
                elif "@" in i:
                    data["Email"].append(i)

# To get MOBILE NUMBER
                elif "-" in i:
                    data["Mobile_number"].append(i)
                    if len(data["Mobile_number"]) ==2:
                        data["Mobile_number"] = " & ".join(data["Mobile_number"])

# To get COMPANY NAME  
                elif ind == len(res)-1:
                    data["Company_name"].append(i)

# To get CARD HOLDER NAME
                elif ind == 0:
                    data["Card_holder"].append(i)

# To get DESIGNATION
                elif ind == 1:
                    data["Designation"].append(i)

# To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["Area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["Area"].append(i)

# To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["City"].append(match1[0])
                elif match2:
                    data["City"].append(match2[0])
                elif match3:
                    data["City"].append(match3[0])

# To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                     data["State"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["State"].append(i.split()[-1])
                if len(data["State"])== 2:
                    data["State"].pop(0)

# To get PINCODE        
                if len(i)>=6 and i.isdigit():
                    data["Pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["Pin_code"].append(i[10:])
        get_data(result)

#FUNCTION TO CREATE DATAFRAME
        def create_df(data):
            df = pd.DataFrame(data)
            return df
        df = create_df(data)
        st.success("### Data Extracted!")
        st.write(df)
        
        if st.button(":white[Upload to Database]"):
            for i,row in df.iterrows():
                sql = """INSERT INTO card_details(Company_name,
                                                Card_holder,
                                                Designation,
                                                Mobile_number,
                                                Email,
                                                Website,
                                                Area,
                                                City,
                                                State,
                                                Pin_code,
                                                Image)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                         
                mycursor.execute(sql, tuple(row))
                mydb.commit()
            st.success("#### Uploaded to database successfully!")
            
            
if selected == "MODIFY":
    col1,col2,col3 = st.columns([3,3,2])
    col2.markdown("### :black[Alter or Delete the data here]")
    column1,column2 = st.columns(2,gap="large")
    try:
        with column1:
            mycursor.execute("SELECT card_holder FROM card_details")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_details WHERE card_holder=%s",
                            (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            Company_name = st.text_input("Company_Name", result[0])
            Card_holder = st.text_input("Card_Holder", result[1])
            Designation = st.text_input("Designation", result[2])
            Mobile_number = st.text_input("Mobile_Number", result[3])
            Email = st.text_input("Email", result[4])
            Website = st.text_input("Website", result[5])
            Area = st.text_input("Area", result[6])
            City = st.text_input("City", result[7])
            State = st.text_input("State", result[8])
            Pin_code = st.text_input("Pin_Code", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE card_details SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (Company_name,Card_holder,Designation,Mobile_number,Email,Website,Area,City,State,Pin_code,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully!")

        with column2:
            mycursor.execute("SELECT card_holder FROM card_details")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                mycursor.execute(f"DELETE FROM card_details WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is no data available in the database")
    
    if st.button("View updated data"):
        mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_details")
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Card_Holder","Designation","Mobile_Number","Email","Website","Area","City","State","Pin_Code"])
        st.write(updated_df)