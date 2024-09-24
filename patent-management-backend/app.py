from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 配置 SQLite 数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 定义客户表
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

# 定义员工表
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# 定义案件表
class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    patent_number = db.Column(db.String(100), nullable=False)
    patent_name = db.Column(db.String(200), nullable=False)
    client_delivery_time = db.Column(db.DateTime, nullable=False)
    review_result = db.Column(db.String(50), nullable=True)  # 审查结果：授权、驳回、涉非
    authorization_time = db.Column(db.DateTime, nullable=True)  # 授权时间

    client = db.relationship('Client', backref=db.backref('cases', lazy=True))

# 定义任务表
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee_delivery_time = db.Column(db.DateTime, nullable=False)
    task_amount = db.Column(db.Float, nullable=False)

    case = db.relationship('Case', backref=db.backref('tasks', lazy=True))
    employee = db.relationship('Employee', backref=db.backref('tasks', lazy=True))

# 创建数据库
with app.app_context():
    db.create_all()

# 获取所有客户
@app.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    client_list = [{"id": c.id, "name": c.name, "description": c.description} for c in clients]
    return jsonify(client_list)

# 获取所有员工
@app.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    employee_list = [{"id": e.id, "name": e.name} for e in employees]
    return jsonify(employee_list)

# 获取所有案件
@app.route('/cases', methods=['GET'])
def get_cases():
    cases = Case.query.all()
    case_list = [{"id": c.id, "client_id": c.client_id, "patent_number": c.patent_number, "patent_name": c.patent_name,
                  "client_delivery_time": c.client_delivery_time, "review_result": c.review_result,
                  "authorization_time": c.authorization_time} for c in cases]
    return jsonify(case_list)

# 获取所有任务
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    task_list = [{"id": t.id, "case_id": t.case_id, "employee_id": t.employee_id,
                  "employee_delivery_time": t.employee_delivery_time, "task_amount": t.task_amount} for t in tasks]
    return jsonify(task_list)

# 创建客户
@app.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    new_client = Client(name=data['name'], description=data.get('description'))
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"message": "Client created successfully!"}), 201

# 创建员工
@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    new_employee = Employee(name=data['name'])
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({"message": "Employee created successfully!"}), 201

# 创建案件
from datetime import datetime

# 创建案件
@app.route('/cases', methods=['POST'])
def create_case():
    data = request.json
    try:
        # 将字符串转换为 datetime 对象
        client_delivery_time = datetime.strptime(data['client_delivery_time'], '%Y-%m-%d')
        authorization_time = datetime.strptime(data['authorization_time'], '%Y-%m-%d')
        
        new_case = Case(
            client_id=data['client_id'],
            patent_number=data['patent_number'],
            patent_name=data['patent_name'],
            client_delivery_time=client_delivery_time,  # 使用 datetime 对象
            review_result=data.get('review_result'),
            authorization_time=authorization_time  # 使用 datetime 对象
        )
        db.session.add(new_case)
        db.session.commit()
        return jsonify({"message": "Case created successfully!"}), 201
    except ValueError as e:
        return jsonify({"message": f"Invalid data: {str(e)}"}), 400


# 创建任务
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    new_task = Task(
        case_id=data['case_id'],
        employee_id=data['employee_id'],
        employee_delivery_time=datetime.strptime(data['employee_delivery_time'], '%Y-%m-%d'),
        task_amount=data['task_amount']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created successfully!"}), 201

# 更新案件的审查结果和授权时间
@app.route('/cases/<int:id>', methods=['PUT'])
def update_case(id):
    case = Case.query.get(id)
    if not case:
        return jsonify({"message": "Case not found"}), 404

    data = request.json
    case.review_result = data.get('review_result', case.review_result)
    case.authorization_time = datetime.strptime(data['authorization_time'], '%Y-%m-%d') if 'authorization_time' in data else case.authorization_time

    db.session.commit()
    return jsonify({"message": "Case updated successfully!"})

# 更新任务
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.json
    task.employee_delivery_time = datetime.strptime(data['employee_delivery_time'], '%Y-%m-%d') if 'employee_delivery_time' in data else task.employee_delivery_time
    task.task_amount = data.get('task_amount', task.task_amount)

    db.session.commit()
    return jsonify({"message": "Task updated successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
