"""
Test script for the Banking Customer Support AI Agent System
"""
from multi_agent_system import MultiAgentSystem
from evaluation import AgentEvaluator

def test_basic_functionality():
    """Test basic functionality of the multi-agent system."""
    print("Testing Banking Customer Support AI Agent System")
    print("=" * 60)
    
    # Initialize the system
    system = MultiAgentSystem()
    
    # Test Case 1: Positive Feedback
    print("\n1. Testing Positive Feedback:")
    result1 = system.process_message(
        customer_name="Alice Smith",
        message="Thanks for resolving my credit card issue."
    )
    print(f"   Classification: {result1['classification']}")
    print(f"   Agent Used: {result1['agent_used']}")
    print(f"   Response: {result1['response']}")
    print(f"   Success: {result1['success']}")
    
    # Test Case 2: Negative Feedback
    print("\n2. Testing Negative Feedback:")
    result2 = system.process_message(
        customer_name="Bob Johnson",
        message="My debit card replacement still hasn't arrived."
    )
    print(f"   Classification: {result2['classification']}")
    print(f"   Agent Used: {result2['agent_used']}")
    print(f"   Response: {result2['response']}")
    print(f"   Ticket Created: {result2['ticket_id']}")
    print(f"   Success: {result2['success']}")
    
    # Test Case 3: Query (with ticket from previous test)
    print("\n3. Testing Query:")
    if result2.get('ticket_id'):
        result3 = system.process_message(
            customer_name="Charlie Brown",
            message=f"Could you check the status of ticket {result2['ticket_id']}?"
        )
        print(f"   Classification: {result3['classification']}")
        print(f"   Agent Used: {result3['agent_used']}")
        print(f"   Response: {result3['response']}")
        print(f"   Ticket Status: {result3['ticket_status']}")
        print(f"   Success: {result3['success']}")
    else:
        print("   Skipped - no ticket created in previous test")
    
    # Test Case 4: Query with non-existent ticket
    print("\n4. Testing Query with non-existent ticket:")
    result4 = system.process_message(
        customer_name="David Wilson",
        message="Could you check the status of ticket 999999?"
    )
    print(f"   Classification: {result4['classification']}")
    print(f"   Agent Used: {result4['agent_used']}")
    print(f"   Response: {result4['response']}")
    print(f"   Success: {result4['success']}")
    
    # Display statistics
    print("\n" + "=" * 60)
    print("System Statistics:")
    stats = system.get_statistics()
    print(f"   Total Interactions: {stats['total_interactions']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    print(f"   Tickets Created: {stats['tickets_created']}")
    print(f"   Classification Distribution: {stats['classification_distribution']}")
    print(f"   Agent Usage: {stats['agent_usage']}")
    
    # Display database contents
    print("\n" + "=" * 60)
    print("Database Contents:")
    tickets = system.database.get_all_tickets()
    for ticket in tickets:
        print(f"   Ticket #{ticket['ticket_id']}: {ticket['customer_name']} - {ticket['status']}")

def test_evaluation():
    """Test the evaluation framework."""
    print("\n" + "=" * 60)
    print("Testing Evaluation Framework")
    print("=" * 60)
    
    system = MultiAgentSystem()
    evaluator = AgentEvaluator(system)
    
    # Run evaluation
    print("\nRunning comprehensive evaluation...")
    results = evaluator.run_evaluation()
    
    print(f"\nTotal Test Cases: {results['total_test_cases']}")
    print(f"Classification Accuracy: {results['classification_accuracy']:.2f}%")
    print(f"Agent Routing Accuracy: {results['agent_routing_accuracy']:.2f}%")
    print(f"Ticket Creation Accuracy: {results['ticket_creation_accuracy']:.2f}%")
    print(f"Overall Success Rate: {results['overall_success_rate']:.2f}%")
    
    # Generate and display report
    print("\n" + "=" * 60)
    print("Evaluation Report:")
    print("=" * 60)
    report = evaluator.generate_evaluation_report()
    # Print report safely handling encoding
    try:
        print(report)
    except UnicodeEncodeError:
        # Fallback to basic ASCII output
        print("Classification Accuracy: {:.2f}%".format(results['classification_accuracy']))
        print("Agent Routing Accuracy: {:.2f}%".format(results['agent_routing_accuracy']))
        print("Ticket Creation Accuracy: {:.2f}%".format(results['ticket_creation_accuracy']))
        print("Overall Success Rate: {:.2f}%".format(results['overall_success_rate']))

if __name__ == "__main__":
    test_basic_functionality()
    test_evaluation()
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)