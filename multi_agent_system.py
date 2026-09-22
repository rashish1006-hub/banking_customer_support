from typing import Dict, Any
from classifier_agent import ClassifierAgent
from feedback_handler_agent import FeedbackHandlerAgent
from query_handler_agent import QueryHandlerAgent
from database import SupportDatabase
from config import Config
import json
from datetime import datetime

class MultiAgentSystem:
    """
    Main orchestration system that coordinates all agents for banking customer support.
    """
    
    def __init__(self, db_path: str = None):
        # Validate configuration
        Config.validate()
        
        self.database = SupportDatabase(db_path)
        self.classifier = ClassifierAgent()
        self.feedback_handler = FeedbackHandlerAgent(self.database)
        self.query_handler = QueryHandlerAgent(self.database)
        
        # Logging system
        self.interaction_log = []
    
    def process_message(self, customer_name: str, message: str) -> Dict[str, Any]:
        """
        Process a customer message through the multi-agent system.
        
        Args:
            customer_name: Name of the customer
            message: The customer's message
            
        Returns:
            Dictionary containing the response and complete interaction metadata
        """
        timestamp = datetime.now().isoformat()
        
        # Step 1: Classify the message
        classification_result = self.classifier.classify(message)
        
        # Step 2: Route to appropriate agent
        target_agent = self.classifier.route_to_agent(classification_result['classification'])
        
        # Step 3: Process with the appropriate agent
        if target_agent == 'feedback_handler':
            result = self.feedback_handler.process(
                classification=classification_result['classification'],
                customer_name=customer_name,
                message=message
            )
        elif target_agent == 'query_handler':
            result = self.query_handler.process(
                customer_name=customer_name,
                message=message
            )
        else:
            result = {
                'success': False,
                'response': 'I apologize, but I encountered an error processing your request.',
                'error': 'Unknown agent routing'
            }
        
        # Step 4: Log the interaction
        interaction = {
            'timestamp': timestamp,
            'customer_name': customer_name,
            'message': message,
            'classification': classification_result['classification'],
            'confidence': classification_result['confidence'],
            'target_agent': target_agent,
            'result': result
        }
        
        self.interaction_log.append(interaction)
        
        # Step 5: Return complete response
        return {
            'response': result.get('response', 'An error occurred'),
            'classification': classification_result['classification'],
            'confidence': classification_result['confidence'],
            'agent_used': target_agent,
            'ticket_id': result.get('ticket_id'),
            'ticket_status': result.get('ticket_status'),
            'success': result.get('success', False),
            'metadata': {
                'classification_scores': classification_result['scores'],
                'ticket_number_found': classification_result.get('ticket_number'),
                'interaction_id': len(self.interaction_log)
            }
        }
    
    def get_interaction_log(self) -> list:
        """Get the complete interaction log."""
        return self.interaction_log
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about agent performance."""
        if not self.interaction_log:
            return {
                'total_interactions': 0,
                'classification_distribution': {},
                'agent_usage': {},
                'success_rate': 0.0
            }
        
        total = len(self.interaction_log)
        
        # Classification distribution
        classification_counts = {}
        for log in self.interaction_log:
            cls = log['classification']
            classification_counts[cls] = classification_counts.get(cls, 0) + 1
        
        # Agent usage
        agent_counts = {}
        for log in self.interaction_log:
            agent = log['target_agent']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        # Success rate
        successful = sum(1 for log in self.interaction_log if log['result'].get('success', False))
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        return {
            'total_interactions': total,
            'classification_distribution': classification_counts,
            'agent_usage': agent_counts,
            'success_rate': success_rate,
            'tickets_created': sum(1 for log in self.interaction_log if log['result'].get('ticket_created', False))
        }
    
    def clear_log(self):
        """Clear the interaction log (for testing)."""
        self.interaction_log = []
    
    def save_log_to_file(self, filepath: str):
        """Save interaction log to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.interaction_log, f, indent=2)
    
    def load_log_from_file(self, filepath: str):
        """Load interaction log from a JSON file."""
        with open(filepath, 'r') as f:
            self.interaction_log = json.load(f)
