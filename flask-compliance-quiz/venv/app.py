import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
app = Flask(__name__)
CORS(app)

# 获取当前文件的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# 配置SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'compliance_quiz.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    dimension = db.Column(db.String(255), nullable=False)
    yes_score = db.Column(db.Integer, nullable=False)
    no_score = db.Column(db.Integer, nullable=False)
    allow_na = db.Column(db.Boolean, nullable=False, default=False)  # 新增字段

class InitializationFlag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    initialized = db.Column(db.Boolean, nullable=False, default=False)

class EvaluationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_score = db.Column(db.Float, nullable=False)
    dimension_scores = db.Column(db.Text, nullable=False)  # JSON string
    answers = db.Column(db.Text, nullable=False)  # JSON string

def initialize_database():
    
    print(InitializationFlag.query.filter_by(id=1).first())
    if not InitializationFlag.query.filter_by(id=1).first():
        print(' 初始化数据库...')
        questions = [
            ("企业近期是否存在违反数据相关法律法规或其他可能导致重大不利影响的行为？（如是否面临过网络安全、数据安全的执法活动，或者遇到过数据安全事件）", "主体合规及组织建设", 10, 15,False),
            ("企业是否接到过用户有关数据隐私的投诉？", "主体合规及组织建设", 10, 15,False),
            ("是否建立健全企业的数据安全管理架构，明确各部门在数据安全方面的职责分工？", "主体合规及组织建设", 15, 10,False),
            ("是否依法指定了数据安全负责人、个人信息保护负责人和网络安全负责人？", "主体合规及组织建设", 15, 10,False),
            ("是否设立专职部门或岗位负责企业各数据处理环节的安全工作？", "主体合规及组织建设", 15, 10,False),
            ("是否制定并切实执行数据安全管理制度，并定期检讨和更新？", "主体合规及组织建设", 15, 10,False),
            ("企业是否购买过网络安全保险？", "主体合规及组织建设", 20, 10,False),
            ("是否进行过企业数据的盘点？", "技术措施及数据分类分级", 10, 15,False),
            ("是否保留企业数据流的记录？", "技术措施及数据分类分级", 10, 15,False),
            ("是否针对个人信息等采取加密、去识别化等技术保护措施？", "技术措施及数据分类分级", 15, 10,False),
            ("是否通过技术手段建立数据目录，实现对各类数据的识别和管控？", "技术措施及数据分类分级", 15, 10,False),
            ("是否采取加密存储、身份验证、访问控制等技术手段，确保数据存储和使用安全？", "技术措施及数据分类分级", 15, 10,False),
            ("是否采取有效技术手段防范网络攻击，保障网络系统安全？", "技术措施及数据分类分级", 15, 10,False),
            ("是否制定数据分类分级管理规范，并形成分级清单？", "技术措施及数据分类分级", 15, 10,False),
            ("是否落实分级保护要求，建立分级数据的管理、维护和更新机制？", "技术措施及数据分类分级", 15, 10,False),
            ("是否建立信息安全事件应急响应机制？", "技术措施及数据分类分级", 15, 10,False),
            ("是否制定并执行覆盖全生命周期的数据安全管理策略和规程？", "数据全生命周期管理", 15, 10,False),
            ("是否草拟了发送给消费者、公司用户客户代表、其他商业伙伴的隐私政策和通知（告知与其有关的个人信息的处理情况）？", "数据全生命周期管理", 15, 10,False),
            ("企业直接营销或者间接营销是否经过客户同意，并保留退出机制？", "数据全生命周期管理", 15, 10,False),
            ("数据收集是否制定明确的目的、方式、范围等操作流程，并进行风险评估？", "数据全生命周期管理", 15, 10,False),
            ("数据存储是否明确存储期限、地点、加密要求，并实现分级分域存储？", "数据全生命周期管理", 15, 10,False),
            ("数据存储是否明确账号权限管理、访问控制、日志记录等管理要求？", "数据全生命周期管理", 15, 10,False),
            ("数据传输是否制定安全传输策略，并采取检测和管控措施？", "数据全生命周期管理", 15, 10,False),
            ("数据使用是否建立审批和审计机制，明确使用限制和安全合规要求？", "数据全生命周期管理", 15, 10,False),
            ("对外提供数据前是否开展风险评估，并采取审批制度和安全保护措施？", "数据全生命周期管理", 15, 10,False),
            ("是否制定并执行数据销毁的审批机制，明确销毁对象、原因、方式等？", "数据全生命周期管理", 15, 10,False),
            ("是否对数据销毁过程进行记录和审计？", "数据全生命周期管理", 15, 10,False),
            ("是否制定合作方数据安全能力评估标准，并开展评估和相应管理？", "第三方和员工管理", 15, 10,False),
            ("是否整理了有权访问数据的服务商清单，并对其进行尽调？", "第三方和员工管理", 15, 10,False),
            ("是否有对数据受托处理者的尽调或审计机制？", "第三方和员工管理", 15, 10,False),
            ("应用人脸识别等生物识别技术时，是否为员工或用户提供其他可选方案？", "第三方和员工管理", 15, 10,False),
            ("是否建立完善的员工个人信息保护管理制度？（如是否向员工发布计算机安全政策、信息安全政策等文件）", "第三方和员工管理", 15, 10,False),
            ("对员工邮箱、电话等系统监控时，是否事先告知监控措施和范围？", "第三方和员工管理", 15, 10,False),
            ("是否根据工作岗位设计差异化的员工个人信息访问权限？", "第三方和员工管理", 15, 10,False),
            ("是否与可能接触员工信息的人员签订保密协议？", "第三方和员工管理", 15, 10,False),
            ("是否定期开展员工数据合规和个人信息保护培训，并保留记录？", "第三方和员工管理", 15, 10,False),
            ("是否公开发布隐私政策等个人信息处理规则？", "APP合规(含小程序、官网、公众号等)", 15, 10,False),
            ("是否采取主动同意的方式收集个人信息？", "APP合规(含小程序、官网、公众号等)", 15, 10,True),
            ("隐私政策内容是否与APP实际处理个人信息的行为一致？", "APP合规(含小程序、官网、公众号等)", 15, 10,True),
            ("是否存在超出隐私政策范围收集个人信息的情况？", "APP合规(含小程序、官网、公众号等)", 15, 10,True),
            ("是否采取明文方式传输个人敏感信息？", "APP合规(含小程序、官网、公众号等)", 15, 10,True),
            ("是否告知用户关闭权限的路径？关闭授权后，是否仍在使用相关个人信息？", "APP合规(含小程序、官网、公众号等)", 15, 10,True),
            ("是否为用户提供删除个人信息的便利渠道？", "APP合规(含小程序、官网、公众号等)", 15, 10,True),
            ("是否建立个人信息保护影响评估机制？", "APP合规(含小程序、官网、公众号等)", 15, 10,True),
            ("是否定期对数据收集工具进行安全测试和优化？", "APP合规(含小程序、官网、公众号等)", 15, 10,True),
            ("公开收集数据时，是否对收集对象、内容、方式进行合规性评估？", "其他合规要求", 15, 10,True),
            ("自主生产数据时，是否具有独立性，不存在侵犯他人权利的情况？", "其他合规要求", 15, 10,True),
            ("获取数据时，是否要求提供方对来源合法性作出承诺，明确使用目的、范围？", "其他合规要求", 15, 10,True),
            ("涉及个人信息时，是否履行告知义务，并为个人信息主体提供方便的权利行使渠道？", "其他合规要求", 15, 10,True),
            ("是否制定并实施网络安全保护措施，并针对潜在风险定期进行安全演练和测试？", "其他合规要求", 15, 10,False),
            ("是否与所有接触敏感数据的内外部人员签订数据保密协议，并进行定期复审？", "其他合规要求", 15, 10,True),
            ("是否存在植入病毒木马、违规收集信息等危害网络安全的行为？", "其他合规要求", 15, 10,False),
            ("是否存在干扰竞争对手正常经营、强制推广软件等不正当竞争行为？", "其他合规要求", 15, 10,False),
            ("数据跨境传输时，是否采取相关合规保护措施？", "其他合规要求", 15, 10,True),
            ("是否根据法律法规要求，保存特定数据达到规定期限？", "其他合规要求", 15, 10,False),
            ("是否对软件开发商等外部合作方开展数据合规评估和管理？", "其他合规要求", 15, 10,True),
            ("是否建立响应个人信息主体权利要求的机制，如删除、撤回同意等？", "其他合规要求", 15, 10,True),
            ("是否对委托加工、共享等数据处理行为进行合规性评估和管理？", "其他合规要求", 15, 10,True),
            ("是否建立数据安全审计制度，定期引入第三方开展审计？", "其他合规要求", 15, 10,False),
            ("是否制定数据安全事件应急预案，并定期开展演练？", "其他合规要求", 15, 10,False),
            ("是否根据不同业务场景制定差异化的数据合规制度和技术措施？", "其他合规要求", 15, 10,False),
            ("是否建立标准化的数据处理协议，涵盖数据提供、委托处理和共享等环节，以确保所有数据活动符合法律法规要求？", "其他合规要求", 15, 10,False)
        ]

        for text, dimension, yes_score, no_score,allow_na in questions:
            question = Question(text=text, dimension=dimension, yes_score=yes_score, no_score=no_score, allow_na=allow_na)
            db.session.add(question)
        
        flag = InitializationFlag(id=1, initialized=True)
        db.session.add(flag)

        db.session.commit()

@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    result = [
        {
            'id': question.id,
            'text': question.text,
            'dimension': question.dimension,
            'yesScore': question.yes_score,
            'noScore': question.no_score,
            'allowNa': question.allow_na
        }
        for question in questions
    ]
    return jsonify(result)

@app.route('/add-question', methods=['POST'])
def add_question():
    data = request.json
    new_question = Question(
        text=data['text'],
        dimension=data['dimension'],
        yes_score=data['yesScore'],
        no_score=data['noScore']
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added successfully!'}), 201

@app.route('/save-evaluation', methods=['POST'])
def save_evaluation():
    data = request.json
    new_evaluation = EvaluationResult(
        total_score=data['totalScore'],
        dimension_scores=data['dimensionScores'],
        answers=data['answers']
    )
    db.session.add(new_evaluation)
    db.session.commit()
    return jsonify({'message': 'Evaluation saved successfully!'}), 201

@app.route('/evaluations', methods=['GET'])
def get_evaluations():
    evaluations = EvaluationResult.query.all()
    result = [
        {
            'id': evaluation.id,
            'date_time': evaluation.date_time,
            'total_score': evaluation.total_score,
            'dimension_scores': json.loads(evaluation.dimension_scores),
            'answers': json.loads(evaluation.answers)
        }
        for evaluation in evaluations
    ]
    return jsonify(result)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建数据库表
        initialize_database()  # 初始化数据库
    app.run(debug=True)
