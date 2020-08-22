from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://engelbrk@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

class TodoList(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  todos = db.relationship('Todo', backref='list', lazy=True)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    todo = Todo(description=description, completed=False)
    db.session.add(todo)
    db.session.commit()
    body['id'] = todo.id
    body['completed'] = todo.completed
    body['description'] = todo.description
    body['list_id'] = todo.list_id
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/<newDeleted>/deleted', methods=['POST'])
def delete_todo(newDeleted):
    try:
        todo = Todo.query.get(newDeleted)
        db.session.delete(todo)
        db.session.commit()
    except:
        print('Except')
        db.session.rollback()
    finally:
        print('Finally')
        db.session.close()
    return redirect(url_for('index'))

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  return render_template('index.html',
  lists = TodoList.query.all(),
  todos=Todo.query.filter_by(list_id = list_id).order_by('id').all()
  )

@app.route('/')
def index():
  return redirect(url_for('get_list_todos', list_id=2))