import streamlit as st
import pandas as pd
from multi_agent_system import MultiAgentSystem
from evaluation import AgentEvaluator
from config import Config
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Banking Customer Support AI Agent",
    page_icon="🏦",
    layout="wide"
)

# Initialize the multi-agent system
@st.cache_resource
def initialize_system():
    return MultiAgentSystem()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3a8a;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">🏦 Banking Customer Support AI Agent</div>', unsafe_allow_html=True)

# Initialize system
system = initialize_system()

# Sidebar for navigation and configuration
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Agent Interaction", "Evaluation Dashboard", "Database View", "Logs & Debugging", "Settings"])

# Settings page
if page == "Settings":
    st.header("System Settings")
    
    st.subheader("OpenRouter API Configuration")
    
    # API Key input
    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        value=Config.OPENROUTER_API_KEY or "",
        help="Enter your OpenRouter API key to enable LLM-powered classification and responses"
    )
    
    # Model selection
    model_options = [
        "anthropic/claude-3-haiku",
        "anthropic/claude-3-sonnet", 
        "anthropic/claude-3-opus",
        "openai/gpt-4",
        "openai/gpt-3.5-turbo",
        "meta-llama/llama-3-8b-instruct"
    ]
    
    selected_model = st.selectbox(
        "Select Model",
        options=model_options,
        index=model_options.index(Config.OPENROUTER_MODEL) if Config.OPENROUTER_MODEL in model_options else 0,
        help="Choose the LLM model to use for classification and response generation"
    )
    
    # Toggle LLM usage
    use_llm = st.checkbox(
        "Enable LLM Features",
        value=Config.USE_LLM,
        help="When enabled, the system will use OpenRouter API for intelligent classification and personalized responses"
    )
    
    # Save settings
    if st.button("Save Settings", type="primary"):
        # Update environment variables
        os.environ["OPENROUTER_API_KEY"] = api_key
        os.environ["OPENROUTER_MODEL"] = selected_model
        os.environ["USE_LLM"] = str(use_llm).lower()
        
        # Update .env file if it exists
        try:
            env_path = ".env"
            env_lines = []
            
            # Read existing .env file
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add configuration
            config_updates = {
                "OPENROUTER_API_KEY": api_key,
                "OPENROUTER_MODEL": selected_model,
                "USE_LLM": str(use_llm).lower()
            }
            
            # Update existing lines or add new ones
            updated_lines = []
            existing_keys = set()
            
            for line in env_lines:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    if key in config_updates:
                        updated_lines.append(f"{key}={config_updates[key]}\n")
                        existing_keys.add(key)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            # Add new configuration keys
            for key, value in config_updates.items():
                if key not in existing_keys:
                    updated_lines.append(f"{key}={value}\n")
            
            # Write updated .env file
            with open(env_path, 'w') as f:
                f.writelines(updated_lines)
            
            st.success("Settings saved successfully! Please restart the application for changes to take effect.")
            st.info("Click 'Restart' in the top right corner or run `streamlit run app.py` again.")
            
        except Exception as e:
            st.error(f"Error saving settings: {e}")
    
    # Current configuration display
    st.subheader("Current Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API Key Configured", "Yes" if Config.OPENROUTER_API_KEY else "No")
    
    with col2:
        st.metric("Current Model", Config.OPENROUTER_MODEL)
    
    with col3:
        st.metric("LLM Enabled", "Yes" if Config.USE_LLM else "No")
    
    # System information
    st.subheader("System Information")
    st.info(f"""
    **Database Path**: {Config.DATABASE_PATH}
    **OpenRouter Base URL**: {Config.OPENROUTER_BASE_URL}
    
    When LLM features are enabled:
    - Classifier Agent uses LLM for intelligent message categorization
    - Feedback Handler generates personalized, empathetic responses
    - Query Handler provides context-aware status updates
    
    When disabled or API key not available:
    - System falls back to rule-based classification
    - Uses template-based responses
    - All functionality remains operational
    """)

# Agent Interaction Page
if page == "Agent Interaction":
    st.header("Customer Support Agent Interaction")
    
    # Input form
    with st.form("customer_input_form"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            customer_name = st.text_input("Customer Name", value="John Doe")
        
        with col2:
            user_message = st.text_area("Customer Message", height=100, placeholder="Enter your message here...")
        
        submit_button = st.form_submit_button("Process Message", type="primary")
    
    # Process the message
    if submit_button and user_message:
        with st.spinner("Processing your message through the multi-agent system..."):
            result = system.process_message(customer_name, user_message)
        
        # Display results
        st.subheader("Agent Response")
        
        # Response box
        if result['success']:
            st.markdown(f'<div class="success-box"><strong>Response:</strong> {result["response"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box"><strong>Response:</strong> {result["response"]}</div>', unsafe_allow_html=True)
        
        # Classification information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Classification", result['classification'].replace('_', ' ').title())
        
        with col2:
            st.metric("Confidence", f"{result['confidence']:.2%}")
        
        with col3:
            st.metric("Agent Used", result['agent_used'].replace('_', ' ').title())
        
        # Additional metadata
        with st.expander("View Processing Details"):
            st.json({
                "Classification Scores": result['metadata']['classification_scores'],
                "Ticket Number Found": result['metadata']['ticket_number_found'],
                "Interaction ID": result['metadata']['interaction_id']
            })
            
            if result.get('ticket_id'):
                st.info(f"Ticket Created: #{result['ticket_id']}")
            
            if result.get('ticket_status'):
                st.info(f"Ticket Status: {result['ticket_status']}")
    
    # Sample use cases
    st.subheader("Sample Use Cases")
    st.info("Try these sample messages to test different agent flows:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Positive Feedback Example"):
            st.session_state.sample_message = "Thanks for resolving my credit card issue."
            st.session_state.sample_name = "Alice Smith"
    
    with col2:
        if st.button("Negative Feedback Example"):
            st.session_state.sample_message = "My debit card replacement still hasn't arrived."
            st.session_state.sample_name = "Bob Johnson"
    
    with col3:
        if st.button("Query Example"):
            st.session_state.sample_message = "Could you check the status of ticket 123456?"
            st.session_state.sample_name = "Charlie Brown"
    
    # Load sample into form if selected
    if 'sample_message' in st.session_state:
        st.text_input("Customer Name", value=st.session_state.sample_name, key="sample_name_input")
        st.text_area("Customer Message", value=st.session_state.sample_message, key="sample_message_input")
        if st.button("Process Sample", key="process_sample"):
            result = system.process_message(st.session_state.sample_name, st.session_state.sample_message)
            st.subheader("Agent Response")
            st.markdown(f'<div class="success-box"><strong>Response:</strong> {result["response"]}</div>', unsafe_allow_html=True)
            st.json(result)

# Evaluation Dashboard Page
elif page == "Evaluation Dashboard":
    st.header("Agent Evaluation Dashboard")
    
    # Run evaluation
    if st.button("Run Agent Evaluation", type="primary"):
        with st.spinner("Running comprehensive agent evaluation..."):
            evaluator = AgentEvaluator(system)
            evaluation_results = evaluator.run_evaluation()
            report = evaluator.generate_evaluation_report()
            
            st.session_state.evaluation_results = evaluation_results
            st.session_state.evaluation_report = report
    
    # Display evaluation results if available
    if 'evaluation_results' in st.session_state:
        results = st.session_state.evaluation_results
        
        # Key metrics
        st.subheader("Key Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{results['classification_accuracy']:.1f}%</div>
                <div class="metric-label">Classification Accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{results['agent_routing_accuracy']:.1f}%</div>
                <div class="metric-label">Agent Routing Accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{results['ticket_creation_accuracy']:.1f}%</div>
                <div class="metric-label">Ticket Creation Accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{results['overall_success_rate']:.1f}%</div>
                <div class="metric-label">Overall Success Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Classification confusion matrix
        st.subheader("Classification Performance")
        confusion_data = []
        for classification, counts in results['classification_confusion_matrix'].items():
            total = counts['correct'] + counts['incorrect']
            accuracy = (counts['correct'] / total * 100) if total > 0 else 0
            confusion_data.append({
                'Classification': classification.replace('_', ' ').title(),
                'Correct': counts['correct'],
                'Incorrect': counts['incorrect'],
                'Total': total,
                'Accuracy': f"{accuracy:.1f}%"
            })
        
        df_confusion = pd.DataFrame(confusion_data)
        st.table(df_confusion)
        
        # Detailed test results
        with st.expander("View Detailed Test Results"):
            for detail in results['detailed_results']:
                status = "✅" if detail['overall_success'] else "❌"
                st.markdown(f"**{status} Test {detail['test_id']}**")
                st.write(f"Message: {detail['message']}")
                st.write(f"Classification: {detail['expected_classification']} → {detail['actual_classification']}")
                st.write(f"Agent: {detail['expected_agent']} → {detail['actual_agent']}")
                st.write(f"Response: {detail['response']}")
                st.write("---")
        
        # Full report
        with st.expander("View Full Evaluation Report"):
            st.text(st.session_state.evaluation_report)
        
        # Download results
        if st.button("Download Evaluation Results"):
            st.download_button(
                label="Download JSON",
                data=json.dumps(results, indent=2),
                file_name=f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Database View Page
elif page == "Database View":
    st.header("Support Tickets Database")
    
    # Get all tickets
    tickets = system.database.get_all_tickets()
    
    if tickets:
        # Display tickets in a table
        df_tickets = pd.DataFrame(tickets)
        st.subheader(f"Total Tickets: {len(tickets)}")
        st.dataframe(df_tickets, use_container_width=True)
        
        # Ticket statistics
        col1, col2 = st.columns(2)
        
        with col1:
            status_counts = df_tickets['status'].value_counts()
            st.subheader("Ticket Status Distribution")
            st.bar_chart(status_counts)
        
        with col2:
            classification_counts = df_tickets['classification'].value_counts()
            st.subheader("Classification Distribution")
            st.bar_chart(classification_counts)
    else:
        st.info("No tickets in the database yet. Process some messages to create tickets.")
    
    # Database management
    st.subheader("Database Management")
    if st.button("Clear All Tickets", type="secondary"):
        if st.confirm("Are you sure you want to clear all tickets? This cannot be undone."):
            system.database.clear_database()
            st.success("Database cleared successfully!")
            st.rerun()

# Logs & Debugging Page
elif page == "Logs & Debugging":
    st.header("System Logs and Debugging")
    
    # Get interaction log
    interaction_log = system.get_interaction_log()
    
    if interaction_log:
        # Display statistics
        stats = system.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Interactions", stats['total_interactions'])
        
        with col2:
            st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
        
        with col3:
            st.metric("Tickets Created", stats['tickets_created'])
        
        with col4:
            st.metric("Active Agents", len(stats['agent_usage']))
        
        # Classification distribution
        st.subheader("Classification Distribution")
        if stats['classification_distribution']:
            st.json(stats['classification_distribution'])
        
        # Agent usage
        st.subheader("Agent Usage")
        if stats['agent_usage']:
            st.json(stats['agent_usage'])
        
        # Detailed interaction log
        st.subheader("Interaction Log")
        
        # Convert log to DataFrame for display
        log_data = []
        for log in interaction_log:
            log_data.append({
                'Timestamp': log['timestamp'],
                'Customer': log['customer_name'],
                'Classification': log['classification'],
                'Agent': log['target_agent'],
                'Success': log['result'].get('success', False),
                'Message': log['message'][:50] + '...' if len(log['message']) > 50 else log['message']
            })
        
        df_log = pd.DataFrame(log_data)
        st.dataframe(df_log, use_container_width=True)
        
        # Detailed view of individual interactions
        st.subheader("Detailed Interaction View")
        selected_index = st.selectbox(
            "Select an interaction to view details",
            range(len(interaction_log)),
            format_func=lambda x: f"Interaction {x + 1} - {interaction_log[x]['timestamp']}"
        )
        
        if selected_index is not None:
            st.json(interaction_log[selected_index])
        
        # Log management
        st.subheader("Log Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Log"):
                system.clear_log()
                st.success("Log cleared successfully!")
                st.rerun()
        
        with col2:
            if st.button("Download Log"):
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(interaction_log, indent=2),
                    file_name=f"interaction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    else:
        st.info("No interaction logs available yet. Process some messages to generate logs.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #6c757d;'>Banking Customer Support AI Agent - MultiAgent Architecture</div>", unsafe_allow_html=True)