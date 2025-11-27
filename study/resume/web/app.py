# -*- coding: utf-8 -*-
"""
小升初简历系统 - Flask后端
基于模板1样式设计
"""
import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# 配置
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xiaoshengchu-resume-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{BASE_DIR / "resume.db"}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

db = SQLAlchemy(app)

# ==================== 数据库模型 ====================

class Student(db.Model):
    """学生信息"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), default='男')
    birth_date = db.Column(db.String(20))
    height = db.Column(db.String(10))
    school = db.Column(db.String(100))
    class_name = db.Column(db.String(50))
    district = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    hobbies = db.Column(db.String(200))
    photo = db.Column(db.String(200))  # 人像照片路径
    self_intro = db.Column(db.Text)
    parent_message = db.Column(db.Text)
    teacher_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    awards = db.relationship('Award', backref='student', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='student', lazy=True, cascade='all, delete-orphan')

class Award(db.Model):
    """荣誉奖项"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    category = db.Column(db.String(50))  # 区级/校级/竞赛
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20))
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

class Certificate(db.Model):
    """证书照片"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200))
    category = db.Column(db.String(50))  # 奖状/证书/活动照片
    order = db.Column(db.Integer, default=0)

# ==================== 工具函数 ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(file, subfolder='photos'):
    """保存上传的文件"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 添加UUID避免重名
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        save_path = UPLOAD_FOLDER / subfolder / unique_filename
        file.save(str(save_path))
        return f"uploads/{subfolder}/{unique_filename}"
    return None

# ==================== 路由 ====================

@app.route('/')
def index():
    """首页 - 简历列表"""
    students = Student.query.order_by(Student.updated_at.desc()).all()
    return render_template('index.html', students=students)

@app.route('/create', methods=['GET', 'POST'])
def create_resume():
    """创建新简历"""
    if request.method == 'POST':
        # 创建学生记录
        student = Student(
            name=request.form.get('name', ''),
            gender=request.form.get('gender', '男'),
            birth_date=request.form.get('birth_date', ''),
            height=request.form.get('height', ''),
            school=request.form.get('school', ''),
            class_name=request.form.get('class_name', ''),
            district=request.form.get('district', ''),
            address=request.form.get('address', ''),
            phone=request.form.get('phone', ''),
            hobbies=request.form.get('hobbies', ''),
            self_intro=request.form.get('self_intro', ''),
            parent_message=request.form.get('parent_message', ''),
            teacher_comment=request.form.get('teacher_comment', '')
        )
        
        # 处理人像照片
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                student.photo = save_upload_file(photo, 'photos')
        
        db.session.add(student)
        db.session.commit()
        
        return redirect(url_for('edit_resume', student_id=student.id))
    
    return render_template('create.html')

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_resume(student_id):
    """编辑简历"""
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        # 更新基本信息
        student.name = request.form.get('name', student.name)
        student.gender = request.form.get('gender', student.gender)
        student.birth_date = request.form.get('birth_date', student.birth_date)
        student.height = request.form.get('height', student.height)
        student.school = request.form.get('school', student.school)
        student.class_name = request.form.get('class_name', student.class_name)
        student.district = request.form.get('district', student.district)
        student.address = request.form.get('address', student.address)
        student.phone = request.form.get('phone', student.phone)
        student.hobbies = request.form.get('hobbies', student.hobbies)
        student.self_intro = request.form.get('self_intro', student.self_intro)
        student.parent_message = request.form.get('parent_message', student.parent_message)
        student.teacher_comment = request.form.get('teacher_comment', student.teacher_comment)
        
        # 处理新上传的照片
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                student.photo = save_upload_file(photo, 'photos')
        
        db.session.commit()
        return redirect(url_for('preview_resume', student_id=student.id))
    
    return render_template('edit.html', student=student)

@app.route('/preview/<int:student_id>')
def preview_resume(student_id):
    """预览简历（棕色模板）"""
    student = Student.query.get_or_404(student_id)
    return render_template('preview.html', student=student)

@app.route('/preview/<int:student_id>/green')
def preview_resume_green(student_id):
    """预览简历（绿色模板 - 基于简历模板1.pdf）"""
    student = Student.query.get_or_404(student_id)
    return render_template('preview_green.html', student=student)

@app.route('/api/award/<int:student_id>', methods=['POST'])
def add_award(student_id):
    """添加荣誉奖项"""
    student = Student.query.get_or_404(student_id)
    data = request.json
    
    award = Award(
        student_id=student_id,
        category=data.get('category', '校级'),
        title=data.get('title', ''),
        date=data.get('date', ''),
        description=data.get('description', ''),
        order=data.get('order', 0)
    )
    db.session.add(award)
    db.session.commit()
    
    return jsonify({'success': True, 'id': award.id})

@app.route('/api/award/<int:award_id>', methods=['DELETE'])
def delete_award(award_id):
    """删除荣誉奖项"""
    award = Award.query.get_or_404(award_id)
    db.session.delete(award)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/certificate/<int:student_id>', methods=['POST'])
def add_certificate(student_id):
    """上传证书照片"""
    student = Student.query.get_or_404(student_id)
    
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': '没有上传文件'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'})
    
    image_path = save_upload_file(file, 'certificates')
    if not image_path:
        return jsonify({'success': False, 'error': '文件类型不支持'})
    
    cert = Certificate(
        student_id=student_id,
        name=request.form.get('name', '证书'),
        image_path=image_path,
        category=request.form.get('category', '证书'),
        order=request.form.get('order', 0)
    )
    db.session.add(cert)
    db.session.commit()
    
    return jsonify({'success': True, 'id': cert.id, 'image_path': image_path})

@app.route('/api/certificate/<int:cert_id>', methods=['DELETE'])
def delete_certificate(cert_id):
    """删除证书照片"""
    cert = Certificate.query.get_or_404(cert_id)
    # 删除文件
    try:
        file_path = BASE_DIR / 'static' / cert.image_path
        if file_path.exists():
            file_path.unlink()
    except:
        pass
    db.session.delete(cert)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/export/word/<int:student_id>')
def export_word(student_id):
    """导出Word文档（棕色模板）"""
    from export import export_to_word
    student = Student.query.get_or_404(student_id)
    output_path = export_to_word(student, BASE_DIR)
    return send_file(output_path, as_attachment=True, 
                     download_name=f'{student.name}_小升初简历.docx')

@app.route('/export/word/<int:student_id>/green')
def export_word_green(student_id):
    """导出Word文档（绿色模板 - 基于简历模板1.pdf）"""
    from export import export_to_word_green
    student = Student.query.get_or_404(student_id)
    output_path = export_to_word_green(student, BASE_DIR)
    return send_file(output_path, as_attachment=True, 
                     download_name=f'{student.name}_小升初简历_绿色.docx')

@app.route('/export/pdf/<int:student_id>')
def export_pdf(student_id):
    """导出PDF文档"""
    from export import export_to_pdf
    student = Student.query.get_or_404(student_id)
    output_path = export_to_pdf(student, BASE_DIR)
    return send_file(output_path, as_attachment=True,
                     download_name=f'{student.name}_小升初简历.pdf')

@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_resume(student_id):
    """删除简历"""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

# ==================== 模板上下文 ====================

@app.context_processor
def utility_processor():
    """添加工具函数到模板上下文"""
    return {'now': datetime.now}

# ==================== 初始化 ====================

def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        print("数据库初始化完成")

if __name__ == '__main__':
    init_db()
    print(f"\n{'='*50}")
    print(f"小升初简历系统启动")
    print(f"{'='*50}")
    print(f"访问地址: http://localhost:5023")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=5023, debug=True)
