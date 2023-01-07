import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# For getting slices of demographic combinations
@st.cache
def get_slice_membership(df, school_types = [], grades = [], sexes = [], outreach_channels = [], age_range = []):
    """
    Implement a function that computes which rows of the given dataframe should
    be part of the slice, and returns a boolean pandas Series that indicates 0
    if the row is not part of the slice, and 1 if it is part of the slice.
    
    In the example provided, we assume genders is a list of selected strings
    (e.g. ['Male', 'Transgender']). We then filter the labels based on which
    rows have a value for gender that is contained in this list. You can extend
    this approach to the other variables based on how they are returned from
    their respective Streamlit components.
    """
    labels = pd.Series([1] * len(df), index=df.index)

    if school_types:
        labels &= df['Do you attend public or private school?'].isin(school_types)
    if grades:
        labels &= df['Grade'].isin(grades)
    if sexes:
        labels &= df['school_level'].isin(sexes)
    if outreach_channels:
        labels &= df['How did you hear about the camp?'].isin(outreach_channels)
    if age_range is not None:
        labels &= df['Age'] >= age_range[0]
        labels &= df['Age'] <= age_range[1]
        
    return labels

# Start of page
#st.image("yiya.webp", width=100)
st.title("BETA Camp Entrance Survey Responses")
st.write(
    """
    This is a prototype of a dashboard to help BETA camp comunicate the impact of their programs through data. 
    For now this prototype uses the entrance survey results from 2017. We hope to incorporate data from more
    additional years to communicate how BETA is changing students perception of STEM and what demographics of 
    student are particpating in BETA Camp.  
    """
)

@st.cache  # add caching so we load the data only once
def load_data():
    # Load the yiya data from assessments-questions.cleaned.csv
    file_name = "data/entrance_survey_2017_clean.csv"
    return pd.read_csv(file_name)

df = load_data()


#st.header("Why do different demographics engage with Yiya?")

# Demographics



## Selection Dropdowns
cols = st.columns(5)
with st.sidebar:
    st.markdown("# Modify demographics")
    st.write(
    """
    Use the selection to restrict visualizations to demographics of interest. 
    For example, female students in public school.
    """
    )
  
    school_types = st.multiselect('School Type', df['Do you attend public or private school?'].unique())
    grades = st.multiselect('Grade', options=df['Grade'].sort_values().unique())
    sexes = st.multiselect('Sex', df['Gender'].unique())
    outreach_channels = st.multiselect('Outreach Channel', df['How did you hear about the camp?'].unique())

    #Age range slider
    age_range = st.slider('Age',
                        min_value=int(df['Age'].min()),
                        max_value=int(df['Age'].max()),
                        value=(int(df['Age'].min()), int(df['Age'].max()))
                        )

slice_labels = get_slice_membership(df, school_types, grades, sexes, outreach_channels, age_range)
df = df[slice_labels]
#Raw data
show_raw_data = st.checkbox('Show raw data')

if show_raw_data:
    st.write(df)

#Gender and School Type
gender_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("count()"),
    y= alt.Y("Gender"),
    color="Do you attend public or private school?",
).properties(
    width=600
).properties(
    title="Gender Distribution by Public/Private School"
)

st.write(gender_chart)

### OPINIONS
st.markdown("# What are student opinions of STEM?")



# Rating Questions
rating_questions = [
    "How would you rate your level of interest in engineering/technology?",
    "How well do you think you understand what engineers do?",
    "On a scale of 1 to 10 how would you rate your ability in Math?",
    "On a scale of 1 to 10 how would you rate your ability in Science?"
]

opinion_charts = alt.vconcat()
for y_encoding in rating_questions:
    opinion_chart = alt.Chart(df).mark_bar().encode(
        y='Gender:O',
        x=alt.X("average({})".format(y_encoding), title="Average"),
        color="Gender",
    ).properties(
        title=y_encoding
    )
    opinion_charts&= opinion_chart

opinion_charts

# ratings1_chart = alt.Chart(df).mark_bar().encode(
#     x='Gender:O',
#     y=alt.Y('average(How would you rate your level of interest in engineering/technology?):Q', title="Averages"),
#     color="Gender",
    
# ).properties(
#     title="Interest in STEM"
# )
# ratings2_chart = alt.Chart(df).mark_bar().encode(
#     x='Gender:O',
#     y=alt.Y('average(How well do you think you understand what engineers do?):Q', title="Averages"),
#     color ="Gender"
# ).properties(
#     title="Understanding of Eng Roles"
# )


# ratings_layered = alt.hconcat(ratings1_chart, ratings2_chart)
# st.write(ratings_layered)

st.markdown("# How does average Interest in STEM change by grade level?")

grade_corr_chart2 = alt.Chart(df).mark_bar().encode(
    x=alt.X("Grade:N"),
    y=alt.Y('average(How would you rate your level of interest in engineering/technology?):Q', title=" Avg Interest in STEM"),
)
grade_corr_chart2 

grade_corr_chart = alt.Chart(df).mark_point(size=60).encode(
    x=alt.X("Grade:N"),
    y=alt.Y('average(How would you rate your level of interest in engineering/technology?):Q', title="Avg Interest in STEM"),
    color=alt.Color('Gender:N', scale=alt.Scale(scheme='dark2')),
    size=alt.Size("count()"),
).properties(
    width= 400,
    height=400,
    title="Average Interest in STEM by Grade"
).interactive()
grade_corr_chart

st.markdown("""
    ## Insight 🎯
    
    Girls interest in STEM seem to lower over time as they progress in school"""
)




# st.metric("People in chosen demographics", len(df))

# # Charts
# gender_brush = alt.selection_multi(fields=['gender'])
# # Showing percentages reference:
# # https://stackoverflow.com/questions/56358977/how-to-show-a-histogram-of-percentages-instead-of-counts-using-altair
# why_chart = alt.Chart(df).transform_filter(gender_brush).transform_joinaggregate(
#     total='count()'
# ).transform_calculate(
#     pct='1 / datum.total'
# ).mark_bar().encode(
#     x="count()",
#     y=alt.Y("why", title="Why do Yiya Airscience?", sort=["Pass exam", "Entrepreneurship/Make money", "Learn science/tech", "Help people", "None of above", "null"]),
#     #color="why",
#     tooltip=[alt.Tooltip("count()", title="Absolute count"), alt.Tooltip("sum(pct):Q", title="Percentage", format='.1%')]
# )

# gender_chart = alt.Chart(df).mark_bar().transform_joinaggregate(
#     total='count()'
# ).transform_calculate(
#     pct='1 / datum.total'
# ).encode(
#     x=alt.X("count()"),
#     y=alt.Y("gender"),
#     tooltip=[alt.Tooltip("count()", title="Absolute count"), alt.Tooltip("sum(pct):Q", title="Percentage", format='.1%')],
#     color=alt.condition(gender_brush, alt.value('steelblue'), alt.value('lightgray'))
# ).add_selection(gender_brush)

# love_stem_chart = alt.Chart(df).mark_bar().transform_filter(gender_brush).transform_joinaggregate(
#     total='count()'
# ).transform_calculate(
#     pct='1 / datum.total'
# ).encode(
#     x=alt.X("count()"),
#     y=alt.Y("love_for_stem", title="Love for STEM?", sort=["Definitely", "Not sure", "Never", "null"]),
#     tooltip=[alt.Tooltip("count()", title="Absolute count"), alt.Tooltip("sum(pct):Q", title="Percentage", format='.1%')],
# )

# job_interest_chart = alt.Chart(df).mark_bar().transform_filter(gender_brush).transform_joinaggregate(
#     total='count()'
# ).transform_calculate(
#     pct='1 / datum.total'
# ).encode(
#     x=alt.X("count()"),
#     y=alt.Y("job_interest", title="Interested in a job in STEM?", sort=["Definitely", "Not sure", "Never", "null"]),
#     tooltip=[alt.Tooltip("count()", title="Absolute count"), alt.Tooltip("sum(pct):Q", title="Percentage", format='.1%')],
# )

# df_no_neighborhood_null = df[df['neighborhood_type'].notna()]

# lang_loc_chart = alt.Chart(df_no_neighborhood_null).mark_rect().transform_filter(gender_brush).encode(
#     x=alt.X("preferred_language", title="Preferred Language"),
#     y=alt.Y("neighborhood_type", title="Neighborhood Type", sort=["city","town center","village","refugee camp"]),
#     color=alt.Color("count()"),
#     tooltip=[alt.Tooltip("count()", title="Count")],
# ).properties(
#     height=100,
#     width=400
# )

# st.write(gender_chart & why_chart  & love_stem_chart & job_interest_chart & lang_loc_chart)

# # Original dataframe
# st.write("Let's look at our raw data.")

# st.write(df)

st.markdown("Learn more about BETA at our [website](https://www.wearebeta.co).")
