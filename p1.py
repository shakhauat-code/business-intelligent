import streamlit as st
import plotly.graph_objects as go
import pandas as pd


st.set_page_config(layout='wide')

df = pd.read_csv('absdata.csv')
bdex_pass = df['Bdex_Pass'].unique().tolist()
bdex_pass = {i:num for i, num in enumerate(bdex_pass)}
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-bottom:0%
    }
    </style>
    <h1 class="centered-title">ABS BI Portal</h1>
    """,
    unsafe_allow_html=True
)


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'Login'


def login_page():

    st.subheader("Login Page")
    username = st.text_input("BDEx Username").strip().lower()
    password = st.text_input("Password", type="password").strip()
    login_button = st.button("Log In")

    if login_button:
        if int(password) in bdex_pass.values():
            st.session_state.logged_in = True
            st.session_state.page = 'Home'
            st.session_state.username = password
            st.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")


def home_page():
    pwd = df['BDEx_Name'][df['Bdex_Pass']==int(st.session_state.username)].unique()[0]
    st.subheader(f"Welcome, {pwd}!")

    st.markdown('')
    st.markdown('')
    active_bdex = pwd

    df1 = df

    years = sorted(df1.Year.unique())
    months = df1.Month.unique().tolist()
    select_ag, col1, col2 = st.columns([.5, .5, 1])
    selected_years = col1.multiselect('Select years', years, default=years)
    selected_months = col2.multiselect('Select months', months, default=months)
    st.markdown('')

    df2 = df1[df1.BDEx_Name == active_bdex]
    df2 = df2[df2['Year'].isin(selected_years)]
    df2 = df2[df2['Month'].isin(selected_months)]

    ag_id = df2.Agent_id.unique().tolist()

    with select_ag:
        options = ["All Agents"] + ag_id
        selected_ag_id = st.selectbox(f"Total Agents, {len(ag_id)}", options, index=0)

        if selected_ag_id != options[0]:
            df2 = df2[df2['Agent_id']==selected_ag_id]

    st.markdown('')

    no_of_acc = df2.No_of_Account.sum()
    dep_acc_count = df2.deposit_acc_count.sum()
    deposit_amt = float("{:.2f}".format(df2.deposit.sum()))
    trans_count = df2.trans_count.sum()
    trans_amount = float("{:.2f}".format(df2.trans_amount.sum()))

    data = {
        "value": [no_of_acc, dep_acc_count, deposit_amt, trans_count, trans_amount],
        "metric": ['no_of_acc', 'dep_acc_count', 'deposit_amt', 'trans_count', 'trans_amount'],
        "color": ["#4caf50", "#f44336", "#2196f3", "#ff9800", "#BB0293"]
    }
    def card_view(title, value, color):
        card_html = f"""
        <div style="
            background-color: {color}; 
            border-radius: 15px; 
            padding: 5px;  
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
            display: flex; 
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 125px;
            width: 100%;
        ">
            <div style="text-align: left;">
                <h4 style="margin: 0; color: white; font-size: .92em;">{title}</h4>
                <p style="margin: 0; font-size: 1.6em; color: white;">{value:,}</p>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    col3, col4, col5, col6 = st.columns(4)
    col7, a, b, c = st.columns(4)
    with col3:
        card_view(
            title=data["metric"][0],
            value=data["value"][0],
            color=data["color"][0]
        )
        st.write('')
    with col4:
        card_view(
            title=data["metric"][1],
            value=data["value"][1],
            color=data["color"][1]
        )
        st.write('')
    with col5:
        card_view(
            title=data["metric"][2],
            value=data["value"][2],
            color=data["color"][2]
        )
        st.write('')
    with col6:
        card_view(
            title=data["metric"][3],
            value=data["value"][3],
            color=data["color"][3]
        )
        st.write('')
    with col7:
        card_view(
            title=data["metric"][4],
            value=data["value"][4],
            color=data["color"][4]
        )
        st.write('')


    st.markdown('')
    st.markdown('')

    agent_ac = df2.groupby('Agent_id')['No_of_Account'].sum().reset_index()
    agent_dep = df2.groupby('Agent_id')['deposit'].sum().reset_index()


    col8, spacer, col9 = st.columns([1, .07, 1])

    with col8:
        # Plotly bar chart
        fig = go.Figure()
        # Add bar trace with data labels
        fig.add_trace(go.Bar(
            x=agent_ac['Agent_id'],
            y=agent_ac['No_of_Account'],
            text=agent_ac['No_of_Account'],  # Add data labels
            textposition='auto',  # Automatic positioning of labels
            name='Number of Accounts',
            marker=dict(color='#BB0293')
        ))
        # Update layout to add x-axis slider with range
        fig.update_layout(
            title='Number of Accounts by Agent ID',
            xaxis=dict(
                title='Agent ID',
                rangeslider=dict(visible=True),
                range=[-0.5, len(ag_id)-1],  # Initially show the first 10 bars
                type='category'
            ),
            yaxis=dict(title='Number of Accounts'),
            template='plotly_white'
        )
        # Display chart in Streamlit
        st.plotly_chart(fig)

    with col9:
        # Plotly bar chart
        fig = go.Figure()
        # Add bar trace with data labels
        fig.add_trace(go.Bar(
            x=agent_dep['Agent_id'],
            y=agent_dep['deposit'],
            text=agent_dep['deposit'],  # Add data labels
            textposition='auto',  # Automatic positioning of labels
            name='Number of Accounts',
            marker=dict(color='#BB0293')
        ))
        # Update layout to add x-axis slider with range
        fig.update_layout(
            title='Deposit Amount by Agent ID',
            xaxis=dict(
                title='Agent ID',
                rangeslider=dict(visible=True),
                range=[-0.5, len(ag_id)-1],  # Initially show the first 10 bars
                type='category'
            ),
            yaxis=dict(title='Deposit Amount'),
            template='plotly_white'
        )
        # Display chart in Streamlit
        st.plotly_chart(fig)

    st.markdown('')

    col10, spacer, col11 = st.columns([1, .07, 1])
    with col10:
        fig = go.Figure()

        # Add donut trace with data labels
        fig.add_trace(go.Pie(
            labels=agent_dep['Agent_id'],  # Labels for each donut section
            values=agent_dep['deposit'],  # Values for each donut section
            textinfo='label+percent',  # Show both label and percentage
            textposition='inside',  # Text position inside the donut sections
            marker=dict(colors=['#FFA07A', '#20B2AA', '#87CEFA', '#FF69B4', '#FFD700']),  # Example colors
            hoverinfo='label+value',  # Hover information shows label and value
            hole=0.4  # Size of the hole in the middle
        ))

        # Update layout
        fig.update_layout(
            title='Deposit Amount by Agent ID',
            template='plotly_white'
        )

        # Display chart in Streamlit
        st.plotly_chart(fig)


    st.write(df2.reset_index(drop=True))

    st.title('')
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.page = 'Login'
        st.experimental_rerun()

# Navigation based on login status
if st.session_state.logged_in:
    if st.session_state.page == 'Home':
        home_page()
    else:
        st.session_state.page = 'Home'
        st.experimental_rerun()
else:
    login_page()
