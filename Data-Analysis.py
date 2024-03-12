import streamlit as st
import pandas as pd
import plotly.express as px
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import base64
import glob

import pygwalker as pyg
import pandas as pd
import streamlit.components.v1 as components

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

# Set Streamlit to be wide by default
st.set_page_config(layout="wide", page_title="House Flipping Dashboard", page_icon="🏠", initial_sidebar_state="collapsed")

def main():

    tab1, tab2, tab3, tab4 = st.tabs(["Listed Homes", "Sold Homes", "Marketing Research", "Ad Hoc"])

    with tab1:
        
        @st.cache
        def read_csv_file():
            current_directory = os.getcwd()
            if 'houseflipping' in current_directory.lower():
                # If running in the 'houseflipping' directory, read the CSV file from the GitHub URL
                file_url = 'https://raw.githubusercontent.com/Nikhil-Lakha/HouseFlipping/main/Listed-Properties/Current-Listed-Properties.csv'
                df = pd.read_csv(file_url)
            else:
                # If running locally, read the CSV file from the local path
                file_path = 'C:/Users/lakha/OneDrive/Documents/House Flipping - Real Life/HouseFlipping/Listed-Properties/Current-Listed-Properties.csv'
                df = pd.read_csv(file_path)

            return df

        df = read_csv_file()

        # Default columns to display
        default_columns = ['title', 'href','property_type', 'Bedrooms', 'Bathrooms', 'price', 'Floor Area', 'Province', 'City', 'Suburb', 'Area', "Price per sqm"]


        # Sidebar for selecting columns
        st.sidebar.title("Column Selection")
        # Filter out default columns that don't exist in the dataframe
        default_columns = [col for col in default_columns if col in df.columns]
        selected_columns = st.sidebar.multiselect("Select Columns", df.columns.tolist(), default=default_columns)
        

    
        # Filter options
        province_options = ['gauteng'] + list(df['Province'].unique())
        city_options = ['All']
        suburb_options = ['All']
        area_options = ['All']

        col1, col2, col3, col4 = st.columns(4)

        # Sidebar filters
        with col1:
            province_selected = st.selectbox('Select Province', province_options)

        with col2:
            if province_selected != 'All':
                city_options = ['All'] + list(df[df['Province'] == province_selected]['City'].unique())
            city_selected = st.selectbox('Select City', city_options)

        with col3:
            if city_selected != 'All':
                suburb_options = ['All'] + list(df[(df['Province'] == province_selected) & (df['City'] == city_selected)]['Suburb'].unique())
            suburb_selected = st.selectbox('Select Suburb', suburb_options)

        with col4:
            if suburb_selected != 'All':
                area_options = ['All'] + list(df[(df['Province'] == province_selected) & (df['City'] == city_selected) & (df['Suburb'] == suburb_selected)]['Area'].unique())
            area_selected = st.selectbox('Select Area', area_options)

        col1, col2 = st.columns(2)

        with col1:
            # Add a price slider for filtering
            price_range = st.slider("Price Range", min_value=df['price'].min(), max_value=10000000.0, value=(df['price'].min(), 10000000.0))

        with col2:
            # Determine the maximum and minimum values for the 'Price per sqm' column
            max_price_per_sqm = 35000.0
            min_price_per_sqm = 0.0
            # Add a price per sqm slider for filtering
            price_per_sqm_range = st.slider("Price per sqm Range",
                                            min_value=min_price_per_sqm,
                                            max_value=max_price_per_sqm,
                                            value=(min_price_per_sqm, max_price_per_sqm))

        # Filter dataframe based on selected options and price range
        filtered_df = df[
            (df['Province'] == province_selected if province_selected != 'All' else True) &
            (df['City'] == city_selected if city_selected != 'All' else True) &
            (df['Suburb'] == suburb_selected if suburb_selected != 'All' else True) &
            (df['Area'] == area_selected if area_selected != 'All' else True) &
            (df['price'].between(price_range[0], price_range[1])) &  # Filter based on the selected price range
            (df['Price per sqm'].between(price_per_sqm_range[0], price_per_sqm_range[1]))  # Filter based on the selected price per sqm range
        ]

        
        col1, col2 = st.columns(2)


        with col1:
        # Display filtered dataframe with selected columns
            st.write(filtered_df[selected_columns],  unsafe_allow_html=True)

        # Create a plotly figure
            fig = px.scatter(
            filtered_df,
            x='price',
            y='Price per sqm',
            color='Area',  # Color by Suburb
            hover_name='title',
            hover_data={'Floor Area': True, 'Bedrooms': True},
            text = 'Bedrooms',
            size = 'Bedrooms'
    )
        fig.update_layout(
        clickmode='event+select',  # Enable click interaction
        legend=dict(
        orientation='v',  # Horizontal orientation
        yanchor='top',      # Anchor to the top
        y=1.1               # Position slightly above the plot
    )
)  # Enable click interaction

        with col2:
            fig.update_traces(textfont_color='white')
        # Use st.plotly_chart to display the interactive plot
            st.plotly_chart(fig, use_container_width=True)
   
    with tab2:

        def read_csv_file():
            current_directory = os.getcwd()
            if 'houseflipping' in current_directory.lower():
                # If running in the 'houseflipping' directory, read the CSV file from the GitHub URL
                file_url = 'https://raw.githubusercontent.com/Nikhil-Lakha/HouseFlipping/main/Sold-Properties/All-Sold-Properties.csv'
                df = pd.read_csv(file_url)
            else:
                # If running locally, read the CSV file from the local path
                file_path = 'C:/Users/lakha/OneDrive/Documents/House Flipping - Real Life/HouseFlipping/Sold-Properties/All-Sold-Properties.csv'
                df = pd.read_csv(file_path)

            return df

        final_df = read_csv_file()

        # Display markdown for the Sold Homes tab
        st.markdown("# List of Sold Homes")
        # Default columns to display
        default_columns = ['title', 'href','property_type', 'Bedrooms', 'Bathrooms', 'price', 'Floor Area', 'Province', 'City', 'Suburb', 'Area', 'Sold Date', 'Listing Number', 'previously listed price', 'Status']

        # Sidebar for selecting columns
        st.sidebar.title("Column Selection")

        # Filter out default columns that don't exist in the dataframe
        default_columns = [col for col in default_columns if col in final_df.columns]

        selected_columns = st.sidebar.multiselect("Select Columns", final_df.columns.tolist(), default=default_columns)

        # Filter options
        province_options = ['gauteng'] + list(final_df['Province'].unique())
        city_options = ['All']
        suburb_options = ['All']
        area_options = ['All']

        

        col1, col2, col3, col4 = st.columns(4)

        # Sidebar filters
        with col1:
            province_selected = st.selectbox('Province', province_options)

        with col2:
            if province_selected != 'All':
                city_options = ['All'] + list(final_df[final_df['Province'] == province_selected]['City'].unique())
            city_selected = st.selectbox('City', city_options)

        with col3:
            if city_selected != 'All':
                suburb_options = ['All'] + list(final_df[(final_df['Province'] == province_selected) & (final_df['City'] == city_selected)]['Suburb'].unique())
            suburb_selected = st.selectbox('Suburb', suburb_options)

        with col4:
            if suburb_selected != 'All':
                area_options = ['All'] + list(final_df[(final_df['Province'] == province_selected) & (final_df['City'] == city_selected) & (final_df['Suburb'] == suburb_selected)]['Area'].unique())
            area_selected = st.selectbox('Area', area_options)


        # Filter dataframe based on selected options and price range
        filtered_df = final_df[
            (final_df['Province'] == province_selected if province_selected != 'All' else True) &
            (final_df['City'] == city_selected if city_selected != 'All' else True) &
            (final_df['Suburb'] == suburb_selected if suburb_selected != 'All' else True) &
            (final_df['Area'] == area_selected if area_selected != 'All' else True)
        ]

        # Display the DataFrame
        st.write(filtered_df[selected_columns])



        def generate_pdf(listing_number, data):
            # Fetch data for the listing number
            listing_data = data[data['Listing Number'] == listing_number]

            # Create a PDF file
            pdf_filename = f"report_listing_{listing_number}.pdf"
            pdf_path = os.path.join(os.getcwd(), pdf_filename)

            # Define ReportLab styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            header_style = styles['Heading2']
            small_header_style = ParagraphStyle(name='SmallHeader', parent=styles['Heading2'], fontSize=11)
            body_style = styles['Normal']

            # Create a PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            content = []

            # Add main header (Title)
            main_title_text = listing_data['title'].iloc[0] if not listing_data.empty else "Main Title"
            main_title = Paragraph(main_title_text, title_style)
            content.append(main_title)

            # Add first image under the main title
            images_folder = f"C:/Users/lakha/OneDrive/Documents/House Flipping - Real Life/HouseFlipping/Sold-House-Images/{listing_number}"
            if os.path.exists(images_folder):
                image_files = sorted(glob.glob(os.path.join(images_folder, '*.jpg')))  # Assuming images are JPG format
                if image_files:
                    first_image = Image(image_files[0], width=5*inch, height=4*inch)  # Adjust width and height as needed
                    content.append(first_image)

                    # Add previously listed price as a smaller header
                    previously_listed_price = listing_data['previously listed price'].iloc[0]
                    small_header = Paragraph(f"Previously Listed Price: {previously_listed_price}", small_header_style)
                    content.append(small_header)

                    # Add Sold date
                    sold_date = listing_data['Sold Date'].iloc[0]
                    small_header = Paragraph(f"Date Sold: {sold_date}", small_header_style)
                    content.append(small_header)

                    # Add Sold date
                    listing_number = listing_data['Listing Number'].iloc[0]
                    small_header = Paragraph(f"Listing Number: {listing_number}", small_header_style)
                    content.append(small_header)

                    # Add Province, City, Suburb, and Area in a bullet point list
                    content.append(Paragraph("<b>Features:</b>", small_header_style))
                    feature_details = [
                        f"Bedrooms: {listing_data['Bedrooms'].iloc[0]}",
                        f"Bathrooms: {listing_data['Bathrooms'].iloc[0]}",
                        f"Floor Area: {listing_data['Floor Area'].iloc[0]}",
                        f"Land Area: {listing_data['Land Area'].iloc[0]}"
                    ]
                    for detail in feature_details:
                        content.append(Paragraph(f"• {detail}", body_style))
                    
                    # Add a spacer to create a space between Features and Location
                    content.append(Spacer(1, 12))  # Adjust the size as needed

                    # Add Province, City, Suburb, and Area in a bullet point list
                    content.append(Paragraph("<b>Location:</b>", small_header_style))
                    location_details = [
                        f"Province: {listing_data['Province'].iloc[0]}",
                        f"City: {listing_data['City'].iloc[0]}",
                        f"Suburb: {listing_data['Suburb'].iloc[0]}",
                        f"Area: {listing_data['Area'].iloc[0]}"
                    ]
                    for detail in location_details:
                        content.append(Paragraph(f"• {detail}", body_style))


                        # Add a spacer to create a space between Features and Location
                    content.append(Spacer(1, 27))  # Adjust the size as needed

                    # Adding key main features
                    content.append(Paragraph("<b>Key main features:</b>", small_header_style))
                    location_details = [
                        f"Key Main Features: {listing_data['key_main_features'].iloc[0]}"
                    ]
                    for detail in location_details:
                        content.append(Paragraph(f"• {detail}", body_style))

                                            # Add Province, City, Suburb, and Area in a bullet point list
                    content.append(Paragraph("<b>Holding Costs:</b>", small_header_style))
                    holding_costs = [
                        f"Levy: {listing_data['Levy'].iloc[0]}",
                        f"Rates: {listing_data['Rates'].iloc[0]}"
                    ]
                    for detail in holding_costs:
                        content.append(Paragraph(f"• {detail}", body_style))

                    


                    content.append(Spacer(1, 12))  # Adjust the size as needed
            # Add other columns as bullet points
            for column in listing_data.drop(['title', 'previously listed price', 'Province', 'City', 
                                             'Suburb', 'Area', 'Bathrooms', 'Bedrooms', 'Land Area', 'Floor Area', 'href', 
                                             'Status', 'Sold Date', 'property_type', 'main_features', 'Listing Number', 'key_main_features', 'Levy', 'Rates'], axis=1).columns:
                if not listing_data[column].isnull().iloc[0]:
                    content.append(Paragraph(f"<b>{column}:</b> {listing_data[column].iloc[0]}", body_style))

            # Add other images under the other columns
            if len(image_files) > 1:  # If there are more than one image files
                for image_file in image_files[1:]:
                    img = Image(image_file, width=5*inch, height=4*inch)  # Adjust width and height as needed
                    content.append(img)

            # Build PDF
            doc.build(content)

            return pdf_path
        
    # Get listing number input
        listing_number = st.text_input("Enter Listing Number")

        # Generate and display PDF if listing number provided
        if listing_number:
            st.markdown(f"## PDF for Listing Number: {listing_number}")
            listing_pdf_path = generate_pdf(listing_number, final_df)

            # Define CSS style for center alignment
            center_style = "<style> div.stButton > button { margin: 0 auto; display: block; }</style>"

            # Display PDF in a centered iframe
            st.markdown(
                f'<div style="text-align:center;"><iframe src="data:application/pdf;base64,{base64.b64encode(open(listing_pdf_path, "rb").read()).decode()}" width="1000" height="600"></iframe></div>',
                unsafe_allow_html=True
            )


            # Apply centering CSS style
            st.markdown(center_style, unsafe_allow_html=True)

    with tab3:
        
        def read_csv_file():
            current_directory = os.getcwd()
            if 'houseflipping' in current_directory.lower():
                # If running in the 'houseflipping' directory, read the CSV file from the GitHub URL
                file_url = 'https://raw.githubusercontent.com/Nikhil-Lakha/HouseFlipping/main/Property-Market-30-days.csv'
                df = pd.read_csv(file_url)
            else:
                # If running locally, read the CSV file from the local path
                file_path = 'C:/Users/lakha/OneDrive/Documents/House Flipping - Real Life/HouseFlipping/Property-Market-30-days.csv'
                df = pd.read_csv(file_path)

            return df

        df = read_csv_file()

        # Filter options
        province_options = ['gauteng'] + list(df['Province'].unique())
        city_options = ['All']
        suburb_options = ['All']
        area_options = ['All']

        col1, col2, col3, col4 = st.columns(4)

        # Sidebar filters
        with col1:
            province_selected = st.selectbox('All Province', province_options)

        with col2:
            if province_selected != 'All':
                city_options = ['All'] + list(df[df['Province'] == province_selected]['City'].unique())
            city_selected = st.selectbox('All City', city_options)

        with col3:
            if city_selected != 'All':
                suburb_options = ['All'] + list(df[(df['Province'] == province_selected) & (df['City'] == city_selected)]['Suburb'].unique())
            suburb_selected = st.selectbox('All Suburb', suburb_options)

        with col4:
            if suburb_selected != 'All':
                area_options = ['All'] + list(df[(df['Province'] == province_selected) & (df['City'] == city_selected) & (df['Suburb'] == suburb_selected)]['Area'].unique())
            area_selected = st.selectbox('All Area', area_options)

        # Filter dataframe based on selected options and price range
        df = df[
            (df['Province'] == province_selected if province_selected != 'All' else True) &
            (df['City'] == city_selected if city_selected != 'All' else True) &
            (df['Suburb'] == suburb_selected if suburb_selected != 'All' else True) &
            (df['Area'] == area_selected if area_selected != 'All' else True)
        ]
        

        col1, col2 = st.columns(2)

        with col1:

            # Sort the DataFrame by 'Sold Properties' column in descending order
            df = df.sort_values(by='Inventory', ascending=True)
            st.write(df)

    with tab4:
        # Add Title
        st.title("Ad Hoc reporting")
        
        # Define function to read CSV and display HTML
        def display_csv_data(df):
            pyg_html = pyg.to_html(df)
            components.html(pyg_html, height=1000, scrolling=True)
        
        # Function to load CSV data
        def load_csv_data(file_path):
            try:
                df = pd.read_csv(file_path)
                return df
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                return None
        
        # Determine CSV file paths based on the current working directory
        current_directory = os.getcwd()
        if 'houseflipping' in current_directory.lower():
            # If running in the 'houseflipping' directory, use GitHub URLs for CSV files
            sold_properties_url = 'https://raw.githubusercontent.com/Nikhil-Lakha/HouseFlipping/main/Sold-Properties/All-Sold-Properties.csv'
            listed_properties_url = 'https://raw.githubusercontent.com/Nikhil-Lakha/HouseFlipping/main/Listed-Properties/Current-Listed-Properties.csv'
        else:
            # If running locally, use local file paths for CSV files
            sold_properties_path = 'C:/Users/lakha/OneDrive/Documents/House Flipping - Real Life/HouseFlipping/Sold-Properties/All-Sold-Properties.csv'
            listed_properties_path = 'C:/Users/lakha/OneDrive/Documents/House Flipping - Real Life/HouseFlipping/Listed-Properties/Current-Listed-Properties.csv'
        
        # Button for Sold Homes
        if st.button("Sold Homes"):
            if 'houseflipping' in current_directory.lower():
                df = load_csv_data(sold_properties_url)
            else:
                df = load_csv_data(sold_properties_path)
            if df is not None:
                display_csv_data(df)
        
        # Button for Currently Listed
        if st.button("Currently Listed"):
            if 'houseflipping' in current_directory.lower():
                df = load_csv_data(listed_properties_url)
            else:
                df = load_csv_data(listed_properties_path)
            if df is not None:
                display_csv_data(df)


if __name__ == "__main__":
    main()
