import streamlit as st  # Import the Streamlit library for building web apps.
import plotly.express as px  # Import Plotly Express for creating interactive charts.
import pandas as pd  # Import pandas for data manipulation and analysis.
import matplotlib  # Import matplotlib, useful for its colormap features even if not explicitly used for plotting here.
import warnings  # Import the warnings library to manage warnings.

# Disable all warnings using the warnings library.
warnings.filterwarnings('ignore')

# Configure the main settings of the Streamlit page, such as title and layout options.
st.set_page_config(page_title='SuperStore!!!', page_icon=':bar_chart:', layout='wide')

# Set the title of the web application, including an emoji as part of the title.
st.title(' :bar_chart: Sample SuperStore EDA')

# Modify HTML/CSS directly to adjust padding at the top of the page container.
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# File uploader that allows users to upload files in specific formats.
uploaded_file = st.file_uploader(':file_folder: Upload a file', type=['csv', 'txt', 'xlsx', 'xls', 'csv'])

# Conditional that checks if a file has been uploaded.
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)  # If file uploaded, read into a DataFrame.
else:
    # Default data loading if no file is uploaded. Path is specific and needs modification for general use.
    df = pd.read_csv('C:\\Users\\ashra\\Downloads\\VS Code\\streamlit_superstore\\Sample - Superstore.csv')

# Split the Streamlit layout into two columns with a specified width ratio.
col1, col2 = st.columns((2))

# Convert the 'Order Date' column to datetime format, handle errors coercively.
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

# Extract minimum and maximum date from the 'Order Date' column.
startDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

# Create date input widgets in each column for selecting a date range.
with col1:
    date1 = pd.to_datetime(st.date_input('Start Date', startDate))
with col2:
    date2 = pd.to_datetime(st.date_input('End Date', endDate))

# Filter the DataFrame based on the selected date range.
df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

# Add a header in the sidebar for filter options.
st.sidebar.header('Choose your filter: ')

# Create a multiselect widget in the sidebar for selecting regions.
region = st.sidebar.multiselect('Pick your region', df['Region'].unique())

# Conditional filtering based on selected regions.
if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]

# Create another multiselect widget for states based on filtered or unfiltered data.
state = st.sidebar.multiselect('Pick the state from selected region', df2['State'].unique())

# Further conditional filtering based on selected states.
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]

# Similar multiselect for cities.
city = st.sidebar.multiselect('Pick the city', df3['City'].unique())

# Comprehensive filtering logic to handle combinations of region, state, and city selections.
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

# Group the filtered DataFrame by 'Category' and calculate the sum of 'Sales'.
category_df = filtered_df.groupby(by=['Category'], as_index=False)['Sales'].sum()

# Plotting and display logic follows similar patterns, involving Plotly charts and Streamlit widgets for interactivity and data visualization.
# Further code is focused on plotting, displaying, and downloading various visualizations and data sets as per user selections.

with col1:
    # Display a subheader for a specific visualization category.
    st.subheader('Category wise Sales')
    # Create a bar chart using Plotly Express for sales by category.
    fig = px.bar(category_df, x='Category', y='Sales', text=['${:,.2f}'.format(x) for x in category_df['Sales']], template='seaborn')
    # Display the bar chart within the Streamlit container and adjust its width to match the container's width.
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    # Display a subheader for region-wise sales.
    st.subheader('Region wise Sales')
    # Create a pie chart using Plotly Express to display sales by region.
    fig = px.pie(filtered_df, values='Sales', names='Region', hole=0.5)
    # Update the text labels to display outside of the chart elements.
    fig.update_traces(text=filtered_df['Region'], textposition='outside')
    # Display the pie chart in the Streamlit app, matching the container's width.
    st.plotly_chart(fig, use_container_width=True)

# Download buttons and data display within expandable Streamlit containers.
cl1, cl2 = st.columns(2)

with cl1:
    # Use an expander to toggle visibility of category data and download option.
    with st.expander("Category_ViewData"):
        # Apply a background gradient to the category DataFrame display.
        st.write(category_df.style.background_gradient(cmap='Blues'))
        # Convert the category DataFrame to a CSV format.
        csv_category = category_df.to_csv(index=False).encode('utf-8')
        # Provide a button to download the category data as CSV.
        st.download_button('Download Data', data=csv_category, file_name='Category.csv', mime='text/csv', help='Click here to download csv')

with cl2:
    # Similar expander setup for region data viewing and downloading.
    with st.expander("Region_ViewData"):
        # Group data by 'Region' and sum up the sales, displaying it with a style.
        region = filtered_df.groupby(by='Region', as_index=False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap='Oranges'))
        # Convert the grouped data to CSV format for download.
        csv_region = region.to_csv(index=False).encode('utf-8')
        # Download button for region data.
        st.download_button('Download Data', data=csv_region, file_name='Region.csv', mime='text/csv', help='Click here to download csv')

# Convert 'Order Date' to a Period object at a monthly frequency, adding as a new column.
filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M')

# Display a subheader for time series analysis.
st.subheader('Time Series Analysis')

# Aggregate sales data by month and year, and reset index for plotting.
linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum()).reset_index()

# Create a line chart with Plotly Express to visualize sales over time.
fig2 = px.line(linechart, x='month_year', y='Sales', labels={'Sales': 'Amount'}, height=500, width=1000, template='gridon')
# Display the line chart in Streamlit, using the full width of the container.
st.plotly_chart(fig2, use_container_width=True)

# Data viewing and downloading for time series data within an expander.
with st.expander('View Data of TimeSeries: '):
    # Apply a background gradient to the transposed line chart data for display.
    st.write(linechart.T.style.background_gradient(cmap = 'Blues'))
    # Convert the line chart data to CSV format for downloading.
    csv = linechart.to_csv(index=False).encode('utf-8')
    # Provide a button to download the time series data as CSV.
    st.download_button('Download Data', data = csv, file_name= 'TimeSeries.csv', mime = 'text/csv')

# Continue with additional visualizations and functionalities in a similar detailed manner.

# Tree map visualization to provide a hierarchical view of sales data.
st.subheader('Hirearcial view of sales using Tree Map')
# Create a tree map with Plotly Express using the filtered DataFrame.
# Paths determine the hierarchy of aggregation: first by Region, then Category, then Sub-Category.
fig3 = px.treemap(filtered_df, path=['Region', 'Category', 'Sub-Category'], values='Sales', hover_data=['Sales'], color='Sub-Category')
# Customize the layout dimensions of the tree map.
fig3.update_layout(width=800, height=650)
# Display the tree map in the Streamlit app, using the container's width.
st.plotly_chart(fig3, use_container_width=True)

# Segment and category-wise sales visualizations using pie charts.
chart1, chart2 = st.columns((2))

with chart1:
    # Display a subheader for segment-wise sales visualization.
    st.subheader('Segment wise sales')
    # Create a pie chart for sales data by segment using Plotly Express.
    fig = px.pie(filtered_df, values='Sales', names='Segment', template='plotly_dark')
    # Update text labels to appear inside the chart slices.
    fig.update_traces(text=filtered_df['Segment'], textposition='inside')
    # Display the pie chart within the Streamlit container.
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    # Display a subheader for category-wise sales visualization.
    st.subheader('Category wise sales')
    # Create another pie chart for sales data by category using Plotly Express.
    fig = px.pie(filtered_df, values='Sales', names='Category', template='gridon')
    # Update text labels to appear inside the chart slices.
    fig.update_traces(text=filtered_df['Category'], textposition='inside')
    # Display the pie chart within the Streamlit container.
    st.plotly_chart(fig, use_container_width=True)

# Importing Plotly Figure Factory, used for creating styled data tables.
import plotly.figure_factory as ff
# Display a subheader indicating the month-wise sub-category sales summary.
st.subheader(':point_right: Month wise sub-category sales summary')
# An expander for showing summary tables and enabling interaction.
with st.expander('Summary_Table'):
    # Sample data from the DataFrame for summary purposes.
    df_sample = df[0:5][['Region', 'State', 'City', 'Category', 'Sales', 'Profit', 'Quantity']]
    # Create a table using Figure Factory, which offers more styling options.
    fig = ff.create_table(df_sample, colorscale='Cividis')
    # Display the created table within the Streamlit app.
    st.plotly_chart(fig, use_container_width=True)

    # Additional markdown for clarifying the content of the summary.
    st.markdown('Month wise sub-Cateogry table')
    # Pivot table to analyze sub-category sales across different months.
    filtered_df['Month'] = filtered_df['Order Date'].dt.month_name()  # Extract the month name from the date.
    sub_category_year = pd.pivot_table(data=filtered_df, values='Sales', index=['Sub-Category'], columns='Month')
    # Display the pivot table with a style.
    st.write(sub_category_year.style.background_gradient(cmap='Blues'))

# Scatter plot to analyze the relationship between sales and profits.
data1 = px.scatter(filtered_df, x='Sales', y="Profit", size='Quantity', labels={'Sales': 'Total Sales', 'Profit': 'Total Profit'})
# Update the layout to include titles and font sizes for better readability.
data1['layout'].update(title='Relationship Between sales and profits using scatter plot', titlefont=dict(size=20),
                       xaxis=dict(title='Sales', titlefont=dict(size=19)),
                       yaxis=dict(title='Profit', titlefont=dict(size=19)))
# Display the scatter plot in the Streamlit app, using the container's width.
st.plotly_chart(data1, use_container_width=True)

# An expander for viewing data and providing a downloadable link.
with st.expander('View Data'):
    # Display a portion of the filtered data styled with a background gradient.
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap='Oranges'))  # Showing only top 500 rows, skipping some columns for brevity.

# Option to download the entire dataset with the applied selections.
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name='Data.csv', mime='text/csv')
