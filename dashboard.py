import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib # its essential as we are using background_gradient and colors
import warnings
warnings.filterwarnings('ignore')



# Set page configuration
st.set_page_config(page_title='SuperStore!!!', page_icon=':bar_chart:', layout='wide')

# Title of the app
st.title(' :bar_chart: Sample SuperStore EDA') # you can do if getting port error in terminal -> streamlit run .\dashboard.py --server.port 8888 or 8080
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True) # to bring the name of title to start at beggining of the page

# File uploader widget for user to upload a file
uploaded_file = st.file_uploader(': file_folder: Upload a file', type=(['csv','txt','xlsx','xls', 'csv'])) # user can upload the file

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    # os.chdir(r'C:\Users\ashra\Downloads\VS Code\streamlit_superstore')
    df = pd.read_csv('C:\\Users\\ashra\\Downloads\\VS Code\\streamlit_superstore\\Sample - Superstore.csv')

col1, col2 = st.columns((2))

df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

# getting the min and max date

startDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input('Start Date', startDate))
with col2:
    date2 = pd.to_datetime(st.date_input('End Date', endDate))

df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

st.sidebar.header('Choose your filter: ')

# create for the region
region = st.sidebar.multiselect('Pick your region', df['Region'].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]

# create fo the state
state = st.sidebar.multiselect('Pick the state from selected region', df2['State'].unique())

if not state:
    df3=df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]

# create for the city
city = st.sidebar.multiselect('Pick the city', df3['City'].unique())

# filter the data based on the Region, state and city

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df[(df["State"].isin(state)) & (df["City"].isin(city))]
elif region and city:
    filtered_df = df[(df["Region"].isin(region)) & (df["City"].isin(city))]
elif region and state:
    filtered_df = df[(df["Region"].isin(region)) & (df["State"].isin(state))]
elif city:
    filtered_df = df[df["City"].isin(city)]
else:
    filtered_df = df[(df["Region"].isin(region)) & (df["State"].isin(state)) & (df["City"].isin(city))]


category_df = filtered_df.groupby(by = ['Category'], as_index = False)['Sales'].sum()

with col1:
    st.subheader('Category wise Sales')
    fig = px.bar(category_df, x='Category', y='Sales', text=['${:,.2f}'.format(x) for x in category_df['Sales']], template='seaborn')
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader('Region wise Sales')
    fig = px.pie(filtered_df, values='Sales', names='Region', hole=0.5)
    fig.update_traces(text=filtered_df['Region'], textposition='outside')  # Corrected method name
    st.plotly_chart(fig, use_container_width=True)


# Download data based on the filtered data/charts

cl1, cl2 = st.columns(2)

with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv_category = category_df.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data', data=csv_category, file_name='Category.csv', mime='text/csv', help='Click here to download csv')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by='Region', as_index=False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap='Oranges'))
        csv_region = region.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data', data=csv_region, file_name='Region.csv', mime='text/csv', help='Click here to download csv')

filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M')

st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum()).reset_index()

fig2 = px.line(linechart, x='month_year', y='Sales', labels={'Sales': 'Amount'}, height=500, width=1000, template='gridon')
st.plotly_chart(fig2, use_container_width=True)


with st.expander('View Data of TimeSeries: '):
    st.write(linechart.T.style.background_gradient(cmap = 'Blues'))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name= 'TimeSeries.csv', mime = 'text/csv')

# create a tree map based on Region, category and sub-category

st.subheader('Hirearcial view of sales using Tree Map')

fig3 = px.treemap(filtered_df, path = ['Region', 'Category', 'Sub-Category'], values = 'Sales', hover_data = ['Sales'], color = 'Sub-Category')
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

# segment wise category wise sales

chart1, chart2 = st.columns((2))

with chart1:
    st.subheader('Segment wise sales')
    fig = px.pie(filtered_df, values = 'Sales', names = 'Segment', template= 'plotly_dark')
    fig.update_traces(text = filtered_df['Segment'], textposition = 'inside')
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise sales')
    fig = px.pie(filtered_df, values = 'Sales', names = 'Category', template= 'gridon')
    fig.update_traces(text = filtered_df['Category'], textposition = 'inside')
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(':point_right: Month wise sub-category sales summary')
with st.expander('Summary_Table'):
    df_sample = df[0:5][['Region', 'State', 'City', 'Category', 'Sales', 'Profit', 'Quantity']]
    fig = ff.create_table(df_sample, colorscale='Cividis')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('Month wise sub-Cateogry table')
    filtered_df['Month']=filtered_df['Order Date'].dt.month_name()
    sub_category_year = pd.pivot_table(data= filtered_df, values = 'Sales', index = ['Sub-Category'], columns = 'Month')
    st.write(sub_category_year.style.background_gradient(cmap='Blues'))

# Create a scatter plot

data1 = px.scatter(filtered_df, x = 'Sales', y="Profit", size= 'Quantity')
data1['layout'].update(title='Relationship Between sales and profits using scatter plot', titlefont = dict(size =20), 
                       xaxis = dict(title = 'Sales', titlefont = dict(size=19)),
                       yaxis = dict(title = 'Profit', titlefont = dict(size=19)))
st.plotly_chart(data1, use_container_width=True)

# download entire dataset with selection

with st.expander('View Data'):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap='Oranges')) # giving only top 500

# download the original dataset

csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name='Data.csv', mime='text/csv')
