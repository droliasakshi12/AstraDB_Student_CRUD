import streamlit as st 
from astrapy import DataAPIClient
import pandas as pd 
import json 


@st.cache_resource
def init_db():
    client = DataAPIClient("Your_AstraDB_Token")

    db = client.get_database_by_api_endpoint("Your_AstraDB_EndPoint_Token")

    return db 

db = init_db()
#collection name and vector dimensions 
collection_name = "stud_info"
vector_dimensions = 5 

#checking if collections exists or not 
def get_collections():
    existing_collection = db.list_collection_names()
    try:
        if collection_name not in existing_collection:
            collection = db.create_collection(
                name=collection_name,
                definition={
                    "vector":{
                        "dimensions":vector_dimensions,
                        "metric":"cosine"
                    }
                }
            )

            st.success(f"collection {collection} created !!")
        else:
            collection = db.get_collection(collection_name)
        return collection
    except Exception as e:
        st.error(f"Error{e}")
        return None

#converting vector from string 
def vector_from_string(vector_str):
    try:
        return [float(x.strip()) for x in vector_str.split(",")]
    except:
        st.error("Invalid vector format. Use comma-separated numbers.")
        return None
    
#main title 
st.title("AstraDB Vector Database Manager")
st.markdown("-------")

#calling get_collection function in collection varaible  
collection = get_collections()

#creating a sidebar for options 
st.sidebar.title("navigation!!")
page = st.sidebar.radio("SELECT OPERATION !!",["view_stud","add_stud","update_stud","delete_stud"])

if collection:
    if page == "view_stud":
        st.title("VIEW STUDENT INFO")
        view_options=st.radio("view student record by:",["VIEW ALL","VIEW BY ID"])
        if view_options=="VIEW ALL":
            get_stud_info = list(collection.find({}))
            view_list = []
            for info in get_stud_info:
                view_list.append({
                    "ID":info.get("id"),
                    "NAME":info.get("NAME"),
                    "VECTOR":info.get("$vector")
                })
                
            df = pd.DataFrame(view_list)
            st.dataframe(df,use_container_width=True)
            st.success(f"TOTAL STUDENTS IN RECORDS ARE : {len(df)}")
        
        if view_options=="VIEW BY ID":
            stud_id = st.number_input(label="STUDENT ID ",placeholder="enter the id of the student you want to view")
            find = st.button("FIND STUDENT")
            if find :
                get_stud_by_id=collection.find_one({"id":stud_id})
                if get_stud_by_id:
                        st.write(f"**ID:**",get_stud_by_id.get("id"))
                        st.write(f"**NAME:**",get_stud_by_id.get("NAME"))
                else:
                    st.error("student not found!!")
                    

#inserting new student info !!!
    if page == "add_stud":
        st.title("ADD NEW RECORDS")
        #lets input  the values from the users!!
        with st.form("student_form"):
            stud_id = st.number_input(label="STUDENT ID",placeholder="ex:6")
            stud_name = st.text_input(label="STUDENT NAME",placeholder="ex:RAJU")
            vector_input= st.text_input(label="VECTOR",placeholder="1.1,1.2,1.3,1.4,1.5")
        
            submit = st.form_submit_button("student_form")
        if submit :
            vector  = vector_from_string(vector_input)
            if vector and len(vector) == vector_dimensions:
                insert_stud = {
                        "id":stud_id,
                        "NAME":stud_name,
                        "$vector":vector
                            }   
                collection.insert_one(insert_stud)
                st.success("student data inserted!!")



#updating student data  
    if page == "update_stud":
        st.header("UPDATE STUDENT INFO")
        #taking inputs from the student  
        #first fetching the data , if student record exists or not
        stud_id = st.number_input(label="STUDENT ID",placeholder="enter the id of the stduent you want to update!")
        fetch_stud_data = collection.find_one({"id":stud_id})
        if fetch_stud_data:
            with st.form("update student data"):
                    # update_stud_id = st.number_input(label="STUDENT ID",placeholder="enter the student id")
                    update_stud_name = st.text_input(label="STUDENT NAME",placeholder="student name")
                    update_vector_input = st.text_input(label="VECTOR",placeholder="1.1,1.2,1.3,1.4,1.5") 
                    update_submit = st.form_submit_button("update_student")
            if update_submit :
                new_vector = vector_from_string(update_vector_input)
                if new_vector and len(new_vector) == vector_dimensions:
                    collection.update_one(
                        {"id":stud_id},
                        {"$set":{
                            "NAME":update_stud_name,
                            "$vector":new_vector
                        }}
                    )   
                    st.success("Student Data  Updated Successfully!!")

#deleting the student 
    if page =="delete_stud":
        st.title("DELETE STUDENT DATA")
        delete_id = st.number_input(label="STUDENT ID",placeholder="enter the id of the student to delete")
        #checking if id exists or not 
        find_record = collection.find_one({"id":delete_id})
        if find_record:
            st.success("STUDENT RECORD FOUND")
            delete_button=st.button(label="DELETE STUDENT RECORD")
            if delete_button:
                collection.delete_one({"id":delete_id})
                st.success("Student data deleted")
            else:
                st.error("UNABLE TO DELETE STUDENT DATA ")
        else:
            st.error("student not found")

    