from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost:3306/job'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100))
    role = db.Column(db.String(100))
    location = db.Column(db.String(100))
    responsibilities = db.Column(db.Text)
    requirements = db.Column(db.Text)
    salary = db.Column(db.String(100))

    def __repr__(self):
        return f"<Job {self.job_title}>"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    education = db.Column(db.Text)
    workexp = db.Column(db.Text)
    resume = db.Column(db.String(100))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id') , nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"


@app.route('/')
def home():
    return redirect(url_for('user'))


@app.route('/jobs', methods=['POST'])
def user():
    if request.method == 'POST':
        # Validate form data
        job_title = request.form.get('jobTitle')
        role = request.form.get('role')
        location = request.form.get('location')
        responsibilities = request.form.get('responsibilities')
        requirements = request.form.get('requirements')
        salary = request.form.get('salary')

        if not job_title or not role or not location:
            return "Please fill in all required fields"

        # Store the data in the database
        job = Job(
            job_title=job_title,
            role=role,
            location=location,
            responsibilities=responsibilities,
            requirements=requirements,
            salary=salary
        )
        db.session.add(job)
        db.session.commit()

        return redirect(url_for('apply', job_id=job.id))  # Pass the newly created job ID to the apply route

    return render_template('form.html')


@app.route("/apply", methods=['GET', 'POST'])
def apply():
    if request.method == 'GET':
        job_id = request.args.get('job_id')
        print(job_id)
        job = Job.query.filter_by(id=job_id).first()
        return render_template('apply.html', job=job)

    if request.method == 'POST':

        # Validate form data
        name = request.form.get('name')
        email = request.form.get('email')
        linkedin = request.form.get('linkedin')
        education = request.form.get('education')
        workexp = request.form.get('workexp')   
        resume = request.form.get('resume')
        job_id = request.form.get('job_id')

        if not name or not email:
            return "Please fill in all required fields"

        # Store the data in the database
        user = User(
            name=name,
            email=email,
            linkedin=linkedin,
            education=education,
            workexp=workexp,
            resume=resume,
            job_id=job_id  # Pass the job_id to the User constructor
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('applied_jobs'))


@app.route('/jobs', methods=['GET'])
def jobs():
    jobs = Job.query.all()
    return render_template('jobs.html', jobs=jobs)


@app.route('/applied_jobs', methods=['GET'])
def applied_jobs():
    users_jobs = db.session.query(User, Job).join(Job).all()
    matched_jobs = []
    for user, job in users_jobs:
        if user.job_id == job.id:
            matched_jobs.append((user, job))
    return render_template('appliedjobs.html', applied_jobs= matched_jobs)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
