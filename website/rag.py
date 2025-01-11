from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .rag_module import fact_check_crew, get_news
from .models import RAGQuery, Admin
from flask_login import login_required, current_user
from . import db

rag = Blueprint('rag', __name__)

def serialize_crew_output(output):
    """
    Convert CrewOutput to JSON serializable format.
    Extracts the relevant information from the output.
    """
    try:
        # Convert the output to a string and parse the content
        output_str = str(output)
        
        # Extract different sections using string manipulation
        sections = {
            "Summary of Findings": "",
            "Cross-Verification": "",
            "Contextual Background": "",
            "Conclusion": "",
            "Verdict": "",
            "References": []
        }
        
        current_section = None
        current_content = []
        
        # Parse the output string line by line
        for line in output_str.split('\n'):
            line = line.strip()
            
            # Check for section headers
            if line.startswith('**') and line.endswith('**'):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip('*').strip()
                current_content = []
            elif current_section and line:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Extract references
        if sections.get("References"):
            references = []
            for ref in sections["References"].split('\n'):
                if ref.strip():
                    references.append(ref.strip())
            sections["References"] = references
        
        # Filter out empty sections
        filtered_sections = {key: value for key, value in sections.items() if value}

        return filtered_sections
        
    except Exception as e:
        print(f"Error in serialization: {str(e)}")
        return {"error": "Failed to serialize output", "details": str(e)}


def format_final_answer(query, context, serialized_output):
    """
    Format the response into the desired structure
    """

    try:
        formatted_response = f"""
**Query:**
{query}

**Context:**
{context}

**Summary of Findings:**
{serialized_output.get('Summary of Findings', 'N/A')}

**Cross-Verification:**
{serialized_output.get('Cross-Verification', 'N/A')}

**Contextual-Background:**
{serialized_output.get('Contextual-Background', 'N/A')}

**Verdict:**
{serialized_output.get('Verdict', 'N/A')}

**References:**
{serialized_output.get('References', 'N/A')}
"""
        return formatted_response
    
    except Exception as e:
        print(f"Error in formatting final answer: {str(e)}")
        return f"Error in formatting response: {str(e)}"
    

@rag.route('/process-query', methods=['GET', 'POST'])
@login_required  
def process_query():
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'Query is required'}), 400
        

        # Get context and output from RAG pipeline
        output = fact_check_crew.kickoff(inputs={'claim': query})

        context = get_news(query)

        # Serialize the output to JSON-compatible format
        serialized_output = serialize_crew_output(output)

        # Save to the database (optional)
        rag_query = RAGQuery(
            question=query,
            context=context,
            output=str(serialized_output), 
            user_id=current_user.id
        )
        db.session.add(rag_query)
        db.session.commit()

        # Prepare response
        response = {
            'question': query,
            'context': context,
            'output': serialized_output
        }

        return jsonify(response), 200

    except Exception as e:
        # Log and return the error
        print(f"Error in process_query: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.session.close()


@rag.route('/admin/process-query', methods=['GET', 'POST'])
@login_required
def admin_process_query():
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if the user is an admin
        admin = Admin.query.filter_by(email=current_user.email).first()
        if not admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get context and output from RAG pipeline
        output = fact_check_crew.kickoff(inputs={'claim': query})
        context = get_news(query)

        # Serialize the output to JSON-compatible format
        serialized_output = serialize_crew_output(output)

        # Save to the database with admin_id
        rag_query = RAGQuery(
            question=query,
            context=context,
            output=str(serialized_output),  
            admin_id=admin.id  
        )
        db.session.add(rag_query)
        db.session.commit()

        # Prepare response
        response = {
            'question': query,
            'context': context,
            'output': serialized_output
        }

        return jsonify(response), 200

    except Exception as e:
        # Log and return the error
        print(f"Error in admin_process_query: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.session.close()