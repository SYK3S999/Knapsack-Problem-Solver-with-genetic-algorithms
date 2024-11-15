# 🎒 Knapsack Problem Solver

A web application that solves the Knapsack Problem using genetic algorithms. The project consists of a Flask backend API for computational logic and a Streamlit frontend for user interaction.

## Features

- Interactive web interface for managing items and parameters
- Genetic algorithm implementation for optimizing item selection
- Real-time visualization of results using Plotly
- RESTful API for solving knapsack problems
- Cross-Origin Resource Sharing (CORS) support

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone the repository:

```bash
git clone [your-repository-url]
cd knapsack-solver
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Required packages:

- Flask
- Flask-CORS
- Streamlit
- Plotly
- Pandas
- Requests

## Usage

### Starting the Application

1. Start the Flask backend server:

```bash
python app.py
```

The API server will run on <http://127.0.0.1:5000>

2. In a new terminal, launch the Streamlit frontend:

```bash
streamlit run frontend.py
```

The web interface will be accessible at <http://localhost:8501>

### Using the Application

1. Add items using the item management interface:
   - Enter item name
   - Specify weight
   - Set value
   - Click "Add Item"

2. Configure algorithm parameters in the sidebar:
   - Maximum Weight (5-100)

3. Click "Solve Knapsack Problem" to run the algorithm

4. View results:
   - Selected items table
   - Total value and weight visualization
   - Value/weight ratio analysis

## API Reference

### POST /solve

Solves the knapsack problem using genetic algorithms.

#### Request Body

```json
{
    "max_weight": integer,
    "items": [
        {
            "name": string,
            "weight": integer,
            "value": integer
        }
    ]
}
```

#### Response

```json
{
    "selected_items": [
        {
            "name": string,
            "weight": integer,
            "value": integer
        }
    ],
    "total_value": integer,
    "total_weight": integer
}
```

## Technical Details

### Backend (app.py)

- Implements genetic algorithm for knapsack problem optimization
- Uses dataclasses for structured data handling
- Includes classes for:
  - `Item`: Represents individual items
  - `Individual`: Represents a possible solution
- Features genetic algorithm operations:
  - Selection (tournament selection)
  - Crossover
  - Mutation
  - Elite preservation

### Frontend (frontend.py)

- Built with Streamlit for interactive UI
- Features:
  - Dynamic item management
  - Parameter configuration
  - Real-time result visualization
  - Error handling and user feedback
- Uses Plotly for data visualization
- Implements session state management

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
