import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any

# Page config
st.set_page_config(
    page_title="Knapsack Problem Solver",
    page_icon="🎒",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'items' not in st.session_state:
        st.session_state['items'] = []
    if 'next_id' not in st.session_state:
        st.session_state['next_id'] = 0

def add_item(name: str, weight: int, value: int):
    """Add a new item to the session state."""
    if name and weight and value:
        st.session_state['items'].append({
            'id': st.session_state['next_id'],
            'name': name,
            'weight': weight,
            'value': value
        })
        st.session_state['next_id'] += 1
        return True
    return False

def delete_item(item_id: int):
    """Delete an item from the session state."""
    st.session_state['items'] = [
        item for item in st.session_state['items']
        if item['id'] != item_id
    ]

def item_management_section():
    """Create the item management section of the UI."""
    st.subheader("📦 Manage Items")

    # Key for the form
    form_key = st.session_state.get('form_key', 0)

    # Input fields for new items
    with st.form(key=f"item_form_{form_key}"):
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            name = st.text_input("Item Name")
        with cols[1]:
            weight = st.number_input("Weight", min_value=1)
        with cols[2]:
            value = st.number_input("Value", min_value=1)
        with cols[3]:
            st.write("")  # Spacing
            submitted = st.form_submit_button("Add Item")
            if submitted and name and weight and value:
                st.session_state['items'].append({
                    'id': st.session_state['next_id'],
                    'name': name,
                    'weight': weight,
                    'value': value
                })
                st.session_state['next_id'] += 1
                # Increment form key to create a fresh form
                st.session_state['form_key'] = form_key + 1
                st.rerun()

    # Display current items with delete buttons
    if st.session_state['items']:
        st.write("Current Items:")
        for item in st.session_state['items']:
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                st.text(item['name'])
            with cols[1]:
                st.text(f"Weight: {item['weight']}")
            with cols[2]:
                st.text(f"Value: {item['value']}")
            with cols[3]:
                if st.button("🗑️", key=f"del_{item['id']}"):
                    delete_item(item['id'])
                    st.rerun()
    else:
        st.info("No items added yet. Add some items to get started!")

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'items' not in st.session_state:
        st.session_state['items'] = []
    if 'next_id' not in st.session_state:
        st.session_state['next_id'] = 0
    if 'form_key' not in st.session_state:
        st.session_state['form_key'] = 0
def create_parameter_inputs() -> Dict[str, Any]:
    """Create and return user input parameters with helpful tooltips."""
    st.sidebar.header("Algorithm Parameters")
    
    params = {}
    
    params['max_weight'] = st.sidebar.slider(
        "Maximum Weight 🏋️",
        min_value=5,
        max_value=100,
        value=15,
        help="Maximum weight capacity of the knapsack"
    )
    
    return params

def display_results(response: Dict[str, Any]):
    """Display the results in a clear, visually appealing way."""
    if response['total_value'] == 0 and not response['selected_items']:
        st.warning("⚠️ No valid solution found. Try adjusting the parameters or items.")
        return
    
    st.success("✅ Solution found!")
    
    # Create two columns for the results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Selected Items")
        if response['selected_items']:
            df = pd.DataFrame(response['selected_items'])
            df['value/weight'] = df['value'] / df['weight']
            st.dataframe(
                df.style.format({
                    'weight': '{:.0f}',
                    'value': '{:.0f}',
                    'value/weight': '{:.2f}'
                }),
                hide_index=True
            )
        else:
            st.info("No items selected")
    
    with col2:
        st.subheader("Summary")
        fig = go.Figure()
        
        # Add value bar
        fig.add_trace(go.Bar(
            x=['Total Value'],
            y=[response['total_value']],
            name='Value',
            marker_color='#2ecc71'
        ))
        
        # Add weight bar
        fig.add_trace(go.Bar(
            x=['Total Weight'],
            y=[response['total_weight']],
            name='Weight',
            marker_color='#e74c3c'
        ))
        
        fig.update_layout(
            title='Total Value vs Weight',
            showlegend=True,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Title and introduction
    st.title("🎒 Knapsack Problem Solver")
    st.markdown("""
    This application uses a genetic algorithm to solve the Knapsack Problem:
    given a set of items with different weights and values, find the most
    valuable combination that fits within a weight limit.
    """)
    
    # Item management section
    item_management_section()
    
    # Get parameters from sidebar
    params = create_parameter_inputs()
    
    # Add solve button
    if st.button("Solve Knapsack Problem", type="primary", disabled=len(st.session_state['items']) == 0):
        if len(st.session_state['items']) == 0:
            st.error("Please add some items first!")
            return
        
        # Add items to parameters
        params['items'] = [
            {k: v for k, v in item.items() if k != 'id'}
            for item in st.session_state['items']
        ]
        
        with st.spinner("🧮 Running genetic algorithm..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/solve",
                    json=params
                ).json()
                
                if 'error' in response:
                    st.error(f"Error: {response['error']}")
                else:
                    display_results(response)
            
            except requests.exceptions.ConnectionError:
                st.error("""
                    ⚠️ Couldn't connect to the backend server. 
                    Make sure it's running on port 5000.
                """)

if __name__ == "__main__":
    main()
