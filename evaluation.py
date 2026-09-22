from typing import Dict, Any, List
from multi_agent_system import MultiAgentSystem
import json

class AgentEvaluator:
    """
    Framework for evaluating agent performance across different metrics.
    """
    
    def __init__(self, system: MultiAgentSystem):
        self.system = system
        self.test_cases = self._load_test_cases()
        self.evaluation_results = []
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load predefined test cases for evaluation."""
        return [
            # Positive Feedback Test Cases
            {
                'id': 'PF001',
                'customer_name': 'John Smith',
                'message': 'Thanks for resolving my credit card issue.',
                'expected_classification': 'positive_feedback',
                'expected_agent': 'feedback_handler',
                'expected_ticket_created': False
            },
            {
                'id': 'PF002',
                'customer_name': 'Sarah Johnson',
                'message': 'Thank you for sorting out my net banking login issue.',
                'expected_classification': 'positive_feedback',
                'expected_agent': 'feedback_handler',
                'expected_ticket_created': False
            },
            {
                'id': 'PF003',
                'customer_name': 'Mike Brown',
                'message': 'Great service! I really appreciate your help with my account.',
                'expected_classification': 'positive_feedback',
                'expected_agent': 'feedback_handler',
                'expected_ticket_created': False
            },
            
            # Negative Feedback Test Cases
            {
                'id': 'NF001',
                'customer_name': 'Emily Davis',
                'message': 'My debit card replacement still has not arrived.',
                'expected_classification': 'negative_feedback',
                'expected_agent': 'feedback_handler',
                'expected_ticket_created': True
            },
            {
                'id': 'NF002',
                'customer_name': 'Robert Wilson',
                'message': 'I am frustrated with the ongoing issue with my account.',
                'expected_classification': 'negative_feedback',
                'expected_agent': 'feedback_handler',
                'expected_ticket_created': True
            },
            {
                'id': 'NF003',
                'customer_name': 'Lisa Anderson',
                'message': 'The mobile banking app is not working properly.',
                'expected_classification': 'negative_feedback',
                'expected_agent': 'feedback_handler',
                'expected_ticket_created': True
            }
        ]
    
    def run_evaluation(self) -> Dict[str, Any]:
        """
        Run comprehensive evaluation of all agents.
        
        Returns:
            Dictionary containing evaluation metrics and results
        """
        results = {
            'total_test_cases': len(self.test_cases),
            'classification_accuracy': 0,
            'agent_routing_accuracy': 0,
            'ticket_creation_accuracy': 0,
            'overall_success_rate': 0,
            'detailed_results': [],
            'classification_confusion_matrix': {
                'positive_feedback': {'correct': 0, 'incorrect': 0},
                'negative_feedback': {'correct': 0, 'incorrect': 0}
            }
        }
        
        classification_correct = 0
        routing_correct = 0
        ticket_creation_correct = 0
        overall_success = 0
        
        for test_case in self.test_cases:
            # Process the test case
            response = self.system.process_message(
                customer_name=test_case['customer_name'],
                message=test_case['message']
            )
            
            # Evaluate classification
            classification_match = response['classification'] == test_case['expected_classification']
            if classification_match:
                classification_correct += 1
                results['classification_confusion_matrix'][test_case['expected_classification']]['correct'] += 1
            else:
                results['classification_confusion_matrix'][test_case['expected_classification']]['incorrect'] += 1
            
            # Evaluate agent routing
            routing_match = response['agent_used'] == test_case['expected_agent']
            if routing_match:
                routing_correct += 1
            
            # Evaluate ticket creation
            ticket_created = response.get('ticket_id') is not None
            ticket_match = ticket_created == test_case['expected_ticket_created']
            if ticket_match:
                ticket_creation_correct += 1
            
            # Overall success (all metrics correct)
            test_success = classification_match and routing_match and ticket_match
            if test_success:
                overall_success += 1
            
            # Store detailed result
            detailed_result = {
                'test_id': test_case['id'],
                'message': test_case['message'],
                'expected_classification': test_case['expected_classification'],
                'actual_classification': response['classification'],
                'expected_agent': test_case['expected_agent'],
                'actual_agent': response['agent_used'],
                'expected_ticket_created': test_case['expected_ticket_created'],
                'actual_ticket_created': ticket_created,
                'classification_correct': classification_match,
                'routing_correct': routing_match,
                'ticket_correct': ticket_match,
                'overall_success': test_success,
                'confidence': response['confidence'],
                'response': response['response']
            }
            results['detailed_results'].append(detailed_result)
        
        # Calculate percentages
        total = len(self.test_cases)
        results['classification_accuracy'] = (classification_correct / total) * 100
        results['agent_routing_accuracy'] = (routing_correct / total) * 100
        results['ticket_creation_accuracy'] = (ticket_creation_correct / total) * 100
        results['overall_success_rate'] = (overall_success / total) * 100
        
        self.evaluation_results = results
        return results
    
    def evaluate_response_quality(self, response_text: str, classification: str) -> Dict[str, Any]:
        """
        Evaluate the quality of generated responses based on classification.
        
        Args:
            response_text: The generated response
            classification: The classification of the original message
            
        Returns:
            Dictionary containing quality metrics
        """
        quality_metrics = {
            'classification': classification,
            'response_length': len(response_text),
            'contains_personalization': False,
            'contains_ticket_reference': False,
            'contains_empathy': False,
            'clarity_score': 0.0,
            'overall_quality': 0.0
        }
        
        # Check for personalization (customer name)
        quality_metrics['contains_personalization'] = any(
            keyword in response_text.lower() 
            for keyword in ['thank you', 'we appreciate', 'we apologize', 'sorry']
        )
        
        # Check for ticket reference
        quality_metrics['contains_ticket_reference'] = 'ticket #' in response_text.lower()
        
        # Check for empathy words
        empathy_keywords = ['apologize', 'sorry', 'understand', 'appreciate', 'delighted', 'happy']
        quality_metrics['contains_empathy'] = any(
            keyword in response_text.lower() 
            for keyword in empathy_keywords
        )
        
        # Calculate clarity score (based on structure and length)
        if 50 <= len(response_text) <= 200:
            quality_metrics['clarity_score'] = 1.0
        elif 30 <= len(response_text) < 50 or 200 < len(response_text) <= 300:
            quality_metrics['clarity_score'] = 0.7
        else:
            quality_metrics['clarity_score'] = 0.4
        
        # Calculate overall quality based on classification
        if classification == 'positive_feedback':
            quality_metrics['overall_quality'] = (
                (1.0 if quality_metrics['contains_personalization'] else 0.5) *
                quality_metrics['clarity_score']
            )
        elif classification == 'negative_feedback':
            quality_metrics['overall_quality'] = (
                (1.0 if quality_metrics['contains_personalization'] else 0.5) *
                (1.0 if quality_metrics['contains_ticket_reference'] else 0.3) *
                (1.0 if quality_metrics['contains_empathy'] else 0.5) *
                quality_metrics['clarity_score']
            )
        elif classification == 'query':
            quality_metrics['overall_quality'] = (
                (1.0 if quality_metrics['contains_ticket_reference'] else 0.5) *
                quality_metrics['clarity_score']
            )
        
        return quality_metrics
    
    def generate_evaluation_report(self) -> str:
        """Generate a human-readable evaluation report."""
        if not self.evaluation_results:
            return "No evaluation results available. Run run_evaluation() first."
        
        results = self.evaluation_results
        
        report = []
        report.append("=" * 60)
        report.append("BANKING CUSTOMER SUPPORT AI AGENT EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"\nTotal Test Cases: {results['total_test_cases']}")
        report.append(f"Classification Accuracy: {results['classification_accuracy']:.2f}%")
        report.append(f"Agent Routing Accuracy: {results['agent_routing_accuracy']:.2f}%")
        report.append(f"Ticket Creation Accuracy: {results['ticket_creation_accuracy']:.2f}%")
        report.append(f"Overall Success Rate: {results['overall_success_rate']:.2f}%")
        
        report.append("\n" + "-" * 60)
        report.append("CLASSIFICATION PERFORMANCE")
        report.append("-" * 60)
        for classification, counts in results['classification_confusion_matrix'].items():
            total = counts['correct'] + counts['incorrect']
            accuracy = (counts['correct'] / total * 100) if total > 0 else 0
            report.append(f"{classification.replace('_', ' ').title()}: {counts['correct']}/{total} correct ({accuracy:.2f}%)")
        
        report.append("\n" + "-" * 60)
        report.append("DETAILED TEST RESULTS")
        report.append("-" * 60)
        
        for detail in results['detailed_results']:
            status = "PASS" if detail['overall_success'] else "FAIL"
            report.append(f"\n[{status}] - Test {detail['test_id']}")
            report.append(f"  Message: {detail['message']}")
            report.append(f"  Classification: {detail['expected_classification']} -> {detail['actual_classification']}")
            report.append(f"  Agent: {detail['expected_agent']} -> {detail['actual_agent']}")
            report.append(f"  Confidence: {detail['confidence']:.2f}")
            report.append(f"  Response: {detail['response']}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def save_evaluation_results(self, filepath: str):
        """Save evaluation results to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2)
