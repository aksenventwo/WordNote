from flask import Flask
from flask import request
from flask import render_template
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
from flask import redirect
from flask import url_for
from flask import session
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'xiaoshengzou note is very good'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

class Notes(db.Model):
	__tablename__ = 'notes'
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(128), index=True)
	create_time = db.Column(db.DateTime, default=datetime.utcnow())

	def __str__(self):
		return 'Notes %r' % self.name

class InputForm(Form):
	content = StringField('Input Your Note', validators=[Required()])
	submit = SubmitField('Submit')


class SearchForm(Form):
	search = StringField('Search', validators=[Required()])
	submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
	form = InputForm()
	if form.validate_on_submit():
		c = Notes(content=form.content.data)
		db.session.add(c)
		form.content.data = ''
		return redirect(url_for('notes'))
	return render_template('index.html', current_time=datetime.utcnow(), form=form)
  

@app.route('/notes', methods=['GET','POST'])
def notes():
	page = request.args.get('page', 1, type=int)
	form = SearchForm()
	pagination = Notes.query.order_by(Notes.id.desc()).paginate(page, per_page=10 ,error_out=False)
	notes = pagination.items
	if form.validate_on_submit():
		note = form.search.data
		session['note'] = note
		return redirect(url_for('notes'))
	note = session.get('note')
	if note is not None:
		pagination = Notes.query.filter(Notes.content.ilike("%"+note+"%")).paginate(page, error_out=False)
		notes = pagination.items
		session['note'] = None
	count = Notes.query.count()
	return render_template('notes.html', notes=notes, pagination=pagination ,form=form, count=count)


@app.route('/deleteNote',methods=['POST'])
def deleteNote():
	id = request.values.get('id', 0, type=int)
	note = Notes.query.filter_by(id=id).first()
	if note is not None:
		db.session.delete(note)
		return 'ok'
	else:
	 	return 'fail'

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404



if __name__ == '__main__':
	#app.run(debug=True)
	manager.run()

