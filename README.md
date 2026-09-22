# Banking Customer Support AI Agent - MultiAgent Architecture

A comprehensive multi-agent AI system for banking customer support that handles message classification, personalized responses, and ticket tracking.

## Project Overview

This project implements a multi-agent GenAI system tailored for banking customer support workflows. The system reduces manual effort, enhances customer satisfaction, and ensures timely response to support-related feedback and queries.

## Features

### Part 1: Multi-Agent Design and Execution Logic

1. **Classifier Agent**
   - Categorizes incoming user messages into:
     - Positive Feedback
     - Negative Feedback
     - Query
   - Routes messages to appropriate downstream agents
   - **LLM Integration**: Uses OpenRouter API for intelligent classification with fallback to rule-based

2. **Feedback Handler Agent**
   - **Positive Feedback**: Generates personalized thank-you messages using LLM
   - **Negative Feedback**: Creates support tickets and generates empathetic responses using LLM

3. **Query Handler Agent**
   - Extracts ticket numbers from user messages
   - Queries the support database for ticket status
   - Returns formatted status updates using LLM for personalization

### Part 2: LLMOps with Evaluation & UI

4. **Model Evaluation**
   - QA-based scoring for response quality
   - Test case coverage for classification logic
   - Agent routing success rate evaluation

5. **Streamlit UI**
   - Interactive dashboard for agent interaction
   - Real-time classification and response display
   - Historical query viewing and logs
   - Test scenarios for each agent role
   - API key configuration interface

6. **Logging and Debugging**
   - Prompt traces and classification output
   - Ticket action logs
   - Agent success/failure rate tracking

### OpenRouter API Integration

The system now supports OpenRouter API for enhanced LLM capabilities:
- **Intelligent Classification**: More accurate message categorization
- **Personalized Responses**: Context-aware, empathetic customer interactions
- **Flexible Model Selection**: Support for multiple LLM models via OpenRouter
- **Graceful Fallback**: Automatic fallback to rule-based system if API unavailable

## Project Structure

```
banking_customer_support/
├── app.py                      # Streamlit UI application
├── multi_agent_system.py       # Main orchestration system
├── classifier_agent.py         # Message classification agent
├── feedback_handler_agent.py   # Feedback processing agent
├── query_handler_agent.py      # Query processing agent
├── database.py                 # SQLite database management
├── evaluation.py               # Evaluation framework
├── test_system.py              # Test script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd banking_customer_support
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenRouter API (optional but recommended):**
   - Copy `.env.example` to `.env`
   - Add your OpenRouter API key to the `.env` file
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```
   
   You can get your API key from [OpenRouter.ai](https://openrouter.ai/)
   
   Without API key configuration, the system will use rule-based classification and template responses.

## Usage

### Running the Streamlit UI

```bash
streamlit run app.py
```

The UI will open in your browser with four main sections:

1. **Agent Interaction**: Process customer messages and view agent responses
2. **Evaluation Dashboard**: Run comprehensive agent evaluations
3. **Database View**: View and manage support tickets
4. **Logs & Debugging**: View interaction logs and system statistics

### Running Tests

```bash
python test_system.py
```

This will run:
- Basic functionality tests for all agents
- Comprehensive evaluation framework tests
- Display system statistics and database contents

### Programmatic Usage

```python
from multi_agent_system import MultiAgentSystem

# Initialize the system
system = MultiAgentSystem()

# Process a customer message
result = system.process_message(
    customer_name="John Doe",
    message="Thanks for resolving my credit card issue."
)

print(f"Response: {result['response']}")
print(f"Classification: {result['classification']}")
print(f"Agent Used: {result['agent_used']}")
```

## Sample Use Cases

### Example 1: Positive Feedback
**Input:** "Thanks for sorting out my net banking login issue."
**Agent Path:** Classifier → Positive Feedback Handler
**Response:** "Thank you for your kind words! We're happy to support you."

### Example 2: Negative Feedback
**Input:** "My debit card replacement still hasn't arrived."
**Agent Path:** Classifier → Negative Feedback Handler
**Response:** "We apologize for the inconvenience. A new ticket #784521 has been created. Our support team will look into this promptly."

### Example 3: Query
**Input:** "Could you check the status of ticket 650932?"
**Agent Path:** Classifier → Query Handler
**Response:** "Your ticket #650932 is currently marked as: Resolved."

## Database Schema

The system uses SQLite with the following schema:

```sql
CREATE TABLE support_tickets (
    ticket_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    message TEXT,
    classification TEXT,
    status TEXT DEFAULT 'Unresolved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Evaluation Metrics

The evaluation framework assesses:

- **Classification Accuracy**: How well messages are categorized
- **Agent Routing Accuracy**: Correct agent selection
- **Ticket Creation Accuracy**: Proper ticket handling
- **Response Quality**: Personalization, empathy, and clarity
- **Overall Success Rate**: Combined performance metric

## Agent Architecture

```
User Message
    ↓
Classifier Agent
    ↓
    ├─→ Positive Feedback → Feedback Handler Agent → Thank You Response
    ├─→ Negative Feedback → Feedback Handler Agent → Ticket Creation + Empathetic Response
    └─→ Query → Query Handler Agent → Ticket Status Response
```

## Configuration

- **Database**: SQLite (support_tickets.db)
- **Ticket IDs**: 6-digit unique numbers (100000-999999)
- **Classification**: Keyword-based with confidence scoring
- **Response Generation**: Template-based with randomization

## Future Enhancements

- Integration with actual banking APIs
- Advanced sentiment analysis using ML models
- Multi-language support
- Real-time agent learning and improvement
- Integration with customer CRM systems
- Advanced analytics and reporting

## Troubleshooting

**Database Issues:**
- Delete `support_tickets.db` to reset the database
- Use the "Database View" page in the UI to manage tickets

**Classification Issues:**
- Check the keyword lists in `classifier_agent.py`
- Adjust confidence thresholds if needed

**UI Issues:**
- Ensure all dependencies are installed
- Check that Streamlit is running on the correct port

## License

This project is part of a capstone project for educational purposes.

## Author

Built as a capstone project demonstrating multi-agent AI architecture for banking customer support.