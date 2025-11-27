# -*- coding: utf-8 -*-
"""
导入现有数据到简历系统
从profile.xlsx读取信息，导入照片和证书
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 设置路径
BASE_DIR = Path(__file__).parent
RESUME_DIR = BASE_DIR.parent
UPLOAD_DIR = BASE_DIR / 'static' / 'uploads'

def import_data():
    """导入所有数据"""
    
    print("=" * 60)
    print("小升初简历系统 - 数据导入")
    print("=" * 60)
    
    # 读取profile.xlsx
    print("\n📊 正在读取 profile.xlsx...")
    import openpyxl
    
    profile_path = RESUME_DIR / 'profile.xlsx'
    wb = openpyxl.load_workbook(profile_path)
    ws = wb.active
    
    profile_data = {}
    for row in ws.iter_rows(values_only=True):
        if row[0] and row[1]:
            profile_data[row[0]] = row[1]
    
    print(f"  读取到 {len(profile_data)} 条基本信息:")
    for k, v in profile_data.items():
        print(f"    {k}: {v}")
    
    # 解析出生日期（Excel日期格式）
    birth_date = profile_data.get('出生年月', '')
    if isinstance(birth_date, (int, float)):
        # Excel日期转换
        from datetime import datetime, timedelta
        excel_date = datetime(1899, 12, 30) + timedelta(days=int(birth_date))
        birth_date = f"{excel_date.year}年{excel_date.month}月"
    
    # 导入Flask应用
    from app import app, db, Student, Award, Certificate
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 检查是否已存在
        existing = Student.query.filter_by(name='赵浩然').first()
        if existing:
            print(f"\n⚠️ 学生 '赵浩然' 已存在 (ID: {existing.id})，将更新数据...")
            student = existing
        else:
            student = Student()
            print("\n✨ 创建新学生记录...")
        
        # 设置基本信息
        student.name = '赵浩然'
        student.gender = profile_data.get('性别', '男')
        student.birth_date = birth_date
        height = profile_data.get('身高', 1.65)
        student.height = f"{int(float(height) * 100)}cm" if isinstance(height, (int, float)) else str(height)
        student.school = '北京小学'
        student.class_name = '五(13)班'
        student.district = '北京市西城区'
        student.hobbies = '围棋、足球、阅读、编程'
        
        # 自我介绍
        student.self_intro = """我叫赵浩然，是北京小学五年级(13)班的学生。我是一个阳光开朗、积极向上的男孩，热爱学习，全面发展。

在学业方面，我认真努力，成绩优异。从一年级到四年级，我连续获得校综合评价优秀生和校三好学生荣誉。2025年，我荣获西城区三好学生称号。在英语学习上，我以130分的成绩通过剑桥英语KET考试，其中写作146分表现尤为突出。在数学方面，我参加华数之星国际数学选拔赛获得二级组三等奖。

在特长方面，我学习围棋多年，已获得中国围棋协会业余2段认证，培养了逻辑思维能力和专注力。

在体育方面，我是北京小学校足球队的一员，足球运动让我懂得了团队合作的重要性。

我希望能够进入贵校学习，成为德智体美劳全面发展的优秀学生！"""

        # 家长寄语
        student.parent_message = """浩然是一个阳光开朗、热爱学习的孩子。他从小就对知识充满好奇心，学习自觉主动。在围棋学习中，他展现出良好的逻辑思维能力；在足球队训练中，他学会了团队合作。

我们很欣慰看到他不仅学业优秀，还能积极参与社会实践。他性格温和，善于与人沟通，是老师的好帮手，同学的好伙伴。

希望浩然在新的学校环境中不断进步，全面发展！"""

        # 老师评语
        student.teacher_comment = """赵浩然同学品学兼优，德智体美劳全面发展。他学习认真刻苦，成绩优异；尊敬师长，团结同学；积极参与班级活动和社会实践，有强烈的集体荣誉感。

他思维敏捷，善于思考，在围棋和数学方面表现出色。作为校足球队队员，他展现了良好的团队协作精神。

我相信他在未来的学习中会取得更大的进步！"""
        
        # 复制人像照片
        print("\n📷 正在导入人像照片...")
        photo_src = RESUME_DIR / '人像照片.png'
        if photo_src.exists():
            photo_dst = UPLOAD_DIR / 'photos' / '人像照片.png'
            photo_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(photo_src, photo_dst)
            student.photo = 'uploads/photos/人像照片.png'
            print(f"  ✓ 已复制人像照片")
        
        if not existing:
            db.session.add(student)
        db.session.commit()
        
        print(f"\n✅ 学生信息已保存 (ID: {student.id})")
        
        # 添加荣誉奖项
        print("\n🏆 正在添加荣誉奖项...")
        
        # 先删除旧的奖项
        Award.query.filter_by(student_id=student.id).delete()
        
        awards_data = [
            # 区级荣誉
            ('区级荣誉', '2025年', '西城区三好学生', '德智体美劳全面发展，获得区级表彰', 1),
            
            # 竞赛获奖
            ('竞赛获奖', '2025年3月', '华数之星国际线上数学选拔赛 二级组三等奖', '华数国际文化科技研究院颁发', 2),
            
            # 特长证书
            ('特长证书', '2024年8月', '中国围棋协会业余2段', '围棋培养了逻辑思维能力和专注力', 3),
            ('特长证书', '2025年3月', '剑桥英语KET考试 A2级别（总分130分）', '阅读110、写作146、听力125、口语137', 4),
            
            # 校级荣誉
            ('校级荣誉', '2024年', '四年级下学期：校三好学生', '', 10),
            ('校级荣誉', '2024年', '四年级上学期：校三好学生', '', 11),
            ('校级荣誉', '2023年', '三年级：红领巾奖章三星章', '', 12),
            ('校级荣誉', '2023年', '三年级：校级优秀中队干部', '', 13),
            ('校级荣誉', '2023年', '三年级下学期：校综合评价优秀生', '', 14),
            ('校级荣誉', '2022年', '二年级：校级优秀中队干部', '', 15),
            ('校级荣誉', '2022年', '二年级下学期：校综合评价优秀生', '', 16),
            ('校级荣誉', '2022年', '二年级上学期：校综合评价优秀生', '', 17),
            ('校级荣誉', '2021年', '一年级下学期：校综合评价优秀生', '', 18),
            ('校级荣誉', '2021年', '一年级上学期：校综合评价优秀生', '', 19),
            
            # 体育活动
            ('体育活动', '', '北京小学校足球队队员', '培养了团队协作精神和拼搏意识', 20),
            
            # 社会实践
            ('社会实践', '', '天安门广场志愿者活动', '积极参与社会公益活动', 21),
        ]
        
        for cat, date, title, desc, order in awards_data:
            award = Award(
                student_id=student.id,
                category=cat,
                date=date,
                title=title,
                description=desc,
                order=order
            )
            db.session.add(award)
        
        db.session.commit()
        print(f"  ✓ 已添加 {len(awards_data)} 项荣誉奖项")
        
        # 导入证书照片
        print("\n📜 正在导入证书照片...")
        
        # 先删除旧的证书
        Certificate.query.filter_by(student_id=student.id).delete()
        
        cert_dir = RESUME_DIR / 'certificate'
        cert_files = [
            ('区三好学生证书', '区三好学生.jpg', '奖状'),
            ('剑桥KET成绩单', 'KET成绩.jpg', '证书'),
            ('华数之星三等奖', '华数之星三等奖.jpg', '证书'),
            ('围棋业余二段', '围棋二段.jpg', '证书'),
            ('红领巾奖章三星章', '三年级红领巾优秀奖章.jpg', '奖状'),
            ('校足球队合影', '校足球队.jpg', '活动照片'),
            ('志愿者活动', '志愿者活动.jpg', '活动照片'),
            ('足球训练', '足球训练.jpg', '活动照片'),
        ]
        
        cert_count = 0
        for name, filename, category in cert_files:
            src = cert_dir / filename
            if src.exists():
                # 复制文件
                dst_dir = UPLOAD_DIR / 'certificates'
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst = dst_dir / filename
                shutil.copy2(src, dst)
                
                # 创建数据库记录
                cert = Certificate(
                    student_id=student.id,
                    name=name,
                    image_path=f'uploads/certificates/{filename}',
                    category=category,
                    order=cert_count
                )
                db.session.add(cert)
                cert_count += 1
                print(f"  ✓ {name}")
        
        db.session.commit()
        print(f"\n  共导入 {cert_count} 张证书照片")
        
        print("\n" + "=" * 60)
        print("✅ 数据导入完成！")
        print("=" * 60)
        print(f"\n📋 简历信息:")
        print(f"   学生ID: {student.id}")
        print(f"   姓名: {student.name}")
        print(f"   学校: {student.school}")
        print(f"   班级: {student.class_name}")
        print(f"   出生日期: {student.birth_date}")
        print(f"   身高: {student.height}")
        print(f"   荣誉奖项: {len(awards_data)} 项")
        print(f"   证书照片: {cert_count} 张")
        print(f"\n🌐 查看简历: http://localhost:5023/preview/{student.id}")
        print(f"📝 编辑简历: http://localhost:5023/edit/{student.id}")

if __name__ == '__main__':
    import_data()

