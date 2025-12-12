from flask import Blueprint, request, jsonify
from app import db
from models import Training, Course, Enrollment, User
from datetime import datetime

training_bp = Blueprint('training', __name__)

# GET /api/training/modules
@training_bp.route('/modules', methods=['GET'])
def list_modules():
    try:
        # optional query param to filter by training_id
        training_id = request.args.get('training_id')
        if training_id:
            courses = Course.query.filter_by(training_id=training_id).all()
        else:
            courses = Course.query.all()

        data = []
        for c in courses:
            data.append({
                'id': c.id,
                'title': c.title,
                'training_id': c.training_id,
                'training_title': c.training.title if c.training else None,
                'content_url': c.content_url,
                'duration_mins': c.duration_mins
            })

        return jsonify({'success': True, 'data': data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# GET /api/training/modules/<id>
@training_bp.route('/modules/<module_id>', methods=['GET'])
def get_module(module_id):
    try:
        c = Course.query.get_or_404(module_id)
        payload = {
            'id': c.id,
            'title': c.title,
            'training_id': c.training_id,
            'training_title': c.training.title if c.training else None,
            'content_url': c.content_url,
            'duration_mins': c.duration_mins
        }

        # optional-- if user_id provided, include user's enrollment info for this module
        user_id = request.args.get('user_id')
        if user_id:
            enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=c.id).first()
            payload['enrollment'] = enrollment.to_dict() if enrollment else None

        return jsonify({'success': True, 'data': payload}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# PUT /api/training/modules/<id>/progress
@training_bp.route('/modules/<module_id>/progress', methods=['PUT'])
def update_module_progress(module_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        progress = float(data.get('progress', 0))

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        if progress < 0 or progress > 100:
            return jsonify({'error': 'progress must be between 0 and 100'}), 400

        # ensure module exists
        course = Course.query.get_or_404(module_id)

        # find or create enrollment
        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course.id).first()
        if not enrollment:
            enrollment = Enrollment(user_id=user_id, course_id=course.id, progress=0.0, status='enrolled')
            db.session.add(enrollment)

        enrollment.progress = progress
        # if progress == 100, you may optionally set status
        if progress >= 100:
            enrollment.status = 'completed'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Progress updated',
            'data': {
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'progress': enrollment.progress,
                'status': enrollment.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# POST /api/training/modules/<id>/complete
@training_bp.route('/modules/<module_id>/complete', methods=['POST'])
def complete_module(module_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        course = Course.query.get_or_404(module_id)

        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course.id).first()
        if not enrollment:
            # create enrollment if missing and mark completed
            enrollment = Enrollment(
                user_id=user_id,
                course_id=course.id,
                progress=100.0,
                status='completed'
            )
            db.session.add(enrollment)
        else:
            enrollment.progress = 100.0
            enrollment.status = 'completed'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Module marked as complete',
            'data': {
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'progress': enrollment.progress,
                'status': enrollment.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= TRAINING PROGRAMS MANAGEMENT =============

# GET /api/training/programs - List all training programs
@training_bp.route('/programs', methods=['GET'])
def list_training_programs():
    try:
        trainings = Training.query.all()
        data = [t.to_dict() for t in trainings]
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# POST /api/training/programs - Create new training program
@training_bp.route('/programs', methods=['POST'])
def create_training_program():
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not title:
            return jsonify({'error': 'title is required'}), 400

        training = Training(
            title=title,
            description=description,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        )
        
        db.session.add(training)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Training program created successfully',
            'data': training.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE /api/training/programs/<id> - Delete training program
@training_bp.route('/programs/<id>', methods=['DELETE'])
def delete_training_program(id):
    try:
        training = Training.query.get_or_404(id)
        
        # Delete all courses for this training
        Course.query.filter_by(training_id=id).delete()
        
        db.session.delete(training)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Training program deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= COURSES MANAGEMENT =============

# GET /api/training/courses - List all courses
@training_bp.route('/courses', methods=['GET'])
def list_courses():
    try:
        training_id = request.args.get('training_id')
        if training_id:
            courses = Course.query.filter_by(training_id=training_id).all()
        else:
            courses = Course.query.all()

        data = [c.to_dict() for c in courses]
        return jsonify({'success': True, 'data': data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# POST /api/training/courses - Create new course
@training_bp.route('/courses', methods=['POST'])
def create_course():
    try:
        data = request.get_json()
        training_id = data.get('training_id')
        title = data.get('title')
        content_url = data.get('content_url')
        duration_mins = data.get('duration_mins')

        if not training_id or not title:
            return jsonify({'error': 'training_id and title are required'}), 400

        # Verify training exists
        training = Training.query.get(training_id)
        if not training:
            return jsonify({'error': 'Training program not found'}), 404

        course = Course(
            training_id=training_id,
            title=title,
            content_url=content_url,
            duration_mins=duration_mins
        )
        
        db.session.add(course)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Course created successfully',
            'data': course.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# PUT /api/training/courses/<id> - Update course
@training_bp.route('/courses/<course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        data = request.get_json()

        if 'training_id' in data:
            training = Training.query.get(data['training_id'])
            if not training:
                return jsonify({'error': 'Training program not found'}), 404
            course.training_id = data['training_id']
        
        if 'title' in data:
            course.title = data['title']
        if 'content_url' in data:
            course.content_url = data['content_url']
        if 'duration_mins' in data:
            course.duration_mins = data['duration_mins']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Course updated successfully',
            'data': course.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# DELETE /api/training/courses/<id> - Delete course
@training_bp.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        
        # Delete all enrollments for this course
        Enrollment.query.filter_by(course_id=course_id).delete()
        
        db.session.delete(course)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Course deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
