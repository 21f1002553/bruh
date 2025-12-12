from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import get_jwt_identity, jwt_required
from extensions import db
from models import ExpenseReport, Report, Role, User
from datetime import datetime
import os
import uuid
import json

expense_bp = Blueprint('expenses', __name__)

# Configuration
UPLOAD_FOLDER = './uploads/receipts'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    return file_length <= MAX_FILE_SIZE


# 1. EXPENSE SUBMISSION
@expense_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_expense():
    """
    Submit a new expense report
    Supports multipart/form-data for single or multiple expense items
    """
    try:
        user_id = get_jwt_identity()
        status = request.form.get('status', 'pending')

        # Load JSON-based items if provided
        items_json = request.form.get('items')
        items = []

        if items_json:
            try:
                items = json.loads(items_json)
            except Exception:
                return jsonify({'error': 'Invalid items JSON format'}), 400

        # Single-item fallback (legacy)
        if not items:
            category = request.form.get('category')
            amount = request.form.get('amount')
            description = request.form.get('description')
            expense_date = request.form.get('expense_date', str(datetime.utcnow().date()))

            if not all([category, amount, description]):
                return jsonify({'error': 'Missing required fields'}), 400

            items = [{
                'category': category,
                'amount': amount,
                'description': description,
                'expense_date': str(expense_date),
                'receipt_url': None
            }]

        # Validate user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # File upload (optional)
        receipt_url = None
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file.filename != '':
                if not allowed_file(file.filename):
                    return jsonify({'error': 'Invalid file type. Allowed: pdf, png, jpg, jpeg, gif'}), 400

                if not validate_file_size(file):
                    return jsonify({'error': 'File size exceeds 5MB limit'}), 400

                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                receipt_url = filepath

        # Attach receipt to first item if uploaded
        if receipt_url and len(items) > 0:
            items[0]['receipt_url'] = receipt_url

        # Validate and compute total
        total_amount = 0
        for it in items:
            try:
                amount_val = float(it.get('amount', 0) or 0)
                if amount_val <= 0:
                    return jsonify({'error': 'Amount must be positive'}), 400
                total_amount += amount_val
            except ValueError:
                return jsonify({'error': 'Invalid amount format'}), 400

        # Create parent report record
        report = Report(
            user_id=user_id,
            report_type='expense',
            start_date=datetime.utcnow().date(),
            end_date=datetime.utcnow().date(),
            format='json',
            filters={},
        )

        db.session.add(report)
        db.session.flush()

        # Create expense report entry
        expense_report = ExpenseReport(
            report_id=report.id,
            total=total_amount,
            status=status
        )
        expense_report.set_items(items)

        db.session.add(expense_report)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Expense submitted successfully',
            'data': {
                'expense_id': expense_report.id,
                'report_id': report.id,
                'amount': total_amount,
                'status': expense_report.status,
                'receipt_url': receipt_url
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# 2. GET ALL EXPENSES (with filtering)
@expense_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    """
    Get all expenses with optional filtering
    Query params: user_id, status, category, start_date, end_date, page, limit
    """
    try:
        # Get query parameters
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        current_user_role = Role.query.filter_by(id=current_user.role_id).first()
        if not current_user_role:
            return jsonify({'error': 'User role not found'}), 404
        
        status = request.args.get('status')
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Build query
        query = db.session.query(ExpenseReport, Report).join(
            Report, ExpenseReport.report_id == Report.id
        )
        
        # Apply filters
        if (current_user_id) and (current_user_role.name == "bda"):
            query = query.filter(Report.user_id == current_user_id)
        # elif (current_user_id) and (current_user_role.name == "hr"):
        #     # No filtering needed for HR, all expense reports are fetched
        #     pass
        
        if status:
            query = query.filter(ExpenseReport.status == status)
        
        if start_date:
            query = query.filter(Report.generated_at >= start_date)
        
        if end_date:
            query = query.filter(Report.generated_at <= end_date)
        
        # Pagination
        total_count = query.count()
        expenses = query.order_by(Report.generated_at.desc()).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        # Format response
        result = []
        for expense_report, report in expenses:
            items = expense_report.get_items()
            
            # Filter by category if provided
            if category:
                items = [item for item in items if item.get('category') == category]
                if not items:
                    continue
            
            result.append({
                'id': expense_report.id,
                'report_id': report.id,
                'user_id': report.user_id,
                'user_name': report.user.name if report.user else None,
                'items': items,
                'total': expense_report.total,
                'status': expense_report.status,
                'generated_at': report.generated_at.isoformat() if report.generated_at else None,
                'approved_by': report.approved_by,
                'approved_by_name': report.approver.name if report.approver else None
            })
        
        return jsonify({
            'data': result,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_count': total_count,
                'per_page': limit
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 3. GET SINGLE EXPENSE
@expense_bp.route('/<expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Get a single expense by ID
    """
    try:
        expense = ExpenseReport.query.get_or_404(expense_id)
        report = Report.query.get(expense.report_id)
        
        return jsonify({
            'id': expense.id,
            'report_id': report.id,
            'user_id': report.user_id,
            'user_name': report.user.name if report.user else None,
            'items': expense.get_items(),
            'total': expense.total,
            'status': expense.status,
            'generated_at': report.generated_at.isoformat() if report.generated_at else None,
            'approved_by': report.approved_by,
            'approved_by_name': report.approver.name if report.approver else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 4. APPROVE EXPENSE
@expense_bp.route('/<expense_id>/approve', methods=['PUT'])
@jwt_required()
def approve_expense(expense_id):
    """
    Approve an expense report
    """
    try:
        data = request.get_json()
        approver_id = get_jwt_identity()
        comments = data.get('comments', '')

        if not approver_id:
            return jsonify({'error': 'Approver ID is required'}), 400

        # Validate approver exists
        approver = User.query.get(approver_id)
        if not approver:
            return jsonify({'error': 'Approver not found'}), 404

        expense = ExpenseReport.query.get_or_404(expense_id)
        report = Report.query.get(expense.report_id)

        if expense.status != 'pending':
            return jsonify({'error': f'Cannot approve expense with status: {expense.status}'}), 400

        # Update status
        expense.status = 'approved'
        report.approved_by = approver_id
        report.approval_status = 'approved'
        report.approved_at = datetime.utcnow()

        # Add comments to items if provided
        if comments:
            items = expense.get_items()
            for item in items:
                item['approval_comments'] = comments
            expense.set_items(items)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Expense approved successfully',
            'data': {
                'expense_id': expense.id,
                'status': expense.status,
                'approved_by': approver.name,
                'approved_at': report.approved_at.isoformat()
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# 5. REJECT EXPENSE
@expense_bp.route('/<expense_id>/reject', methods=['PUT'])
@jwt_required()
def reject_expense(expense_id):
    """
    Reject an expense report
    """
    try:
        data = request.get_json()
        approver_id = get_jwt_identity()
        reason = data.get('reason', '')

        if not approver_id:
            return jsonify({'error': 'Approver ID is required'}), 400

        if not reason:
            return jsonify({'error': 'Rejection reason is required'}), 400

        # Validate approver exists
        approver = User.query.get(approver_id)
        if not approver:
            return jsonify({'error': 'Approver not found'}), 404

        expense = ExpenseReport.query.get_or_404(expense_id)
        report = Report.query.get(expense.report_id)

        if expense.status != 'pending':
            return jsonify({'error': f'Cannot reject expense with status: {expense.status}'}), 400

        # Update status
        expense.status = 'rejected'
        report.approved_by = approver_id
        report.approval_status = 'rejected'
        report.approved_at = datetime.utcnow()

        # Add rejection reason to items
        items = expense.get_items()
        for item in items:
            item['rejection_reason'] = reason
        expense.set_items(items)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Expense rejected',
            'data': {
                'expense_id': expense.id,
                'status': expense.status,
                'rejected_by': approver.name,
                'rejected_at': report.approved_at.isoformat(),
                'reason': reason
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# 6. GET PENDING EXPENSES
@expense_bp.route('/pending', methods=['GET'])
def get_pending_expenses():
    """
    Get all pending expenses
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        query = db.session.query(ExpenseReport, Report).join(
            Report, ExpenseReport.report_id == Report.id
        ).filter(ExpenseReport.status == 'pending')
        
        total_count = query.count()
        expenses = query.order_by(Report.generated_at.desc()).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        result = []
        for expense_report, report in expenses:
            result.append({
                'id': expense_report.id,
                'report_id': report.id,
                'user_id': report.user_id,
                'user_name': report.user.name if report.user else None,
                'items': expense_report.get_items(),
                'total': expense_report.total,
                'status': expense_report.status,
                'generated_at': report.generated_at.isoformat() if report.generated_at else None
            })
        
        return jsonify({
            'data': result,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_count': total_count,
                'per_page': limit
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 7. GET EXPENSE REPORTS/SUMMARY
@expense_bp.route('/reports', methods=['GET'])
def get_expense_reports():
    """
    Get expense summary/reports with analytics
    Query params: user_id, start_date, end_date, group_by
    """
    try:
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'category')  # category, user, month
        
        # Build base query
        query = db.session.query(ExpenseReport, Report).join(
            Report, ExpenseReport.report_id == Report.id
        )
        
        # Apply filters
        if user_id:
            query = query.filter(Report.user_id == user_id)
        
        if start_date:
            query = query.filter(Report.generated_at >= start_date)
        
        if end_date:
            query = query.filter(Report.generated_at <= end_date)
        
        expenses = query.all()
        
        # Calculate summaries
        total_expenses = 0
        total_approved = 0
        total_pending = 0
        total_rejected = 0
        category_breakdown = {}
        user_breakdown = {}
        
        for expense_report, report in expenses:
            total_expenses += expense_report.total
            
            if expense_report.status == 'approved':
                total_approved += expense_report.total
            elif expense_report.status == 'pending':
                total_pending += expense_report.total
            elif expense_report.status == 'rejected':
                total_rejected += expense_report.total
            
            # Category breakdown
            items = expense_report.get_items()
            for item in items:
                category = item.get('category', 'Other')
                if category not in category_breakdown:
                    category_breakdown[category] = {
                        'total': 0,
                        'count': 0
                    }
                category_breakdown[category]['total'] += item.get('amount', 0)
                category_breakdown[category]['count'] += 1
            
            # User breakdown
            user_name = report.user.name if report.user else 'Unknown'
            if user_name not in user_breakdown:
                user_breakdown[user_name] = {
                    'total': 0,
                    'count': 0
                }
            user_breakdown[user_name]['total'] += expense_report.total
            user_breakdown[user_name]['count'] += 1
        
        return jsonify({
            'summary': {
                'total_expenses': total_expenses,
                'total_approved': total_approved,
                'total_pending': total_pending,
                'total_rejected': total_rejected,
                'expense_count': len(expenses)
            },
            'category_breakdown': category_breakdown,
            'user_breakdown': user_breakdown
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 8. AI VERIFICATION (Placeholder for future AI integration)
@expense_bp.route('/ai-verify/<expense_id>', methods=['POST'])
def ai_verify_expense(expense_id):
    """
    AI-powered expense verification
    This is a placeholder for future AI integration
    """
    try:
        expense = ExpenseReport.query.get_or_404(expense_id)
        items = expense.get_items()
        
        # Placeholder AI verification logic
        # In a real implementation, this would:
        # 1. Extract text from receipt images using OCR
        # 2. Compare extracted amounts with claimed amounts
        # 3. Check for policy violations
        # 4. Flag suspicious expenses
        
        verification_results = []
        for item in items:
            verification_results.append({
                'item': item.get('description'),
                'claimed_amount': item.get('amount'),
                'verified_amount': item.get('amount'),  # Placeholder
                'confidence_score': 0.95,  # Placeholder
                'policy_compliant': True,  # Placeholder
                'flags': []  # Placeholder for any issues
            })
        
        return jsonify({
            'expense_id': expense_id,
            'verification_status': 'verified',
            'overall_confidence': 0.95,
            'results': verification_results,
            'recommendations': 'All expenses appear valid and policy-compliant.'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 9. POLICY CHECK
@expense_bp.route('/policy-check/<expense_id>', methods=['GET'])
def policy_check_expense(expense_id):
    """
    Check if expense complies with company policies
    """
    try:
        expense = ExpenseReport.query.get_or_404(expense_id)
        items = expense.get_items()
        
        # Define policy limits (these should come from a config or database)
        policy_limits = {
            'Travel': {'max_per_day': 500, 'max_total': 5000},
            'Food': {'max_per_meal': 50, 'max_per_day': 150},
            'Supplies': {'max_per_item': 200, 'max_total': 1000},
            'Other': {'max_per_item': 100, 'max_total': 500}
        }
        
        violations = []
        warnings = []
        
        for item in items:
            category = item.get('category', 'Other')
            amount = item.get('amount', 0)
            
            if category in policy_limits:
                limits = policy_limits[category]
                
                # Check per-item limits
                if 'max_per_item' in limits and amount > limits['max_per_item']:
                    violations.append({
                        'item': item.get('description'),
                        'type': 'per_item_limit',
                        'limit': limits['max_per_item'],
                        'actual': amount
                    })
                
                if 'max_per_meal' in limits and amount > limits['max_per_meal']:
                    violations.append({
                        'item': item.get('description'),
                        'type': 'per_meal_limit',
                        'limit': limits['max_per_meal'],
                        'actual': amount
                    })
                
                # Warning if approaching limit
                if 'max_per_item' in limits and amount > limits['max_per_item'] * 0.8:
                    warnings.append({
                        'item': item.get('description'),
                        'message': f"Approaching policy limit for {category}"
                    })
        
        # Check total limits
        category_totals = {}
        for item in items:
            category = item.get('category', 'Other')
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += item.get('amount', 0)
        
        for category, total in category_totals.items():
            if category in policy_limits and 'max_total' in policy_limits[category]:
                if total > policy_limits[category]['max_total']:
                    violations.append({
                        'category': category,
                        'type': 'total_limit',
                        'limit': policy_limits[category]['max_total'],
                        'actual': total
                    })
        
        is_compliant = len(violations) == 0
        
        return jsonify({
            'expense_id': expense_id,
            'is_compliant': is_compliant,
            'violations': violations,
            'warnings': warnings,
            'policy_limits': policy_limits,
            'category_totals': category_totals
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 10. UPDATE EXPENSE
@expense_bp.route('/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """
    Update an existing expense (only if pending)
    """
    try:
        expense = ExpenseReport.query.get_or_404(expense_id)
        data = request.get_json() or {}

        # Disallow updating approved/rejected reports
        if expense.status in ['approved', 'rejected']:
            return jsonify({'error': 'Cannot update approved or rejected expense'}), 400

        # Update items if provided
        if 'items' in data and isinstance(data['items'], list):
            expense.set_items(data['items'])
            # Recalculate total
            total = sum(float(item.get('amount', 0) or 0) for item in data['items'])
            expense.total = total

        # Update total if provided directly
        if 'total' in data:
            try:
                expense.total = float(data['total'])
            except Exception:
                pass

        # Allow status transitions (e.g., draft -> pending)
        if 'status' in data:
            new_status = data.get('status')
            # Basic validation: do not allow setting to approved/rejected via this endpoint
            if new_status in ['approved', 'rejected']:
                return jsonify({'error': 'Cannot set approved/rejected via this endpoint'}), 400
            expense.status = new_status

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Expense updated successfully',
            'data': expense.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# 11. DELETE EXPENSE
@expense_bp.route('/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Delete an expense (only if pending)
    """
    try:
        expense = ExpenseReport.query.get_or_404(expense_id)
        
        if expense.status != 'draft':
            return jsonify({'error': 'Cannot delete non-pending expense'}), 400
        
        report = Report.query.get(expense.report_id)
        
        # Delete associated files
        items = expense.get_items()
        for item in items:
            receipt_url = item.get('receipt_url')
            if receipt_url and os.path.exists(receipt_url):
                os.remove(receipt_url)
        
        db.session.delete(expense)
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Expense deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500