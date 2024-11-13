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

def create_parameter_inputs() -> Dict[str, Any]:
    """Create and return user input parameters with helpful tooltips"""
    st.sidebar.header("Algorithm Parameters")
    
    params = {}
    
    params['max_weight'] = st.sidebar.slider(
        "Maximum Weight 🏋️",
        min_value=5,
        max_value=30,
        value=15,
        help="Maximum weight capacity of the knapsack"
    )
    
    params['population_size'] = st.sidebar.slider(
        "Population Size 👥",
        min_value=4,
        max_value=20,
        value=6,
        step=2,
        help="Number of solutions in each generation (must be even)"
    )
    
    params['generations'] = st.sidebar.slider(
        "Number of Generations 🔄",
        min_value=10,
        max_value=1000,
        value=100,
        help="How many generations to evolve the solutions"
    )
    
    params['crossover_rate'] = st.sidebar.slider(
        "Crossover Rate 🔀",
        min_value=0.0,
        max_value=1.0,
        value=0.53,
        format="%.2f",
        help="Probability of combining two parent solutions"
    )
    
    params['mutation_rate'] = st.sidebar.slider(
        "Mutation Rate 🧬",
        min_value=0.0,
        max_value=0.1,
        value=0.013,
        format="%.3f",
        help="Probability of randomly modifying a solution"
    )
    
    return params

def display_results(response: Dict[str, Any]):
    """Display the results in a clear, visually appealing way"""
    st.success("✅ Solution found!")
    
    # Create two columns for the results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Selected Items")
        if response['selected_items']:
            df = pd.DataFrame(response['selected_items'])
            st.dataframe(
                df.style.format({
                    'weight': '{:.0f}',
                    'value': '{:.0f}'
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
    # Title and introduction
    st.title("🎒 Knapsack Problem Solver")
    st.markdown("""
    This application uses a genetic algorithm to solve the Knapsack Problem:
    given a set of items with different weights and values, find the most
    valuable combination that fits within a weight limit.
    """)
    
    # Get parameters from sidebar
    params = create_parameter_inputs()
    
    # Add solve button
    if st.button("Solve Knapsack Problem", type="primary"):
        with st.spinner("🧮 Running genetic algorithm..."):
            try:
                response = requests.post(
                    "http://localhost:5000/solve",
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